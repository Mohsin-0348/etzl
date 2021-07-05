import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, AbstractUser, UserManager
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings

# ThirdParty Library Import
from easy_thumbnails.fields import ThumbnailerImageField
from django_countries.fields import CountryField

# Own Apps Files Import
from .choices import GenderChoices, CurrentCityChoices
from bases.models import BaseModel

'''
    User:: Store custom user information. all fields are common for all users.  
'''


class User(BaseModel, AbstractUser):
    email = models.EmailField(max_length=100, unique=True)  # unique email to perform email login and send alert mail.
    phone_code = models.CharField(max_length=5, blank=True, null=True)
    phone = models.CharField(max_length=15, unique=True, blank=True)  # unique contact number.
    gender = models.CharField(max_length=8, choices=GenderChoices.choices, blank=True, null=True)  # user gender specification.
    date_of_birth = models.DateField(blank=True, null=True)  # date of user birth.
    photo = ThumbnailerImageField(_('Profile Picture'), upload_to='profile_pictures/', blank=True, null=True)  # user photo.
    photo_uploaded_at = models.DateTimeField(blank=True, null=True)  # user photo uploaded timestamp
    is_superuser = models.BooleanField(default=False)  # main man of this application.
    last_active_on = models.DateTimeField(null=True, blank=True)  # define last time of active.
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)  # define when account is created.
    deactivation_reason = models.TextField(null=True, blank=True)  # store account deactivation reason.
    nationality = CountryField(blank=True, null=True)
    current_city = models.CharField(max_length=30, choices=CurrentCityChoices.choices, blank=True, null=True)
    carrier_level = models.CharField(max_length=20, blank=True, null=True)
    current_position = models.CharField(max_length=32, blank=True, null=True)
    current_company = models.CharField(max_length=32, blank=True, null=True)
    salary_expectations = models.CharField(max_length=32, blank=True, null=True)
    commitment = models.CharField(max_length=32, blank=True, null=True)
    notice_period = models.CharField(max_length=32, blank=True, null=True)
    visa_status = models.CharField(max_length=32, blank=True, null=True)
    highest_education = models.CharField(max_length=32, blank=True, null=True)
    cv = models.FileField(upload_to="user/cv/", blank=True, null=True)
    is_deleted = models.BooleanField(default=False)
    term_and_condition_accepted = models.BooleanField(default=False)
    privacy_policy_accepted = models.BooleanField(default=False)
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # generate unique id.

    # last login will provide by django abstract_base_user
    # password also provide by django abstract_base_user

    # objects = UserManager()  # define user manager

    '''
        email assign as username because by default django auth use username and password.
        to login email and password we did it.
    '''
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]  # while creating account username is must.

    # class Meta:
    #     db_table = f"{settings.DB_PREFIX}_users"  # define database table name.

    # generate user full name.
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return self.username
