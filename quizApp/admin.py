from django.contrib import admin
from .models import *

# Register your models here.
admin.site.site_header = admin.site.site_title = "Quiz Play"

all_models = [Master, UserProfile, QuesAns, Quiz, QuizCategory, QuizPlay, Subject]

for model in all_models:
    admin.site.register(model)
