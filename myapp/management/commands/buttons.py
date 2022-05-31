import json
import requests
from myapp.models import Address, Category, SubCategory, i18n
from .globals import *
from telegram import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,

)

from geopy.geocoders import Nominatim
import geopy.distance
lang = [
    [
        InlineKeyboardButton(text="uz", callback_data="uz"),
        InlineKeyboardButton(text="ru", callback_data="ru"),
    ]
]


geolocator = Nominatim(user_agent="google")


def extra_buttons(lang):
    buttons = [
        InlineKeyboardButton(i18n('history')[lang], callback_data="history"),
        InlineKeyboardButton(i18n("go_cart")[lang], callback_data="cart"),
    ]
    return buttons


def is_odd(a):
    return bool(a - ((a >> 1) << 1))


def distribute(items, number) -> list:
    res = []
    start = 0
    end = number
    for item in items:
        if items[start:end] == []:
            return res
        res.append(items[start:end])
        start += number
        end += number
    return res


def get_category(lang: str, category: Category = None):
    category = Category.objects.filter(active=True, parent=category)
    keyboards = []
    for cat in category:
        keyboards.append(InlineKeyboardButton(
            cat[lang], callback_data=f"category_{cat.id}"))
    keyboard = distribute(keyboards, 2)

    return keyboard


def get_subcategory(lang, category):
    subcategory = SubCategory.objects.filter(categroy_id=category, active=True)
    keyboards = []
    for i in range(len(subcategory)):
        keyboards.append(
            InlineKeyboardButton(
                subcategory[i][lang],
                callback_data=f"subcategory_{subcategory[i].id}_{category}",
            )
        )
    keyboards.append(
        InlineKeyboardButton(
            i18n('back_btn')[
                lang], callback_data=f"subcategory_back_{category}"
        )
    )
    return InlineKeyboardMarkup(distribute(keyboards, 2))


def calculate(count, lang, category_id, subcategory_id):
    buttons = [
        [
            InlineKeyboardButton(
                "-", callback_data=f"-_{count}_{category_id}_{subcategory_id}"
            ),
            InlineKeyboardButton(count, callback_data="count"),
            InlineKeyboardButton(
                "+", callback_data=f"+_{count}_{category_id}_{subcategory_id}"
            ),
        ],
        [
            InlineKeyboardButton(
                i, callback_data=f"number_{i}_{category_id}_{subcategory_id}"
            )
            for i in range(1, 4)
        ],
        [
            InlineKeyboardButton(
                i, callback_data=f"number_{i}_{category_id}_{subcategory_id}"
            )
            for i in range(4, 7)
        ],
        [
            InlineKeyboardButton(
                i, callback_data=f"number_{i}_{category_id}_{subcategory_id}"
            )
            for i in range(7, 10)
        ],
        [
            InlineKeyboardButton(
                i18n('set_cart')[lang],
                callback_data=f"set_{category_id}_{subcategory_id}_{count}",
            )
        ],
        [
            InlineKeyboardButton(
                i18n('back_btn')[lang],
                callback_data=f"change_back_{category_id}_{subcategory_id}",
            )
        ],
    ]
    return buttons


def deliver_type_btn(db_user):
    buttons = [
        [
            InlineKeyboardButton(
                i18n("on_car")[db_user.lan], callback_data="deliver_car_0"),
            InlineKeyboardButton(
                i18n("on_foot")[db_user.lan], callback_data="deliver_foot_1"),
        ],
        [InlineKeyboardButton(i18n("back_btn")[db_user.lan],
                              callback_data="deliver_back_cart")],
    ]

    return buttons


def loc_address(longitude, latitude):
    location = geolocator.reverse(f"{latitude}, {longitude}")
    return location


def distace(your_distance, all_loc, db_user):
    data = [
        {
            "distance": geopy.distance.distance(
                your_distance, (float(i.latitude), float(i.longitude))
            ).km,
            "address": i.id,
        }
        for i in all_loc
    ]
    for j in data:
        if j['distance'] == min([i['distance'] for i in data]):
            return j


def get_all_address(lang):
    address = Address.objects.all()
    keyboards = []
    keyboards.append(KeyboardButton(i18n("near_fillial")[lang]))
    keyboards.append(KeyboardButton(
        i18n("resend_loc")[lang], request_location=True))
    for i in range(len(address)):
        keyboards.append(
            KeyboardButton(
                address[i][lang]
            )
        )

    keyboards.append(
        KeyboardButton(
            i18n('back_btn')[lang]
        )
    )
    return ReplyKeyboardMarkup(distribute(keyboards, 2), resize_keyboard=True)


