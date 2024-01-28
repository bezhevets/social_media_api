from rest_framework import routers

from social_media.views import (
    ProfileViewSet,
    PostViewSet,
    CommentViewSet,
    LikeViewSet
)

router = routers.DefaultRouter()
router.register("profiles", ProfileViewSet)
router.register("posts", PostViewSet)
router.register("comments", CommentViewSet)
router.register("likes", LikeViewSet)


urlpatterns = router.urls


app_name = "social_media"
