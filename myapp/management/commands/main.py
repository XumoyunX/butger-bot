from flask import  request
import random
import time
from django.core.management.base import BaseCommand
from django.db.models.query import QuerySet
from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    LabeledPrice
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    Filters,
    CallbackContext, PreCheckoutQueryHandler
)
from datetime import datetime
import json
from myapp.management.commands.constant import ttrt

from myapp.views import settings
from .buttons import *
from .globals import *
from myapp.models import Address, BotSettings, Cart, Costumers, Order, i18n,Comments
from flask import Flask
import threading


def check_user_data(func):
    def inner(update: Update, context: CallbackContext):
        try:
            chat_id = update.message.from_user.id
        except:
            chat_id = update.callback_query.message.chat_id
        user = Costumers.objects.filter(chat_id=chat_id)
        state = context.user_data.get("state", 0)
        if state in ['phone', 'name', 'languageCode', 0, 'code']:
            if user:
                user = user.first()
                if not user.lang:
                    callback_data = update.callback_query
                    if callback_data:
                        if callback_data.data in ["uz", "ru"]:
                            print("vvvvv")
                            Costumers.objects.filter(chat_id=chat_id).update(
                                lang=callback_data.data
                            )
                            user.refresh_from_db()
                            context.user_data["state"] = "name"
                            return check_user_state(update, context)

                    context.user_data['language_message'] = context.bot.send_message(
                        chat_id=chat_id,
                        text=i18n("start_text").uz_text.replace("<p>", "").replace("</p>", "").replace("strong", "b").replace(
                            "<em>", "<i>").replace("</em>", "</i>").replace("<br/>", "\n").replace("&nbsp;", ""),
                        reply_markup=InlineKeyboardMarkup(lang), parse_mode="HTML"
                    )

                    context.user_data["state"] = "languageCode"
                elif not user.name:
                    lang_code = Costumers.objects.filter(chat_id=chat_id)
                    if state == "name":
                        try:
                            context.user_data['name_message'].delete()
                        except:
                            ...
                        update.message.delete()
                        if update.message.text == "/start":
                            return check_user_state(update, context)

                        Costumers.objects.filter(chat_id=chat_id).update(
                            name=update.message.text)
                        user.refresh_from_db()
                        context.user_data["state"] = "name"
                        return check_user_state(update, context)
                    context.user_data['name_message'] = context.bot.send_message(
                        chat_id=chat_id, text=i18n("your_name")[
                            lang_code.first().lan], parse_mode="HTML"
                    )
                    context.user_data["state"] = "name"
                elif not user.phone:
                    try:
                        context.bot.delete_message(
                            chat_id=chat_id, message_id=update.message.message_id-1)
                    except:
                        ...
                    update.message.delete()
                    lang_code = Costumers.objects.filter(chat_id=chat_id)
                    buttons = [
                        [
                            KeyboardButton(
                                text=i18n("contact")[lang_code.first().lan],
                                request_contact=True,
                            )
                        ]
                    ]
                    context.user_data['contact_message'] = update.message.reply_text(
                        text=i18n("contact_text")[lang_code.first().lan],
                        reply_markup=ReplyKeyboardMarkup(
                            buttons, resize_keyboard=True),
                    )
                    context.user_data["state"] = "phone"
                elif user.code != 0:
                    try:
                        context.bot.delete_message(
                            chat_id=chat_id, message_id=update.message.message_id-1)
                        update.message.delete()
                    except:
                        ...
                    lang_code = Costumers.objects.filter(chat_id=chat_id)
                    msg = update.message.text
                    if msg == i18n("resend_code")[lang_code.first().lan]:
                        context.bot.send_message(
                            chat_id=chat_id,
                            text=i18n("resend_code_text")[
                                lang_code.first().lan],
                            reply_markup=ReplyKeyboardRemove(), parse_mode="HTML")
                        code = random.randint(123456, 987654)
                        lang_code.update(code=code)
                        send_req(lang_code.first().phone, message_id=update.message.message_id, message=i18n(
                            "send_sms_text")[lang_code.first().lan].format(code=code))
                    elif msg == "/start":
                        return check_user_state(update, context)
                    elif state == "code":
                        if msg.isdigit() and len(msg) == 6 and int(msg) == user.code:
                            try:
                                context.bot.delete_message(
                                    chat_id=chat_id, message_id=update.message.message_id-1)
                                update.message.delete()
                            except:
                                ...
                            Costumers.objects.filter(
                                chat_id=chat_id).update(code=0)
                            return start_handler(update, context)

                        else:
                            button = [
                                [KeyboardButton(i18n("resend_code")[lang_code.first().lan])]]
                            context.bot.send_message(chat_id=chat_id, text=i18n("error_code")[lang_code.first(
                            ).lan], reply_markup=ReplyKeyboardMarkup(button, resize_keyboard=True), parse_mode="HTML")
                            context.user_data["state"] = "code"

                else:
                    return func(update, context)

            else:
                Costumers.objects.create(chat_id=chat_id)
                context.user_data['language_message'] = context.bot.send_message(
                    chat_id=chat_id,
                    text=i18n("start_text").uz_text.replace("<p>", "").replace("</p>", "").replace("strong", "b").replace(
                        "<em>", "<i>").replace("</em>", "</i>").replace("<br/>", "\n").replace("&nbsp;", ""),
                    reply_markup=InlineKeyboardMarkup(lang), parse_mode="HTML"
                )
                context.user_data["state"] = "languageCode"
        else:
            return func(update, context)

    return inner


def check_user_state(update: Update, context):
    try:
        chat_id = update.message.from_user.id
    except:
        chat_id = update.callback_query.message.chat_id
    user = Costumers.objects.filter(chat_id=chat_id)
    if user:
        user = user.first()
        if not user.lang:
            context.user_data['language_message'] = context.bot.send_message(
                chat_id=user.id,
                text=i18n("start_text").uz_text.replace("<p>", "").replace("</p>", "").replace("strong", "b").replace(
                    "<em>", "<i>").replace("</em>", "</i>").replace("<br/>", "\n").replace("&nbsp;", ""),
                reply_markup=InlineKeyboardMarkup(lang), parse_mode="HTML"
            )
            context.user_data["state"] = "languageCode"
        elif not user.name:
            try:
                context.user_data['language_message'].delete()
            except:
                ...
            lang_code = Costumers.objects.filter(chat_id=chat_id)
            context.user_data['name_message'] = context.bot.send_message(
                chat_id=chat_id, text=i18n("your_name")[
                    lang_code.first().lan], parse_mode="HTML"
            )
            context.user_data["state"] = "name"

        elif not user.phone:
            lang_code = Costumers.objects.filter(chat_id=chat_id)
            buttons = [
                [
                    KeyboardButton(
                        text=i18n("contact")[lang_code.first().lan],
                        request_contact=True,
                    )
                ]
            ]
            context.user_data['contact_message'] = update.message.reply_text(
                text=i18n("contact_text")[lang_code.first().lan],
                reply_markup=ReplyKeyboardMarkup(
                    buttons, resize_keyboard=True),
            )
            context.user_data["state"] = "phone"

        elif user.code != 0:
            lang_code = Costumers.objects.filter(chat_id=chat_id)
            button = [
                [KeyboardButton(i18n("resend_code")[lang_code.first().lan])]]
            context.bot.send_message(
                chat_id=chat_id,
                text=i18n("v_code")[lang_code.first().lan],
                reply_markup=ReplyKeyboardMarkup(button, resize_keyboard=True), parse_mode="HTML"
            )
            context.user_data["state"] = "code"

        else:
            lang_code = Costumers.objects.filter(chat_id=chat_id)
            buttons = get_category(lang_code.first().lan)
            buttons.append(extra_buttons(lang_code.first().lan))
            buttons.append([InlineKeyboardButton(i18n("change_lang")[
                           lang_code.first().lan], callback_data="change_lang")])
            buttons.append([InlineKeyboardButton(i18n("leave_comment")[
                   lang_code.first().lan], callback_data="leave_comment")])
            context.bot.send_message(
                chat_id=chat_id,
                text=i18n("menu")[lang_code.first().lan],
                reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML"
            )

    else:
        context.user_data['language_message'] = context.bot.send_message(
            chat_id=chat_id,
            text=i18n("start_text").uz_text.replace("<p>", "").replace("</p>", "").replace("strong","b").replace("<em>", "<i>").replace("</em>", "</i>").replace("<br/>", "\n").replace("&nbsp;", ""),
            reply_markup=InlineKeyboardMarkup(lang), parse_mode="HTML"
        )
        context.user_data["state"] = "languageCode"


