import email
import calendar
import datetime
import json
import os
#import github

from django.contrib.auth.models import User

from django.http import HttpResponseRedirect

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

# from .forms import RequestCreationForm
# from .models import Req

from pathlib import Path
from slack_sdk import WebClient as SlackClient
from dotenv import load_dotenv

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

from calendar import HTMLCalendar
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import User

from .models import Req, Oscmodel, Osrmodel, Slpmodel, Srmodel, TaskList, Task, TaskState
from .models import RequestTypes, Comment, Approver, Admin
from .forms import ReqForm, OscForm, OsrForm, SlpForm, SrForm, TaskForm, CommentForm
from .dicts import form_dict, model_dict, show_dict, thtml_dict
from .actions import do_action, gh_get_token

from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.text import slugify
from django.db.utils import IntegrityError

from django.conf import settings
from django.urls import reverse
from django.http import (HttpResponse, HttpResponseRedirect,
                         HttpResponseServerError)

from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt

from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.utils import OneLogin_Saml2_Utils

from django.template.defaulttags import register


#
# Template helpers to grab labels from forms info
#
@register.filter
def get_value(dictionary, key):
    return dictionary.get(key)


@register.filter
def form_work_nature(key):
    from .forms import nature
    return get_label(nature, key)


@register.filter
def form_relation(key):
    from .forms import relation
    return get_label(relation, key)


@register.filter
def form_license(key):
    from .forms import license_list
    return get_label(license_list, key)


def get_label(data, key):
    for n in data:
        if n[0] == key:
            return n[1]
    return key


#
# Boilerplate
#
def init_saml_auth(req):
    auth = OneLogin_Saml2_Auth(req, custom_base_path=settings.SAML_FOLDER)
    return auth


def prepare_django_request(request):
    # If server is behind proxys or balancers use the HTTP_X_FORWARDED fields
    result = {
        'https': 'on' if request.is_secure() else 'off',
        'http_host': request.META['HTTP_HOST'],
        'script_name': request.META['PATH_INFO'],
        'get_data': request.GET.copy(),
        # Uncomment if using ADFS as IdP, https://github.com/onelogin/python-saml/pull/144
        # 'lowercase_urlencoding': True,
        'post_data': request.POST.copy(),
        # 'request_uri': '/acs'
    }
    return result


def saml_attrs(request):
    attributes = False
    if 'samlUserdata' in request.session:
        if len(request.session['samlUserdata']) > 0:
            attributes = request.session['samlUserdata'].items()
    return attributes


def saml_email(request):
    return request.session.get('email')


def home(request, year=datetime.now().year, month=datetime.now().strftime('%B')):
    auth_email = saml_email(request)
    if auth_email is None and os.getenv('DISABLE_SAML') != '1':
        return redirect('login_saml')
    month = month.capitalize()
    # Convert month from name to number
    month_number = list(calendar.month_name).index(month)
    month_number = int(month_number)

    # create a calendar
    cal = HTMLCalendar().formatmonth(
        year,
        month_number)
    # Get current year
    now = datetime.now()
    current_year = now.year

    # Get current time
    time = now.strftime('%I:%M %p')
    return render(request, 'events/home.html',
                  {
                      'year': year,
                      'month': month,
                      'month_number': month_number,
                      'current_year': current_year,
                      'time': time,
                      'auth_email': auth_email,
                  })


@never_cache
def login_saml(request):
    req = prepare_django_request(request)
    auth = init_saml_auth(req)
    sso_built_url = auth.login()
    if 'next' in request.GET:
        redirect_to = OneLogin_Saml2_Utils.get_self_url(req) + request.GET['next']
        sso_built_url = auth.login(redirect_to)
    return HttpResponseRedirect(sso_built_url)


