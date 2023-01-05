from django.urls import path
from . import views

urlpatterns = [
    # Path Converters
    # int: numbers
    # str: strings
    # path: whole urls /
    # slug: hyphen-and_underscores_stuff
    # UUID: universally unique identifier

    path('', views.home, name='home'),
    path('acs', views.acs, name='acs'),
    path('attrs', views.attrs, name='attrs'),
    path('login_saml', views.login_saml, name='login_saml'),
    path('<int:year>/<str:month>/', views.home, name='home'),
    path('new_request', views.initial, name='new_request'),
    path('add_request', views.router_add, name='router_add'),
    path('show_request/<request_id>', views.show_request, name='show_request'),
    path('show_task/<task_id>', views.show_task, name='show_task'),
    path('list_requests', views.list_requests, name='list_requests'),
    path('search_requests', views.search_requests, name='search_requests'),
    path('update_request', views.update_request, name='update_request'),
    path('comments', views.do_comments, name='do_comments'),
    # path('add/', views.request_create_view, name='request_add'),
    # path('ajax/load-vp-approval/', views.load_vp_approval, name='ajax_load_vp_approval'),

]