@check_user_data
def start_handler(update, context: CallbackContext):
    try:
        chat_id = update.message.from_user.id
        first_name = update.message.from_user.first_name
    except:
        chat_id = update.callback_query.message.chat_id
    db_user = Costumers.objects.filter(chat_id=chat_id).first()
    state = context.user_data.get("state", 0)
    if db_user:
        if update:
            try:
                msg = update.message.text
            except:
                msg = update.callback_query
            if msg == "/start":
                now = datetime.now().strftime("%H")
                if int(now) <= 12:
                    context.user_data['hello'] = context.bot.send_message(chat_id=chat_id,text=i18n("good_morning")[db_user.lan].format(first_name=first_name),reply_markup=ReplyKeyboardRemove())
                elif 12 < int(now) <= 18:
                    context.user_data['hello'] = context.bot.send_message(chat_id=chat_id,text=i18n("good_afternoon")[db_user.lan].format(first_name=first_name),reply_markup=ReplyKeyboardRemove())
                elif 18 < int(now) <= 23:
                    context.user_data['hello'] = context.bot.send_message(chat_id=chat_id,text=i18n("good_evening")[db_user.lan].format(first_name=first_name),reply_markup=ReplyKeyboardRemove())
                else:
                    pass
        buttons = get_category(db_user.lan)
        buttons.append(extra_buttons(db_user.lan))
        buttons.append([InlineKeyboardButton(i18n("change_lang")[
                       db_user.lan], callback_data="change_lang")])
        buttons.append([InlineKeyboardButton(i18n("leave_comment")[
                   db_user.lan], callback_data="leave_comment")])

        context.bot.send_message(
            chat_id=chat_id,
            text=i18n("menu")[db_user.lan],
            reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML"
        )
    else:
        check_user_state(update, context)


@check_user_data
def start_inline(update, context):
    chat_id = update.callback_query.message.chat_id
    message_id = update.callback_query.message.message_id
    db_user = Costumers.objects.filter(chat_id=chat_id).first()
    state = context.user_data.get("state", 0)
    buttons = get_category(db_user.lan)
    buttons.append(extra_buttons(db_user.lan))
    buttons.append([InlineKeyboardButton(i18n("change_lang")[
                   db_user.lan], callback_data="change_lang")])
    buttons.append([InlineKeyboardButton(i18n("leave_comment")[
                   db_user.lan], callback_data="leave_comment")])
    context.bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=i18n("menu")[db_user.lan],
        reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML"
    )


