from django.contrib import admin

from myapp.forms import BotSettingsForm
from .models import Category,Costumers,Order,SubCategory,Cart,Address, Texts, UsersType,BotSettings,AdsModel




class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at')
# Register your models here.
admin.site.register(Category)
admin.site.register(Costumers)
admin.site.register(Order, OrderAdmin)
admin.site.register(SubCategory)
admin.site.register(Cart)
admin.site.register(Address)
admin.site.register(Texts)
admin.site.register(UsersType)
admin.site.register(BotSettings)
admin.site.register(AdsModel)