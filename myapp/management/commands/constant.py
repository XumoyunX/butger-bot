from telegram import Update
from telegram.ext import CallbackContext
from myapp.models import BotSettings, Costumers, i18n
from datetime import datetime
def ttrt(func:callable) -> callable:
    def wrapper(update:Update, context:CallbackContext):
        settings:BotSettings = BotSettings.objects.first()
        start = settings.deliver_time_from
        end = settings.deliver_time_to
        now = datetime.time(datetime.now())
        func(update, context) if ((now >= start and now <= end) if start < end else (now >= start or now <= end)) else update.callback_query.answer(i18n("end_work")[Costumers.objects.filter(chat_id=update.callback_query.from_user.id).first().lan].format(from_time=start, to_time=end),show_alert=True)
    return wrapper
