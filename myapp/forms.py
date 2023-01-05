from django import forms
from django.db.models import fields
from django.forms import ModelForm
from .models import Req, Oscmodel, Osrmodel, Srmodel, Slpmodel, RequestTypes, GHOrgs, Task, Comment


def get_label(key, data):
    for d in data:
        if d[0] == key:
            return d[1]
    return d[0]


options = [
    (True, 'Yes'),
    (False, 'No'),
]

nature = [
    ('SFDC', 'Salesforce Corporate Initiative'),
    ('JOB', 'This is something I am doing as part of my job.'),
    ('PERS', 'This is a personal project.'),
    ('VTO', 'This is a VTO project.'),
    ('NOTSURE', 'I am not sure!'),
]

size_of_change = [

    ('LESS', 'Less than or equal 100 lines of code'),
    ('MORE', 'More than 100 lines of code'),
]

license_list = [

    ('AGPL', 'Affero GPL(AGPL), any version'),
    ('ALV2', 'Apache License 2.0'),
    ('BSD3', 'BSD 3-Clause'),
    ('CC', 'Creative Commons, any version'),
    ('EPL2', 'Eclipse Public License 2.0'),
    ('GPL', 'GNU General Public License (GPL), any version'),
    ('LGPL', 'Lesser General Public License (LGPL), any version'),
    ('MIT', 'MIT'),
    ('MPL2', 'Mozilla Public License 2.0'),
    ('PD', 'Public Domain'),
    ('OTHER', 'Other'),
]

relation = [

    ('UNR', 'Unrelated'),
    ('SDK', 'Product SDK'),
    ('SAMP', 'Sample or Demo'),
    ('DCP', 'Used within developer, CI/CD, or production environments'),
    ('OTHER', 'Other'),
]

start_with = [
    ('REPO', 'Github Repo Request'),
    ('PART', 'Join the Partner Community'),
]

security_review = [
    ('GOING', 'In Progress'),
    ('NOTYET', 'Not yet'),
    ('PASS', 'Passed Security Review'),
]

patent_application = [
    ('YES', 'Yes, a patent application has been filed.'),
    ('NO',
     'No. I have already discussed my paper with the Patent Team, and the Patent Team decided not to file a patent application.'),
    ('NOTYET', 'No. I have not yet discussed my paper with the Patent Team.'),
    ('OTHER', 'Other'),
]

project_type = [
    ('TOOL', 'Tool'),
    ('INFRA', 'Infrastructure'),
    ('LIB', 'Framework / Library'),
    ('SDX', 'Salesforce Platform / DX Package'),
    ('MISC', 'Sample / Demo / Example in Docs / Blogs'),
]

run_where = [
    ('Nowhere', 'Nowhere'),
    ('CLOUD', 'Somewhere in a customer / cloud app stock (i.e., CRM, Marketing, Commerce, Heroku, etc)'),
    ('NPO', 'Non-profit donated stack (e.g. donated CRM org)'),
    ('INT', 'Internal / employees only'),
    ('CICD', 'CI / Delivery pipeline'),
    ('DEV', 'Only on Developers machine'),
]

how_related = [
    ('UNR', 'Unrelated (e.g. infrastructure, monitoring, donated org, etc)'),
    ('INT', 'A product uses this internally'),
    ('OTHER', 'Other'),
]

how_related_dj = [
    ('JOB', 'Related - I built this as part of my day job'),
    ('VTO', 'Related - I built this as part of my VTO time'),
    ('WORK', 'Not Related - But I built this on work time'),
    ('OWN', 'Not Related - And I built this on work time and own machine'),
]

how_related_ap = [
    ('NO',
     'Totally unrelated to CRM, Data Science, Commerce, Marketing, Productivity, Cloud everything, etc (e.g. it is a beanie baby database)'),
    ('KINDA', 'It is kinda related (e.g. Probono VTO using Salesforce products)'),
    ('YES', 'It is totally related'),
]

sfdc_clouds = [
    ('Analytics Cloud', 'Analytics Cloud'),
    ('Availability Cloud', 'Availability Cloud'),
    ('Big Data Cloud', 'Big Data Cloud'),
    ('Commerce Cloud', 'Commerce Cloud'),
    ('CRM Cloud', 'CRM Cloud'),
    ('Einstein', 'Einstein'),
    ('Experience Cloud', 'Experience Cloud'),
    ('Industries Cloud', 'Industries Cloud'),
    ('Integration Cloud', 'Integration Cloud'),
    ('Marketing Cloud', 'Marketing Cloud'),
    ('Net Zero Cloud', 'Net Zero Cloud'),
    ('Operations Cloud', 'Operations Cloud'),
    ('Partners Cloud', 'Partners Cloud'),
    ('Platform Cloud', 'Platform Cloud'),
    ('Research Cloud', 'Research Cloud'),
    ('Safety Cloud', 'Safety Cloud'),
    ('Sales Cloud', 'Sales Cloud'),
    ('Service Cloud', 'Service Cloud'),
    ('Success Cloud', 'Success Cloud'),
    ('Sustainability Cloud', 'Sustainability Cloud'),
    ('Tableau', 'Tableau'),
    ('Not-Listed', 'Not-Listed'),
]


