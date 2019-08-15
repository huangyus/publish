from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('index', views.APIGateWayViewSet)
router.register('upstreams', views.UpstreamsViewSet)
router.register('globalconfig', views.GlobalConfigViewSet)
router.register('maps', views.MapsViewSet)
router.register('vhosts', views.VhostsViewSet)
router.register('deploy', views.DeployVeiwSet, basename='apigateway-deploy')

urlpatterns = []
urlpatterns += router.urls