@check_user_data
def message_handler(update, context):
    chat_id = update.message.from_user.id
    msg = update.message.text
    message_id = update.message.message_id
    state = context.user_data.get("state", 0)
    cart = context.user_data.get("cart", {})
    db_user = Costumers.objects.filter(chat_id=chat_id).first()
    if state == "name" and msg != i18n("back_btn")[db_user.lan]:
        try:
            context.bot.delete_message(chat_id=chat_id,message_id=message_id-1)
        except:...
        update.message.delete()
        Costumers.objects.filter(chat_id=chat_id).update(name=msg)
        check_user_state(update, context)
    elif msg == i18n("main_btn")[db_user.lan]:
        try:
            update.message.delete()
            context.bot.delete_message(chat_id=chat_id,message_id=message_id-2)
            context.user_data['invoice'].delete()
        except:...
        start_handler(update,context)
    elif state == "code":
        if msg.isdigit() and len(msg) == 6 and int(msg) == db_user.code:
            Costumers.objects.filter(chat_id=chat_id).update(code=0)
            context.bot.delete_message(
                chat_id=chat_id, message_id=message_id-2)
            update.message.delete()
            start_handler(update, context)
        elif msg != i18n("resend_code")[db_user.lan]:
            button = [[KeyboardButton(i18n("resend_code")[db_user.lan])]]
            context.bot.send_message(
                chat_id=chat_id,
                text=i18n("error_code")[db_user.lan],
                reply_markup=ReplyKeyboardMarkup(button, resize_keyboard=True), parse_mode="HTML"
            )
        else:
            context.bot.send_message(
                chat_id=chat_id,
                text=i18n("resend_code_text")[db_user.lan],
                reply_markup=ReplyKeyboardRemove(), parse_mode="HTML")
    elif msg == i18n("back_btn")[db_user.lan] and state not in ["comment", "loc","phone","name"]:
        update.message.delete()
        try:
            context.bot.delete_message(
                chat_id=chat_id, message_id=message_id-1)
        except:
            ...
        
        buttons = deliver_type_btn(db_user)
        context.bot.send_message(
            chat_id=chat_id,
            text=i18n("deliver_type")[db_user.lan],
            reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML"
        )
    elif msg == i18n("back_btn")[db_user.lan] and state in ["phone","name"]:
        update.message.delete()
        context.bot.delete_message(chat_id=chat_id,message_id=message_id-1)
        settings_page(update,db_user)

    elif state == 'loc':
        buttons = [[KeyboardButton(i18n("next_btn")[db_user.lan])], [
            KeyboardButton(i18n("back_btn")[db_user.lan])]]
        if msg == i18n("near_fillial")[db_user.lan]:
            context.bot.send_message(chat_id=chat_id, text=i18n("comment")[
                                     db_user.lan], reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True), parse_mode="HTML")
            context.user_data['state'] = "comment"
        elif msg == i18n("back_btn")[db_user.lan]:
            try:
                context.bot.delete_message(
                    chat_id=chat_id, message_id=message_id-1)
                update.message.delete()
            except:
                ...
            if cart:
                if cart['deliver_type'] ==1:
                    buttons = deliver_type_btn(db_user)
                    context.bot.send_message(
                    chat_id=chat_id,
                    text=i18n("deliver_type")[db_user.lan],
                    reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML"
                    )
                else:
                    costum_time(update,context,datetime.now().strftime("%H:%M").split(":")[0],"00",db_user)
            else:
                costum_time(update,context,datetime.now().strftime("%H:%M").split(":")[0],"00",db_user)
            
        elif msg == i18n("accept")[db_user.lan]:
            context.bot.send_message(chat_id=chat_id, text=i18n("comment")[
                                     db_user.lan], reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True), parse_mode="HTML")
            context.user_data['state'] = "comment"

        else:
            ad = Address.objects.filter(**{f"name_{db_user.lang}": msg})
            context.user_data['cart'].update(
                {"near": ad.first().id if ad.exists() else None})
            context.bot.send_message(chat_id=chat_id, text=i18n("comment")[
                                     db_user.lan], reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True), parse_mode="HTML")
            context.user_data['state'] = "comment"

    elif state == "comment":
        if msg != i18n("next_btn")[db_user.lan] and msg != i18n("back_btn")[db_user.lan]:
            context.user_data['cart'].update({"msg": msg})
            try:
                context.bot.delete_message(
                    chat_id=chat_id, message_id=message_id-1)
            except:
                ...

            update.message.delete()
            all_carts = Cart.objects.filter(
                status=False, costumer=db_user).all()
            address = Address.objects.filter(pk=cart['near']).first()
            if cart['deliver_type'] == 1:
                data = Cart.objects.filter(
                    status=False, costumer_id=db_user.id).all()
                button = []
                if data:
                    text = f""
                    total = 0
                    for i in data:
                        text += f"<b>{i.category[db_user.lan]}\n   └ {i.sub_category[db_user.lan]}→</b> {i.count} x {i.sub_category.price} = {i.count * i.sub_category.price} {i18n('price_lang')[db_user.lan]}\n\n"
                        total += i.count * i.sub_category.price
                    button.append(
                        [
                            InlineKeyboardButton(
                                i18n("accept")[db_user.lan],
                                callback_data=f"accept_order",
                            )
                        ]
                    )
                    button.append(
                        [
                            InlineKeyboardButton(
                                i18n("resend_loc")[
                                    db_user.lan], callback_data=f"accept_loc"
                            )
                        ]
                    )
                    text += i18n("bring_order")[db_user.lan].format(total=total, deliver_type=i18n("on_foot")[
                        db_user.lan], address=cart['address'], fillial=Address.objects.filter(pk=cart['near']).first()[db_user.lan])
                    context.bot.send_message(
                        chat_id=chat_id,
                        text=text,
                        reply_markup=InlineKeyboardMarkup(button),
                        parse_mode="HTML",
                    )
            else:
                pay_method(Cart, db_user, cart, update, context, chat_id)

        elif msg == i18n("back_btn")[db_user.lan]:
            address = loc_address(cart['longitude'], cart['latitude'])
            data = address.raw["address"]
            try:
                home = data['road']
            except:
                home = data['house_number']
            try:
                neighbourhood = data['neighbourhood']
            except:
                neighbourhood = ""
            text = f"{data['country']}, {data['city']}, {data['county']}, {neighbourhood}, {home}"
            all_address = Address.objects.filter(active=True).all()
            near_address = distace(
                your_distance=(cart['latitude'], cart['longitude']
                               ), all_loc=all_address, db_user=db_user
            )
            context.user_data['cart'].update({"address": text})
            if cart['deliver_type'] == 1:
                context.bot.send_message(
                    chat_id=chat_id,
                    text=i18n("your_address")[db_user.lan].format(
                        your_address=text, near_address=Address.objects.filter(
                            pk=near_address["address"]).first()[db_user.lan]
                    ), reply_markup=get_all_address(db_user.lan), parse_mode="HTML"
                )
                context.user_data['cart'].update(
                    {"near": near_address['address'], "latitude": cart['latitude'], "longitude": cart['longitude']})
                context.user_data['state'] = 'loc'

            elif cart['deliver_type'] == 0:
                context.bot.send_message(
                    chat_id=chat_id,
                    text=i18n("your_address")[db_user.lan].format(
                        your_address=text, near_address=Address.objects.filter(
                            pk=near_address["address"]).first()[db_user.lan]
                    ), reply_markup=get_near_address(db_user.lan), parse_mode="HTML"
                )
                context.user_data['cart'].update(
                    {"near": near_address['address'], "latitude": cart['latitude'], "longitude": cart['longitude']})
                context.user_data['state'] = 'loc'

        else:
            context.user_data['cart'].update({"msg": ""})
            try:
                context.bot.delete_message(
                    chat_id=chat_id, message_id=message_id-1)
            except:
                ...
            update.message.delete()
            all_carts = Cart.objects.filter(
                status=False, costumer=db_user).all()
            address = Address.objects.filter(pk=cart['near']).first()
            if cart['deliver_type'] == 1:
                data = Cart.objects.filter(
                    status=False, costumer_id=db_user.id).all()
                button = []
                if data:
                    text = f""
                    total = 0
                    for i in data:
                        text += f"<b>{i.category[db_user.lan]}\n   └ {i.sub_category[db_user.lan]}→</b> {i.count} x {i.sub_category.price} = {i.count * i.sub_category.price} {i18n('price_lang')[db_user.lan]}\n\n"
                        total += i.count * i.sub_category.price
                    button.append(
                        [
                            InlineKeyboardButton(
                                i18n("accept")[db_user.lan],
                                callback_data=f"accept_order",
                            )
                        ]
                    )
                    button.append(
                        [
                            InlineKeyboardButton(
                                i18n("resend_loc")[
                                    db_user.lan], callback_data=f"accept_loc"
                            )
                        ]
                    )
                    button.append(
                        [
                            InlineKeyboardButton(
                                i18n("back_btn")[
                                    db_user.lan], callback_data=f"backk"
                            )
                        ]
                    )
                    text += i18n("bring_order")[db_user.lan].format(total=total, deliver_type=i18n("on_foot")[
                        db_user.lan], address=cart['address'], fillial=Address.objects.filter(pk=cart['near']).first()[db_user.lan])
                    context.bot.send_message(
                        chat_id=chat_id,
                        text=text,
                        reply_markup=InlineKeyboardMarkup(button),
                        parse_mode="HTML",
                    )
            else:
                pay_method(Cart, db_user, cart, update, context, chat_id)
    elif state == "com_del":
        try:
            context.bot.delete_message(chat_id=chat_id,message_id=message_id-1)
        except:...
        context.bot.send_message(chat_id=chat_id,text=i18n("create_comment")[db_user.lan],reply_markup=ReplyKeyboardRemove())
        Comments.objects.create(costumer_id=db_user.id,comment=msg,com_type="Доставка")
        start_handler(update,context)
    elif state == "com_food":
        try:
            context.bot.delete_message(chat_id=chat_id,message_id=message_id-1)
        except:...
        context.bot.send_message(chat_id=chat_id,text=i18n("create_comment")[db_user.lan],reply_markup=ReplyKeyboardRemove())
        Comments.objects.create(costumer_id=db_user.id,comment=msg,com_type="Еда")
        start_handler(update,context)

