from django.test import TestCase, Client
from django.urls import reverse
from quizApp.models import Master, UserProfile, QuizCategory, Subject, Quiz, QuesAns, QuizPlay


class QuizAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create test user
        self.email = "testuser@example.com"
        self.password = "secret123"
        self.master = Master.objects.create(Email=self.email, Password=self.password)
        self.profile = UserProfile.objects.create(Master=self.master, FullName="Test User")

        # Create category and subject
        self.category = QuizCategory.objects.create(category="Science")
        self.subject = Subject.objects.create(name="Physics")

        # Create a sample quiz
        self.quiz = Quiz.objects.create(
            UserProfile=self.profile,
            Category=self.category,
            Subject=self.subject,
            Title="Basic Physics",
            Duration=10,
            DifficultyLevel="easy",
            TotalScore=100,
        )

        # Create questions
        self.q1 = QuesAns.objects.create(
            Quiz=self.quiz,
            Question="What is the unit of Force?",
            Options="Newton | Joule | Watt | Pascal",
            Answer="Newton",
        )
        self.q2 = QuesAns.objects.create(
            Quiz=self.quiz,
            Question="What is the speed of light approx in vacuum?",
            Options="3x10^8 m/s | 3x10^6 m/s | 3x10^4 m/s",
            Answer="0",  # index-based answer
        )

    def test_login_page_renders(self):
        response = self.client.get(reverse("login_page"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "quiz_manage/login_page.html")

    def test_register_page_renders(self):
        response = self.client.get(reverse("register_page"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "quiz_manage/register_page.html")

    def test_registration_initiates_otp(self):
        response = self.client.post(
            reverse("registration"),
            {"email": "newuser@example.com", "password": "newpassword"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("otp_page"))
        self.assertIn("reg_data", self.client.session)
        self.assertIn("otp", self.client.session)

    def test_verify_otp_success(self):
        # Seed session with registration data
        session = self.client.session
        session["reg_data"] = {"email": "verified@example.com", "pwd": "pass"}
        session["otp"] = 123456
        session.save()

        response = self.client.post(reverse("verify_otp"), {"otp": "123456"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login_page"))

        # Verify created in DB
        self.assertTrue(Master.objects.filter(Email="verified@example.com").exists())
        master = Master.objects.get(Email="verified@example.com")
        self.assertTrue(UserProfile.objects.filter(Master=master).exists())

    def test_verify_otp_failure(self):
        session = self.client.session
        session["reg_data"] = {"email": "verified2@example.com", "pwd": "pass"}
        session["otp"] = 123456
        session.save()

        response = self.client.post(reverse("verify_otp"), {"otp": "000000"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("otp_page"))

    def test_login_success(self):
        response = self.client.post(
            reverse("login"),
            {"email": self.email, "password": self.password},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("profile_page"))
        self.assertEqual(self.client.session.get("email"), self.email)

    def test_login_invalid_password(self):
        response = self.client.post(
            reverse("login"),
            {"email": self.email, "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login_page"))

    def test_profile_page_authenticated(self):
        # Log in
        session = self.client.session
        session["email"] = self.email
        session.save()

        response = self.client.get(reverse("profile_page"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "quiz_manage/profile_page.html")
        self.assertContains(response, "Basic Physics")

    def test_profile_update(self):
        session = self.client.session
        session["email"] = self.email
        session.save()

        response = self.client.post(
            reverse("profile_update"),
            {
                "full_name": "Updated Name",
                "mobile": "9876543210",
                "gender": "m",
                "birth_date": "1995-05-15",
                "city": "Ahmedabad",
                "state": "Gujarat",
                "country": "India",
                "pincode": "380001",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.FullName, "Updated Name")
        self.assertEqual(self.profile.City, "Ahmedabad")

    def test_create_quiz(self):
        session = self.client.session
        session["email"] = self.email
        session.save()

        response = self.client.post(
            reverse("create_quiz"),
            {
                "subject": str(self.subject.id),
                "category": str(self.category.id),
                "quiz_title": "Chemistry 101",
                "duration": "15",
                "difficulty_level": "2",
                "total_score": "50",
            },
        )
        self.assertEqual(response.status_code, 302)
        created = Quiz.objects.filter(Title="Chemistry 101").first()
        self.assertIsNotNone(created)
        self.assertEqual(created.DifficultyLevel, "mid")

    def test_add_options_and_fetch_questions(self):
        session = self.client.session
        session["email"] = self.email
        session.save()

        response = self.client.post(
            reverse("add_options", args=[self.quiz.id]),
            {
                "question": "What is the capital of France?",
                "option_a": "Paris",
                "option_b": "Lyon",
                "option_c": "Marseille",
                "set_answer": "0",
            },
        )
        self.assertEqual(response.status_code, 302)

        # Test fetch_questions API
        fetch_res = self.client.get(reverse("fetch_questions", args=[self.quiz.id]))
        self.assertEqual(fetch_res.status_code, 200)
        data = fetch_res.json()
        self.assertTrue(len(data["ques_ans"]) >= 3)

    def test_play_quiz_and_scoring(self):
        # GET quiz play page
        res_get = self.client.get(reverse("play_quiz", args=[self.quiz.id]))
        self.assertEqual(res_get.status_code, 200)
        self.assertTemplateUsed(res_get, "play/quiz_play.html")

        # POST quiz play answers (both correct)
        res_post = self.client.post(
            reverse("play_quiz", args=[self.quiz.id]),
            {
                f"question_{self.q1.id}": "Newton",
                f"question_{self.q2.id}": "3x10^8 m/s",
            },
        )
        self.assertEqual(res_post.status_code, 200)
        self.assertTemplateUsed(res_post, "play/quiz_play_result.html")
        self.assertEqual(res_post.context["score"], 2)
        self.assertEqual(res_post.context["percentage"], 100.0)
        self.assertEqual(res_post.context["remark_level"], "Excellent")

    def test_change_password(self):
        session = self.client.session
        session["email"] = self.email
        session.save()

        response = self.client.post(
            reverse("change_password"),
            {
                "current_pwd": self.password,
                "new_pwd": "newsecret123",
                "rewrite_pwd": "newsecret123",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.master.refresh_from_db()
        self.assertEqual(self.master.Password, "newsecret123")

    def test_logout(self):
        session = self.client.session
        session["email"] = self.email
        session.save()

        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn("email", self.client.session)

    def test_forgot_password_success(self):
        response = self.client.post(
            reverse("forgot_pwd"),
            {"email": self.email},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("login_page"))

    def test_forgot_password_not_found(self):
        response = self.client.post(
            reverse("forgot_pwd"),
            {"email": "nonexistent@example.com"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "quiz_manage/forgot_pwd.html")
