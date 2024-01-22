from rest_framework import routers

from social_media.views import ProfileViewSet, PostViewSet

router = routers.DefaultRouter()
router.register("profiles", ProfileViewSet)
router.register("posts", PostViewSet)


urlpatterns = router.urls


app_name = "social_media"
