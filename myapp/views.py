import os
from django.core.handlers.wsgi import WSGIRequest
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
import json
from django.db.models import Q
import requests
from requests.api import post
from myapp.models import (
    Address,
    AdsModel,
    BotSettings,
    Cart,
    Category,
    Comments,
    Order,
    Costumers,
    SubCategory,
    Texts,
    UsersType,
)
from .forms import (
    AddressForm,
    AdsForm,
    BotSettingsForm,
    CategoryForm,
    SubCategoryForm,
    TextsForm,
    UsersTypeForm,
    UsersTypeFormEdit,
)
from django.contrib import messages
import datetime
from myapp.management.commands.buttons import send_req,loc_address

def login_required_decorator(f):
    return login_required(f, login_url="login")


@login_required_decorator
def dashboard_page(request):
    orders: Order = Order.objects.filter(status=0)
    all_list = []
    for i in orders:
        address = f"https://maps.google.com/maps?q={i.latitude},{i.longitude}&ll={i.latitude},{i.longitude}&z=16"
        address_text =str(loc_address(i.longitude,i.latitude)).split(",")
        address_text.reverse()
        address_text = " ".join(address_text)
        data = i.carts.all()
        text = "<b>Состав заказа:</b><br>"
        price = 8000
        for j in data:
            text += f"  - {j.sub_category.name_ru} x {j.count} от {int(j.sub_category.price) * int(j.count)} сум<br>"
            price += int(j.sub_category.price) * int(j.count)
        all_list.append(
            {
                "fillial": i.address.name_ru,
                "cart": text,
                "costumer": i.user.name,
                "phone": i.user.phone,
                "order_type": i.order_type,
                "address": address,
                "address_text": address_text,
                "comment": i.comment,
                "created_at": i.created_at,
                "all_price": price,
                "id": i.id,
                "deliver_time": i.deliver_time,
                "cost_type": i.cost_type,
            }
        )
    ctx = {"orders": all_list, "kassir_active": "menu-open"}

    return render(request, "dashboard/index.html", ctx)


def dashboard_page2(request):
    orders: Order = Order.objects.filter(status=1)
    all_list = []
    for i in orders:
        address = f"https://maps.google.com/maps?q={i.latitude},{i.longitude}&ll={i.latitude},{i.longitude}&z=16"
        data = i.carts.all()
        text = "<b>Состав заказа:</b><br>"
        price = 8000
        for j in data:
            text += f"  - {j.sub_category.name_ru} x {j.count} от {int(j.sub_category.price) * int(j.count)} сум<br>"
            price += int(j.sub_category.price) * int(j.count)
        all_list.append(
            {
                "fillial": i.address.name_ru,
                "cart": text,
                "costumer": data.first().costumer.name,
                "phone": data.first().costumer.phone,
                "order_type": i.order_type,
                "address": address,
                "comment": i.comment,
                "created_at": i.created_at,
                "all_price": price,
                "id": i.id,
                "deliver_time": i.deliver_time,
            }
        )
    ctx = {"orders": all_list, "order_active": "menu-open"}
    return render(request, "dashboard/index1.html", ctx)
def dashboard_page3(request):
    orders: Order = Order.objects.filter(status__in=[2,3])
    all_list = []
    for i in orders:
        address = f"https://maps.google.com/maps?q={i.latitude},{i.longitude}&ll={i.latitude},{i.longitude}&z=16"
        data = i.carts.all()
        text = "<b>Состав заказа:</b><br>"
        price = 8000
        for j in data:
            text += f"  - {j.sub_category.name_ru} x {j.count} от {int(j.sub_category.price) * int(j.count)} сум<br>"
            price += int(j.sub_category.price) * int(j.count)
        all_list.append(
            {
                "fillial": i.address.name_ru,
                "cart": text,
                "costumer": data.first().costumer.name,
                "phone": data.first().costumer.phone,
                "order_type": i.order_type,
                "address": address,
                "comment": i.comment,
                "created_at": i.created_at,
                "all_price": price,
                "id": i.id,
                "status":str(i.status)
            }
        )
    ctx = {"orders": all_list, "history_active": "menu-open"}
    return render(request, "dashboard/index2.html", ctx)


