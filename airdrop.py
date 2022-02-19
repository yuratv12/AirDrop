import random
import smtplib
import email.message
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import pandas as pd
import logging
import config, database, menu
from datetime import datetime, timedelta

#Инициализация бота
bot = Bot(config.token)
dp = Dispatcher(bot, storage=MemoryStorage())
#Вывод логирования
logging.basicConfig(level=logging.INFO)

class User_wallet_state(StatesGroup):
    #Класс который отвечает за развернутые ответы на
    # вопросы, в которых нельзя ответить кнопками
    user_wallet = State()

class Admin_sender(StatesGroup):
    #Класс который отвечает за развернутые ответы на
    # вопросы, в которых нельзя ответить кнопками
    text_send = State()


@dp.message_handler(commands="start")
async def start_command(message: types.Message):
    #Обработчик команды "старт"
    #получаем информацию о пользователе
    user_id = message.from_user.id
    user_nickname = message.from_user.username
    message_data = message.text
    refer = str(message_data[6:]).strip()
    if refer:
        if str(refer) != str(user_id):
            if not database.old_refer(user_id, refer):
                database.add_coin_to_balance(refer, '0.025')
                database.add_refer(user_id, refer)
                database.update_count_refer(refer)
                await bot.send_message(refer, '👥 Присоединился новый друг!')

    if not database.old_user(user_id):
        message_text = """* 👋 Добро пожаловать, регистрация прошла успешно.
🍀 Участвуйте в розыгрыше коллекции NFT «Cozy Monkey World», соберы все 4 банана и получи одну nft из коллекции!

❕ Пожалуйста, пришлите свой кошелек Metamask или TrustWallet (BEP-20)*!
    """
        database.insert_new_user(user_id, user_nickname, str(datetime.now().date()))
        await User_wallet_state.user_wallet.set()
    else:
        message_text = '💩 У тебя есть крутая клавиатура, нажимай на кнопочки, не пиши ручками!'

    await message.answer(message_text, parse_mode='Markdown')

@dp.message_handler(commands="chatid")
async def get_chat_id(message: types.Message):
    chat_id = message.chat.id
    await message.answer(chat_id)


@dp.message_handler(state=User_wallet_state.user_wallet)
async def get_user_wallet_data(message: types.Message, state: FSMContext):
    #Получаем айди пользователя и текст сообщения
    user_id = message.chat.id
    wallet = message.text
    if '0x' in str(wallet):
        database.add_user_wallet(user_id, wallet)
        await state.finish()
        message_text = """*💾 Кошелек успешно установлен! *
{0}

1⃣ Вам необходимо подписаться на наш канал!
👉 [Перейти к каналу](https://t.me/nft_monkey_price)

*После подписки нажмите на кнопку «Далее»!*""".format(wallet)
        await message.answer(message_text, parse_mode='Markdown', reply_markup=menu.next_button)
    else:
        message_text = '<b>Пожалуйста, пришлите кошелек в сети BEP-20</b>\n\
Пример: 0x0A0A00BC01AA0123456B65555AB01A0EC012A01A\n\
*используйте Metamask или TrustWallet'
        await message.answer(message_text, parse_mode='html')
        await User_wallet_state.user_wallet.set()


@dp.message_handler(lambda message: message.text == "Далее")
async def check_user_in_chat(message: types.Message):
    user_id = message.chat.id
    result = await bot.get_chat_member('@nft_monkey_price', user_id)
    print(result.status)
    if str(result.status) != 'left':
        message_text = """🐵 Получить бесплатно nft можно нажав на кнопку "Бонус"
💎 Отлично! 

Используйте клавиатуру для навигации по боту.
"""
        database.add_coin_to_balance(user_id, '0.02')
        await message.answer(message_text, parse_mode='Markdown', reply_markup=menu.home_menu)
    else:
        message_text = """❌ Похоже, Вы не подписались на канал.

👉 [Перейти к каналу](https://t.me/nft_monkey_price)

После подписки нажмите на кнопку «Далее»!
"""
        await message.answer(message_text, parse_mode='Markdown')


@dp.message_handler(lambda message: message.text == "👥 Рефералы")
async def get_refer_data(message: types.Message):
    user_id = message.chat.id
    count_refer = database.get_count_refer_by_user(user_id)
    message_text = """💪 Вы пригласили <b>{0}</b> друзей 

🍀 <b>Гарантированные NFT:
💓 30 друзей = 1 Monkey NFT</b> (~30$)
💓 <b>100 друзей = 1 Uncommon Monkey NFT</b> (~150$)

<b>Ваша индивидуальная пригласительная ссылка:</b>
https://t.me/monkeynft_bot?start={1}<code>
https://t.me/monkeynft_bot?start={1}
</code>
*нажмите, чтобы скопировать

<b>💎 За каждых 10 приглашенных друзей +1 nft. Вывод NFT в течение 24 часа</b>
""".format(count_refer, user_id)
    await message.answer(message_text, parse_mode='html')


