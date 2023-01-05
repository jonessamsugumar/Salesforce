import os

import github
import github3
import requests
import json
import datetime

from django.utils import timezone

from django_q.tasks import async_task, schedule
from django_q.tasks import Task as ATask
from django_q.models import Schedule

from .models import Req, Oscmodel, Osrmodel, Slpmodel, Srmodel, TaskList, TaskState
from .models import RequestTypes, Comment, Approver, Admin
from .models import Task as OssTask  # Task is used by Q


def do_action(task):
    if task.tasklist.action_func is None:  # Should never happen
        return
    if task.tasklist.action_hook is None:
        async_task(task.tasklist.action_func, task)
    else:
        async_task(task.tasklist.action_func, task, hook=task.tasklist.action_hook)


def gh_get_token(org):
    priv = os.getenv('GITHUB_APP_PRIVATE_KEY')
    gid = os.getenv('GITHUB_APP_ID')
    if priv is None or gid is None:
        return None
    priv = priv.strip().encode()
    gid = int(gid)
    gh = github3.github.GitHub()
    gh.login_as_app(priv, gid)
    for installation in gh.app_installations():
        if installation.account['login'] == org:
            gh.login_as_app_installation(priv, gid, installation.id)
            return gh.session.auth.token
    return None


def gh_add_team_to_repo(github_team, new_repo, permission):
    github_team.add_to_repos(new_repo)
    github_team.update_team_repository(new_repo, permission)


def gh_get_or_create_team(github_org, team_name):
    github_team = None
    try:
        github_team = github_org.get_team_by_slug(team_name)
    except github.UnknownObjectException:
        pass

    if not github_team:
        try:
            github_team = github_org.create_team(team_name)
        except github.GithubException:
            pass

    return github_team


def gh_ensure_repo_is_internal(access_token, new_repo):
    # print(f"Setting {new_repo.name} to visibility:internal at {new_repo.url}...")
    # https://github.com/PyGithub/PyGithub/pull/1872 will allow us to directly use PyGithub
    # Background: https://developer.github.com/changes/2019-12-03-internal-visibility-changes/
    head = {'Authorization': f'token {access_token}', 'Accept': 'application/vnd.github.nebula-preview+json'}
    url = new_repo.url
    payload = {'visibility': 'internal'}
    r = requests.patch(url, json=payload, headers=head)


def gh_setup(task: OssTask):
    try:
        oss_request = Osrmodel.objects.get(request_id=task.request_id)
    except Exception:
        return False, 'Cannot grab request data'
    access_token = gh_get_token(oss_request.github_org)
    if access_token is None:
        return False, 'GitHub access denied: No token'

    g = github.Github(access_token)
    github_org = g.get_organization(oss_request.github_org)
    repo_name = oss_request.github_repo
    try:
        new_repo = github_org.get_repo(repo_name)
        # We got a repo? That shouldn't happen.
        return False, f'Already existing repo name "{repo_name}"'
    except github.UnknownObjectException:
        # Weird pattern of try/excepts - I know...
        new_repo = github_org.create_repo(repo_name)
        if new_repo:
            ret = f'github.com/{oss_request.github_org}/{repo_name} created'
            gh_ensure_repo_is_internal(access_token, new_repo)
            github_admin_team = gh_get_or_create_team(github_org, f'{repo_name}-admin')
            if github_admin_team is None:
                ret += ' (could not create team)'  # Is this an ERROR?
            else:
                admins = [i.strip() for i in oss_request.github_admin.split(',')]
                for admin in admins:
                    try:
                        admin = g.get_user(admin)
                        github_admin_team.add_membership(admin, "maintainer")
                    except github.GithubException:
                        pass
                gh_add_team_to_repo(github_admin_team, new_repo, 'admin')
            return True, ret
        return False, f'Could not create github.com/{oss_request.github_org}/{repo_name}'


def next_round(task: OssTask):
    tasks = OssTask.objects.filter(request_id=task.request_id)
    prev_task_id = None
    for t in tasks:
        if t.state == TaskState.NOT_STARTED and prev_task_id == task.id:
            t.state = TaskState.IN_PROCESS
            t.opened = timezone.now()
            t.save()
            break
        prev_task_id = t.id


def gh_hook(atask: ATask):
    task = OssTask.objects.get(id=atask.args[0].id)
    task.closed = timezone.now()
    task.state = TaskState.COMPLETE
    task.email = '[GitHub oss-bot]'
    if atask.success:
        #
        # Note: This just means that the async call worked, but doesn't
        # imply anything about the success of the _ACTION_ performed
        #
        task.action_response = atask.result[1]
        if atask.result[0] is False:
            task.state = TaskState.ERROR_COMPLETE
    else:
        task.action_response = 'async_task error (fail)'
        task.state = TaskState.ERROR_COMPLETE
    task.save()
    next_round(task)


