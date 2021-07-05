from django.shortcuts import render, redirect
from django.views.generic import View, ListView, DetailView, CreateView
from django.urls import reverse_lazy, reverse
from django.apps import apps
from django import forms
from django.contrib.contenttypes.models import ContentType

from .models import Category, BaseAdvertise
from .forms import AdvertiseForm
from advertise.models.motor_model import Motors, MotorCycle, Car, AutoAccessoriesAndParts, HeavyVehicles
from advertise.forms import CarForm


def get_form(a):
    class MyForm(forms.ModelForm):
        class Meta:
            model = a
            fields = '__all__'
    return MyForm


class CategoryList(View):
    model = Category
    template_name = 'category/category_list.html'

    def get(self, request):
        context = {}
        if request.GET.get('id'):
            qs = self.model.objects.filter(parent__id=request.GET.get('id'))
            context['category'] = self.model.objects.get(id=request.GET.get('id'))
        else:
            qs = self.model.objects.filter(parent__isnull=True)
        context['object_list'] = qs
        context['advertise_form'] = AdvertiseForm()
        return render(request, self.template_name, context=context)


class CreateCategory(CreateView):
    model = Category
    fields = '__all__'
    template_name = 'category/category_create.html'
    success_url = reverse_lazy('categories')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.model.objects.filter(id=self.request.GET.get('parent')):
            context['parent'] = self.model.objects.get(id=self.request.GET.get('parent'))
            print(context['parent'])
        return context

    def post(self, request, **kwargs):
        request.POST = request.POST.copy()
        if self.request.GET.get('parent'):
            request.POST['parent'] = self.model.objects.get(id=self.request.GET.get('parent'))
        return super(CreateCategory, self).post(request, **kwargs)


class CreateAd(View):
    model = BaseAdvertise
    template_name = 'category/create_ad.html'

    def get(self, request):
        context = {}
        if request.GET.get('id'):
            qs = Category.objects.filter(parent__id=request.GET.get('id'))
            context['category'] = Category.objects.get(id=request.GET.get('id'))
            try:
                md = apps.get_model(app_label='advertise', model_name=context['category'].keyword)
                context['model_form'] = get_form(md)
            except Exception as err:
                print(err)
        else:
            qs = Category.objects.filter(parent__isnull=True)
        context['object_list'] = qs
        context['advertise_form'] = AdvertiseForm()
        return render(request, self.template_name, context=context)

    def post(self, request):
        if not request.user:
            raise ValueError()
        print(request.POST)
        user = request.user
        category = Category.objects.get(id=request.POST['ct_id'])
        try:
            md = apps.get_model(app_label='advertise', model_name=category.keyword)
            model_form = get_form(md)(request.POST)
        except Exception as err:
            raise ValueError(err)
        if model_form.is_valid():
            obj = model_form.save()
            obj.base_advertise.create(object_id=obj.id, title=model_form.data['title'], price=model_form.data['price'],
                                      description=model_form.data['description'], location=model_form.data['location'],
                                      user=user, category=category)
            print(model_form.data)

        return redirect('categories')


class CarDetail(DetailView):
    model = Car
    template_name = 'category/advertise_detail.html'