@login_required_decorator
def status(request, pk, status):
    model = Order.objects.get(id=pk)
    model.status = status
    model.save()

    return redirect("order_list")


def dashboard_login(request):
    if request.POST:
        username = request.POST.get("username")
        usertye = UsersType.objects.filter(user__username__contains=username)
        password = request.POST.get("password")
        user = authenticate(username=username, password=password)
        if usertye:
            if user is not None and usertye.first().active:
                login(request, user)
                return redirect("dashboard")
        else:
            if user is not None:
                login(request, user)
                return redirect("dashboard")
    return render(request, "dashboard/login.html")


@login_required_decorator
def dashboard_logout(request):
    logout(request)
    res = redirect("login")
    res.delete_cookie("sessionid")
    return res


@login_required_decorator
def statistic(request):
    uz = Costumers.objects.filter(lang="uz").count()
    ru = Costumers.objects.filter(lang="ru").count()
    today_user = Costumers.objects.filter(
        created_at__day=datetime.datetime.now().day, code=0
    ).count()
    today_start = Costumers.objects.filter(
        ~Q(code=0), created_at__day=datetime.datetime.now().day
    ).count()

    all_user = Costumers.objects.all().count()
    all_user_start = Costumers.objects.filter(~Q(code=0)).all().count()
    address = Address.objects.all()
    all_list = []
    for i in address:
        order = Order.objects.filter(address_id=i.pk).count()
        all_list.append(order)
    uz_month = []
    ru_month = []
    line_chart = []
    for i in range(1, 13):
        uz_month.append(
            Costumers.objects.filter(
                lang="uz",
                created_at__month=i,
                created_at__year=datetime.datetime.now().year,
            ).count()
        )
        ru_month.append(
            Costumers.objects.filter(
                lang="ru",
                created_at__month=i,
                created_at__year=datetime.datetime.now().year,
            ).count()
        )
        line_chart.append(
            Order.objects.filter(
                created_at__month=i, created_at__year=datetime.datetime.now().year
            ).count()
        )

    ctx = {
        "uz": uz,
        "ru": ru,
        "all": all_user,
        "all_start": all_user_start,
        "statistic_active": "menu-open",
        "all_list": all_list,
        "address": address,
        "uz_month": uz_month,
        "ru_month": ru_month,
        "line_chart": line_chart,
        "today_user": today_user,
        "today_start": today_start,
    }
    return render(request, "dashboard/statistic.html", ctx)


@login_required_decorator
def category_list(request):
    categories = Category.objects.all()
    return render(
        request,
        "dashboard/category/list.html",
        {"categories": categories, "menu_active": "menu-open", "c_active": "active"},
    )


@login_required_decorator
def category_create(request):
    model = Category()
    form = CategoryForm(request.POST, request.FILES, instance=model)
    if request.POST:
        if form.is_valid():
            form.save()
            return redirect("category_list")
        else:
            print(form.errors)
    ctx = {"form": form}
    return render(request, "dashboard/category/form.html", ctx)


@login_required_decorator
def category_edit(request, pk):
    model = Category.objects.get(pk=pk)
    form = CategoryForm(request.POST or None, request.FILES or None, instance=model)
    if request.POST:
        if form.is_valid():
            form.save()
            return redirect("category_list")
        else:
            print(form.errors)
    ctx = {"form": form}
    return render(request, "dashboard/category/form.html", ctx)


@login_required_decorator
def category_delete(request, pk):
    model = Category.objects.get(pk=pk)
    model.delete()
    return redirect("category_list")


@login_required_decorator
def subcategory_list(request):
    subcategories = SubCategory.objects.all()
    return render(
        request,
        "dashboard/subcategory/list.html",
        {
            "subcategories": subcategories,
            "menu_active": "menu-open",
            "s_active": "active",
        },
    )


@login_required_decorator
def subcategory_create(request):
    model = SubCategory()
    form = SubCategoryForm(request.POST, request.FILES, instance=model)
    if request.POST:
        if form.is_valid():

            form.save()
            return redirect("subcategory_list")
        else:
            print(form.errors)
    ctx = {"form": form}
    return render(request, "dashboard/subcategory/form.html", ctx)


