from django import forms
from django.db import models


class RequestTypes(models.TextChoices):
    OSR = ('OSR', 'Release Internal Project as Open Source')
    OSC = ('OSC', 'Contribute to External Open Source Project')
    RES = ('RES', 'Salesforce Research - NOT READY')
    LAB = ('LAB', 'Salesforce Lab Program - NOT READY')


"""
    for i in RequestTypes:
        print(i.name)
        print(i.value)
        print(i.label)
"""


class GHOrgs(models.TextChoices):
    SFMISC = ('salesforce-misc', 'https://github.com/salesforce-misc/')
    SF = ('salesforce', 'https://github.com/salesforce/')
    FDC = ('forcedotcom', 'https://github.com/forcedotcom/')


class TaskState(models.IntegerChoices):
    NOT_STARTED = (0, 'Not Started')
    IN_PROCESS = (1, 'In Process')
    DENIED = (2, 'Denied')
    CANCELLED = (3, 'Cancelled')
    COMPLETE = (4, 'Completed')
    ERROR_COMPLETE = (5, 'Task Error')


class Req(models.Model):
    request_name = models.TextField('request_name', unique=True, max_length=50)
    slug_name = models.SlugField(unique=True, max_length=50)
    project_name = models.TextField('project_name', null=True)
    requester = models.EmailField()
    slack = models.TextField(blank=True, null=True)

    type = models.TextField(choices=RequestTypes.choices,
                            default=RequestTypes.OSR)

    opened = models.DateTimeField(null=True)
    closed = models.DateTimeField(null=True)
    state = models.IntegerField(choices=TaskState.choices, null=True)
    updated = models.DateTimeField(null=True)
    current_task = models.ForeignKey('Task', on_delete=models.CASCADE, null=True)

    class Meta:
        ordering = ['opened']

    def __str__(self):
        return self.request_name


# LAB - Salesforce Lab
class Slpmodel(models.Model):
    request_name = models.TextField('request_name', unique=True, max_length=50)
    request_id = models.ForeignKey('Req', on_delete=models.CASCADE)
    start_with = models.TextField('start_with', null=True)
    repository_name = models.TextField('repository_name', null=True)
    project_description = models.TextField('project_description', null=True)
    lab_app = models.TextField('lab_app', null=True)
    author = models.TextField('author', null=True)
    security = models.TextField('security', null=True)

    def __str__(self):
        return self.request_name


# OSR - Open Source Release (of internal project)
class Osrmodel(models.Model):
    request_name = models.TextField('request_name', unique=True, max_length=50)
    request_id = models.ForeignKey('Req', on_delete=models.CASCADE)
    project_name = models.TextField('project_name', null=True)
    work_nature = models.TextField('work_nature', null=True)
    vp_email = models.EmailField('vp_email', null=True)
    vp_approval = models.BooleanField('vp_approval', null=True)
    manager_email = models.EmailField('manager_email', null=True)
    manager_approval = models.BooleanField('manager_approval', null=True)
    first_time = models.BooleanField('first_time', null=True)
    current_repository_url = models.TextField('current_repository_url', null=True)
    readme_url = models.TextField('readme_url', null=True)
    license = models.TextField('license', null=True)
    third_party_code = models.BooleanField('third_party_code', null=True)
    product_ecosystem = models.TextField('product_ecosystem', null=True)
    relation_to_product = models.TextField('relation_to_product', null=True)
    #
    # Dependency License Report Task Data
    dependency_list = models.TextField('dependency_list', blank=True, null=True)
    #
    # Github Repo Info Task Data
    github_org = models.TextField(choices=GHOrgs.choices,
                                  default=GHOrgs.SFMISC, null=True)
    github_repo = models.TextField(max_length=35, null=True)    # These will be slugs
    github_admin = models.TextField(null=True)   # JSON list
    #
    # ProdSec Approval Task Data
    tmp_request = models.BooleanField('tmp_request', null=True)
    app_ex = models.BooleanField('app_ex', null=True)
    sec_ass = models.BooleanField('sec_ass', null=True)

    def __str__(self):
        return self.request_name