def get_near_address(lang):
    keyboards = []
    keyboards.append(KeyboardButton(i18n("accept")[lang]))
    keyboards.append(KeyboardButton(
        i18n("resend_loc")[lang], request_location=True))
    keyboards.append(
        KeyboardButton(
            i18n('back_btn')[lang]
        )
    )
    return ReplyKeyboardMarkup(distribute(keyboards, 1), resize_keyboard=True)


def order_func(Cart, db_user, cart, Order, group_id, context):
    all_carts = Cart.objects.filter(
        status=False, costumer=db_user).all()
    address = Address.objects.filter(pk=cart['near']).first()
    data: Order = Order.objects.create(
        user_id=db_user.id, address=address, order_type=cart['deliver_type'], latitude=cart['latitude'], longitude=cart['longitude'], comment=cart['msg'],deliver_time=cart['time'],cost_type=cart['cost_type'])
    for i in all_carts:
        data.carts.add(i)
        Cart.objects.filter(pk=i.id).update(status=True)
    order: Order = data
    address_link = f"https://maps.google.com/maps?q={order.latitude},{order.longitude}&ll={order.latitude},{order.longitude}&z=16"
    data = order.carts.all()
    text = ""
    price = 0
    o_time = order.created_at.strftime("%d-%m-%Y %H:%M")
    for j in data:
        text += f"\n<b>-</b> {j.sub_category.name_ru} x {j.count} от {int(j.sub_category.price) * int(j.count)} сум"
        price += int(j.sub_category.price) * int(j.count)
    if order.order_type == 0:
        d_type = "Доставлять"
        Text = f"<b>№ Заказы:</b> #N{order.id}\n<b>Филиал:</b> {order.address.name_ru}\n<b>Состав заказа:</b> {text}\n<b>Клиент:</b> {data.first().costumer.name}\n<b>Тип доставки:</b> {d_type}\n<b>Время доставки:</b> {cart['time']}\n<b>Комментарий</b> {cart['msg'] if cart['msg'] else 'Нет'}\n<b>Способ оплаты:</b>{cart['cost_type']}\n<b>Адрес доставки:</b> <a href='{address_link}'>{cart['address']}</a>\n<b>Время заказа:</b> {o_time}\n<b>Итого:</b> {price+8000} сум"
    else:
        d_type = "Забрать"
        Text = f"<b>№ Заказы:</b> #N{order.id}\n<b>Филиал:</b> {order.address.name_ru}\n<b>Состав заказа:</b> {text}\n<b>Клиент:</b> {data.first().costumer.name}\n<b>Тип доставки:</b> {d_type}\n<b>Комментарий</b> {cart['msg'] if cart['msg'] else 'Нет'}\n<b>Адрес доставки:</b> <a href='{address_link}'>{cart['address']}</a>\n<b>Время заказа:</b> {o_time}\n<b>Итого:</b> {price} сум"

    try:
        context.bot.send_message(
            chat_id=int(group_id), text=Text, parse_mode="HTML")
    except Exception as e:
        print(e)



def send_req(phone, message_id, message):
    data = {
        "messages":
        [
            {
                "recipient": phone.replace("+", ""),
                "message-id": f"abc{message_id}",
                "sms": {

                    "originator": "3700",
                    "content": {
                        "text": message
                    }
                },
            }
        ]}

    res = requests.post("http://91.204.239.44/broker-api/send", data=json.dumps(data), headers={
        "Content-Type": "application/json",
        "Authorization": "Basic Y2VudHJhbGRvbmVyOjU2ZlZtUEpiNTQ=",
    })


