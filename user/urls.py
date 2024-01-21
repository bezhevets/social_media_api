from django.urls import path

from user.views import CreateUserView, CreateTokenView, ManageUserView, DeleteTokenView

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register"),
    path("login/", CreateTokenView.as_view(), name="login"),
    path("logout/", DeleteTokenView.as_view(), name="logout"),
    path("me/", ManageUserView.as_view(), name="profile"),
]

app_name = "user"