class ReqForm(forms.ModelForm):
    class Meta:
        model = Req
        fields = ['request_name', 'type']

        labels = {
            'request_name': 'Request Name',
            'type': 'Open Source Request Type',
        }
        widgets = {
            'request_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Request Name'}),
            'type': forms.Select(choices=RequestTypes.choices, attrs={'class': 'form-select'}),
        }


class SrForm(forms.ModelForm):
    class Meta:
        model = Srmodel
        fields = "__all__"
        exclude = ['request_id']
        labels = {
            'request_name': 'Request Name',
            'conference': '',
            'paper_title': '',
            'exp_results': 'Is the code solely used to reproduce experimental results in a conference paper?',
            'approval': 'Have you gotten approval from Caiming Xiong?',
            'patent_application': 'Has a patent application already been filed covering the concepts that will be disclosed by the code you would like to release?',
            'code_released': 'Is the code you would like to release used, directly or indirectly, in any current SFDC products or services?',
            'code_released_likely': 'Is the code you would like to release likely to be used, directly or indirectly, in any future SFDC products or services?',
            'code_third_party': 'Does the code you would like to release have any third-party (i.e., non-Salesforce) dependencies?',
        }

        widgets = {
            'request_name': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'conference': forms.TextInput(attrs={'class': 'form-control',
                                                 'placeholder': 'What is the name of the conference you are submitting to?'}),
            'paper_title': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'What is the title of the paper you are submitting?'}),
            'exp_results': forms.Select(choices=options, attrs={'class': 'form-select'}),
            'approval': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'patent_application': forms.Select(choices=patent_application, attrs={'class': 'form-select'}),
            'code_released': forms.RadioSelect(choices=options, attrs={'class': 'radio'}),
            'code_released_likely': forms.RadioSelect(choices=options, attrs={'class': 'radio'}),
            'code_third_party': forms.RadioSelect(choices=options, attrs={'class': 'radio'}),

        }


class SlpForm(forms.ModelForm):
    class Meta:
        model = Slpmodel
        fields = "__all__"
        exclude = ['request_id']
        labels = {
            'request_name': 'Request Name',
            'start_with': 'Start With',
            'repository_name': '',
            'project_description': '',
            'lab_app': '',
            'author': '',
            'security': 'Submitted for Security Review',
        }

        widgets = {
            'request_name': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'start_with': forms.Select(choices=start_with, attrs={'class': 'form-select'}),
            'repository_name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Desired repository Name (app name)'}),
            'project_description': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Project Description'}),
            'lab_app': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Labs App AppExchange Listing'}),
            'author': forms.TextInput(attrs={'class': 'form-control',
                                             'placeholder': 'Comma separated Author and contributor GitHub handles (ie. jdoe, rsmith)'}),
            'security': forms.Select(choices=security_review, attrs={'class': 'form-select'}),

        }


class OsrForm(forms.ModelForm):
    class Meta:
        model = Osrmodel

        fields = ['request_name', 'project_name', 'work_nature', 'vp_email', 'vp_approval', 'manager_email',
                  'manager_approval', 'first_time', 'current_repository_url', 'license',
                  'readme_url', 'third_party_code', 'product_ecosystem', 'relation_to_product']
        labels = {
            'request_name': 'Request Name',
            'project_name': 'Project Name',
            'work_nature': 'What is the nature of this work?',
            'manager_email': 'Manager\'s Email',
            'manager_approval': 'Please confirm that you have discussed this with your Manager and that they have approved.',
            'first_time': 'Is this your first time contributing to open source while at Salesforce?',
            'current_repository_url': 'URL Location of the current code/project',
            'license': 'License',
            'readme_url': 'URL Location of the current project\'s README',
            'third_party_code': 'Does this project repository contain any third party code? (Dependencies pulled in through requirements.txt or similar mechanisms do not count.)',
            'product_ecosystem': 'Related Product Cloud or Ecosystem',
            'relation_to_product': 'Relation to Product',
            'vp_email': 'VP\'s Email',
            'vp_approval': 'Please confirm that you have discussed this with your VP and that they have approved open sourcing this project.',
        }

        widgets = {
            'request_name': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'project_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project Name'}),
            'work_nature': forms.Select(choices=nature, attrs={'class': 'form-select'}),
            'manager_email': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Manager\'s Email'}),
            'manager_approval': forms.CheckboxInput(attrs={'class': 'checkbox', 'required': True}),
            'first_time': forms.RadioSelect(choices=options, attrs={'class': 'radio'}),
            'current_repository_url': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Current Repository URL'}),
            'license': forms.Select(choices=license_list, attrs={'class': 'form-select'}),
            'readme_url': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'README URL'}),
            'third_party_code': forms.RadioSelect(choices=options, attrs={'class': 'radio', 'required': True}),
            'product_ecosystem': forms.Select(choices=sfdc_clouds, attrs={'class': 'form-select', 'required': True}),
            'relation_to_product': forms.Select(choices=relation, attrs={'class': 'form-select'}),
            'vp_email': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'VP Email'}),
            'vp_approval': forms.CheckboxInput(attrs={'class': 'checkbox', 'required': True}),
        }


