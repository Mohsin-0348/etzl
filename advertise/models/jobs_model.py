from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericRelation

from rnd.models import Category, BaseAdvertise

User = get_user_model()


class JobTypeChoice(models.TextChoices):
    HIRING = 'hiring'
    SEEKING = 'seeking'


class Company(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='company_user')
    name = models.CharField(max_length=100)
    trade_license = models.CharField(max_length=32, blank=True, null=True)
    industry = models.CharField(max_length=32)
    company_size = models.CharField(max_length=10)
    company_website = models.URLField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    contact_name = models.CharField(max_length=32, blank=True, null=True)
    phone_number = models.CharField(max_length=16, blank=True, null=True)
    address = models.CharField(max_length=64, blank=True, null=True)

    def __str__(self):
        return self.name


class Jobs(models.Model):
    # jobs fields
    type = models.CharField(max_length=64, choices=JobTypeChoice.choices)  # hiring or seeking
    carrier_level = models.CharField(max_length=64, blank=True, null=True)
    work_experience = models.CharField(max_length=64, blank=True, null=True)
    education_level = models.CharField(max_length=64, blank=True, null=True)
    salary_range = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        abstract = True


class JobHiring(Jobs):
    company = models.ForeignKey(Company, on_delete=models.DO_NOTHING, related_name='job_company',
                                blank=True, null=True)
    # job hiring fields
    employment_type = models.CharField(max_length=32)
    cv_required = models.BooleanField(default=False)
    benefits = models.CharField(max_length=64)

    base_advertise = GenericRelation(BaseAdvertise)


class Skills(models.Model):
    job = models.ForeignKey(JobHiring, on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=32)


class JobSeeking(Jobs):
    # job seeking fields
    cv = models.BooleanField(default=False)
    gender = models.CharField(max_length=64, blank=True, null=True)
    nationality = models.CharField(max_length=64, blank=True, null=True)
    current_location = models.CharField(max_length=64, blank=True, null=True)
    current_company = models.CharField(max_length=64, blank=True, null=True)
    current_position = models.CharField(max_length=64, blank=True, null=True)
    notice_period = models.CharField(max_length=64, blank=True, null=True)
    visa_status = models.CharField(max_length=64, blank=True, null=True)
    commitment = models.CharField(max_length=64, blank=True, null=True)
    location_prefer = models.CharField(max_length=64, blank=True, null=True)

    base_advertise = GenericRelation(BaseAdvertise)
