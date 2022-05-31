from ast import Constant
from re import M, T
from django.db import models
from django.db.models.query import QuerySet
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from multiselectfield import MultiSelectField
# Create your models here.
from ckeditor.fields import RichTextField
import html
val=[FileExtensionValidator(allowed_extensions=['mp4', 'jpg','png','jpeg','avi','mov'])]
class UsersType(models.Model):
    status = [
        ("admin","Администратор"),
        ("manager","Менеджер"),
        ("kassir","Кассир")
    ]
    access  =(
        ("cashier","Кассир"),
        ("order","Заказ"),
        ("menu","Меню"),
        ("statistic","Статистика"),
        ("map","Карта"),
        ("Ad","Рассылки"),
        ("fillial","Филиалы"),
        ("users","Пользователи"),
        ("followers","Подписчики"),
        ("settings_bot","Настройки бота"),
        ("history","История заказов"),
        ("comments","Комментарии"),
    )
    
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    type = models.CharField(max_length=200,choices=status)
    accesses = MultiSelectField(choices=access)
    phone = models.CharField(max_length=13)
    active = models.BooleanField(default=False)
    @property
    def status_str(self):
        return self.get_type_display()

class Costumers(models.Model):
    lang = models.CharField(max_length=2)
    name = models.CharField(max_length=100,null=True, blank=True)
    chat_id = models.IntegerField()
    phone  =models.CharField(max_length=100,null=True, blank=True)
    code = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def lan(self):
        return f"name_{self.lang}"


class Category(models.Model):
    name_uz = models.CharField(max_length=200)
    name_ru = models.CharField(max_length=200)
    img = models.ImageField(upload_to="images/")
    active = models.BooleanField(default=False)
    parent = models.ForeignKey("Category",on_delete=models.SET_NULL,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    desc = RichTextField(null=True, blank=True)
    def __str__(self):
        return self.name_uz
    
    def __getitem__ (self, lang:str):
        if lang == "uz" or lang == "ru":
            return self.name_uz if lang == "uz" else self.name_ru
        return getattr(self, lang) if hasattr(self, lang) else None
    
        

class SubCategory(models.Model):
    categroy = models.ForeignKey(Category,on_delete=models.CASCADE)
    name_uz = models.CharField(max_length=200)
    name_ru = models.CharField(max_length=200)
    img =  models.ImageField(upload_to="images/",)
    price = models.IntegerField()
    active = models.BooleanField(default=False)
    desc = RichTextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __getitem__ (self, lang:str):
        if lang == "uz" or lang == "ru":
            return self.name_uz if lang == "uz" else self.name_ru
        return getattr(self, lang) if hasattr(self, lang) else None


class Address(models.Model):
    name_uz = models.CharField(max_length=200)
    name_ru = models.CharField(max_length=200)
    latitude = models.CharField(max_length=100,null=True,blank=True)
    longitude = models.CharField(max_length=100,null=True,blank=True)
    active = models.BooleanField(default=False)
    def __getitem__ (self, lang:str):
        if lang == "name_uz" or lang == "name_ru":
            return self.name_uz if lang == "name_uz" else self.name_ru
        return getattr(self, lang) if hasattr(self, lang) else None

class Cart(models.Model):
    costumer = models.ForeignKey(Costumers,on_delete=models.CASCADE)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    sub_category = models.ForeignKey(SubCategory,on_delete=models.CASCADE)
    count = models.IntegerField(null=True,blank=True)
    status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class Order(models.Model):
    user = models.ForeignKey(Costumers,on_delete=models.CASCADE)
    carts = models.ManyToManyField(Cart)
    address = models.ForeignKey(Address,on_delete=models.CASCADE)
    order_type = models.IntegerField(default=0)
    status = models.IntegerField(default=0)#0 yuborildi 1 tayyor bo'ldi #2 yetkazildi #3 atkaz qilindi
    latitude = models.CharField(max_length=100,null=True,blank=True)
    longitude = models.CharField(max_length=100,null=True,blank=True)
    comment = models.TextField()
    deliver_time = models.CharField(max_length=100,null=True)
    cost_type = models.CharField(max_length=100,null=True)
    created_at = models.DateTimeField(auto_now_add=True)




class Texts(models.Model):
    name = models.CharField(max_length=255)
    uz_text = RichTextField()
    ru_text = RichTextField()

    def __getitem__ (self, lang:str):
        if lang == "name_uz" or lang == "name_ru":
            return html.unescape(self.uz_text if lang == "name_uz" else html.unescape(self.ru_text) ).replace("<p>","").replace("</p>","").replace("strong","b").replace("<em>","<i>").replace("</em>","</i>").replace("<br/>","\n").replace("&nbsp;","")
        return getattr(self, lang) if hasattr(self, lang) else None
    
    def __str__(self):
        return self.name

def i18n(name:str) -> Texts:
    objs:QuerySet = Texts.objects.filter(name=name)
    return objs.first() if objs.exists() else None

import os
class AdsModel(models.Model):
    choices = [
        ("all","Все"),
        ("uz","Uz"),
        ("ru","Ru"),
    ]
    status = models.CharField(max_length=255, choices=choices)
    file =models.FileField(upload_to="images/",validators=val) 
    active = models.BooleanField(default=False)
    message = RichTextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def extension(self):        
        extension = os.path.splitext(self.file.name)
        return extension

    
class BotSettings(models.Model):
    token = models.CharField(max_length=255,default="5075005699:AAGGFW7NCbRq-TvflzsECUfU6ZzzGDFpLXU")
    click = models.CharField(max_length=255,default="1")
    payme = models.CharField(max_length=255,default="1")
    group_id = models.CharField(max_length=30,default=1)
    deliver_km = models.CharField(max_length=3,default=10)
    deliver_time_from = models.TimeField() 
    deliver_time_to = models.TimeField()


class Comments(models.Model):
    costumer = models.ForeignKey(Costumers,on_delete=models.CASCADE)
    file = models.URLField(null=True)
    comment = models.TextField()
    com_type = models.CharField(max_length=255,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
