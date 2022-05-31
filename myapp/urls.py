from os import name
from django.urls import path
from .views import *


urlpatterns = [
    path('', dashboard_page, name="dashboard"),
    path('orders/', dashboard_page2, name="orders"),
    path('history/', dashboard_page3, name="history"),
    path('login/', dashboard_login, name="login"),
    path('logout/', dashboard_logout, name="logout"),

    path('category/', category_list, name="category_list"),
    path('category_add/', category_create, name="category_add"),
    path('category_edit/<int:pk>/', category_edit, name="category_edit"),
    path('category_delete/<int:pk>/', category_delete, name="category_delete"),

    path('subcategory/', subcategory_list, name="subcategory_list"),
    path('subcategory_add/', subcategory_create, name="subcategory_add"),
    path('subcategory_edit/<int:pk>/', subcategory_edit, name="subcategory_edit"),
    path('subcategory_delete/<int:pk>/', subcategory_delete, name="subcategory_delete"),


    path('address/', fillials_list, name="fillials_list"),
    path('fillials_add/', fillials_create, name="fillials_add"),
    path('fillials_edit/<int:pk>/', fillials_edit, name="fillials_edit"),
    path('fillials_delete/<int:pk>/', fillials_delete, name="fillials_delete"),

    path('statistic/',statistic,name="statistic"),
    path('more/<str:code>/',more_info,name="more"),
    path('more/',more_info,name="more_info"),
    path('settings/',settings,name="settings"),
    path('users_list/',users_list,name="users_list"),
    path('comments_list/',comments_list,name="comments_list"),
    path('settings_edit/<int:pk>/', settings_edit, name="settings_edit"),



    path("create_user/",create_user_type,name="create_user"),
    path("get_users/",get_users_types,name="get_users"),
    path("manager_edit/<int:pk>/",manager_edit, name="manager_edit"),
    path("manager_delete/<int:pk>/",manager_delete,name="manager_delete"),
    
    
    
    path("cerate_ads/", cerate_ads, name="cerate_ads"),
    path("ads_list/", ads_list, name="ads_list"),
    path("edit_ads/<int:pk>/", edit_ads, name="edit_ads"),
    path("send_ads/<int:pk>/", send_ads, name="send_ads"),
    path("delete_ads/<int:pk>/", delete_ads, name="delete_ads"),

    path("bot_settings/",bot_settings, name="bot_settings"),
    path("bot_settings_edit/<int:pk>/",bot_settings_edit, name="bot_settings_edit"),


    path("maps/",map_view, name="maps"),
    path("update_order/<int:pk>/<str:status>/",update_order,name="update_order"),
    path("send_sms/<str:phone>/",send_sms,name="send_sms"),
    path("send_telegram/<int:chat_id>/",send_telegram,name="send_telegram"),
    path("inner/<int:pk>/",inner,name="inner"),



]
