from aiogram import types
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from aiosqlite import connect
from data import first_join, User, messages, get_user, register_user
from middlewares.throttling import rate_limit
from filters import IsPrivate, IsAdmin
from keyboards import defaut as key, inline as menu
from loader import bot, vip
from utils import config, market
import logging

logger = logging.getLogger(__name__)

async def check_sub(m: types.Message):
    """Foydalanuvchi kanalga a'zoligini tekshirish"""
    try:
        # Kanal ID sini configdan olish yoki default qiymat
        channel_id = -1003188505762  # steamcomm_uz kanali ID si
        res = await bot.get_chat_member(chat_id=channel_id, user_id=m.from_user.id)
        
        # A'zolik holatini tekshirish
        if res.status in ("member", "administrator", "creator"):
            return True
            
        # Debug ma'lumotlari
        logger.debug(f"[SUBSCRIPTION] User {m.from_user.id} is not a member of channel {channel_id}")
        
        # A'zo bo'lish tugmasi
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("📢 Kanalga a'zo bo'lish", url=f"https://t.me/steamcomm_uz"))
        
        await m.answer(
            "❌ Botdan foydalanish uchun avval kanalimizga a'zo bo'ling:",
            reply_markup=keyboard
        )
        return False
        
    except Exception as e:
        logger.error(f"Subscription check error for user {m.from_user.id}: {e}")
        # Xatolik yuz berganda ham foydalanuvchiga ruxsat berish (agar kerak bo'lsa)
        return True  # Yoki False qilib qo'yishingiz mumkin, bu sizning logikangizga bog'liq

@vip.callback_query_handler(text='subbed')
async def subbed(c: types.CallbackQuery):
    if await check_sub(c) == True:
        await c.answer()
        # Remove the first message and keep only the welcome message
        await c.message.answer(f'<b>⚡️ Добро пожаловать в GREEN SHOP</b>\n\n'
                        f'Данный бот, предназначен для продажи различных электронных товаров от кошельков до скриптов!\n\n'
                        f'🛠 Для навигации используйте кнопки',
                        reply_markup=key.main_menu())
    else:
        await c.answer()
        await c.message.answer('<b>❗️Вы не подписались на канал</b>', parse_mode='HTML', reply_markup=menu.kbsub)

@rate_limit(limit=1)
@vip.message_handler(IsPrivate(), commands=['start'])
async def start_handler(msg: types.Message):
    print(f"[START PAYLOAD] = {msg.text}")
    refcode = msg.text.split(' ')[1] if " " in msg.text else ''
    print(f'[REFCODE] = {refcode}')
    if "p_" in refcode:
        user = User(msg.from_user.id)
        info = await market.Product().get_product(msg.text[7:])
        products = await market.Product().get_amount_products(msg.text[7:])
        txt = messages.product.format(name = info[2], price = info[3],
                    balance = user.balance, description = info[4], amount_product = products)
        markup = InlineKeyboardMarkup().row(InlineKeyboardButton(text="🖲 Купить", callback_data=f'product_buy:{msg.text[7:]}'))
        markup.row(InlineKeyboardButton(text="💳 Пополнить", callback_data='payments'))
        await msg.answer_photo(photo="https://imgur.com/a/lyNqELJ", caption=txt, reply_markup=markup)
    elif 'p_' not in refcode and refcode != '':
        if await get_user(msg.from_user.id) == False:
            txxt = f'''<b>👤 Новый пользователь

◽️Пользователь: {msg.from_user.get_mention()}
◽️ID: {msg.from_user.id}</b>'''
            await register_user(msg.from_user.id, refcode, msg.from_user.username)
            await msg.answer('<b>🕹 Докажи что ты не бот</b>', reply_markup=menu.gen_nb_kb(msg.from_user.id, refcode))
            await bot.send_message(config.config('admin_group'), txxt)
        else:
            await msg.answer('<b>💔 Данный человек уже есть в нашем боте</b>')
    else:
        if await get_user(msg.from_user.id) == False:
            txxt = f'''<b>👤 Новый пользователь

◽️Пользователь: {msg.from_user.get_mention()}
◽️ID: {msg.from_user.id}</b>'''
            await bot.send_message(config.config('admin_group'), txxt)
            await register_user(msg.from_user.id, 0, msg.from_user.username)
            if await check_sub(msg):
                await msg.answer(f'<b>⚡️ Добро пожаловать в GREEN SHOP</b>\n\n'
							f'Данный бот, предназначен для продажи различных электронных товаров от кошельков до скриптов!\n\n'
						 	f'🛠 Для навигации используйте кнопки',
							reply_markup = key.main_menu())
            else:
                await msg.answer('''⭐️ <b>Информационный канал проекта GREEN SHOP</b> 

<i>- Пополнения товара 
- Раздача промо кодов 
- Опросы голосования
- Другие интересные посты</i>

✅ <b>Заявки принимаються автоматически!</b>''', reply_markup=menu.kbsub, parse_mode='HTML')
        else:
            if await check_sub(msg):
                await msg.answer(f'*{msg.from_user.full_name}, рад видеть тебя снова!*', 
								parse_mode='Markdown', reply_markup = key.main_menu())
            else:
                await msg.answer('''⭐️ <b>Информационный канал проекта GREEN SHOP</b> 

<i>- Пополнения товара 
- Раздача промо кодов 
- Опросы голосования
- Другие интересные посты</i>

✅ <b><i>Заявки принимаються автоматически!</i></b>''', reply_markup=menu.kbsub, parse_mode='HTML')
        