def pay_method(Cart, db_user, cart, update, context, chat_id):
    data = Cart.objects.filter(
        status=False, costumer_id=db_user.id).all()
    button = []
    if data:
        text = f""
        total = 0
        check_type = ""
        if cart['deliver_type'] == 0:
            check_type = i18n("on_car")[db_user.lan]
        else:
            check_type = i18n("on_foot")[db_user.lan]
        for i in data:
            text += f"<b>{i.category[db_user.lan]}\n   └ {i.sub_category[db_user.lan]}→</b> {i.count} x {i.sub_category.price} = {i.count * i.sub_category.price} {i18n('price_lang')[db_user.lan]}\n\n"
            total += i.count * i.sub_category.price
        button.append(
            [
                InlineKeyboardButton(
                    i18n("cash")[db_user.lan],
                    callback_data=f"cost_cash_1",
                )
            ]
        )
        button.append(
            [
                InlineKeyboardButton(
                    i18n("payme")[
                        db_user.lan], callback_data=f"cost_payme_2"
                ),
                InlineKeyboardButton(
                    i18n("click")[
                        db_user.lan], callback_data=f"cost_click_3"
                )
            ]
        )
        button.append(
            [
                InlineKeyboardButton(
                    i18n("resend_loc")[
                        db_user.lan], callback_data=f"cost_loc"
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
        text += i18n("check_order")[db_user.lan].format(total=total+8000, deliver_type=check_type,
                                                        address=cart['address'], near_address=Address.objects.filter(pk=cart['near']).first()[db_user.lan])
        context.bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=InlineKeyboardMarkup(button),
            parse_mode="HTML",
        )


def settings_page(update, db_user):
    name = {
        "uz": "<b>👤 Ism:</b>",
        "ru": "<b>👤 Имя:</b>",
    }
    phone = {
        "uz": "<b>📞 Telefon:</b>",
        "ru": "<b>📞 Телефон:</b>",
    }
    language = {
        "uz": "<b>🇺🇿 Til:</b>",
        "ru": "<b>🇷🇺 Язык:</b>",
    }
    text = f"{name[db_user.lang]} {db_user.name}\n\n{phone[db_user.lang]} {db_user.phone}\n\n{language[db_user.lang]} {db_user.lang}"
    button = [
        [InlineKeyboardButton(name[db_user.lang].replace("<b>", "").replace(
            "</b>", "").replace(":", ""), callback_data="name")],
        [InlineKeyboardButton(phone[db_user.lang].replace("<b>", "").replace(
            "</b>", "").replace(":", ""), callback_data="phone")],
        [InlineKeyboardButton(language[db_user.lang].replace("<b>", "").replace(
            "</b>", "").replace(":", ""), callback_data="change_lang")]
    ]
    update.message.reply_html(
        text=text, reply_markup=InlineKeyboardMarkup(button))


def format_time(time):
    if int(time) < 10:
        return f"0{int(time)}"
    return time
from datetime import datetime

def costum_time(update, context, deliver_from, deliver_to, db_user):
    buttns = [
        [InlineKeyboardButton("+", callback_data=f"costum_hour_+_{deliver_from}_{deliver_to}"), InlineKeyboardButton(
            "+", callback_data=f"costum_minute_+_{deliver_from}_{deliver_to}")],
        [InlineKeyboardButton(format_time(deliver_from), callback_data=f"costum_{deliver_from}"),
            InlineKeyboardButton(format_time(deliver_to), callback_data=f"costum_{deliver_to}")],
        [InlineKeyboardButton("-", callback_data=f"costum_hour_-_{deliver_from}_{deliver_to}"), InlineKeyboardButton(
            "-", callback_data=f"costum_minute_-_{deliver_from}_{deliver_to}")],
        [InlineKeyboardButton(i18n("now_btn")[db_user.lan],callback_data="costum_now")],
        [InlineKeyboardButton(i18n("accept")[
                              db_user.lan], callback_data=f"costum_accept_{deliver_from}_{deliver_to}"),
        InlineKeyboardButton(i18n("back_btn")[db_user.lan],
                              callback_data="confirm_back")]
    ]
    try:
        update.message.reply_text(text=i18n("costum_time_text")[
                                  db_user.lan], reply_markup=InlineKeyboardMarkup(buttns))
    except:
        update.callback_query.edit_message_text(text=i18n("costum_time_text")[db_user.lan], reply_markup=InlineKeyboardMarkup(buttns)
                                                )


def loc_func(db_user, context, chat_id, message_id):
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
    context.bot.send_message(
        chat_id=chat_id,
        text=i18n("send_location")[db_user.lan],
        reply_markup=ReplyKeyboardMarkup(loc, resize_keyboard=True), parse_mode="HTML"
    )
    context.bot.delete_message(chat_id=chat_id, message_id=message_id)
