from django.db.models import Q
from django_filters import rest_framework as filters
from flogapp.accounts.choices import RoleChoices
from .choices import ServiceRequestStatusChoices
from .models import Service, Feature, ServiceRequest, ServiceProvider


class ServiceFilter(filters.FilterSet):
    query = filters.CharFilter(method="q_filter")
    cities = filters.CharFilter(method="cities_filter")

    def cities_filter(self, queryset, name, value, *args, **kwargs):
        if value:
            queryset = queryset.filter(feature__cities__icontains=value)
        return queryset
    
    def q_filter(self, queryset, name, value, *args, **kwargs):
        queryset = queryset.filter(
            Q(name__icontains=value)
        )
        return queryset
    
    class Meta:
        model = Service
        fields = ['query', 'parent']


class ServiceFeaturerFilter(filters.FilterSet):
    query = filters.CharFilter(method="q_filter")
    cities = filters.CharFilter(lookup_expr="icontains")

    def q_filter(self, queryset, name, value, *args, **kwargs):
        queryset = queryset.filter(
            Q(name__icontains=value)
        )
        return queryset
    
    class Meta:
        model = Feature
        fields = ['query', 'service', 'cities']
        

class ServiceRequestFilter(filters.FilterSet):
    status = filters.CharFilter(method="status_filter")
    query = filters.CharFilter(method="q_filter")

    def q_filter(self, queryset, name, value, *args, **kwargs):
        return queryset.filter(
            Q(serial__icontains=value)
        )
    
    def status_filter(self, queryset, name, value, *args, **kwargs):
        try:
            value = value.split(",")
        except:
            value = [value]
        print(self.request.user.role)
        if self.request.user.role==RoleChoices.SERVICE_PROVIDER and ServiceRequestStatusChoices.APPROVED in value:
            queryset = queryset.exclude(service_provider_rejected=self.request.user.service_provider)
        return queryset.filter(status__in=value)
        
    class Meta:
        model = ServiceRequest
        fields = ['status', 'assign', 'assigned_service_provider', 'service_provider_rejected']    

class ServiceProviderFilter(filters.FilterSet):
    query = filters.CharFilter(method="q_filter")
    
    def q_filter(self, queryset, name, value, *args, **kwargs):
        queryset = queryset.filter(
            Q(name__icontains=value) |
            Q(user__name__icontains=value)
        )
        return queryset
    
    class Meta:
        model = ServiceProvider
        fields = ['query']