@ttrt
@check_user_data
def inline_handler(update: Update, context: CallbackContext):
    print("inline")
    query = update.callback_query
    chat_id = update.callback_query.message.chat_id
    message_id = query.message.message_id
    data_split = query.data.split("_")
    state = context.user_data.get("state", 0)
    db_user = Costumers.objects.filter(chat_id=chat_id).first()
    cart = context.user_data.get("cart", {})
    settings_bot = BotSettings.objects.all().first()
    if data_split[0] == "category":
        if not Category.objects.filter(parent_id=int(data_split[1])):
            sub = SubCategory.objects.filter(
                categroy_id=int(data_split[1]))
            text = ""
            if sub:
                for i in sub:
                    text += f"<b>{i[db_user.lan]}</b> - {i.price} {i18n('price_lang')[db_user.lan]}\n"
                text+="<b>-----</b>\n"
                text += Category.objects.filter(id=int(data_split[1])).first().desc.replace("<p>", "").replace("</p>", "").replace(
                    "strong", "b").replace("<em>", "<i>").replace("</em>", "</i>").replace("<br/>", "\n").replace("&nbsp;", "")
            context.bot.delete_message(
                message_id=message_id, chat_id=chat_id)
            subcategory = get_subcategory(db_user.lan, int(data_split[1]))
            category = Category.objects.filter(
                pk=int(data_split[1])).first()
            context.bot.send_photo(
                chat_id=chat_id,
                photo=open(category.img.path, "rb"), caption=text,
                reply_markup=subcategory,parse_mode="HTML"
            )
        else:
            context.bot.delete_message(
                message_id=message_id, chat_id=chat_id)
            category = Category.objects.filter(
                pk=int(data_split[1])).first()
            subcategory = get_category(db_user.lan, category)
            subcategory.append([InlineKeyboardButton(
                i18n("back_btn")[db_user.lan], callback_data=f"subcategory_back")])
            dat = Category.objects.filter(active=True, parent=category)
            text = ""
            if dat:
                for i in dat:
                    text += f"<b>{i[db_user.lan]}</b>\n"
                text += "<b>-----</b>\n"
                text += category.desc.replace("<p>", "").replace("</p>", "").replace("strong", "b").replace(
                    "<em>", "<i>").replace("</em>", "</i>").replace("<br/>", "\n").replace("&nbsp;", "")
            context.bot.send_photo(
                chat_id=chat_id,
                photo=open(category.img.path, "rb"), caption=text,
                reply_markup=InlineKeyboardMarkup(subcategory),parse_mode="HTML")

    # else:
    #     context.bot.answer_callback_query(callback_query_id=query.id, text=i18n("end_work")[db_user.lan].format(
    #         from_time=settings_bot.deliver_time_from, to_time=settings_bot.deliver_time_to), show_alert=True)
    elif data_split[0] == "subcategory":
        if data_split[1] == "back":
            context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            start_handler(update, context)
        else:
            sub = SubCategory.objects.filter(pk=int(data_split[1])).first()
            text = ""
            text += f"<b>{sub[db_user.lan]}</b>\n    {1} * {sub.price} = {1 * int(sub.price)} {i18n('price_lang')[db_user.lan]}\n<b>-----</b>\n"
            text += sub.desc.replace("<p>", "").replace("</p>", "").replace("strong", "b").replace("<em>", "<i>").replace("</em>", "</i>").replace("<br/>", "\n").replace("&nbsp;", "")
            a = calculate(1, db_user.lan, int(
                data_split[2]), int(data_split[1]))
            context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            context.bot.send_photo(
                chat_id=chat_id,
                photo=open(sub.img.path, "rb"),
                caption=text,
                reply_markup=InlineKeyboardMarkup(a),parse_mode="HTML"
            )
            context.user_data["state"] = "test"
    elif data_split[0] == "accept":
        if data_split[1] == "order":
            context.user_data['cart'].update({"time":"Сейчас"})
            cart = context.user_data.get('cart')
            all_carts = Cart.objects.filter(
                status=False, costumer=db_user).all()
            address = Address.objects.filter(pk=cart['near']).first()
            data: Order = Order.objects.create(
                user_id=db_user.id, address=address, order_type=cart['deliver_type'], latitude=cart['latitude'], longitude=cart['longitude'], comment=cart['msg'],deliver_time=cart['time'])
            for i in all_carts:
                data.carts.add(i)
                Cart.objects.filter(pk=i.id).update(status=True)
            order: Order = data
            address_link = f"https://maps.google.com/maps?q={order.latitude},{order.longitude}&ll={order.latitude},{order.longitude}&z=16"
            data = order.carts.all()
            text = ""
            price = 0
            d_type = ""
            o_time = order.created_at.strftime("%d-%m-%Y %H:%M")
            for j in data:
                text += f"\n<b>-</b> {j.sub_category.name_ru} x {j.count} от {int(j.sub_category.price) * int(j.count)} сум"
                price += int(j.sub_category.price) * int(j.count)

            d_type = "Забрать"
            Text = f"<b>№ Заказы:</b> #N{order.id}\n<b>Филиал:</b> {order.address.name_ru}\n<b>Состав заказа:</b> {text}\n<b>Клиент:</b> {data.first().costumer.name}\n<b>Тип доставки:</b> {d_type}\n<b>Комментарий</b> {cart['msg'] if cart['msg'] else 'Нет'}\n<b>Итого:</b> {price} сум"

            group_id = int(settings_bot.group_id)
            try:
                context.bot.send_message(
                    chat_id=group_id, text=Text, parse_mode="HTML")
            except:
                ...
            start_inline(update, context)
            context.bot.send_message(chat_id=chat_id, text=i18n("accept_order")[
                                     db_user.lan], reply_markup=ReplyKeyboardRemove(), parse_mode="HTML")
        else:
            loc = [
                [
                    KeyboardButton(
                        i18n("send_location_btn")[
                            db_user.lan], request_location=True
                    )
                ],
                [
                    KeyboardButton(
                        i18n("back_btn")[db_user.lan]
                    )
                ]
            ]
            data = context.bot.send_message(
                chat_id=chat_id,
                text=i18n("send_location")[db_user.lan],
                reply_markup=ReplyKeyboardMarkup(loc, resize_keyboard=True), parse_mode="HTML"
            )
            context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            context.user_data['cart'] = {"deliver_type": 1}
            context.user_data['state'] = "loc"

    elif data_split[0] == "cost":
        if data_split[1] == "loc":
            context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            loc = [
                [
                    KeyboardButton(
                        i18n("send_location_btn")[
                            db_user.lan], request_location=True
                    )
                ],
                [
                    KeyboardButton(
                        i18n("back_btn")[db_user.lan]
                    )
                ]
            ]
            data = context.bot.send_message(
                chat_id=chat_id,
                text=i18n("send_location")[db_user.lan],
                reply_markup=ReplyKeyboardMarkup(loc, resize_keyboard=True), parse_mode="HTML"
            )
            context.user_data['cart'] = {"deliver_type": 0}
            context.user_data['state'] = "loc"
        else:
            data = Cart.objects.filter(status=False, costumer_id=db_user.id)
            price = 8000
            for j in data:
                price += int(j.sub_category.price) * int(j.count)
            if price >= 11000:
                if data_split[1] == "cash":
                    try:
                        context.bot.delete_message(chat_id=chat_id, message_id=message_id)
                    except:...
                    context.user_data['cart'].update({"cost_type":"Наличные"})
                    order_func(Cart, db_user, cart, Order,BotSettings.objects.all().first().group_id, context)
                    context.bot.send_message(chat_id=db_user.chat_id, text=i18n("accept_order")[
                                             db_user.lan], reply_markup=ReplyKeyboardRemove(), parse_mode="HTML")                      
                    start_handler(update, context)
                elif data_split[1] == "payme":
                    # context.bot.answer_callback_query(
                    # callback_query_id=query.id, text="Bot da texnik ishlar olib borilayotganligi sababli bu bo'lim vaqtincha ishlamayapti.Noqulayliklar uchun uzr so'raymiz!", show_alert=True)
                    context.bot.send_message(chat_id=chat_id, text="to'lov uchun", reply_markup=ReplyKeyboardMarkup(
                        [[KeyboardButton(i18n("main_btn")[db_user.lan])]], resize_keyboard=True))
                    payme(update, context, price)
                    context.user_data['cart'].update({"cost_type":"Payme"})

                elif data_split[1] == "click":
                    # context.bot.answer_callback_query(
                    # callback_query_id=query.id, text="Bot da texnik ishlar olib borilayotganligi sababli bu bo'lim vaqtincha ishlamayapti.Noqulayliklar uchun uzr so'raymiz!", show_alert=True)
                    context.bot.send_message(chat_id=chat_id, text="to'lov uchun", reply_markup=ReplyKeyboardMarkup(
                        [[KeyboardButton(i18n("main_btn")[db_user.lan])]], resize_keyboard=True))
                    click(update, context, price)
                    context.user_data['cart'].update({"cost_type":"Click"})
            else:
                context.bot.answer_callback_query(
                    callback_query_id=query.id, text="Buyurtmaning umumiy narxi kamida 20 ming bo'lish kerak", show_alert=True)
                start_inline(update, context)
    elif data_split[0] == "change":
        if data_split[1] == "back":
            context.bot.delete_message(chat_id=chat_id, message_id=message_id)
            subcategory = get_subcategory(db_user.lan, int(data_split[2]))
            category = Category.objects.filter(pk=int(data_split[2])).first()
            sub = SubCategory.objects.filter(categroy_id=int(data_split[2]))
            text = ""
            if sub:
                text += category.desc.replace("<p>", "").replace("</p>", "").replace("strong", "b").replace(
                    "<em>", "<i>").replace("</em>", "</i>").replace("<br/>", "\n").replace("&nbsp;", "")
                for i in sub:
                    text += f"{i[db_user.lan]} - {i.price}\n"
            context.bot.send_photo(
                chat_id=chat_id,
                photo=open(category.img.path, "rb"), caption=text,
                reply_markup=subcategory,
            )
        else:
            context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=i18n("change_lang")[db_user.lan],
                reply_markup=InlineKeyboardMarkup(lang),
            )
            context.user_data["state"] = "change_again"

    elif state == "languageCode":
        print("aaaa")
        Costumers.objects.filter(chat_id=chat_id).update(lang=query.data)
        check_user_state(update, context)

    elif data_split[0] in ["uz", "ru"] and state != "languageCode":
        dat = Costumers.objects.filter(chat_id=chat_id).update(lang=query.data)
        db_user = Costumers.objects.filter(chat_id=chat_id)

        start_inline(update, context)
    elif data_split[0] == "history" or state == "history":
        data = Order.objects.order_by('-id').filter(user_id=db_user.id)[:10]
        status = {
            0: {
                "uz": "Kutilmoqda",
                "ru": "Ожидающий",
            },
            1: {
                "uz": "Jarayonda",
                "ru": "Процесс",
            },
            2: {
                "uz": "Tayyor bo'ldi",
                "ru": "Готово",
            },
            3: {
                "uz": "Bekor qilindi",
                "ru": "Отменено",
            }
        }
        st = {
            "uz": "<b>Holati</b>",
            "ru": "<b>Статус</b>"
        }
        ordd = {
            1: {
                "uz": "<b>Buyurtma nomeri:</b>",
                "ru": "<b>Номер заказа:</b>"
            },
            2: {
                "uz": "<b>Umumiy narx {price} so'm</b>",
                "ru": "<b>Общая цена {price} сум</b>"
            },
        }
        if data:
            text = ""
            price = 0
            for i in data:
                text += f"{ordd[1][db_user.lang]} #N{i.id}\n"
                for j in i.carts.all():
                    text += f"<b>{j.category[db_user.lan]}\n   └ {j.sub_category[db_user.lan]}→</b> {j.count} x {j.sub_category.price} = {j.count * j.sub_category.price} {i18n('price_lang')[db_user.lan]}\n{st[db_user.lang]}: {status[i.status][db_user.lang]} \n\n"
                    price += j.count * j.sub_category.price
            text += ordd[2][db_user.lang].format(price=price)
            button = [[InlineKeyboardButton(
                text=i18n('back_btn')[db_user.lan], callback_data="start_to")]]
            context.bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                          text=text, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(button))

        else:
            context.bot.answer_callback_query(
                callback_query_id=query.id, text=i18n("no_order")[db_user.lan])
    elif data_split[0] == 'start':
        start_inline(update, context)
    elif data_split[0] == "cart":
        data = Cart.objects.filter(
            status=False, costumer_id=db_user.id).all()
        button = []
        if data:
            text = f""
            for i in data:
                button.append(
                    [
                        InlineKeyboardButton(
                            "-",
                            callback_data=f"cartupdate_-_{i.count}_{i.sub_category.id}_{i.sub_category[db_user.lan]}",
                        ),
                        InlineKeyboardButton(
                            f"{i.category[db_user.lan]} ({i.count})",
                            callback_data="vvv",
                        ),
                        InlineKeyboardButton(
                            "+",
                            callback_data=f"cartupdate_+_{i.count}_{i.sub_category.id}_{i.sub_category[db_user.lan]}",
                        ),
                    ]
                )
                text += f"<b>{i.category[db_user.lan]}\n   └ {i.sub_category[db_user.lan]}→</b> {i.count} x {i.sub_category.price} = {i.count * i.sub_category.price} {i18n('price_lang')[db_user.lan]}\n\n"
            button.append(
                [
                    InlineKeyboardButton(
                        i18n("confirm_order")[db_user.lan],
                        callback_data=f"confirm_order",
                    )
                ]
            )
            button.append(
                [
                    InlineKeyboardButton(
                        i18n("again_buy")[
                            db_user.lan], callback_data=f"again_append"
                    )
                ]
            )
            context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=InlineKeyboardMarkup(button),
                parse_mode="HTML",
            )
            context.user_data['cart'] = {}
        else:
            context.bot.answer_callback_query(
                callback_query_id=query.id,
                text=i18n("empty_cart")[db_user.lan],
                show_alert=True,
            )
    elif data_split[0] == "cartupdate":
        if data_split[1] == "-":
            if int(data_split[2]) > 1:
                count = int(data_split[2]) - 1
                context.bot.answer_callback_query(
                    callback_query_id=query.id,
                    text=f"{data_split[4]} {count}",
                    show_alert=False,
                )
                data = Cart.objects.filter(status=False, sub_category_id=int(data_split[3])).update(
                    count=count
                )
            else:
                Cart.objects.filter(
                    status=False, sub_category_id=int(data_split[3])).delete()
        if data_split[1] == "+":
            count = int(data_split[2]) + 1
            context.bot.answer_callback_query(
                callback_query_id=query.id,
                text=f"{data_split[4]} {count}",
                show_alert=False,
            )
            Cart.objects.filter(status=False, sub_category_id=int(
                data_split[3])).update(count=count)
        data = Cart.objects.filter(costumer_id=db_user.id, status=False).all()
        button = []
        if data:
            text = f""
            for i in data:
                button.append(
                    [
                        InlineKeyboardButton(
                            "-",
                            callback_data=f"cartupdate_-_{i.count}_{i.sub_category.id}_{i.sub_category[db_user.lan]}",
                        ),
                        InlineKeyboardButton(
                            f"{i.category[db_user.lan]} ({i.count})",
                            callback_data="vvv",
                        ),
                        InlineKeyboardButton(
                            "+",
                            callback_data=f"cartupdate_+_{i.count}_{i.sub_category.id}_{i.sub_category[db_user.lan]}",
                        ),
                    ]
                )
                text += f"<b>{i.category[db_user.lan]}\n   └ {i.sub_category[db_user.lan]}→</b> {i.count} x {i.sub_category.price} = {i.count * i.sub_category.price} {i18n('price_lang')[db_user.lan]}\n\n"
            button.append(
                [
                    InlineKeyboardButton(
                        i18n("confirm_order")[db_user.lan],
                        callback_data=f"confirm_order",
                    )
                ]
            )
            button.append(
                [
                    InlineKeyboardButton(
                        i18n("again_buy")[
                            db_user.lan], callback_data=f"again_append"
                    )
                ]
            )
            context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=InlineKeyboardMarkup(button),
                parse_mode="HTML",
            )
        else:
            context.bot.answer_callback_query(
                callback_query_id=query.id,
                text=i18n("empty_cart")[db_user.lan],
                show_alert=True,
            )
            start_inline(update, context)

    elif data_split[0] == "number":
        a = calculate(
            data_split[1], db_user.lan, int(data_split[2]), int(data_split[3])
        )
        context.bot.answer_callback_query(
            callback_query_id=query.id, text=data_split[1], show_alert=False
        )
        sub = SubCategory.objects.filter(pk=int(data_split[3])).first()
        text = ""
        text += f"<b>{sub[db_user.lan]}</b>\n    {data_split[1]} * {sub.price} = {int(data_split[1]) * int(sub.price)} {i18n('price_lang')[db_user.lan]}\n<b>-----</b>\n"
        text += sub.desc.replace("<p>", "").replace("</p>", "").replace("strong", "b").replace("<em>", "<i>").replace("</em>", "</i>").replace("<br/>", "\n").replace("&nbsp;", "")
        context.bot.edit_message_caption(
            chat_id=chat_id,
            message_id=message_id,
            caption=text,
            reply_markup=InlineKeyboardMarkup(a),parse_mode="HTML"
        )

    elif data_split[0] == "set":
        data = Cart.objects.filter(status=False,
                                   sub_category_id=int(data_split[2]), costumer_id=db_user.id
                                   )
        if data:
            Cart.objects.filter(status=False,
                                sub_category_id=int(data_split[2]), costumer_id=db_user.id
                                ).update(count=data.first().count + int(data_split[3]))
        else:
            Cart.objects.create(
                costumer_id=db_user.id,
                category_id=int(data_split[1]),
                sub_category_id=int(data_split[2]),
                count=int(data_split[3]),
            )
        context.bot.answer_callback_query(
            callback_query_id=query.id,
            text=i18n("done_cart")[db_user.lan],
            show_alert=True,
        )
        context.bot.delete_message(message_id=message_id, chat_id=chat_id)
        start_handler(update, context)

    elif data_split[0] == "again":
        start_inline(update, context)
    elif data_split[0] == "confirm":
        buttons = deliver_type_btn(db_user)
        context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=i18n("deliver_type")[db_user.lan],
            reply_markup=InlineKeyboardMarkup(buttons), parse_mode="HTML"
        )
    elif data_split[0] == "deliver":
        if data_split[1] == "back":
            data = Cart.objects.filter(
                costumer_id=db_user.id, status=False).all()
            button = []
            if data:
                text = f""
                for i in data:
                    button.append(
                        [
                            InlineKeyboardButton(
                                "-",
                                callback_data=f"cartupdate_-_{i.count}_{i.sub_category.id}_{i.sub_category[db_user.lan]}",
                            ),
                            InlineKeyboardButton(
                                f"{i.category[db_user.lan]} ({i.count})",
                                callback_data="vvv",
                            ),
                            InlineKeyboardButton(
                                "+",
                                callback_data=f"cartupdate_+_{i.count}_{i.sub_category.id}_{i.sub_category[db_user.lan]}",
                            ),
                        ]
                    )
                    text += f"<b>{i.category[db_user.lan]}\n   └ {i.sub_category[db_user.lan]}→</b> {i.count} x {i.sub_category.price} = {i.count * i.sub_category.price} {i18n('price_lang')[db_user.lan]}\n\n"
                button.append(
                    [
                        InlineKeyboardButton(
                            i18n("confirm_order")[db_user.lan],
                            callback_data=f"confirm_order",
                        )
                    ]
                )
                button.append(
                    [
                        InlineKeyboardButton(
                            i18n("again_buy")[
                                db_user.lan], callback_data=f"again_append"
                        )
                    ]
                )
                context.bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=message_id,
                    text=text,
                    reply_markup=InlineKeyboardMarkup(button),
                    parse_mode="HTML",
                )

        else:
            if data_split[1] != "car":
                loc_func(db_user,context,chat_id,message_id)
                context.user_data['cart'] = {"deliver_type": int(data_split[2])}
                context.user_data['state'] = "loc"
            else:
                costum_time(update,context,datetime.now().strftime("%H:%M").split(":")[0],"00",db_user)
        
    elif state == "test" and data_split[0] not in ["costum","leave"]:
        if data_split[0] == "+":
            count = int(data_split[1]) + 1
            a = calculate(count, db_user.lan, int(
                data_split[2]), int(data_split[3]))
            context.bot.answer_callback_query(
                callback_query_id=query.id, text=count, show_alert=False
            )
            sub = SubCategory.objects.filter(pk=int(data_split[3])).first()
            text = ""
            text += f"<b>{sub[db_user.lan]}</b>\n    {count} * {sub.price} = {int(count) * int(sub.price)} {i18n('price_lang')[db_user.lan]}\n<b>-----</b>\n"
            text += sub.desc.replace("<p>", "").replace("</p>", "").replace("strong", "b").replace("<em>", "<i>").replace("</em>", "</i>").replace("<br/>", "\n").replace("&nbsp;", "")
            context.bot.edit_message_caption(
                chat_id=chat_id,
                message_id=message_id,
                caption=text,
                reply_markup=InlineKeyboardMarkup(a),parse_mode="HTML"
            )
        elif data_split[0] == "-":
            if data_split[1] != "1":
                count = int(data_split[1]) - 1
                a = calculate(
                    count, db_user.lan, int(data_split[2]), int(data_split[3])
                )
                context.bot.answer_callback_query(
                    callback_query_id=query.id, text=count, show_alert=False
                )
                sub = SubCategory.objects.filter(pk=int(data_split[3])).first()
                text = ""
                text += f"<b>{sub[db_user.lan]}</b>\n    {count} * {sub.price} = {int(count) * int(sub.price)} {i18n('price_lang')[db_user.lan]}\n<b>-----</b>\n"
                text += sub.desc.replace("<p>", "").replace("</p>", "").replace("strong", "b").replace("<em>", "<i>").replace("</em>", "</i>").replace("<br/>", "\n").replace("&nbsp;", "")
                context.bot.edit_message_caption(
                    chat_id=chat_id,
                    message_id=message_id,
                    caption=text,
                    reply_markup=InlineKeyboardMarkup(a),parse_mode="HTML"
                )
            else:
                context.bot.answer_callback_query(
                    callback_query_id=query.id,
                    text=i18n("min_product")[db_user.lan],
                    show_alert=True,
                )
    elif data_split[0] == "name":
        context.bot.delete_message(chat_id=chat_id,message_id=message_id)
        buttons = [
                [
                    KeyboardButton(
                        text=i18n("back_btn")[db_user.lan]
                    )
                ]
            ]
        context.user_data['name_message'] = context.bot.send_message(chat_id=chat_id, text=i18n("your_name")[db_user.lan], parse_mode="HTML",reply_markup=ReplyKeyboardMarkup(buttons,resize_keyboard=True))
        context.user_data['state'] = 'name'
    elif data_split[0] == "phone":
        context.bot.delete_message(chat_id=chat_id,message_id=message_id)
        buttons = [
                [
                    KeyboardButton(
                        text=i18n("contact")[db_user.lan],
                        request_contact=True,
                    )
                ],
                [
                    KeyboardButton(
                        text=i18n("back_btn")[db_user.lan]
                    )
                ]
            ]
        context.user_data['contact_message'] = update.callback_query.message.reply_html(text=i18n("contact_text")[db_user.lan],reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))
        context.user_data["state"] = "phone"

    elif data_split[0] == "leave":
        buttonss = [[InlineKeyboardButton(i18n("delivery_comment")[db_user.lan],callback_data="com_delivery"),InlineKeyboardButton(i18n("foods_comment")[db_user.lan],callback_data="com_foods")],[InlineKeyboardButton(i18n("back_btn")[db_user.lan],callback_data="subcategory_back")]]
        context.bot.edit_message_text(chat_id=chat_id,message_id=message_id,text=i18n("comment_text")[db_user.lan],reply_markup=InlineKeyboardMarkup(buttonss))

    elif data_split[0] == "costum":
        if data_split[1] == "hour":
            if data_split[2] == "+":
                if int(data_split[3])< int(BotSettings.objects.first().deliver_time_to.strftime("%H:%M").split(":")[0]):
                    costum_time(update,context,int(data_split[3])+1,data_split[4],db_user)
                else:
                    context.bot.answer_callback_query(callback_query_id=query.id,text=i18n("out_time")[db_user.lan],show_alert=True)
            elif data_split[2] == "-":
                if int(data_split[3])> int(datetime.now().strftime("%H:%M").split(":")[0]):
                    costum_time(update,context,int(data_split[3])-1,data_split[4],db_user)
                else:
                    context.bot.answer_callback_query(callback_query_id=query.id,text=i18n("out_time")[db_user.lan],show_alert=True)

        elif data_split[1] == "minute":
            if data_split[2] == "+":
                if data_split[4] !="60":
                    costum_time(update,context,data_split[3],int(data_split[4])+10,db_user)
                else:
                    costum_time(update,context,data_split[3],"00",db_user)
            elif data_split[2] == "-":
                if int(data_split[4]) !=0:
                    costum_time(update,context,data_split[3],int(data_split[4])-10,db_user)
                else:
                    costum_time(update,context,data_split[3],"60",db_user)
        elif data_split[1] == "accept":
            loc_func(db_user,context,chat_id,message_id)
            context.user_data['cart'] = {"deliver_type":0}
            context.user_data['cart'].update(
                    {"time":f"{data_split[2]}:{data_split[3]}"})
            context.user_data['state'] = "loc"
        elif data_split[1] == "now":
            loc_func(db_user,context,chat_id,message_id)
            context.user_data['cart'] = {"deliver_type":0}
            context.user_data['cart'].update(
                    {"time":"Сейчас"})
            context.user_data['state'] = "loc"
    elif data_split[0] == "com":
        if data_split[1] == "delivery":
            context.user_data['state'] = "com_del"
        else:
            context.user_data['state'] = "com_food"
        context.bot.edit_message_text(chat_id=chat_id,message_id=message_id,text=i18n("commet_btn_text")[db_user.lan],reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(i18n("back_btn")[db_user.lan],callback_data="leave_comment")]]))
        

            

