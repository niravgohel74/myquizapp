# 🎯 Django Quiz Application

A full-featured, responsive web-based Quiz Application built with **Python**, **Django**, and **Bootstrap 5**. Users can register, manage their profiles, create custom quizzes with varied categories and difficulty levels, add questions, play quizzes with real-time scoring, and view detailed results.

---

## 🌐 Live Demo

🚀 **Production URL:** [https://myquizapp-dkdh.onrender.com/](https://myquizapp-dkdh.onrender.com/)

---

## ✨ Features

- **User Authentication & Security**:
  - Secure registration with OTP verification.
  - User login & session management.
  - Password recovery (Forgot Password) with OTP & credential dispatch.
  - Password change functionality inside the dashboard.
- **User Dashboard & Profile**:
  - Profile customization (Name, Contact, Gender, Birth Date, Address).
  - Profile avatar upload and storage.
  - Overview of user-created quizzes with question counts and scores.
- **Quiz Management**:
  - Create quizzes by **Subject** and **Category**.
  - Set custom time durations, total score, and difficulty level (*Easy*, *Medium*, *Hard*).
  - Add questions with multiple dynamic choices (Option A, B, C, D...) and set the correct answer.
  - AJAX-powered interactive question viewer modal.
- **Interactive Quiz Player**:
  - Clean, distraction-free quiz interface.
  - Real-time score calculation and evaluation.
  - Instant results screen displaying Score, Percentage, and Performance Remarks (*Poor*, *Average*, *Good*, *Excellent*).
- **Administration**:
  - Full Django Admin integration for managing users, quizzes, subjects, categories, and plays.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.11+, Django 5.0+
- **Database:** SQLite (Local) / PostgreSQL (Production via `DATABASE_URL`)
- **Frontend:** HTML5, CSS3, JavaScript, jQuery, Bootstrap 5
- **Static Asset Delivery:** WhiteNoise (Compressed Manifest)
- **WSGI Server:** Gunicorn
- **Deployment Platform:** Render

---

## 🚀 Getting Started Locally

### Prerequisites
- Python 3.10 or higher installed on your machine.
- Git.

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/myquizapp.git
cd myquizapp
```

### 2. Create and Activate a Virtual Environment

**On Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**On macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py migrate
```

### 5. Create an Admin Account (Optional)
```bash
python manage.py createsuperuser
```

### 6. Run the Development Server
```bash
python manage.py runserver
```

Open your browser and navigate to:
👉 **[http://127.0.0.1:8000/](http://127.0.0.1:8000/)**

---

## 🧪 Running Automated Tests

The application includes a comprehensive unit test suite covering registration, OTP verification, quiz creation, play evaluation, and profile management:

```bash
python manage.py test quizApp
```

---

## 📁 Project Structure

```text
myquizapp/
├── quizproject/          # Django project configuration (settings, urls, wsgi)
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── quizApp/              # Main Quiz application
│   ├── models.py         # Database models (Master, UserProfile, Quiz, QuesAns, etc.)
│   ├── views.py          # Application views and business logic
│   ├── urls.py           # Application route definitions
│   ├── tests.py          # Automated test suite
│   ├── templates/        # HTML templates (quiz_manage, play)
│   └── static/           # Static CSS, JavaScript, and images
├── uploads/              # User-uploaded files (profile images, question images)
├── build.sh              # Build script for Render deployment
├── render.yaml           # Render blueprint specification
├── requirements.txt      # Production & local dependencies
└── manage.py             # Django management script
```

---

## ☁️ Deployment on Render

This repository is pre-configured for deployment on **Render**:

1. Connect your GitHub repository to [Render](https://render.com/).
2. Select **Web Service** with the following settings:
   - **Environment:** `Python 3`
   - **Build Command:** `./build.sh`
   - **Start Command:** `gunicorn quizproject.wsgi:application`
3. Add environment variables under **Environment**:
   - `PYTHON_VERSION`: `3.11.9`
   - `DEBUG`: `False`
   - `SECRET_KEY`: *(Auto-generated)*

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