class OscForm(forms.ModelForm):
    class Meta:
        model = Oscmodel

        fields = ['request_name', 'project_name', 'work_nature', 'manager_email', 'manager_approval',
                  'first_time', 'current_repository_url', 'license', 'have_cla', 'cla_url', 'size_of_change',
                  'scope']
        labels = {
            'request_name': 'Request Name',
            'project_name': 'Project Name',
            'work_nature': 'What is the nature of this work?',
            'manager_email': 'Manager\'s Email',
            'manager_approval': 'Please confirm that you have discussed this with your Manager and that they have approved.',
            'first_time': 'Is this your first time contributing to open source while at Salesforce?',
            'current_repository_url': 'URL Location of your patch/PULL request',
            'license': 'License',
            'have_cla': 'Does the project have a Contributor License Agreement (CLA) or Developer Certificate of Origin (DCO)?',
            'cla_url': 'Provide URL to CLA/DCO',
            'size_of_change': 'Size of Change',
            'scope': 'Scope of work',

        }

        widgets = {
            'request_name': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'project_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Project Name'}),
            'work_nature': forms.Select(choices=nature, attrs={'class': 'form-select'}),
            'manager_email': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Your Manager\'s Email Address'}),
            'manager_approval': forms.CheckboxInput(attrs={'class': 'checkbox', 'required': True}),
            'first_time': forms.RadioSelect(choices=options, attrs={'class': 'radio'}),
            'current_repository_url': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Current Repository URL'}),
            'license': forms.Select(choices=license_list, attrs={'class': 'form-select'}),
            'have_cla': forms.RadioSelect(choices=options, attrs={'class': 'radio', 'required': True}),
            'cla_url': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'URL'}),
            'size_of_change': forms.Select(choices=size_of_change, attrs={'class': 'form-select'}),
            'scope': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Scope'}),

        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['id']

        widgets = {
            'id': forms.HiddenInput(),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['id', 'content']
        labels = {
            'content': 'Add Comment',
        }
        widgets = {
            'id': forms.HiddenInput(),
            'content': forms.TextInput(
                attrs={'class': 'form-control', 'required': True}),
        }


#
# Task Related forms
#

class OSR_dlr(forms.ModelForm):
    class Meta:
        model = Osrmodel

        fields = ['dependency_list', 'request_id']
        labels = {
            'dependency_list': 'Dependency License Report',
        }

        widgets = {
            'dependency_list': forms.Textarea(
                attrs={'class': 'form-control', 'placeholder': 'Report', 'required': True}),
            'request_id': forms.HiddenInput(),
        }


class OSR_gri(forms.ModelForm):
    class Meta:
        model = Osrmodel

        fields = ['github_org', 'github_repo', 'github_admin', 'request_id']
        labels = {
            'github_org': 'Which GitHub org should this project be under',
            'github_repo': 'Requested GitHub repo name',
            'github_admin': 'GitHub IDs of the repo admins (comma separated)'
        }

        widgets = {
            'request_id': forms.HiddenInput(),
            'github_org': forms.Select(choices=GHOrgs.choices, attrs={'class': 'form-select'}),
            'github_repo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'repo name', 'required': True}),
            'github_admin': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your GitHub ID', 'required': True}),
        }


class OSR_psr(forms.ModelForm):
    class Meta:
        model = Osrmodel

        fields = ['tmp_request', 'app_ex', 'sec_ass', 'request_id']
        labels = {
            'tmp_request': 'Is this a TMP Request?',
            'app_ex': 'Is this already been reviewed as part of the AppExchange review?',
            'sec_ass': 'Is this security review already covered as part of a Security Assessment?'
        }

        widgets = {
            'request_id': forms.HiddenInput(),
            'tmp_request': forms.RadioSelect(choices=options, attrs={'class': 'radio', 'required': True}),
            'app_ex': forms.RadioSelect(choices=options, attrs={'class': 'radio', 'required': True}),
            'sec_ass': forms.RadioSelect(choices=options, attrs={'class': 'radio', 'required': True}),
        }