def contact_handler(update:Update, context):
    chat_id = update.message.from_user.id
    contact = update.message.contact.phone_number
    db_user = Costumers.objects.filter(chat_id=chat_id).first()
    state = context.user_data.get("state", 0)
    update.message.delete()
    if state in ('phone', 'code'):
        code = random.randint(123456, 987654)
        context.user_data['contact_message'].delete()
        Costumers.objects.filter(chat_id=chat_id).update(
            phone=contact, code=code)
        send_req(contact, message_id=update.message.message_id,
                 message=i18n("send_sms_text")[db_user.lan].format(code=code))
        check_user_state(update, context)


def location_handler(update: Update, context: CallbackContext):

    chat_id = update.message.from_user.id
    db_user = Costumers.objects.filter(chat_id=chat_id).first()
    state = context.user_data.get("state", 0)
    cart = context.user_data.get("cart", {})
    if state == "loc":
        longitude = update.message.location["longitude"]
        latitude = update.message.location["latitude"]
        address = loc_address(longitude, latitude)
        data = address.raw["address"]
        try:
            home = data['road']
        except:
            home = data['house_number']
        try:
            neighbourhood = data['neighbourhood']
        except:
            neighbourhood = ""
        try:
            city = data['city']
        except:
            city = ""
        try:
            county = data['county']
        except:
            county = ""
        text = f"{data['country']}, {city}, {county}, {neighbourhood}, {home}"
        all_address = Address.objects.filter(active=True).all()
        near_address = distace(
            your_distance=(
                latitude, longitude), all_loc=all_address, db_user=db_user
        )
        km = BotSettings.objects.all().first().deliver_km
        if cart['deliver_type'] == 1:
            context.user_data['cart'].update({"address": text})
            context.bot.send_message(
                chat_id=chat_id,
                text=i18n("your_address")[db_user.lan].format(
                    your_address=text, near_address=Address.objects.filter(
                        pk=near_address['address']).first()[db_user.lan]
                ), reply_markup=get_all_address(db_user.lan), parse_mode="HTML"
            )
            context.user_data['cart'].update(
                {"near": near_address['address'], "latitude": latitude, "longitude": longitude})
            context.user_data['state'] = 'loc'

        elif near_address['distance'] <= int(km):
            context.user_data['cart'].update({"address": text})
            if cart['deliver_type'] == 0:
                context.bot.send_message(
                    chat_id=chat_id,
                    text=i18n("your_address")[db_user.lan].format(
                        your_address=text, near_address=Address.objects.filter(
                            pk=near_address['address']).first()[db_user.lan]
                    ), reply_markup=get_near_address(db_user.lan), parse_mode="HTML"
                )
                context.user_data['cart'].update(
                    {"near": near_address['address'], "latitude": latitude, "longitude": longitude})
                context.user_data['state'] = 'loc'
        else:
            context.bot.send_message(chat_id=chat_id, text=i18n(
                'deliver_km')[db_user.lan].format(km=km))

    else:
        update.message.delete()


