import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.message import ContentType
import markups_new as nav
from db import Database
from wg_get_profile import Wg_Profile
import time
import datetime

now_time = int(time.time())


TOKEN = "5572128662:AAGDkW_bQ3tg7UmXOcH9XATfi4HsIM5IMGg"
YOOTOKEN = "381764678:TEST:47011"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

db = Database('database.db')


def days_to_seconds(days):
    return days * 24 * 60 * 60


# Получение времени подписки
def time_sub_day(get_time):
    time_now = int(time.time())
    middle_time = int(get_time) - time_now
    if middle_time <= 0:
        return False
    else:
        dt = str(datetime.timedelta(seconds=middle_time))
        dt = dt.replace("days", "дней")
        dt = dt.replace("day", "день")
        return dt


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.reply("Добро пожаловать в безопасный мир!", reply_markup=types.ReplyKeyboardRemove())
    if (not db.user_exists(message.from_user.id)):
        db.add_user(message.from_user.id)
        await bot.send_message(message.from_user.id, "Вы под нашей защитой!",
                               reply_markup=nav.mainMenu)

    else:
        await bot.send_message(message.from_user.id, "Вы под нашей защитой!", reply_markup=nav.mainMenu)



# ------------ Главное меню ---------


@dp.callback_query_handler(lambda call: call.data == 'Profile')
async def vote_callback(call: types.CallbackQuery):
    #await bot.delete_message(call.from_user.id, call.message.message_id)
    if db.get_wg_profile_status(call.from_user.id) > 0:
        user_id_str = str(call.from_user.id)
        await bot.send_message(call.from_user.id, "Ваш профиль VPN")
        await bot.send_document(call.from_user.id, open(user_id_str + ".conf", 'rb'))
    else:
        await bot.send_message(call.from_user.id, "Чтобы выпустить профиль VPN, оформте подписку")

    user_sub = time_sub_day(db.get_time_sub(call.from_user.id))
    end_sub = str(user_sub)
    end_sub = end_sub[:-10]
    if user_sub == False:
        end_sub = "У вас нет подписки"
    end_sub = "\nПодписка истекает через: " + end_sub
    await bot.send_message(call.from_user.id, "Ваш профиль:" + "\nВаш ID: " + str(call.from_user.id) + end_sub,
                           reply_markup=nav.backBtn)


#-----------------------------------Main_menu-----------------------------------
@dp.callback_query_handler(lambda call: call.data == 'BuySub')
async def vote_callback(call: types.CallbackQuery):
    #await bot.delete_message(call.from_user.id, call.message.message_id)
    await call.message.answer("Выберите период", reply_markup=nav.subMenu)
    await call.answer("Оплата в данный момент не работает. \nУ всех бесплатный доступ к нашему VPN...", show_alert=True)


@dp.callback_query_handler(lambda call: call.data == 'Trial')
async def vote_callback(callSub: types.CallbackQuery):
    #await bot.delete_message(callSub.from_user.id, callSub.message.message_id)
    await callSub.message.answer("Здесь мы можете оформить бесплатную подписку на 70 дней", reply_markup=nav.trialMenu)


@dp.callback_query_handler(lambda call: call.data == 'Help')
async def vote_callback(callSub: types.CallbackQuery):
    #await bot.delete_message(callSub.from_user.id, callSub.message.message_id)
    await callSub.message.answer("@connect_vpn_support", reply_markup=nav.backBtn)
    bot.send_contact('@connect_vpn_support', 'Имя', 'Фамилия')


@dp.callback_query_handler(lambda call: call.data == 'Info')
async def vote_callback(callSub: types.CallbackQuery):
    #await bot.delete_message(callSub.from_user.id, callSub.message.message_id)
    await callSub.message.answer("Тут будет какая-то инфа", reply_markup=nav.backBtn)
#---------------------------------------------------------------------------------------------------------

# --------- Кнопка вернуться в главное меню -------

@dp.callback_query_handler(lambda call: call.data == 'main_menu')
async def vote_callback(call: types.CallbackQuery):
    #await bot.delete_message(call.from_user.id, call.message.message_id)
    await call.message.answer("Главное меню", reply_markup=nav.mainMenu)


# ---------- Кнопки меню пробная подписка --------
@dp.callback_query_handler(lambda call: call.data == 'SubTrial')
async def vote_callback(call: types.CallbackQuery):
    #await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(call.from_user.id, "Проверка...")
    #if db.get_promo_sub(call.from_user.id) == 0:
        #if db.get_wg_profile_status(call.from_user.id) == 0:
    await bot.send_message(call.from_user.id, "Ожидайте выдачу профиля...")
    await call.answer("Ожидайте выдачу профиля...", show_alert=True)
    Wg_Profile.get_profile(call.from_user.id, TOKEN)
    plus_time = days_to_seconds(70) + int(time.time())
    db.set_time_sub(call.from_user.id, plus_time)
    db.set_promo_sub(call.from_user.id, 1)
    user_id_str = str(call.from_user.id)
    await bot.send_document(call.from_user.id, open(user_id_str + ".conf", 'rb'))
    db.set_wg_profile_status(call.from_user.id, 1, )
    await bot.send_message(call.from_user.id, "Поздравляем! Вы получили бесплатную подписку на 70 дней.")
    await bot.send_message(call.from_user.id,
                           'Инструкция по установке - https://telegra.ph/Instrukciya-kak-polzovatsya-VPN-12-16-2')
    await call.message.answer("Вы оформили бесплатную подписку", reply_markup=nav.backBtn)
    await call.answer("Вы оформили бесплатную подписку на" + str(70) + " дней", show_alert=True)
    await call.answer("Ваша подписка будет активируется в течении 15 минут", show_alert=True)