# OSC - Open Source Contribution
class Oscmodel(models.Model):
    request_name = models.TextField('request_name', unique=True, max_length=50)
    request_id = models.ForeignKey('Req', on_delete=models.CASCADE)
    project_name = models.TextField('project_name', null=True)
    work_nature = models.TextField('work_nature', null=True)
    manager_email = models.EmailField('manager_email', null=True)
    manager_approval = models.BooleanField('manager_approval', null=True)
    first_time = models.BooleanField('first_time', null=True)
    current_repository_url = models.TextField('current_repository_url', null=True)
    scope = models.TextField('scope', null=True)
    license = models.TextField('license', null=True)
    have_cla = models.BooleanField('have_cla', null=True)
    cla_url = models.TextField('cla_url', null=True)
    size_of_change = models.TextField('size_of_change', null=True)

    def __str__(self):
        return self.request_name


# RES - Salesforce Research
class Srmodel(models.Model):
    request_name = models.TextField('request_name', unique=True, max_length=50)
    request_id = models.ForeignKey('Req', on_delete=models.CASCADE)
    conference = models.TextField('conference', null=True)
    paper_title = models.TextField('paper_title', null=True)
    exp_results = models.TextField('exp_results', null=True)
    approval = models.BooleanField('approval', null=True)
    patent_application = models.TextField('patent_application', null=True)
    code_released = models.TextField('code_released', null=True)
    code_released_likely = models.TextField('code_released_likely', null=True)
    code_third_party = models.TextField('code_third_party', null=True)

    def __str__(self):
        return self.request_name


class Adminmodel(models.Model):
    admin_id = models.TextField('admin_id', null=True)
    admin_name = models.TextField('admin_name', null=True)
    admin_email = models.TextField('admin_email', null=True)
    admin_program = models.TextField('admin_program', null=True)

    def __str__(self):
        return self.admin_id


class TaskList(models.Model):
    id = models.TextField(primary_key=True)  # alphanum ID of this task
    name = models.TextField(blank=True)  # Name of this task
    request_type = models.TextField(choices=RequestTypes.choices, blank=True,
                                    null=True)  # This task is associated w/ this req type (eg: 'OSR')
    description = models.TextField(blank=True, null=True)  # Description of this task
    order = models.IntegerField(blank=True, null=True)  # Which order this task should be done
    html_file = models.TextField(blank=True, null=True)
    action_func = models.TextField(blank=True, null=True)
    action_hook = models.TextField(blank=True, null=True)
    active = models.BooleanField(default=True, null=True)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name


class Approver(models.Model):
    tasklist = models.ForeignKey('TaskList', on_delete=models.CASCADE)
    email = models.EmailField(null=True)  # Their email
    slack = models.TextField(blank=True, null=True)


class Admin(models.Model):
    type = models.TextField(choices=RequestTypes.choices,
                            default=RequestTypes.OSR)
    email = models.EmailField(null=True)  # Their email
    slack = models.TextField(blank=True, null=True)


class Task(models.Model):
    tasklist = models.ForeignKey('TaskList', on_delete=models.CASCADE)
    request_id = models.ForeignKey('Req', on_delete=models.CASCADE)
    request_type = models.TextField(null=True)  # for search ease; also accessible via tasklist.request_type
    state = models.IntegerField(choices=TaskState.choices, null=True)  # Which state this task is in
    opened = models.DateTimeField(null=True)  # Timestamp when task was opened
    closed = models.DateTimeField(null=True)  # Timestamp when task was closed
    order = models.IntegerField(null=True)  # Search ease; also accessible via tasklist.order
    email = models.EmailField(null=True)  # who updated/approved/denied/etc it?
    action_data = models.TextField(blank=True, null=True)
    action_response = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['order']


class Comment(models.Model):
    task = models.ForeignKey('Task', on_delete=models.CASCADE)  # Task.id associated w/ this comment
    email = models.EmailField(null=True)  # who made it?
    name = models.TextField(blank=True, null=True)  # Their name
    content = models.TextField(null=True)  # And the comment itself
    created = models.DateTimeField(null=True)  # Timestamp when comment was created

    class Meta:
        ordering = ['created']