def register_group(update: Update, context: CallbackContext):
    group_id = update.message.chat.id
    if update.message.chat.type in ['supergroup', 'group']:
        context.bot.send_message(
            chat_id=group_id, text=f"<b>Группа ид:</b>  <code>{group_id}</code>", parse_mode="HTML")
    else:
        update.message.reply_text(
            "Kechirasiz bu komanda faqat guruhda ishlatish mumkin!")


def start_handler1(update, context):
    pass
    



def payme(update: Update, context: CallbackContext, price):
    settings_bot = BotSettings.objects.all().first()
    chat_id = update.callback_query.message.chat_id
    db_user = Costumers.objects.filter(chat_id=chat_id).first()
    title = i18n("pay_title")[db_user.lan]
    description = i18n("pay_desc")[db_user.lan]
    payload = "Custom-Payload"
    provider_token = settings_bot.payme
    print(provider_token,"provider_token")
    currency = "UZS"
    prices = [LabeledPrice("Buyutmalar\Заказы", price*100)]
    context.user_data['invoice']=context.bot.send_invoice(
        chat_id, title, description, payload, provider_token, currency, prices, need_name=True, need_phone_number=True
    )
    print("hello")


def click(update: Update, context: CallbackContext, price) -> None:
    settings_bot = BotSettings.objects.all().first()
    chat_id = update.callback_query.message.chat_id
    db_user = Costumers.objects.filter(chat_id=chat_id).first()
    title = i18n("pay_title")[db_user.lan]
    description = i18n("pay_desc")[db_user.lan]
    payload = "Custom-Payload"
    provider_token = settings_bot.click
    currency = "UZS"
    prices = [LabeledPrice("Buyutmalar\Заказы", price*100)]
    context.user_data['invoice'] = context.bot.send_invoice(
        chat_id, title, description, payload, provider_token, currency, prices, need_name=True, need_phone_number=True
    )
    print('Hi!')