@login_required_decorator
def subcategory_edit(request, pk):
    model = SubCategory.objects.get(pk=pk)
    form = SubCategoryForm(request.POST or None, request.FILES or None, instance=model)
    if request.POST:
        if form.is_valid():
            form.save()
            return redirect("subcategory_list")
        else:
            print(form.errors)
    ctx = {"form": form}
    return render(request, "dashboard/subcategory/form.html", ctx)


@login_required_decorator
def subcategory_delete(request, pk):
    model = SubCategory.objects.get(pk=pk)
    model.delete()
    return redirect("subcategory_list")


@login_required_decorator
def fillials_list(request):
    address = Address.objects.all()

    ctx = {"subcategories": address, "fillial_active": "menu-open"}

    return render(request, "dashboard/address/list.html", ctx)


@login_required_decorator
def fillials_create(request):
    model = Address()
    form = AddressForm(request.POST, request.FILES, instance=model)
    if request.POST:
        if form.is_valid():

            form.save()
            return redirect("fillials_list")
        else:
            print(form.errors)
    ctx = {"form": form}
    return render(request, "dashboard/address/form.html", ctx)


@login_required_decorator
def fillials_edit(request, pk):
    model = Address.objects.get(pk=pk)
    form = AddressForm(request.POST or None, instance=model)
    if request.POST:
        if form.is_valid():
            form.save()
            return redirect("fillials_list")
        else:
            print(form.errors)
    ctx = {"form": form}
    return render(request, "dashboard/address/form.html", ctx)


@login_required_decorator
def fillials_delete(request, pk):
    model = Address.objects.get(pk=pk)
    model.delete()
    return redirect("fillials_list")


@login_required_decorator
def more_info(request, code=None):
    if code:
        if code == "today":
            users = Costumers.objects.filter(
                created_at__day=datetime.datetime.now().day
            )
            return render(
                request,
                "dashboard/more.html",
                {"users": users, "lang": code, "data": True},
            )
        users = Costumers.objects.filter(lang=code)
        if str(code) == "uz":
            code = True
        else:
            code = False
        return render(
            request, "dashboard/more.html", {"users": users, "lang": code, "data": True}
        )
    return render(
        request,
        "dashboard/more.html",
        {"users": Costumers.objects.all(), "data": False},
    )


def settings(request):
    settings = Texts.objects.order_by('id').all()
    ctx = {"t_active": "active", "settings": settings, "settings_active": "menu-open"}
    return render(request, "dashboard/settings/list.html", ctx)


def settings_edit(request, pk):
    model = Texts.objects.get(pk=pk)
    form = TextsForm(request.POST or None, instance=model)
    if request.POST:
        if form.is_valid():
            form.save()
            return redirect("settings")
        else:
            print(form.errors)
    ctx = {"form": form}
    return render(request, "dashboard/settings/form.html", ctx)


def users_list(request):
    costumers = Costumers.objects.all()
    ctx = {"costumers": costumers, "follow_active": "menu-open"}
    return render(request, "dashboard/users/list.html", ctx)


def cerate_ads(request: WSGIRequest):
    model = AdsModel()
    form = AdsForm(request.POST, request.FILES, instance=model)
    if form.is_valid():
        form.save()
        return redirect("ads_list")

    else:
        messages.info(
            request, "Тип файла должен быть в формате mp4, avi, mov, jpg, png, jpeg"
        )
    ctx = {"form": form}
    return render(request, "dashboard/ads/ads.html", ctx)


def ads_list(request: WSGIRequest):
    data = AdsModel.objects.order_by("-id").all()
    ctx = {"ads": data, "ad_active": "menu-open"}
    return render(request, "dashboard/ads/list.html", ctx)


def edit_ads(request: WSGIRequest, pk):
    model = AdsModel.objects.get(pk=pk)
    form = AdsForm(request.POST or None, request.FILES or None, instance=model)
    if form.is_valid():
        form.save()
        return redirect("ads_list")
    else:
        messages.info(
            request, "Тип файла должен быть в формате mp4, avi, mov, jpg, png, jpeg"
        )
        print(form.errors)
    ctx = {"form": form}
    return render(request, "dashboard/ads/ads.html", ctx)