def gus_create_workdict(task: OssTask):
    try:
        oss_request = Osrmodel.objects.get(request_id=task.request_id)
    except Exception:
        return False, 'Cannot grab request data'

    work_req = {
        'request': {
            'program': 'Open Source Project Request TEST',
            'slug': oss_request.request_id.slug_name,
            'name': oss_request.request_id.request_name,
            'owner': oss_request.request_id.requester,
        },
        'task': {
            'id': task.id,
            'url': f'https://oss-request2.sfdc.sh/show_request/{oss_request.request_id.slug_name}',
            'label': task.tasklist.name,
            'data': {
                'foo': 'bar'
            },
            'dependencies': {
                'start': {
                    'Cloud/Product Ecosystem': oss_request.product_ecosystem,
                    'How related to Cloud': oss_request.relation_to_product,
                    'Is this a TMP Request': oss_request.tmp_request,
                    'Already reviewed as part of AppExchange review': oss_request.app_ex,
                    'Security Review covered as part of a Security Assessment': oss_request.sec_ass,
                    'Current Repo URL': oss_request.app_ex,
                    'Project Name': oss_request.project_name,
                    'License': oss_request.license,
                    '3rd Party Code': oss_request.third_party_code,
                }
            },
            'form': {
              'product-tag-name': 'Prodsec Core Adjacent Skills Group: Open Source (OSS)',
              'epic-name': 'Prodsec Security Advisory',
              'subject': '[Security Advisory] OSS Request TEST',
            },
        },
    }
    return work_req


def gus_work_order(task: OssTask):
    psk = os.getenv('PSK_GUS')
    if psk is None:
        return False, 'No GUS PSK'
    psk = 'psk ' + psk
    gus_url = os.getenv('GUS_URL')
    if gus_url is None:
        return False, 'No GUS URL'

    work_req = gus_create_workdict(task)
    headers = {"Authorization": psk}
    try:
        r = requests.post(gus_url, json=work_req, headers=headers, timeout=60)
    except requests.exceptions.Timeout:
        return False, 'GUS Submission error: Timeout'
    if r.status_code != requests.codes.created:
        return False, f'GUS Submission error: {r.text}'
    try:
        ret = json.loads(r.text)
    except Exception:
        return False, 'GUS Submission error: garbled JSON'

    ntask = OssTask.objects.get(id=task.id)
    ntask.action_data = r.text     # This will be in JSON format
    ntask.save()
    return True, f'GUS Work Order: {ret.get("state")} {ret.get("url")}'


def gus_hook(atask: ATask):
    task = OssTask.objects.get(id=atask.args[0].id)
    task.email = '[GUS oss-bot]'
    if atask.success:
        task.action_response = atask.result[1]
        if atask.result[0] is False:
            task.state = TaskState.ERROR_COMPLETE
    else:
        task.action_response = 'async_task error (fail)'
        task.state = TaskState.ERROR_COMPLETE
    if task.state == TaskState.ERROR_COMPLETE:
        task.closed = timezone.now()
        task.save()
        next_round(task)
    else:
        task.save()
        # If we successfully created a work ticket, kick off
        # periodic checks to update the status
        schedule('myapp.actions.gus_check', task.id,
                 schedule_type=Schedule.ONCE,
                 next_run=timezone.now() + datetime.timedelta(hours=6))


def close_with_state(task_id, state):
    task = OssTask.objects.get(id=task_id)
    task.state = state
    if state == TaskState.ERROR_COMPLETE:
        task.action_response += ' !!GUS Status Check Error!!'
    task.closed = timezone.now()
    task.save()
    next_round(task)


def gus_check(task_id):
    task = OssTask.objects.get(id=task_id)
    psk = os.getenv('PSK_GUS')
    if psk is None:
        return close_with_state(task.id, TaskState.ERROR_COMPLETE)
    psk = 'psk ' + psk
    gus_url = os.getenv('GUS_URL')
    if gus_url is None:
        return close_with_state(task.id, TaskState.ERROR_COMPLETE)
    try:
        data = json.loads(task.action_data)
    except Exception:
        return close_with_state(task.id, TaskState.ERROR_COMPLETE)

    head = {'Authorization': psk}
    r = requests.get(gus_url + f'?url={data.get("url")}', headers=head)

    try:
        ret = json.loads(r.text)
    except Exception:
        return close_with_state(task.id, TaskState.ERROR_COMPLETE)

    status = ret.get('state')
    if status == 'CANCELLED':
        return close_with_state(task.id, TaskState.CANCELLED)
    elif status == 'COMPLETED':
        return close_with_state(task.id, TaskState.COMPLETE)
    else:
        schedule('myapp.actions.gus_check', task.id,
                 schedule_type=Schedule.ONCE,
                 next_run=timezone.now() + datetime.timedelta(hours=6))
