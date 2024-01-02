from django.urls import path
from .views import *

urlpatterns = [
    path("", login_page, name="login_page"),
    path("login/", login, name="login"),
    path("register_page/", register_page, name="register_page"),
    path("registration/", registration, name="registration"),
    path("otp_page/", otp_page, name="otp_page"),
    path("verify_otp/", verify_otp, name="verify_otp"),

    path("profile_page/", profile_page, name="profile_page"),
    path("forgot_pwd/", forgot_pwd, name="forgot_pwd"),
    path("profile_update/", profile_update, name="profile_update"),

    path("logout/", logout, name="logout"),
    

]