def send_ads(request: WSGIRequest, pk):
    new_ad = AdsModel.objects.filter(pk=pk).first()
    post_list = {
        "id": new_ad.id,
        "users": new_ad.status,
        "file": new_ad.file.path,
        "message": new_ad.message.replace("<p>","").replace("</p>","").replace("strong","b").replace("<em>","<i>").replace("</em>","</i>").replace("<br/>","\n").replace("&nbsp;",""),
        "file_type": os.path.splitext(new_ad.file.path)[1],
        "type": "ads",
    }
    requests.get(f"http://127.0.0.1:6002/send_ads", json={"data": post_list})
    AdsModel.objects.filter(pk=pk).update(active=True)
    return redirect("ads_list")


def delete_ads(request: WSGIRequest, pk):
    model = AdsModel.objects.get(pk=pk)
    model.delete()
    return redirect("ads_list")


def create_user_type(request):
    model = UsersType()
    form = UsersTypeForm(request.POST, instance=model)
    if form.is_valid():
        req = request.POST
        password = req["password"]
        password1 = req["password1"]
        username = req["username"]
        name = req["name"]
        type = req["type"]
        phone = req["phone"]
        active = req["active"]
        access = request.POST.getlist("accesses")
        if password == password1:
            if User.objects.filter(username=username).exists():
                messages.info(request, "Пользователь существует")
            else:
                user = User.objects.create_user(
                    username=username, password=password1, first_name=name
                )
                user.save()
                UsersType.objects.create(
                    user=user,
                    type=type,
                    phone=phone,
                    accesses=access,
                    active=True if active == "on" else False,
                )
                return redirect("get_users")

        else:
            messages.info(request, "Пароль не совпадает")
            return redirect("create_user")

    ctx = {"form": form}
    return render(request, "dashboard/managers/create.html", ctx)


def get_users_types(request):
    data = UsersType.objects.order_by("-id").all()
    ctx = {"user_types": data, "manager_active": "menu-open"}
    return render(request, "dashboard/managers/list.html", ctx)


@login_required_decorator
def manager_edit(request, pk):
    model = UsersType.objects.get(pk=pk)
    form = UsersTypeFormEdit(request.POST or None, instance=model)
    if request.POST:
        if form.is_valid():
            form.save()
            return redirect("get_users")
    ctx = {
        "form": form,
        "username": model.user.username,
        "name": model.user.first_name,
    }
    return render(request, "dashboard/managers/edit.html", ctx)


@login_required_decorator
def manager_delete(request, pk):
    model = UsersType.objects.get(pk=pk)
    user = User.objects.filter(pk=model.user.id)
    user.delete()
    return redirect("get_users")


def bot_settings(request):
    bot_settings = BotSettings.objects.all()
    ctx = {
        "bot_settings": bot_settings,
        "n_active": "active",
        "settings_active": "menu-open",
    }
    return render(request, "dashboard/bot_settings/list.html", ctx)


def bot_settings_edit(request, pk):
    model = BotSettings.objects.get(pk=pk)
    form = BotSettingsForm(request.POST or None, instance=model)
    if request.POST:
        if form.is_valid():
            form.save()
            return redirect("bot_settings")
        else:
            print(form.errors)
    ctx = {"form": form}
    return render(request, "dashboard/bot_settings/form.html", ctx)


def map_view(request):
    data = Order.objects.all()
    adresses = Address.objects.filter(active=True).all()
    # [loc_address(i.longitude, i.latitude)]
    all_coord = [[(i.latitude, i.longitude),[str(i.created_at)]] for i in data]
    all_fillial = [[(i.latitude, i.longitude),i.name_ru] for i in adresses]
    ctx = {
        "all_coord": json.dumps(all_coord),
        "all_address": json.dumps(all_fillial),
        "map_active": "menu-open",
    }
    return render(request, "dashboard/maps.html", ctx)