"""
@rate_limit(limit=1)
@vip.message_handler(IsPrivate(), commands=['start'])
async def start_handler(msg: types.Message):
	#status, invite = await first_join(msg.from_user.id, msg.from_user.username, msg.text[7:])
	#if msg.text[7:] is not None and msg.text[7:] != 0 and msg.text[7:] != '':
	#	await msg.answer('<b>🕹 Докажи что ты не бот</b>', reply_markup=menu.gen_nb_kb(msg.from_user.id, invite))
	if await check_sub(msg):
		status, invite = await first_join(msg.from_user.id, msg.from_user.username, msg.text[7:])
		if status != False:
			txxt = f'''<b>👤 Новый пользователь

◽️Пользователь: {msg.from_user.get_mention()}
◽️ID: {msg.from_user.id}</b>'''
			await msg.answer(f'<b>⚡️ Добро пожаловать в ZORO SHOP</b>\n\n'
							f'<code>Данный бот, предназначен для продажи различных электронных товаров от кошельков до скриптов!</code>\n\n'
						 	f'🛠 Для навигации используйте кнопки',
							reply_markup = key.main_menu())
			await bot.send_message(config.config('admin_group'), f'Новый пользователь {msg.from_user.get_mention()} | {msg.from_user.id}')
			if invite != 0:
				await bot.send_message(invite, f'У вас новый реферал: {msg.from_user.get_mention(as_html=True)} !')
				await msg.answer('<b>🕹 Докажи что ты не бот</b>', reply_markup=menu.gen_nb_kb(msg.from_user.id, 0))
		else:
			if User(msg.from_user.id).ban == 'no':
				if msg.text[7:] != '' and msg.text[7:].startswith("p_"):
					user = User(msg.from_user.id)
					info = await market.Product().get_product(msg.text[7:])
					products = await market.Product().get_amount_products(msg.text[7:])
					txt = messages.product.format(name = info[2], price = info[3],
                            balance = user.balance, description = info[4], amount_product = products)
					markup = InlineKeyboardMarkup().row(InlineKeyboardButton(text="🖲 Купить", callback_data=f'product_buy:{msg.text[7:]}'))
					markup.row(InlineKeyboardButton(text="💳 Пополнить", callback_data='payments'))
					await msg.answer_photo(photo="https://imgur.com/upload", caption=txt, reply_markup=markup)
				else: await msg.answer(f'*{msg.from_user.full_name}, рад видеть тебя снова!*', 
								parse_mode='Markdown', reply_markup = key.main_menu())
	else:
		await msg.answer('''⭐️ <b>Информационный канал проекта ZORO SHOP</b> 

<i>- Пополнения товара 
- Раздача промо кодов 
- Опросы голосования
- Другие интересные посты</i>''', reply_markup=menu.kbsub, parse_mode='HTML')
"""
@vip.callback_query_handler(text='showlinks')
async def lisst(c: types.CallbackQuery):
    async with connect("./data/database.db") as db:
        select = await db.execute("SELECT * FROM product")
        fall = await select.fetchall()
        botx = await bot.get_me()
        s = []
        for i in fall:
            s.append(f'<a href="https://t.me/{botx.username}?start={i[0]}">Клик</a> - {i[2]}')
        await c.message.answer('\n'.join(s), parse_mode='HTML')