def precheckout_callback(update: Update, context: CallbackContext):
    """Answers the PreQecheckoutQuery"""
    query = update.pre_checkout_query
    if query.invoice_payload != 'Custom-Payload':
        query.answer(ok=False, error_message="Xatolik yuz berdi. Qayta urunib ko'ring...Произошла ошибка. Пожалуйста, попробуйте еще раз")
    else:
        query.answer(ok=True)
    print("Bye")


def successful_payment_callback(update: Update, context: CallbackContext):
    chat_id = update.message.chat.id
    try:
        context.bot.delete_message(chat_id=chat_id,message_id=update.message.message_id-1)
    except:...
    db_user = Costumers.objects.filter(chat_id=chat_id).first()
    cart = context.user_data.get('cart')
    order_func(Cart, db_user, cart, Order, BotSettings.objects.all().first().group_id, context)
    context.bot.send_message(chat_id=db_user.chat_id, text=i18n("accept_order")[
        db_user.lan], parse_mode="HTML")
    print("Success")
    start_handler(update, context)


def support(update, context):
    chat_id = update.message.from_user.id
    db_user = Costumers.objects.filter(chat_id=chat_id).first()
    button = [[InlineKeyboardButton("aloqa", url="t.me/MHojimurod_1")]]
    update.message.reply_html(
        text=i18n("support")[db_user.lan], reply_markup=InlineKeyboardMarkup(button))


