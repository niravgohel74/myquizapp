from django.db import models

# Create your models here.
class Master(models.Model):
    Email = models.EmailField(unique=True)
    Password = models.CharField(max_length=20, null=True)

gender_choices={
    ('m', 'male'),
    ('f', 'female')
}


class UserProfile(models.Model):
    Master = models.ForeignKey(Master, on_delete = models.CASCADE)
    FullName = models.CharField(max_length=25, null=True, default='')
    Mobile = models.CharField(max_length=10, null=True, default='')
    Gender = models.CharField(choices=gender_choices, max_length=2, default='')
    BirthDate = models.DateField(auto_created=True, default='1990-01-01')
    City = models.CharField(max_length=30, null=True, default='')
    State = models.CharField(max_length=25, null=True, default='')
    Country = models.CharField(max_length=15, null=True, default='')
    Pincode = models.CharField(max_length=10, null=True, default='')

