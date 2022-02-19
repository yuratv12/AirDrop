from aiogram import types

home_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
home_menu.row('👥 Рефералы', '🎁 Бонус')
home_menu.row('🌏 Канал-промоутер', '🌎 Наш чат')
home_menu.row('ℹ️ О нас', '💸 Вывод NFT')

next_button = types.ReplyKeyboardMarkup(resize_keyboard=True)
next_button.row('Далее')

admin_menu = types.ReplyKeyboardMarkup(resize_keyboard=True)
admin_menu.row('Статистика', 'Рассылка')
admin_menu.row('Топ по рефералам')
admin_menu.row('Главное меню')