def settings(update, context):
    chat_id = update.message.from_user.id
    db_user = Costumers.objects.filter(chat_id=chat_id).first()
    settings_page(update,db_user)

def all_handler(update:Update, context:CallbackContext):
    state = context.user_data.get('state')
    if "com" in state:
        chat_id = update.message.from_user.id
        db_user = Costumers.objects.filter(chat_id=chat_id).first()
        video = update.message.video
        photo = update.message.photo
        audio = update.message.audio
        sticker = update.message.sticker
        document = update.message.document
        com_type = {
            "com_del":"Доставка",
            "com_food":"Еда"
        }
        if video:
            Comments.objects.create(costumer=db_user,file=context.bot.get_file(video['file_id'])['file_path'],com_type=com_type[state])
        elif photo:
            Comments.objects.create(costumer=db_user,file=context.bot.get_file(photo[0]['file_id'])["file_path"],com_type=com_type[state])
        if audio:
            Comments.objects.create(costumer=db_user,file=context.bot.get_file(audio['file_id'])['file_path'],com_type=com_type[state])
        if sticker:
            Comments.objects.create(costumer=db_user,file=context.bot.get_file(sticker['file_id'])["file_path"],com_type=com_type[state])
        if document:
            Comments.objects.create(costumer_id=db_user.id,file=context.bot.get_file(document['file_id'])["file_path"],com_type=com_type[state])
        context.bot.delete_message(chat_id=chat_id,message_id=update.message.message_id-1)
        context.bot.send_message(chat_id=chat_id,text=i18n("create_comment")[db_user.lan],reply_markup=ReplyKeyboardRemove())
        start_handler(update,context)

    else:
        update.message.delete()

def buy(update,context):
    start_handler(update,context)
class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        settings_bot = BotSettings.objects.all().first()
        updater = Updater(settings_bot.token)
        # updater = Updater("1955026889:AAFD98J6x8rW_0pftC4kktkTARDJALfrPGs")

        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler("start", start_handler))
        dispatcher.add_handler(CommandHandler("support", support))
        dispatcher.add_handler(CommandHandler("buy", buy))
        dispatcher.add_handler(CommandHandler("settings", settings))

        dispatcher.add_handler(CommandHandler("payme", payme))

        dispatcher.add_handler(CommandHandler("click", click))

        dispatcher.add_handler(CommandHandler(
            "register_group", register_group))

        dispatcher.add_handler(PreCheckoutQueryHandler(precheckout_callback))

        dispatcher.add_handler(MessageHandler(
            Filters.successful_payment, successful_payment_callback))

        dispatcher.add_handler(MessageHandler(Filters.text, message_handler))

        dispatcher.add_handler(CallbackQueryHandler(inline_handler))

        dispatcher.add_handler(MessageHandler(
            Filters.contact, contact_handler))

        dispatcher.add_handler(MessageHandler(
            Filters.location, location_handler))
        dispatcher.add_handler(MessageHandler(
            Filters.all, all_handler))

        updater.start_polling()

        def run_temp_server():
            app = Flask(__name__)

            @app.route('/send_ads', methods=['GET', 'POST'])
            def x():
                data = json.loads(request.data)
                error_users: list = []
                users: QuerySet[Costumers] = Costumers.objects.filter(
                    lang=data['data']['users']) if data['data']['users'] != "all" else Costumers.objects.all()
                if data['data']["file_type"] in [".jpg", ".jpeg", ".png"]:
                    times_photo = 0
                    if times_photo <= 25:
                        for user in users:
                            try:
                                updater.bot.send_photo(chat_id=user.chat_id, photo=open(
                                    data['data']['file'], 'rb'), caption=data['data']['message'], parse_mode="HTML")
                            except:
                                error_users.append(user.id)
                            times_photo += 1
                    else:
                        time.sleep(1)
                        times_photo = 0
                elif data['data']["file_type"] in [".mp4", ".mov", '.avi']:
                    times_video = 0
                    if times_video <= 25:
                        for user in users:
                            try:
                                updater.bot.send_video(chat_id=user.chat_id, video=open(
                                    data['data']['file'], 'rb'), caption=data['data']['message'], parse_mode="HTML")
                            except:
                                error_users.append(user.id)
                            times_video += 1
                    else:
                        time.sleep(1)
                        times_video = 0
                return {
                    "unsent_users": error_users
                }

            @app.route('/update_order', methods=['GET', 'POST'])
            def update_order():
                data = json.loads(request.data)['data']
                if data['action'] == "deny":
                    order = Order.objects.filter(id=data['order'])
                    if order.exists():
                        order: Order = order.first()
                        try:
                            updater.bot.send_message(chat_id=order.user.chat_id, text=i18n(
                                "deny_order")[order.user.lan].format(number=order.id), parse_mode="HTML")
                        except:
                            ...
                elif data['action'] == "confirm":
                    order = Order.objects.filter(id=data['order'])
                    if order.exists():
                        order: Order = order.first()
                        try:
                            updater.bot.send_message(chat_id=order.user.chat_id, text=i18n(
                                "confirm_order_text")[order.user.lan].format(number=order.id), parse_mode="HTML")
                        except:...
                elif data['action'] == "send":
                    updater.bot.send_message(chat_id=data['chat_id'], text=data['text'], parse_mode="HTML")
                return "True"
            app.run('127.0.0.1', 6002)

        threading.Thread(target=run_temp_server).start()
        print("Polling")
        updater.idle()