@never_cache
@csrf_exempt
def acs(request):
    if request.method != 'POST':
        return HttpResponse('Method not allowed.', status=405)
    req = prepare_django_request(request)
    auth = init_saml_auth(req)

    auth.process_response()
    errors = auth.get_errors()

    if auth.is_authenticated():
        request.session['samlUserdata'] = auth.get_attributes()
        request.session['email'] = auth.get_nameid()
        return redirect('home')

        # if 'RelayState' in req['post_data'] \
        #        and OneLogin_Saml2_Utils.get_self_url(req) != req['post_data']['RelayState']:
        #    url = auth.redirect_to(req['post_data']['RelayState'])
        #    return HttpResponseRedirect(url)
        # else:
        #    return HttpResponseRedirect('/')

    errs = ' '.join(errors)
    return HttpResponse(content=errs, status=400)


def attrs(request):
    return render(request, 'events/attrs.html',
                  {
                      'attributes': saml_attrs(request),
                      'email': saml_email(request),
                  })


def is_authorized(reqo, task, auth_email):
    try:
        approvers = Approver.objects.filter(tasklist=task.tasklist)
    except Exception:
        return False
    for approver in approvers:
        if approver.email == auth_email or (approver.email == 'requester' and reqo.requester == auth_email):
            return True

    try:
        admins = Admin.objects.filter(type=task.request_type)
    except Exception:
        return False
    for admin in admins:
        if admin.email == auth_email:
            return True

    return False


#
# ############ END BOILERPLATE #############
#


def initial(request):
    auth_email = saml_email(request)
    if auth_email is None and os.getenv('DISABLE_SAML') != '1':
        return redirect('login_saml')
    submitted = False
    if request.method == 'POST':
        form = ReqForm(request.POST)
        if form.is_valid():
            req = form.save(commit=False)
            req.slug_name = slugify(req.request_name)
            req.requester = auth_email
            req.state = TaskState.NOT_STARTED
            req.opened = timezone.now()
            try:
                req.save()
            except IntegrityError:
                return render(request, 'events/initial.html',
                              {
                                  'form': form,
                                  'submitted': submitted,
                                  'auth_email': auth_email,
                                  'error_msg': '<div class="alert alert-warning" role="alert">Request Name was not unique</div>',
                              })
            req_type = form.cleaned_data["type"]
            return add_ossr(request, req_type)
    else:
        form = ReqForm()
        if 'submitted' in request.GET:
            submitted = True

    return render(request, 'events/initial.html',
                  {
                      'form': form,
                      'submitted': submitted,
                      'auth_email': auth_email,
                      'error_msg': '',
                  })


def router_add(request):
    try:
        reqo = Req.objects.get(request_name=request.POST.get('request_name', ''))
    except Req.DoesNotExist:
        return initial(request)
    req_type = reqo.type
    return add_ossr(request, req_type)


def add_ossr(request, req_type):
    auth_email = saml_email(request)
    if auth_email is None and os.getenv('DISABLE_SAML') != '1':
        return redirect('login_saml')
    submitted = False
    if request.method == 'POST':
        form = form_dict[req_type](request.POST)
        if form.is_valid():
            # Get the Req model for this request
            reqo = Req.objects.get(request_name=form.cleaned_data["request_name"])
            reqo.project_name = form.cleaned_data["project_name"]
            reqo.state = TaskState.IN_PROCESS
            req = form.save(commit=False)
            req.request_id = reqo
            req.save()
            reqo.save()
            # Now load up the Tasks
            first = True
            for tl in TaskList.objects.filter(request_type=req_type):
                if not tl.active:
                    continue
                t = Task()
                t.tasklist = tl
                t.request_id = req.request_id
                t.request_type = req_type
                t.order = tl.order
                if first:
                    t.state = TaskState.IN_PROCESS
                    t.opened = timezone.now()
                    first = False
                else:
                    t.state = TaskState.NOT_STARTED
                t.save()
            envpath = Path('.') / '.env'
            load_dotenv(dotenv_path=envpath)
            client = SlackClient(token='xoxb-1814240140212-2628342876662-liTewS1U4tH3pwNus8K0JNh7')
            client.chat_postMessage(channel='oss_notif', text='You have a request')
            client.chat_postMessage(channel='oss_notif_user', text='Request Created')
            return redirect(f'show_request/{reqo.slug_name}')
        else:
            if req_type == 'OSC' or req_type == 'OSR':
                form = form_dict[req_type](
                    initial={'license': 'BSD3', 'request_name': form.cleaned_data["request_name"]})
            else:
                form = form_dict[req_type]()
    else:
        if req_type == 'OSC' or req_type == 'OSR':
            form = form_dict[req_type](initial={'license': 'BSD3'})
        else:
            form = form_dict[req_type]()
        if 'submitted' in request.GET:
            submitted = True

    title = [i.label for i in RequestTypes if i.name == req_type][0]

    return render(request, 'events/add_request.html',
                  {
                      'form': form,
                      'submitted': submitted,
                      'auth_email': auth_email,
                      'title': title,
                  })


