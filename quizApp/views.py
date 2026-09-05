import os
from random import randint
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from .models import (
    Master,
    UserProfile,
    QuizCategory,
    Subject,
    Quiz,
    QuesAns,
    QuizPlay,
    gender_choices,
)

# Page template paths
login_page_link = "quiz_manage/login_page.html"
register_page_link = "quiz_manage/register_page.html"
profile_page_link = "quiz_manage/profile_page.html"
otp_page_link = "quiz_manage/otp_page.html"
forgot_pwd_page_link = "quiz_manage/forgot_pwd.html"
quiz_play_link = "play/quiz_play.html"
play_result_link = "play/quiz_play_result.html"


def parse_options_list(options_str):
    """Safely parse question options string into a list."""
    if not options_str:
        return []
    if "|" in options_str:
        return [opt.strip() for opt in options_str.split("|") if opt.strip()]
    elif "\n" in options_str:
        return [opt.strip() for opt in options_str.splitlines() if opt.strip()]
    return [opt.strip() for opt in options_str.split() if opt.strip()]


# EMAIL FUNCTION
def send_otp(request):
    otp = randint(100000, 999999)
    request.session["otp"] = otp

    recipient = request.session.get("reg_data", {}).get("email")
    if not recipient:
        return

    send_to = [recipient]
    send_from = settings.EMAIL_HOST_USER or "noreply@quizapp.local"
    subject = "Your Quiz App Verification OTP"
    email_body = f"Hello!\n\nYour OTP for registration is: {otp}\n\nThank you!"

    print(f"Generated OTP: {otp}")
    try:
        send_mail(subject, email_body, send_from, send_to, fail_silently=True)
    except Exception as err:
        print(f"Email send error: {err}")


# EMAIL Verification
def verify_otp(request):
    if request.method == "POST":
        stored_otp = request.session.get("otp")
        entered_otp = request.POST.get("otp", "").strip()

        if stored_otp and entered_otp.isdigit() and int(entered_otp) == stored_otp:
            reg_data = request.session.get("reg_data")
            if reg_data:
                master, _ = Master.objects.get_or_create(
                    Email=reg_data["email"],
                    defaults={"Password": reg_data["pwd"]},
                )
                UserProfile.objects.get_or_create(Master=master)
                messages.success(request, "Account created successfully! Please login.")
                request.session.pop("reg_data", None)
                request.session.pop("otp", None)
                return redirect(login_page)
            else:
                messages.error(request, "Registration session expired. Please register again.")
                return redirect(register_page)
        else:
            messages.error(request, "Invalid OTP. Please try again.")
            return redirect(otp_page)

    return redirect(otp_page)


### VIEWS FOR PAGES ###

def login_page(request):
    if "email" in request.session:
        return redirect(profile_page)
    return render(request, login_page_link)


def register_page(request):
    return render(request, register_page_link)


def otp_page(request):
    return render(request, otp_page_link)