@dp.message_handler(lambda message: message.text == "🎁 Бонус")
async def add_gift_user(message: types.Message):
    user_id = message.chat.id
    date_now = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")
    last_user_gift = database.get_last_gift(user_id)
    diff = datetime.strptime(date_now, "%Y-%m-%d %H:%M:%S") - datetime.strptime(last_user_gift, "%Y-%m-%d %H:%M:%S")
    diff_hours = int(diff.total_seconds() / 3600)
    user_balance = database.get_user_balance(user_id)
    print(diff_hours)

    count_ref = database.get_count_refer_by_user(user_id)
    get_nft_hist = database.get_nft_hist(user_id)
    print(count_ref)
    print(count_ref % 10)
    if count_ref > 0 and int(count_ref) % 10 == 0 and get_nft_hist > 0 and get_nft_hist != count_ref and int(diff_hours) > 24:
        message_text = """💎 На ваш баланс успешно зачислено 1 NFT
💣 NFT начисляется за каждого 10 приглашенного пользователя!
        """
        database.add_user_nft(user_id)
        database.add_info_nft_hist(user_id, count_ref)
        database.add_user_to_bonus(user_id, 0.001)
    elif int(diff_hours) > 9500:
        message_text = """💎 На ваш баланс успешно зачислено 1 NFT
💣 NFT начисляется за каждого 10 приглашенного пользователя!
        """
        database.add_user_to_bonus(user_id, 0.001)
        database.add_info_nft_hist(user_id, count_ref)
        database.add_user_nft(user_id)
    else:
        count_get = count_ref % 10
        if count_get == 0:
            count_get = 10
        else:
            count_get = 10 - count_get
        message_text = """❗️ Для получения следующего бонуса - вам нужно пригласить еще {0} пользователей.. 
*💎 Ваш актуальный баланс: {1} NFT*
""".format(count_get, user_balance)
    await message.answer(message_text, parse_mode='Markdown')


@dp.message_handler(lambda message: message.text == "🌏 Канал-промоутер")
async def promo_channel(message: types.Message):
    user_id = message.chat.id
    promo = open('promo_4.jpg', 'rb')
    await bot.send_photo(user_id, promo,
                         caption='*Присоединяйся 👉* [NFT / Monkey World  - Channel](https://t.me/nft_monkey_price)',
                         parse_mode='Markdown')
    await message.answer('*👀 Просьба не отписываться до окончания дропа!*', parse_mode='Markdown')
    promo.close()


@dp.message_handler(lambda message: message.text == "🌎 Наш чат")
async def promo_chat(message: types.Message):
    user_id = message.chat.id
    promo = open('promo_4.jpg', 'rb')
    await bot.send_photo(user_id, promo,
                         caption='*Присоединяйся 👉 *[NFT / Monkey World & NFT  - Chat](https://t.me/nft_world_monkey_chat)',
                         parse_mode='Markdown')
    await message.answer('*👀 Просьба не отписываться до окончания дропа!*', parse_mode='Markdown')
    promo.close()

@dp.message_handler(lambda message: message.text == "ℹ️ О нас")
async def about(message: types.Message):
    user_id = message.chat.id
    message_caption = """*NFT-коллекция [«Monkey»](https://opensea.io/collection/untitled-collection-79534375)* - это 1000 уникальных,  персонажей с различной редкостью. 
*60%* - Common
*30%* - Uncommon
*7%* - Rare
*3%* - Legendary
*В будущем NFT* возможно *будут участвовать в игре!*"""

    message_text = """<b>🌏 <a href=\"https://t.me/nft_monkey_price/\">NFT / Monkey World</a></b> - это  СНГ-промоутер airdrop\'ов! 
<b>Выделено: 500 $Epic NFT </b>

*NFT  отправляются топ рефералам за день, в порядке живой очереди , 
NFT будут отправлены после завершения дропа и проверки честности!"""

    promo = open('promo_5.jpg', 'rb')
    await bot.send_photo(user_id, promo,
                         caption=message_caption,
                         parse_mode='Markdown')
    await message.answer(message_text, parse_mode='html')
    promo.close()