def list_requests(request):
    auth_email = saml_email(request)
    if auth_email is None and os.getenv('DISABLE_SAML') != '1':
        return redirect('login_saml')

    type = request.GET.get('req')
    request_list = Req.objects.exclude(state=TaskState.NOT_STARTED)
    if type == 'mine':
        request_list = request_list.filter(requester=auth_email)
    elif type == 'OSR' or type == 'OSC' or type == 'LAB' or type == 'RES':
        request_list = request_list.filter(type=type)
    for req in request_list:
        req.state = [i.label for i in TaskState if i.value == req.state][0]
        req.type = [i.label for i in RequestTypes if i.name == req.type][0]
    return render(request, 'events/requests.html',
                  {
                      'request_list': request_list,
                      'auth_email': auth_email,
                  })


def show_request(request, request_id):
    return show_request_internal(request, request_id, '')


def show_request_internal(request, request_id, message):
    try:
        reqo = Req.objects.get(slug_name=request_id)
    except Req.DoesNotExist:
        return initial(request)
    slug_name = request_id
    req_type = reqo.type
    request_id = reqo.id
    auth_email = saml_email(request)
    if auth_email is None and os.getenv('DISABLE_SAML') != '1':
        return redirect('login_saml')
    oss_request = model_dict[req_type].objects.get(request_id=request_id)
    tasks = list(Task.objects.filter(request_id=request_id).exclude(state=TaskState.NOT_STARTED))
    comments = {}
    for task in tasks:
        comments[task.tasklist.id] = list(Comment.objects.filter(task=task.id))
    try:
        if tasks[-1].state != TaskState.COMPLETE:
            next_task = tasks.pop()
            form = thtml_dict.get(next_task.tasklist.id)
            if form is not None:
                form = form(instance=oss_request)
    except IndexError:
        return redirect('list_requests')
    return render(request, 'events/request.html',
                  {
                      'request': oss_request,
                      'auth_email': auth_email,
                      'tasks': tasks,
                      'form': form,
                      'next_task': next_task,
                      'request_id': request_id,
                      'oss_data': show_dict[req_type],
                      'comments': comments,
                      'slug_name': slug_name,
                      'message': message,
                  })


# Double check if a form is valid. We have some magic here pertaining to certain forms
def double_check(form):
    ret_str = ''
    ret = True
    if isinstance(form, thtml_dict.get('OSR_gri')):
        # GitHub Data

        if form.cleaned_data['github_repo'].lower() != slugify(form.cleaned_data['github_repo']):
            ret = False
            ret_str += ' Invalid Repo Name;'
        admins = [i.strip() for i in form.cleaned_data['github_admin'].split(',')]
        token = gh_get_token(form.cleaned_data['github_org'])
        g = github.Github(token)
        try:
            dummy = g.get_repo(f'{form.cleaned_data["github_org"]}/{form.cleaned_data["github_repo"]}')
            ret = False
            ret_str += ' Repo name already exists;'
        except github.UnknownObjectException:
            pass
        for admin in admins:
            try:
                dummy = g.get_user(admin)
            except github.GithubException:
                ret = False
                ret_str += f' {admin} is invalid GitHub ID;'
    return ret, ret_str


