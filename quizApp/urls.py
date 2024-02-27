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
    path("upload_profile_image/", upload_profile_image, name="upload_profile_image"),
    path("change_password/", change_password, name="change_password"),
    path("add_options/<int:id>/", add_options, name="add_options"),
    path("fetch_questions/<int:id>/", fetch_questions, name="fetch_questions"),


    path("play_page/", play_page, name="play_page"),
    
    path("logout/", logout, name="logout")
    

]