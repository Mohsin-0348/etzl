from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from celery.schedules import crontab
from flogapp.taskapp.celery import app
from flogapp.utils import get_html_from_template
from flogapp.email import send_mail, send_mail_from_template
from flogapp.fcm import FCMNotificationV1
from flogapp.accounts.models import User, UserDeviceToken
from flogapp.services.models import ServiceRequest 
from flogapp.notifications.tasks import send_user_notification, send_bulk_notification

@app.task
def pending_for_approval(service_id):
    obj = ServiceRequest.objects.get(service_id)
    title = "Service Status ⌛ Under Approval ⌛"
    body = f'Your needed Service “{obj.description}“ under approval'
    send_user_notification(obj.requester_id, title, body)
    
@app.task
def request_approved(service_id):
    obj = ServiceRequest.objects.get(pk=service_id)
    title = "Service Status ⌛ FlogApp Admin Approved ⌛"
    body = f'Your Needed Service “{obj.service_feature.name}“ is approved by the FlogApp Admin team 👍'
    send_user_notification(obj.requester_id, title, body)
    
@app.task
def request_rejected(service_id):
    obj = ServiceRequest.objects.get(pk=service_id)
    title = "Service Status ⌛ FlogApp Rejected service ⌛"
    body = f'Your Needed Service "{service.service_feature.name}“ is rejected, please contact us at info@flogapp.com'
    send_user_notification(obj.requester_id, title, body)

    
@app.task
def request_accepted(service_id):
    obj = ServiceRequest.objects.get(pk=service_id)
    title = "Service Status ⌛ Aceepted ⌛"
    body = f'Your Needed Service “{obj.service_feature.name}“ is aceepted by service provider.'
    send_user_notification(obj.requester_id, title, body)

@app.task
def request_assigned(service_id):
    #TODO  -  Have to discuss
    return 
    obj = ServiceRequest.objects.get(pk=service_id)
    title = '{obj.description} assigned person'
    body = f'Your Needed Service “ Service Name “ is assigned to “Assigned person name”'
    send_user_notification(obj.requester_id, title, body)

@app.task
def request_started(service_id):
    obj = ServiceRequest.objects.get(pk=service_id)
    title = "Your job status 🌟  Started  🌟"
    body = f'Your Job has been started -Make sure to keep your cient Happy & Satisfied 🎯🤩'
    tokens = UserDeviceToken.objects.filter(user__in=obj.assign.all())
    if tokens:
        send_bulk_notification(title, body, tokens)


@app.task
def request_completed_by_maid(service_id):
    obj = ServiceRequest.objects.get(pk=service_id)
    title = "Your Service Status 👍 Completed 👍"
    body = f'Your Service has been completed - Make sure to Review & Rate your completed service 🔏'
    send_user_notification(obj.requester_id, title, body)

@app.task
def extra_hours_service_request(service_id):
    obj = ServiceRequest.objects.get(pk=service_id)
    title = f'“{obj.requester.name}” asking for extra service ⌛⏰'
    body = f'Please check your portal and accept your client extra service for client satisfaction 💼👍'
    send_user_notification(obj.assigned_service_provider.user_id, title, body)
 
@app.task
def request_extra_hours_approved(service_id):
    #TODO - To be discuss
    obj = ServiceRequest.objects.get(pk=service_id)
    title = "Extra Service Requested Status 🌟Approved 🌟"
    body = f'Your extra service requested has been approved '
    send_user_notification(obj.requester_id, title, body)

@app.task
def request_extra_hours_rejected(service_id):
    #TODO - To be discuss
    obj = ServiceRequest.objects.get(pk=service_id)
    title = "Extra Service Requested Status ⌛ Rejected  ⌛"
    body = f'Your extra service has been rejected - please contact Info@flogapp.com'
    send_user_notification(obj.requester_id, title, body)

@app.task
def new_service_request(service_id):
    obj = ServiceRequest.objects.get(pk=service_id)
    title = f"New Job is waiting for you 👀 {obj.description} 👀"
    body = f'Check it out now 🏃‍♂️ & Accept the new job for  better reputation 💼👍 & Extra Income 💰'
    tokens = UserDeviceToken.objects.values_list('device_token', flat=True).filter(user__service_provider__isnull=False)
    send_bulk_notification(title, body, tokens)

@app.task
def request_completed_by_client(service_id):
    #TODO - To be discuss
    obj = ServiceRequest.objects.get(pk=service_id)
    title = f'”{obj.requester.name}” Extra Service status 💰 Paid successfully 💰'
    body = f'“{obj.description}“ has been completed successfully 👍'
    send_user_notification(obj.assigned_service_provider.user_id, title, body)

@app.task
def request_completed_by_client_demo(service_id):
    #TODO - To be discuss
    obj = ServiceRequest.objects.get(pk=service_id)
    title = f'”{obj.requester.name}” Extra Service status 💰 Paid successfully 💰'
    body = f'“{obj.service_feature.name}“ has been completed successfully 👍'
    send_user_notification(obj.assigned_service_provider.user_id, title, body)
    
@app.task
def request_assigned(service_id, assign_ids):
    obj = ServiceRequest.objects.get(pk=service_id)
    title = f'New Job assigned “{obj.description}“'
    body = f'A new job has been assigned under your name - Make sure to be on time and do the needed service.'
    tokens = UserDeviceToken.objects.filter(user_id__in=assign_ids)
    if tokens:
        send_bulk_notification(title, body, tokens)

@app.task
def extra_service_request(service_id):
    #TODO DUplicate
    obj = ServiceRequest.objects.get(pk=service_id)
    title = f'“{obj.requester.name}“ Requested Extra Service'
    body = f'Please Accept the extra service for “{obj.description}“ so the client will do the needed payment'
    send_user_notification(obj.assigned_service_provider.user_id, title, body)


@app.task
def extra_service_request_payment_done(service_id):
    obj = ServiceRequest.objects.get(pk=service_id)
    title = f'”{obj.requester.name}” Extra Service status 💰 Paid successfully 💰'
    body = f'“{obj.requester.name}“  has been done the needed payment for the extra service job - make sure to increase his satisfaction & do the needed job  👍'
    tokens = UserDeviceToken.objects.filter(user__in=obj.parent.assign.all())
    if tokens:
        send_bulk_notification(title, body, tokens)
        
@app.task
def extra_hours_service_request_payment_success(service_id):
    #TODO - Duplicate
    obj = ServiceRequest.objects.get(pk=service_id)
    title = f'“{obj.requester.name}” asking for extra service ⌛⏰'
    body = f'Please check your portal and accept your client extra service for client satisfaction 💼👍'
    send_user_notification(obj.assigned_service_provider.user_id, title, body)
    extra_service_request_payment_done(service_id)
    
@app.task
def service_request_completed(service_id):
    obj = ServiceRequest.objects.get(pk=service_id)
    title = f'“{obj.service_feature.name}“ status 👍 Completed 👍'
    body = f'“{obj.service_feature.name}“ has been completed successfully 👍'
    send_user_notification(obj.requester_id, title, body)