def update_request(request):
    auth_email = saml_email(request)
    if auth_email is None and os.getenv('DISABLE_SAML') != '1':
        return redirect('login_saml')
    try:
        reqo = Req.objects.get(id=request.POST['request_id'])
    except Req.DoesNotExist:
        return initial(request)
    try:
        task_id = request.POST['task_id']
        task = Task.objects.get(id=task_id)
        oss_request = model_dict[reqo.type].objects.get(request_id=reqo.id)
    except Exception:
        return redirect(f'show_request/{reqo.slug_name}')

    if not is_authorized(reqo, task, auth_email):
        return show_request_internal(request, reqo.slug_name,
                                     '<div class="alert alert-warning" role="alert">Not Authorized to Update Task</div>')

    form = thtml_dict.get(task.tasklist.id)
    if form is None:
        form = TaskForm(request.POST, instance=task)
    else:
        form = form(request.POST, instance=oss_request)
    is_valid = form.is_valid()      # We need this called so we can access cleaned data
    dc, dc_str = double_check(form)
    if is_valid and dc:
        form.save()
        # Now handle which task this relates to
        task.closed = timezone.now()
        action = request.POST.get('action', '')
        if action == 'Deny':
            task.state = TaskState.DENIED
        elif action == 'Cancel':
            task.state = TaskState.CANCELLED
        elif action in ['Mark As Completed', 'Submit']:
            task.state = TaskState.COMPLETE
        task.email = auth_email
        task.save()
        if task.state == TaskState.COMPLETE:
            tasks = Task.objects.filter(request_id=request.POST['request_id'])
            prev_task_id = None
            for t in tasks:
                if t.state == TaskState.NOT_STARTED and prev_task_id == task.id:
                    t.state = TaskState.IN_PROCESS
                    t.opened = timezone.now()
                    t.save()
                    if t.tasklist.action_func is not None:
                        do_action(t)
                    reqo.current_task = t
                    reqo.updated = t.opened
                    reqo.save()
                    break
                prev_task_id = t.id
        client = SlackClient(token='xoxb-1814240140212-2628342876662-liTewS1U4tH3pwNus8K0JNh7')
        client.chat_postMessage(channel='oss_notif_user', text='Change of Status')
        return show_request_internal(request, reqo.slug_name,
                                 '<div class="alert alert-success" role="alert">Update Successful</div>')
    ret = 'Form Validation Error:' + dc_str
    return show_request_internal(request, reqo.slug_name,
                                 f'<div class="alert alert-warning" role="alert">{ret}</div>')


def search_requests(request):
    auth_email = saml_email(request)
    if auth_email is None and os.getenv('DISABLE_SAML') != '1':
        return redirect('login_saml')
    if request.method == 'POST':
        searched = request.POST['searched']
        request_list = Req.objects.filter(request_name__icontains=searched)
        for req in request_list:
            req.state = [i.label for i in TaskState if i.value == req.state][0]
            req.type = [i.label for i in RequestTypes if i.name == req.type][0]
        return render(request, 'events/requests.html',
                      {
                          'request_list': request_list,
                          'auth_email': auth_email,
                      })


def do_comments(request):
    auth_email = saml_email(request)
    if auth_email is None and os.getenv('DISABLE_SAML') != '1':
        return redirect('login_saml')
    task_id = request.POST.get('task_id')
    if task_id is None:
        # print('task_id')
        return redirect('list_requests')
    task = Task.objects.get(id=task_id)  # cannot fail (we hope!)
    slug_name = request.POST.get('slug_name')
    if slug_name is None:
        # print('slug_name')
        return redirect('list_requests')
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.email = auth_email
            comment.task = task
            comment.created = timezone.now()
            comment.save()
    return redirect(f'show_request/{slug_name}')


def show_task(request, task_id):
    pass