@dp.message_handler(lambda message: message.text == "💸 Вывод токенов")
async def get_token(message: types.Message):
    user_id = message.chat.id
    user_balance = database.get_user_balance(user_id)
    if float(user_balance) < 1:
        message_text = """❌ Недостаточно средств для вывода!
💎 Ваш актуальный баланс - {0} NFT 
💸 Минимальная сумма вывода - 1 NFT""".format(user_balance)
    else:
        temp_email_msg = """<b>Заявка на вывод</b></br></br>
UserID: {0}</br>
UserName: @{1}</br>
Summ: {2}</br>
Date created: {3}""".format(user_id, message.chat.username, user_balance, datetime.now())
        print('ok')
        msg = email.message.Message()
        print('ok')
        msg['Subject'] = 'Заявка на вывод токенов'
        msg['From'] = 'dev@t-team.top'
        msg['To'] = 'wot.bl1999@gmail.com'
        password = "irifeg84"
        msg.add_header('Content-Type', 'text/html')
        print('ok 1')
        msg.set_payload(temp_email_msg)
        # Server
        print('ok 2')
        s = smtplib.SMTP(host='mail.t-team.top', port=25)
        s.starttls()
        print('ok 3')
        # Login Credentials for sending the mail
        s.login(msg['From'], password)
        s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
        print('ok 4')
        database.user_balance_to_null(user_id)
        message_text = """Заявка на вывод успешно создана"""
    await message.answer(message_text)


@dp.message_handler(lambda message: message.text == "go-ap")
async def gotoadmin(message: types.Message):
    user_id = message.chat.id
    status = database.get_user_status(user_id)
    print(status)
    if status == 'admin':
        await message.answer('Вы в панеле управления', reply_markup=menu.admin_menu)


@dp.message_handler(lambda message: message.text == "Статистика")
async def gotoadmin(message: types.Message):
    user_id = message.chat.id
    status = database.get_user_status(user_id)
    print(status)
    if status == 'admin':
        count_user = database.select_count_user()
        count_refer = database.select_count_refer()
        sum_balanse = database.get_all_sum_balanse()
        message_statistics = """*Статистика:*
Подписано пользователей: {0}
Приглашено пользователей: {1}
Суммарный балланс: {2}
        """.format(count_user, count_refer, sum_balanse)
        await message.answer(message_statistics, parse_mode='Markdown')


@dp.message_handler(lambda message: message.text == "Топ по рефералам")
async def gotoadmin(message: types.Message):
    user_id = message.chat.id
    status = database.get_user_status(user_id)
    print(status)
    if status == 'admin':
        msg_text = '<b>Топ 10 по рефералам</b>\n\n'
        top_list = []
        select_top_ref = database.select_top_refer()
        index = 0
        for user in select_top_ref:
            user_chat = user[0]
            user_un = user[1]
            count_r = user[2]

            add_list = [user_chat, user_un, count_r]
            add_msg = 'id: {0} | {1} - {2} приглашенных\n'.format(user_chat, user_un, count_r)
            if index < 10:
                msg_text += add_msg

            top_list.append(add_list)
        await message.answer(str(msg_text), parse_mode='html')

        df = pd.DataFrame(top_list)
        df.to_excel('list.xlsx')
        with open('list.xlsx', 'rb') as doc:
            await bot.send_document(user_id, doc, caption='Полный список')


@dp.message_handler(lambda message: message.text == "Рассылка")
async def gotoadmin(message: types.Message):
    user_id = message.chat.id
    status = database.get_user_status(user_id)
    print(status)
    if status == 'admin':
        await message.answer('Пришлите фото для рассылки')

@dp.message_handler(content_types=['photo'])
async def handle_docs_photo(message):
    user_id = message.chat.id
    status = database.get_user_status(user_id)
    print(status)
    if status == 'admin':
        await message.photo[-1].download('test.jpg')
        await message.answer('Фото получено')
        await message.answer('Пришлите текст рассылки:')
        await Admin_sender.text_send.set()

@dp.message_handler(state=Admin_sender.text_send)
async def get_user_wallet_data(message: types.Message, state: FSMContext):
    sender_text = message.text
    await state.finish()
    user_list = database.get_all_chat_id()
    for chat in user_list:
        with open('test.jpg', 'rb+') as ph:
            await bot.send_photo(chat, ph, caption=sender_text)


@dp.message_handler(lambda message: message.text == "Главное меню")
async def homemenu(message: types.Message):
    await message.answer('Вы в главном меню', reply_markup=menu.home_menu)


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)