from django.conf.urls import url
from . import views

app_name="medialab_keywords"
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^(P<group_id>[0-9]{4})/groupdetail$', views.groupdetail, name='gdetail'),
    url(r'^(P<subgroup_id>[0-9]{4})/subgroupdetail$', views.subgroupdetail, name='sgdetail'),
    url(r'^(P<keyword_id>[0-9]{4})/keyworddetail$', views.keyworddetail, name='kdetail'),
    url(r'^(P<keyword_id>[0-9]{4})/keyworddetail$', views.keyworddetail, name='kdetail'),
    url(r'^keywordlist$', views.keywords_list, name='keywords_list'),
    url(r'^keywords_management$', views.keywords_management, name='kwds_mgmt'),
    url(r'^editor_assignment_ui$', views.editor_assignment_ui, name='edtr_asgn_ui'),
    url(r'^editor_assignment_service$', views.editor_assignment_service, name='edtr_asgn_svc'), 
    
    url(r'^load_keywords$', views.load_keywords, name='load_kwds'),
    url(r'^keywords_loaded$', views.keywords_loaded, name='kwds_ldd'),
    
#   url(r'^<int:group_id>/groupdetail$', views.groupdetail, name='gdetail'),
#   url(r'^<int:subgroup_id>/subgroupdetail$', views.subgroupdetail, name='sgdetail'),
#   url(r'^<int:keyword_id>/keyworddetail$', views.keyworddetail, name='kdetail'),
]


