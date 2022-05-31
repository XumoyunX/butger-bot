from xmlrpc.client import Boolean
from django import forms
from django.contrib.auth.models import User
from django.contrib.messages.api import add_message
from django.db.models import fields
from django.db.models.query import QuerySet
from django.forms import ModelForm, NumberInput, TextInput, EmailInput, widgets
from django.forms.fields import TimeField
from .models import Address, AdsModel, Category,SubCategory,Texts, UsersType,BotSettings

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = "__all__"
        widgets = {
            'desc': forms.Textarea(attrs={'style':'min-height: 30vh;','class': 'h-50 col-s-6 form-control','rows':3}),
            'name_uz': TextInput(attrs={
                'class': "form-control",
                
                }),
            'name_ru': TextInput(attrs={
                'class': "form-control",
                
                }),
            
        }

class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = "__all__"
        widgets = {
            'name_uz': TextInput(attrs={
                'class': "form-control",
                
                }),
            'name_ru': TextInput(attrs={
                'class': "form-control",
                
                }),
            'price': NumberInput(attrs={
                'class': "form-control",
                
                }),
        }
        
class TextsForm(forms.ModelForm):
    class Meta:
        model = Texts
        fields = ("uz_text","ru_text")
        widgets = {
            'uz_text': forms.Textarea(attrs={'class': 'form-control','rows':3}),
            'ru_text': forms.Textarea(attrs={'class': 'form-control','rows':3}),
        }

class UsersTypeForm(forms.ModelForm):
    name = forms.CharField(max_length=100)
    username = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100)
    password1 = forms.CharField(max_length=100)
    
    class Meta:
        model = UsersType
        fields = ("name","username","password","password1","type","phone","accesses","active")

        
class UsersTypeFormEdit(forms.ModelForm):
    class Meta:
        model = UsersType
        fields = ("type","phone","accesses","active")

class AddressForm(forms.ModelForm):
    class Meta:
        model =Address
        fields = "__all__"
        widgets = {
            'name_uz': TextInput(attrs={
                'class': "form-control",
                
                }),
            'name_ru': TextInput(attrs={
                'class': "form-control",
                
                }),
            'latitude': TextInput(attrs={
                'class': "form-control",
                
                }),
            'longitude': TextInput(attrs={
                'class': "form-control",
                
                }),
        }



class AdsForm(forms.ModelForm):
    class Meta: 
        model = AdsModel
        fields = ("status","file","message")
        widgets = {
            'message': forms.Textarea(attrs={'style':'min-height: 30vh;','class': 'h-50 col-s-6 form-control','rows':3}),
        }


class BotSettingsForm(forms.ModelForm):
    class Meta:
        model = BotSettings
        fields = "__all__"
        widgets = {
            'token': TextInput(attrs={
                'class': "form-control",
                
                }),
            'click': TextInput(attrs={
                'class': "form-control",
                
                }),
            'payme': TextInput(attrs={
                'class': "form-control",
                
                }),
            'group_id': TextInput(attrs={
                'class': "form-control",
                
                }),
            'deliver_km': TextInput(attrs={
                'class': "form-control",
                
                }),
            'deliver_time_from': TextInput(attrs={
                'class': "form-control"
                }),
            'deliver_time_to': TextInput(attrs={
                'class': "form-control"
                })
        }
   