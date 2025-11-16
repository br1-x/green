from aiogram import types
from aiogram.dispatcher import FSMContext

from loader import vip, bot
from states import AdmSearch, AdmGiveBalance
from data import User, get_user
from keyboards import inline as menu

@vip.callback_query_handler(text='admin_search')
async def adm_search(call: types.CallbackQuery):
    await AdmSearch.user_id.set()
    await bot.send_message(chat_id = call.from_user.id, 
                text = 'Введите user_id пользователя:')


@vip.message_handler(state = AdmSearch.user_id)
async def adm_search2(msg: types.Message, state: FSMContext):
    try:
        if await get_user(msg.text) == True:
            user = User(msg.text)
            await bot.send_message(chat_id = msg.from_user.id,
                    text = f'<b>👤 Пользователь:</b> @{user.username}\n\n'
                           f'<b>💳 Баланс:</b> <code>{user.balance}</code> <b>⭐</b>\n\n'
                           f'<b>⚙️ Статус:</b> <code>{user.status}</code>\n\n'
                           f'<b>♻️ Количество покупок:</b> <code>{user.purchases}</code>\n\n'
                           f'<b>💢 Бан:</b> <code>{user.ban}</code> (yes - значит в бане)\n\n'
                           f'<b>🕰 Дата регистрации:</b> <code>{user.date[:10]}</code>',
                    reply_markup = menu.admin_user_menu(msg.text))
        else:
            await msg.answer('💢 Я не нашел такого пользователя')
        await state.finish()
    except:
        await state.finish()
        await msg.answer('💢 Ошибка, чето наебнулось')

@vip.message_handler(state = AdmGiveBalance.amount)
async def adm_give_balance(msg: types.Message, state: FSMContext):
    try:
        if msg.text.isdigit() == True:
            amount = float(msg.text)
            async with state.proxy() as data:
                    user_id = data['user_id']
            await User(user_id).up_balance(amount)
            await bot.send_message(chat_id = msg.from_user.id,
                    text = '💳 <b>Баланс успешно изменен</b>', reply_markup = menu.close_markup())
        else:
            await msg.answer('Ввводи число!')
        await state.finish()
    except:
        await state.finish()
        await msg.answer('💢 Ошибка')

