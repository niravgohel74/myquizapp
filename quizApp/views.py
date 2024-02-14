from django.shortcuts import render, redirect
from .models import *
from django.core.mail import send_mail
from django.conf import settings
from random import randint
from django.db import IntegrityError

# Create your views here.
default_data = {}

login_page_link = "quiz_manage/login_page.html"
register_page_link = "quiz_manage/register_page.html"
profile_page_link = "quiz_manage/profile_page.html"
otp_page_link = "quiz_manage/otp_page.html"
forgot_pwd_page_link = "quiz_manage/forgot_pwd.html"


# EMAIL FUNCTION
def send_otp(request):
    otp = randint(100000, 999999)
    request.session["otp"] = otp

    send_to = [request.session["reg_data"]["email"]]
    send_from = settings.EMAIL_HOST_USER
    subject = "Login Attempt"
    messages = f"Hello! Someone entered your account. OTP is: {otp}"

    print(otp)
    print("done")

    send_mail(subject, messages, send_from, send_to)


# EMAIL Verification
def verify_otp(request):
    if int(request.POST["otp"]) == request.session["otp"]:
        master = Master.objects.create(
            Email=request.session["reg_data"]["email"],
            Password=request.session["reg_data"]["pwd"],
        )
        UserProfile.objects.create(Master=master)
        print("Account Created Successfully")
        return redirect(login_page)
    else:
        print("Invalid OTP.")

    return redirect(otp_page_link)


### START: VIEWS FOR PAGES ONLY ###
# login page
def login_page(request):
    if "email" in request.session:
        load_profile(request)
        return render(request, profile_page_link, default_data)
    return render(request, login_page_link)


# register page
def register_page(request):
    return render(request, register_page_link)


# OTP PAGE
def otp_page(request):
    return render(request, otp_page_link)


# profile page
def profile_page(request):
    # calling load profile
    if "email" in request.session:
        load_profile(request)
        return render(request, profile_page_link, default_data)

    return redirect(login_page)


# password forgot page
def forgot_pwd(request):
    return render(request, forgot_pwd_page_link)


### END: VIEWS FOR PAGES ONLY ###


### FUNCTIONALITY VIEWS ONLY ###

### START: REGISTRATION_FUNCTIONALITY ###


def registration(request):
    try:
        master = Master.objects.get(Email=request.POST["email"])
        print("Account Exist. Login")
    except Master.DoesNotExist as err:
        print(err)
        print("Account Not Found")

        request.session["reg_data"] = {
            "email": request.POST["email"],
            "pwd": request.POST["password"],
        }
        send_otp(request)
        return redirect(otp_page)

    return redirect(login_page)


### END: REGISTRATION_FUNCTIONALITY ###

### START: LOGIN_FUNCTIONALITY ###


def login(request):
    try:
        master = Master.objects.get(Email=request.POST["email"])
        if master.Password == request.POST["password"]:
            request.session["email"] = master.Email

            # send_otp(request)
            return redirect(profile_page)
        else:
            print("Incorrect Password")

    except Master.DoesNotExist as err:
        print("Account Does Not Exist")

    return redirect(login_page)


### END: LOGIN_FUNCTIONALITY ###


### START: GET_PROFILE_DATA_FUNCTIONALITY ###
def load_profile(request):
    master = Master.objects.get(Email=request.session["email"])
    user = UserProfile.objects.get(Master=master)

    user.BirthDate = user.BirthDate.strftime("%y-%m-%d")

    default_data["user_profile"] = user

    default_data["gender_choices"] = dict()
    for gc in gender_choices:
        default_data["gender_choices"].setdefault(gc[0], gc[1])

    default_data["quiz_preset_data"] = {
        "categories": QuizCategory.objects.all(),
        "subjects": Subject.objects.all(),
    }

    myquizes = Quiz.objects.filter(UserProfile=user)

    for myquiz in myquizes:
        myquiz.TotalQuestions = len(QuesAns.objects.filter(Quiz=myquiz))

    default_data["my_quizes"] = myquizes


### END: GET_PROFILE_DATA_FUNCTIONALITY ###

### START: PROFILE_UPDATE_FUNCTIONALITY ###

import os


def upload_profile_image(request):
    master = Master.objects.get(Email=request.session["email"])
    user = UserProfile.objects.get(Master=master)

    image_name = request.FILES["profile_image"].name
    img_ext = image_name.split(".")[-1]

    image_new_name = f"{master.Email.split('@')[0]}.{img_ext}"
    print(image_new_name)

    image = request.FILES["profile_image"]
    image.name = image_new_name

    image_path = os.path.join(settings.MEDIA_ROOT, "profile_images")

    for file in os.scandir(image_path):
        if file.name == image.name:
            del_file = os.path.join(image_path, file.name)
            os.remove(del_file)

        print(file.name)

    user.ProfileImage = image
    user.save()

    # print(request.FILES['profile_image'])

    return redirect(profile_page)


def profile_update(request):
    print(request.POST)

    master = Master.objects.get(Email=request.session["email"])
    print("master", master, master.Email)
    user = UserProfile.objects.get(Master=master)
    user.FullName = request.POST["full_name"]
    user.Mobile = request.POST["mobile"]
    user.Gender = request.POST["gender"]
    user.City = request.POST["city"]
    user.State = request.POST["state"]
    user.Country = request.POST["country"]
    user.Pincode = request.POST["pincode"]

    user.save()
    return redirect(profile_page)


### END: PROFILE_UPDATE_FUNCTIONALITY ###


# Change Password #
def change_password(request):
    master = Master.objects.get(Email=request.session["email"])
    if master.Password == request.POST["current_pwd"]:
        if request.POST["new_pwd"] == request.POST["rewrite_pwd"]:
            master.password = request.POST["new_pwd"]
            master.save()
            print("Password has been changed.")
        else:
            print("New Password and Rewrite Password should be same.")
    else:
        print("Current Password not matched")

    return redirect(profile_page)


# CREATE NEW QUIZ
def create_quiz(request):
    master = Master.objects.get(Email=request.session["email"])
    user = UserProfile.objects.get(Master=master)

    subject = Subject.objects.get(pk=int(request.POST["subject"]))
    category = QuizCategory.objects.get(pk=int(request.POST["category"]))

    Quiz.objects.create(
        UserProfile=user,
        Category=category,
        Subject=subject,
        Title=request.POST["title"],
        Duration=request.POST["duration"],
        DifficultyLevel=request.post["difficulty_level"],
        TotalScore=request.POST["total_score"],
    )


# ADD OPTIONS
def add_options(request, id):
    master = Master.objects.get(Email=request.session["email"])
    user = UserProfile.objects.get(Master=master)

    quiz = Quiz.objects.get(
        id=id,
        UserProfile=user
    )

    options = []
    for d in request.POST:
        if d.startswith("option"):
            options.append(request.POST[d])
    options = " | ".join(options)

    QuesAns.objects.create(
        Quiz=quiz,
        Question=request.POST["question"],
        Options=options,
        Answer=request.POST["set_answer"],
    )

    return redirect(profile_page)


def view_question(request):
    pass


## LOGOUT ##
def logout(request):
    if "email" in request.session:
        del request.session["email"]
    return redirect(login_page)