#else:
#await bot.send_message(call.from_user.id,
                       #"Вы уже активировали пробную подписку или у вас была куплена подписка!",
                       #reply_markup=nav.backBtn)


# -----------------------------------------------List sub----------------------------------------------------------------

@dp.callback_query_handler(lambda call: call.data == '1_month')
async def vote_callback(call: types.CallbackQuery):
    db.set_day(call.from_user.id, 31)
    #await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_invoice(chat_id=call.from_user.id, title="Оформление подписки",
                           description="Подписка на VPN 1 месяц", payload="month_sub", provider_token=YOOTOKEN,
                           currency="RUB", start_parameter="VPN", prices=[{"label": "Руб", "amount": 19000}])
    await bot.send_message(call.from_user.id, "Вам выставлен счет на " + str(190) + " рублей", reply_markup=nav.backBtn)


@dp.callback_query_handler(lambda call: call.data == '2_month')
async def vote_callback(call: types.CallbackQuery):
    db.set_day(call.from_user.id, 61)
    #await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_invoice(chat_id=call.from_user.id, title="Оформление подписки",
                           description="Подписка на VPN 2 месяца", payload="month_sub", provider_token=YOOTOKEN,
                           currency="RUB", start_parameter="VPN", prices=[{"label": "Руб", "amount": 38000}])
    await bot.send_message(call.from_user.id, "Вам выставлен счет на "+ str(380) +" рублей", reply_markup=nav.backBtn)


@dp.callback_query_handler(lambda call: call.data == '3_month')
async def vote_callback(call: types.CallbackQuery):
    db.set_day(call.from_user.id, 92)
    #await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_invoice(chat_id=call.from_user.id, title="Оформление подписки",
                           description="Подписка на VPN 3 месяца", payload="month_sub", provider_token=YOOTOKEN,
                           currency="RUB", start_parameter="VPN", prices=[{"label": "Руб", "amount": 49000}])
    await bot.send_message(call.from_user.id, "Вам выставлен счет на " + str(490) + " рублей", reply_markup=nav.backBtn)


@dp.callback_query_handler(lambda call: call.data == '6_month')
async def vote_callback(call: types.CallbackQuery):
    db.set_day(call.from_user.id, 180)
    #await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_invoice(chat_id=call.from_user.id, title="Оформление подписки",
                           description="Подписка на VPN 6 месяцев", payload="month_sub", provider_token=YOOTOKEN,
                           currency="RUB", start_parameter="VPN", prices=[{"label": "Руб", "amount": 89000}])
    await bot.send_message(call.from_user.id, "Вам выставлен счет на " + str(890) + " рублей", reply_markup=nav.backBtn)


# ---------------------------------------------------------------------------------------------------------------


#-----------------------------------Payment-----------------------------------
@dp.pre_checkout_query_handler()
async def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_pay(message: types.Message):
    if message.successful_payment.invoice_payload == "month_sub":
        await bot.send_message('938346742', "Купили подписочку )))")
        if db.get_sub_status(message.from_user.id) == True:
            day_sub = int(db.get_day_pay(message.from_user.id))
            plus_time = int(db.get_time_sub(message.from_user.id)) + days_to_seconds(day_sub)
            db.set_time_sub(message.from_user.id, plus_time)
            # await bot.send_message(message.from_user.id, "Вам продлена подписка на" + day_sub + " дней !")
            db.set_promo_sub(message.from_user.id, 1)
            db.set_wg_profile_status(message.from_user.id, 1)
            str_day_sub = str(day_sub)
            await bot.send_message(message.from_user.id, "Вам выдана подписка на " + str_day_sub + " дней",
                                   reply_markup=nav.mainMenu)

        if db.get_wg_profile_status(message.from_user.id) == 0:
            Wg_Profile.get_profile(message.from_user.id, TOKEN)
            day_sub = int(db.get_day_pay(message.from_user.id))
            time_sub = int(time.time()) + days_to_seconds(day_sub)
            db.set_time_sub(message.from_user.id, time_sub)
            # await bot.send_message(message.from_user.id, "Вам выдана подписка на " + day_sub + " дней")
            await bot.send_message(message.from_user.id,
                                   'Инструкция по установке - https://telegra.ph/Instrukciya-kak-polzovatsya-VPN-12-16-2')
            await bot.send_message(message.from_user.id, "Ожидайте выдачу профиля...")
            user_id_str = str(message.from_user.id)
            await bot.send_document(message.from_user.id, open(user_id_str + ".conf", 'rb'))
            db.set_promo_sub(message.from_user.id, 1)
            db.set_wg_profile_status(message.from_user.id, 1)
            str_day_sub = str(day_sub)
            await bot.send_message(message.from_user.id, "Вы оформили подписка на " + str_day_sub + " дней",
                                   reply_markup=nav.mainMenu)

        if db.get_wg_profile_status(message.from_user.id) == 1:
            if db.get_sub_status(message.from_user.id) != True:
                day_sub = int(db.get_day_pay(message.from_user.id))
                time_sub = int(time.time()) + days_to_seconds(day_sub)
                db.set_time_sub(message.from_user.id, time_sub)
                str_day_sub = str(day_sub)
                await bot.send_message(message.from_user.id,
                                       'Инструкция по установке - https://telegra.ph/Instrukciya-kak-polzovatsya-VPN-12-16-2')
                await bot.send_message("Вы оформили подписку" + str_day_sub + "дней", reply_markup=nav.mainMenu)


#---------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
