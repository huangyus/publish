from django.conf.urls import url
from django.urls import include
from rest_framework.routers import DefaultRouter
from rest_framework_jwt.views import ObtainJSONWebToken

from . import views

router = DefaultRouter()
router.register('user', views.UserViewSet)
router.register('datacenter', views.DatacenterViewSet)
router.register('servers', views.ServersViewSet)
router.register('projects', views.ProjectsViewSet)
router.register('modules', views.ModulesViewSet)
router.register('middleware', views.MiddlewareViewSet)
router.register('business', views.BusinessViewSet)
router.register('bstemplate', views.BsTemplateViewSet)
router.register('workflow', views.WorkFlowViewSet)
router.register('wftemplate', views.WorkFlowTemplateViewSet)
router.register('group', views.GroupViewSet)
router.register('basic', views.BasicViewSet)
router.register('bctemplate', views.BasicTemplateViewSet)
router.register('log', views.LoggerViewSet)
router.register('version', views.VersionViewSet, basename='version')
router.register('deploy', views.DeployViewSet, basename='deploy')
router.register('rollback', views.RollbackViewSet, basename='rollback')
router.register('dashboard', views.DashBoardViewSet, basename='dashboard')
router.register('dashboardpie', views.DashBoardPieViewSet, basename='dashboardpie')
router.register('autodeploy', views.AutoDeployViewSet, basename='autodeploy')

urlpatterns = [
    url(r'^apigateway/', include('apigateway.urls')),
    url(r'^api-token-auth/', ObtainJSONWebToken.as_view()),
]

urlpatterns += router.urls