def forgot_pwd(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        if not email:
            messages.error(request, "Please enter your email.")
            return render(request, forgot_pwd_page_link)

        try:
            master = Master.objects.get(Email=email)
            subject = "Quiz App Password Recovery"
            body = (
                f"Hello!\n\n"
                f"You requested password recovery for your Quiz App account.\n"
                f"Your account password is: {master.Password}\n\n"
                f"Please keep your password secure.\n"
                f"Thank you!"
            )
            print(f"[Password Recovery] Email: {email} | Password: {master.Password}")
            send_mail(
                subject,
                body,
                settings.EMAIL_HOST_USER or "noreply@quizapp.local",
                [email],
                fail_silently=True,
            )
            messages.success(request, "Password details sent to your email. Please login.")
            return redirect(login_page)
        except Master.DoesNotExist:
            messages.error(request, "No account found with that email address.")
            return render(request, forgot_pwd_page_link)

    return render(request, forgot_pwd_page_link)


def get_profile_context(request):
    """Build fresh profile context for the logged-in user."""
    master = Master.objects.get(Email=request.session["email"])
    user, _ = UserProfile.objects.get_or_create(Master=master)

    formatted_birthdate = (
        user.BirthDate.strftime("%Y-%m-%d") if user.BirthDate else "1990-01-01"
    )

    gender_dict = {}
    for gc in gender_choices:
        gender_dict[gc[0]] = gc[1]

    myquizes = list(Quiz.objects.filter(UserProfile=user))
    for myquiz in myquizes:
        myquiz.TotalQuestions = QuesAns.objects.filter(Quiz=myquiz).count()

    context = {
        "user_profile": user,
        "formatted_birthdate": formatted_birthdate,
        "gender_choices": gender_dict,
        "quiz_preset_data": {
            "categories": QuizCategory.objects.all(),
            "subjects": Subject.objects.all(),
        },
        "my_quizes": myquizes,
    }
    return context


def profile_page(request):
    if "email" not in request.session:
        return redirect(login_page)

    context = get_profile_context(request)
    return render(request, profile_page_link, context)


### FUNCTIONALITY VIEWS ###

def registration(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        pwd = request.POST.get("password", "").strip()

        if not email or not pwd:
            messages.error(request, "Email and password are required.")
            return redirect(register_page)

        if Master.objects.filter(Email=email).exists():
            messages.error(request, "An account with this email already exists. Please log in.")
            return redirect(login_page)

        request.session["reg_data"] = {
            "email": email,
            "pwd": pwd,
        }
        send_otp(request)
        return redirect(otp_page)

    return redirect(register_page)


def login(request):
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        pwd = request.POST.get("password", "").strip()

        try:
            master = Master.objects.get(Email=email)
            if master.Password == pwd:
                request.session["email"] = master.Email
                UserProfile.objects.get_or_create(Master=master)
                return redirect(profile_page)
            else:
                messages.error(request, "Incorrect password.")
        except Master.DoesNotExist:
            messages.error(request, "Account does not exist. Please register.")

    return redirect(login_page)


def upload_profile_image(request):
    if "email" not in request.session:
        return redirect(login_page)

    if request.method == "POST" and "profile_image" in request.FILES:
        master = Master.objects.get(Email=request.session["email"])
        user, _ = UserProfile.objects.get_or_create(Master=master)

        uploaded_file = request.FILES["profile_image"]
        img_ext = uploaded_file.name.split(".")[-1].lower()
        clean_email_prefix = master.Email.split("@")[0].replace(".", "_")
        image_new_name = f"{clean_email_prefix}.{img_ext}"
        uploaded_file.name = image_new_name

        image_dir = os.path.join(settings.MEDIA_ROOT, "profile_images")
        os.makedirs(image_dir, exist_ok=True)

        existing_path = os.path.join(image_dir, image_new_name)
        if os.path.exists(existing_path):
            try:
                os.remove(existing_path)
            except OSError:
                pass

        user.ProfileImage = uploaded_file
        user.save()
        messages.success(request, "Profile image updated successfully.")

    return redirect(profile_page)


def profile_update(request):
    if "email" not in request.session:
        return redirect(login_page)

    if request.method == "POST":
        master = Master.objects.get(Email=request.session["email"])
        user, _ = UserProfile.objects.get_or_create(Master=master)

        user.FullName = request.POST.get("full_name", user.FullName)
        user.Mobile = request.POST.get("mobile", user.Mobile)
        user.Gender = request.POST.get("gender", user.Gender)

        birth_date = request.POST.get("birth_date")
        if birth_date:
            user.BirthDate = birth_date

        user.City = request.POST.get("city", user.City)
        user.State = request.POST.get("state", user.State)
        user.Country = request.POST.get("country", user.Country)
        user.Pincode = request.POST.get("pincode", user.Pincode)

        user.save()
        messages.success(request, "Profile updated successfully.")

    return redirect(profile_page)


def change_password(request):
    if "email" not in request.session:
        return redirect(login_page)

    if request.method == "POST":
        master = Master.objects.get(Email=request.session["email"])
        current_pwd = request.POST.get("current_pwd", "")
        new_pwd = request.POST.get("new_pwd", "")
        rewrite_pwd = request.POST.get("rewrite_pwd", "")

        if master.Password == current_pwd:
            if new_pwd and new_pwd == rewrite_pwd:
                master.Password = new_pwd
                master.save()
                messages.success(request, "Password has been changed successfully.")
            else:
                messages.warning(request, "New password and confirmation do not match.")
        else:
            messages.error(request, "Current password does not match.")

    return redirect(profile_page)


def create_quiz(request):
    if "email" not in request.session:
        return redirect(login_page)

    if request.method == "POST":
        master = Master.objects.get(Email=request.session["email"])
        user, _ = UserProfile.objects.get_or_create(Master=master)

        try:
            subject_id = int(request.POST.get("subject", 0))
            category_id = int(request.POST.get("category", 0))
            subject = Subject.objects.get(pk=subject_id)
            category = QuizCategory.objects.get(pk=category_id)
        except (ValueError, TypeError, Subject.DoesNotExist, QuizCategory.DoesNotExist):
            messages.error(request, "Please select a valid Subject and Category.")
            return redirect(profile_page)

        diff_raw = str(request.POST.get("difficulty_level", "1"))
        diff_map = {"1": "easy", "2": "mid", "3": "hrd"}
        difficulty = diff_map.get(diff_raw, diff_raw if diff_raw in ["easy", "mid", "hrd"] else "easy")

        title = request.POST.get("quiz_title", "Untitled Quiz").strip() or "Untitled Quiz"

        try:
            duration = int(request.POST.get("duration", 0))
        except (ValueError, TypeError):
            duration = 0

        try:
            total_score = int(request.POST.get("total_score", 100))
        except (ValueError, TypeError):
            total_score = 100

        Quiz.objects.create(
            UserProfile=user,
            Category=category,
            Subject=subject,
            Title=title,
            Duration=duration,
            DifficultyLevel=difficulty,
            TotalScore=total_score,
        )
        messages.success(request, f"Quiz '{title}' created successfully.")

    return redirect(profile_page)


def add_options(request, id):
    if "email" not in request.session:
        return redirect(login_page)

    if request.method == "POST":
        master = Master.objects.get(Email=request.session["email"])
        user, _ = UserProfile.objects.get_or_create(Master=master)

        try:
            quiz = Quiz.objects.get(id=id, UserProfile=user)
        except Quiz.DoesNotExist:
            messages.error(request, "Quiz not found.")
            return redirect(profile_page)

        options = []
        for key in sorted(request.POST.keys()):
            if key.startswith("option") and request.POST[key].strip():
                options.append(request.POST[key].strip())

        options_str = " | ".join(options)
        question_text = request.POST.get("question", "").strip()
        answer = request.POST.get("set_answer", "0")

        if not question_text:
            messages.error(request, "Question text cannot be empty.")
            return redirect(profile_page)

        QuesAns.objects.create(
            Quiz=quiz,
            Question=question_text,
            Options=options_str,
            Answer=answer,
        )
        messages.success(request, "Question added successfully.")

    return redirect(profile_page)


def fetch_questions(request, id):
    quiz = Quiz.objects.filter(id=id).first()
    if not quiz:
        return JsonResponse({"ques_ans": []})

    questions = QuesAns.objects.filter(Quiz=quiz)
    result = []
    for ques in questions:
        result.append({
            "question": ques.Question,
            "options": ques.Options,
            "answer": ques.Answer,
        })

    return JsonResponse({"ques_ans": result})


def logout(request):
    request.session.flush()
    return redirect(login_page)


### QUIZ PLAY ###

def quiz_play(request):
    return render(request, quiz_play_link)


def quiz_play_result(request, id=None):
    quiz = Quiz.objects.filter(id=id).first() if id else None
    return render(request, play_result_link, {"quiz": quiz})


def play_quiz(request, id):
    try:
        quiz = Quiz.objects.get(id=id)
    except Quiz.DoesNotExist:
        messages.error(request, "Quiz not found.")
        return redirect(login_page)

    questions = list(QuesAns.objects.filter(Quiz=quiz))
    all_questions = len(questions)

    # Attach parsed options list to each question object
    for question in questions:
        question.options_list = parse_options_list(question.Options)

    if request.method == "POST":
        if all_questions == 0:
            messages.warning(request, "This quiz has no questions.")
            return redirect(profile_page)

        score = 0
        for question in questions:
            selected_option = request.POST.get(f"question_{question.id}")
            if not selected_option:
                continue

            # Check direct match or numerical index match
            if selected_option == question.Answer:
                score += 1
            elif str(question.Answer).isdigit():
                ans_idx = int(question.Answer)
                if 0 <= ans_idx < len(question.options_list) and question.options_list[ans_idx] == selected_option:
                    score += 1

        percentage = round((score / all_questions) * 100, 1)
        if percentage <= 25:
            remark_level = "Poor"
        elif percentage <= 50:
            remark_level = "Average"
        elif percentage <= 75:
            remark_level = "Good"
        else:
            remark_level = "Excellent"

        # Record play if user is authenticated
        if "email" in request.session:
            master = Master.objects.filter(Email=request.session["email"]).first()
            if master and questions:
                user_profile, _ = UserProfile.objects.get_or_create(Master=master)
                QuizPlay.objects.create(
                    QuesAns=questions[0],
                    UserProfile=user_profile,
                    Score=score,
                    RemarkLevel=remark_level,
                )

        context = {
            "quiz": quiz,
            "questions": questions,
            "score": score,
            "total_questions": all_questions,
            "percentage": percentage,
            "remark_level": remark_level,
        }
        return render(request, play_result_link, context)

    context = {
        "quiz": quiz,
        "questions": questions,
        "total_questions": all_questions,
    }
    return render(request, quiz_play_link, context)
