
start_text = "Salom alkeum  tilni tanlang"


your_name = {
    "name_uz":"Izmingizni kiritng:",
    "name_ru":"Enter your name:",
    }

menu = {
    "name_uz":"Menu",
    "name_ru":"Menu1",
    }

contact = {
    "name_uz":"Telefon",
    "name_ru": "Contact1"
}

contact_text = {
    "name_uz":"raqamni kiriting",
    "name_ru":"raqamni kiriting1",
}


v_code = {
    "name_uz":"tasdiqlash kodini kiriting",
    "name_ru":"tasdiqlash kodini kiritng1"
}

error_code = {
    "name_uz":"kod xato tekshirib qayta urinib ko'ring kod kelmagan bolsa qayta yuboring",
    "name_ru":"kod xato tekshirib qayta urinib ko'ring kod kelmagan bolsa qayta yuboring1",
}

resend_code = {
    "name_uz":"qayta yuborish",
    "name_ru":"qayta yuborish1",
}

history = {
    "name_uz":"Buyurtmalar tarixi",
    "name_ru":"Buyurtmalar tarixi1",
}

go_cart = {
    "name_uz":"Savatchaga o'tish",
    "name_ru":"Savatchaga o'tish1",
}
set_cart = {
    "name_uz":"Savatchaga joylash",
    "name_ru":"Savatchaga joylash1",
}
done_cart = {
    "name_uz":"Savatchaga joylandi",
    "name_ru":"Savatchaga joylandi",
}
empty_cart = {
    "name_uz":"Savatcha bo'sh",
    "name_ru":"Savatcha bo'sh",
}

change_lang = {
    "name_uz":"Tilni o'zgartirish",
    "name_ru":"Tilni o'zgartirish1",
}

back_btn = {
    "name_uz":"Ortga",
    "name_ru":"Ortga1",
}

min_product = {
    "name_uz":"Kechirasiz maksimum 1 ta mahsulot tanlashingiz kerak",
    "name_ru":"Kechirasiz maksimum 1 ta mahsulot tanlashingiz kerak",
}

price_lang = {
    "name_uz":"so‘m",
    "name_ru":"сум",
}
confirm_order = {
    "name_uz":"Buyurtmani Tasdiqlash",
    "name_ru":"Buyurtmani Tasdiqlash",
}
again_buy = {
    "name_uz":"Yana buyurtma berish",
    "name_ru":"Yana buyurtma berish",
}
deliver_type = {
    "name_uz":"Yetkazib berish usulini tanlang",
    "name_ru":"Yetkazib berish usulini tanlang",
}
on_car = {
    "name_uz":"Yetkazib berish",
    "name_ru":"Yetkazib berish",
}
on_foot = {
    "name_uz":"Olib ketish",
    "name_ru":"Olib ketish",
}
send_location_btn = {
    "name_uz":"📍 Geolokatsiyani jo‘natish",
    "name_ru":"📍 Geolokatsiyani jo‘natish",
}
send_location = {
    "name_uz":"Iltimos, “📍 Geolokatsiyani jo‘natish” tugmasini bosish orqali geolokatsiyangizni yuboring. Bunda telefoningizda manzilni aniqlash funksiyasi yoqilgan bo‘lishi lozim.",
    
    "name_ru":"Iltimos, “📍 Geolokatsiyani jo‘natish” tugmasini bosish orqali geolokatsiyangizni yuboring. Bunda telefoningizda manzilni aniqlash funksiyasi yoqilgan bo‘lishi lozim.",
}

def your_addresss(lang,y_a,n_a):
    address = {
        "name_uz":f"Sizning manzilingiz: {y_a}\n\nJoylashuvni noto'g'rimi?\nQayta jo'nating📍\n\nEng yaqin filial: {n_a}",
        "name_ru":f"Sizning manzilingiz: {y_a}\n\nJoylashuvni noto'g'rimi?\nQayta jo'nating📍\n\nEng yaqin filial: {n_a}"
    }
    return address[lang]