def update_order(request, pk, status):
    if status == "confirm":
        Order.objects.filter(pk=pk).update(status=1)
        requests.get(f"http://127.0.0.1:6002/update_order", json={"data": {
            "action": "confirm",
            "order": pk
        }})
        return redirect("dashboard")
    elif status == "deny":
        Order.objects.filter(pk=pk).update(status=3)
        requests.get(f"http://127.0.0.1:6002/update_order", json={"data": {
            "action": "deny",
            "order": pk
        }})
        return redirect("dashboard")
    elif status == "done":
        Order.objects.filter(pk=pk).update(status=2)
        return redirect("orders")



def send_sms(request,phone):
    user = Costumers.objects.filter(phone=phone)
    if request.POST:
        message = request.POST['message']
        phone = request.POST['phone']
        if message and phone:
            send_req(phone.replace("+",""),user.first().id,message)
            return redirect("users_list")
    return render(request,"dashboard/sms.html",{"phone":user.first().phone})


def send_telegram(request,chat_id):
    user = Costumers.objects.filter(chat_id=chat_id)
    if request.POST:
        message = request.POST['message']
        chat_id = request.POST['chat_id']
        if message and chat_id:
            requests.get(f"http://127.0.0.1:6002/update_order", json={"data": {
            "action": "send",
            "chat_id": chat_id,
            "text":message
        }})
            return redirect("users_list")
    return render(request,"dashboard/t_sms.html",{"chat_id":user.first().chat_id})



def comments_list(request):
    comments = Comments.objects.order_by("-id").all()
    return render(request,"dashboard/users/comments.html",{"comments":comments,"comment_active":"menu-open"})


def inner(request,pk):
    orders: Order = Order.objects.filter(pk=pk)
    all_list = []
    for i in orders:
        address = f"https://maps.google.com/maps?q={i.latitude},{i.longitude}&ll={i.latitude},{i.longitude}&z=16"
        address_text =str(loc_address(i.longitude,i.latitude)).split(",")
        address_text.reverse()
        address_text = " ".join(address_text)
        data = i.carts.all()
        text = "<b>Состав заказа:</b><br>"
        price = 8000
        for j in data:
            text += f"  -{j.sub_category.name_ru} x {j.count} от {int(j.sub_category.price) * int(j.count)} сум<br>"
            price += int(j.sub_category.price) * int(j.count)
        all_list.append(
            {
                "fillial": i.address.name_ru,
                "cart": text,
                "costumer": i.user.name,
                "phone": i.user.phone,
                "order_type": i.order_type,
                "address": address,
                "address_text": address_text,
                "comment": i.comment,
                "created_at": i.created_at,
                "all_price": price,
                "id": i.id,
                "deliver_time": i.deliver_time,
                "cost_type": i.cost_type,
            }
        )
    ctx = {"orders": all_list, "z_active": "menu-open"}
    return render(request,"dashboard/zakaz.html",ctx)

# @login_required_decorator
# def dashboard_page(request):
#     orders: Order = Order.objects.filter(status=0)
#     all_list = []
#     for i in orders:
#         address = f"https://maps.google.com/maps?q={i.latitude},{i.longitude}&ll={i.latitude},{i.longitude}&z=16"
#         address_text =str(loc_address(i.longitude,i.latitude)).split(",")
#         address_text.reverse()
#         address_text = " ".join(address_text)
#         data = i.carts.all()
#         text = "<b>Состав заказа:</b><br>"
#         price = 0
#         for j in data:
#             text += f"  -{j.sub_category.name_ru} x {j.count} от {int(j.sub_category.price) * int(j.count)} сум<br>"
#             price += int(j.sub_category.price) * int(j.count)
#         all_list.append(
#             {
#                 "fillial": i.address.name_ru,
#                 "cart": text,
#                 "costumer": i.user.name,
#                 "phone": i.user.phone,
#                 "order_type": i.order_type,
#                 "address": address,
#                 "address_text": address_text,
#                 "comment": i.comment,
#                 "created_at": i.created_at,
#                 "all_price": price,
#                 "id": i.id,
#                 "deliver_time": i.deliver_time,
#                 "cost_type": i.cost_type,
#             }
#         )
#     print(all_list)
#     ctx = {"orders": all_list, "kassir_active": "menu-open"}

#     return render(request, "dashboard/index.html", ctx)
