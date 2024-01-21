from rest_framework import routers

from social_media.views import ProfileViewSet

router = routers.DefaultRouter()
router.register("profiles", ProfileViewSet)


urlpatterns = router.urls


app_name = "social_media"
