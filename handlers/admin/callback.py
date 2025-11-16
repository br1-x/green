from aiogram import types
from aiogram.dispatcher import FSMContext


from loader import bot, vip
from filters import IsAdmin
from keyboards import defaut as key, inline as menu
from data import admin_stats, User, messages as mes, AdmPromo
from utils import Catalog, SubCatalog, Product
from states import CreateSubCatalog, AdminDownloadProduct, AdmGiveBalance, \
    CreateSubCatalog, CreateProduct, CreatePromo, QiwiChange, CreateCatalog

@vip.callback_query_handler(text='admin_stats')
async def admin_statistic(call: types.CallbackQuery):
    await call.message.edit_text(text=await admin_stats(), reply_markup=menu.admin_markup())

@vip.callback_query_handler(text_startswith='adm_catalog:')
async def admin_catalog(call: types.CallbackQuery):
    name = await Catalog().get_category(call.data.split(":")[1])
    text = f'Каталог: {name[1]}\nЧто хотите сделать?'
    markup = menu.adm_catalog_info(call.data.split(":")[1])

    await call.message.edit_text(text=text, reply_markup=markup)

@vip.callback_query_handler(text='admin_promo')
async def admin_promo(call: types.CallbackQuery):
    text = 'Выбери действие действие:'
    await call.message.edit_text(text=text, reply_markup=menu.adm_promo_info())

@vip.callback_query_handler(text='create_catalog')
async def create_catalog_handler(call: types.CallbackQuery, state: FSMContext):
    """Handle the creation of a new catalog"""
    await call.message.edit_text("📝 Введите название новой категории:")
    await CreateCatalog.name.set()

@vip.message_handler(state=CreateCatalog.name)
async def process_catalog_name(message: types.Message, state: FSMContext):
    """Process the catalog name and create it"""
    try:
        catalog = Catalog()
        await catalog.create_catalog(message.text)
        await message.answer(f"✅ Категория '{message.text}' успешно создана!")
        
        # Show the updated catalog list
        markup = await catalog.adm_catalog_menu()
        await message.answer("📂 Список категорий:", reply_markup=markup)
    except Exception as e:
        logger.error(f"Error creating catalog: {e}")
        await message.answer("❌ Произошла ошибка при создании категории. Попробуйте снова.")
    
    await state.finish()

@vip.callback_query_handler(text_startswith='delete_catalog:')
async def delete_catalog_handler(call: types.CallbackQuery):
    """Handle catalog deletion with confirmation"""
    catalog_id = call.data.split(":")[1]
    catalog = Catalog()
    try:
        catalog_info = await catalog.get_category(catalog_id)
        if not catalog_info:
            await call.answer("❌ Категория не найдена", show_alert=True)
            return
            
        # Show confirmation dialog
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton("✅ Да, удалить", callback_data=f"confirm_delete_catalog:{catalog_id}"),
            types.InlineKeyboardButton("❌ Отмена", callback_data="cancel_delete_catalog")
        )
        
        await call.message.edit_text(
            f"⚠️ Вы уверены, что хотите удалить категорию '{catalog_info[1]}'?\n"
            "Все подкатегории и товары в этой категории будут также удалены!",
            reply_markup=markup
        )
    except Exception as e:
        logger.error(f"Error in delete_catalog_handler: {e}")
        await call.answer("❌ Ошибка при удалении категории", show_alert=True)

@vip.callback_query_handler(text_startswith='confirm_delete_catalog:')
async def confirm_delete_catalog(call: types.CallbackQuery):
    """Confirm and process catalog deletion"""
    catalog_id = call.data.split(":")[1]
    catalog = Catalog()
    try:
        catalog_info = await catalog.get_category(catalog_id)
        if not catalog_info:
            await call.answer("❌ Категория не найдена", show_alert=True)
            return
            
        # Delete the catalog
        await catalog.delete_catalog(catalog_id)
        await call.message.edit_text(f"✅ Категория '{catalog_info[1]}' успешно удалена!")
        
        # Show updated catalog list
        markup = await catalog.adm_catalog_menu()
        await call.message.answer("📂 Список категорий:", reply_markup=markup)
        
    except Exception as e:
        logger.error(f"Error in confirm_delete_catalog: {e}")
        await call.answer("❌ Ошибка при удалении категории", show_alert=True)

@vip.callback_query_handler(text='cancel_delete_catalog')
async def cancel_delete_catalog(call: types.CallbackQuery):
    """Cancel catalog deletion"""
    catalog = Catalog()
    markup = await catalog.adm_catalog_menu()
    await call.message.edit_text("📂 Список категорий:", reply_markup=markup)

#@vip.message_handler(commands="change_qiwi:")
async def change(message : types.Message):
    qiwi_data = message.text.split(":")[1]
    qiwi_data = qiwi_data.split(",")
    await change_token(qiwi_data[1])
    await change_number(qiwi_data[0])

@vip.callback_query_handler(text="change_qiwi")
async def admin_qiwi(callback: types.CallbackQuery()):
    await QiwiChange.number.set()
    await callback.message.answer("<b>📱 Введите номер кошелька в формате <code>79872679812</code></b>")

@vip.message_handler(state=QiwiChange.number)
async def qiwiNumber_accept(message: types.Message, state: FSMContext):
    await QiwiChange.next()
    await message.answer("<b>🔒 Введите токен кошелька</b>")
    await change_number(message.text)

@vip.message_handler(state=QiwiChange.token)
async def qiwi_number(message: types.Message, state: FSMContext):
    await change_token(message.text)
    await message.answer("☑️ <b>Киви кошелек успешно сменен! Не забудьте перезапустить бота на сервере</b> ( <code> tmux a -t 0</code> )") 
    await state.finish()


async def change_number(number):
    new_number = number

    import sqlite3

    path = './data/database.db'
    connect = sqlite3.connect(path)
    cur = connect.cursor()
    cur.execute(f"UPDATE qiwi_data SET qiwi_number = '{new_number}'")
    connect.commit()
    connect.close()

async def change_token(token):
    new_token = token

    import sqlite3

    path = './data/database.db'
    connect = sqlite3.connect(path)
    cur = connect.cursor()
    cur.execute(f"UPDATE qiwi_data SET qiwi_token = '{new_token}'")
    connect.commit()
    connect.close()

@vip.callback_query_handler(text='create_promo')
async def admin_create_promo(call: types.CallbackQuery):
    await CreatePromo.name.set()
    text = '🔖 <b>Введите название промокода, если хотите отменить напишите «-»</b>'
    await call.message.answer(text=text)

@vip.callback_query_handler(text='activ_promo')
async def active_promocode(call: types.CallbackQuery):
    markup = await AdmPromo().activ_promo_menu()
    await call.message.edit_text(text='Активные промокоды', reply_markup=markup)

@vip.callback_query_handler(text_startswith='adm_promo:')
async def info_promocode(call: types.CallbackQuery):
    promo_id = call.data.split(":")[1]
    text, markup = await AdmPromo().get_info_promo(promo_id)
    await call.message.edit_text(text=text, reply_markup=markup)

@vip.callback_query_handler(text_startswith='promo_delete:')
async def delete_promocode(call: types.CallbackQuery):
    await AdmPromo().delete_promocode(call.data.split(":")[1])
    await call.message.delete()
    await call.message.answer(text='Промокод удален!', reply_markup=menu.close_markup())

@vip.callback_query_handler(text_startswith='delete_ category:')
async def adm_delete_catalog(call: types.CallbackQuery):
    await Catalog().delete_catalog(call.data.split(":")[1])

    await bot.delete_message(call.from_user.id, call.message.message_id)
    await call.message.answer('Каталог успешно удален!', reply_markup=menu.close_markup())

@vip.callback_query_handler(text_startswith='create_subcatalog:')
async def adm_create_subcatalog(call: types.CallbackQuery, state: FSMContext):
    await CreateSubCatalog.name.set()
    async with state.proxy() as data:
        data['category'] = call.data.split(":")[1]
    await call.message.edit_text('Введите название подкатегории:')

@vip.callback_query_handler(text_startswith='delete_subcatalog:')
async def adm_delete_subcatalog(call: types.CallbackQuery):
    await SubCatalog().delete_subcatalog(call.data.split(":")[1])
    await call.message.edit_text(text = 'Подкаталог удален!', reply_markup = menu.close_markup())

@vip.callback_query_handler(text_startswith='adm_subcatalog:')
async def adm_subcatalog(call: types.CallbackQuery):
    try:
        subcategory_id = call.data.split(":")[1]
        subcategory = SubCatalog()
        result = await subcategory.get_subcategory(subcategory_id)
        
        if not result or not all(result):
            await call.answer('❌ Подкаталог не найден', show_alert=True)
            # Return to the catalog menu instead of main admin menu
            catalog = Catalog()
            markup = await catalog.adm_catalog_menu()
            await call.message.edit_text('📂 Выберите категорию:', reply_markup=markup)
            return
            
        subcategory_id, subcategory_name = result
        markup = menu.adm_subcatalog_info(subcategory_id)
        text = f'📂 Подкаталог: {subcategory_name}\nВыберите действие:'
        await call.message.edit_text(text=text, reply_markup=markup)
    except Exception as e:
        logger.error(f"Error in adm_subcatalog: {e}")
        await call.answer('❌ Ошибка при загрузке подкаталога', show_alert=True)
        # Return to catalog menu on error
        catalog = Catalog()
        markup = await catalog.adm_catalog_menu()
        await call.message.edit_text('📂 Выберите категорию:', reply_markup=markup)
        await call.answer('❌ Произошла ошибка при загрузке подкаталога', show_alert=True)

@vip.callback_query_handler(text_startswith='delete_product:')
async def adm_delete_product(call: types.CallbackQuery):
    await Product().delete_product(call.data.split(":")[1])
    await call.message.edit_text("Успешно удален товар!", reply_markup = menu.close_markup())

@vip.callback_query_handler(text_startswith='adm_product:')
async def adm_product(call: types.CallbackQuery):
    product_id = call.data.split(":")[1]
    info = await Product().get_product(product_id)
    text = mes.adm_product.format(name = info[2], price = info[3], 
                        description = info[4], amount_product = await Product().get_amount_products(product_id))
    await call.message.edit_text(text = text, reply_markup = menu.adm_product_info(product_id))

@vip.callback_query_handler(text_startswith='create_product:')
async def adm_create_product(call: types.CallbackQuery, state: FSMContext):
    await CreateProduct.name.set()
    async with state.proxy() as data:
        data['subcategory_id'] = call.data.split(":")[1]
    await call.message.edit_text(text = 'Введите название нового товара:')

@vip.callback_query_handler(text_startswith='adm_unban:')
async def adm_unban(call: types.CallbackQuery):
    await User(call.data.split(":")[1]).up_ban("no")
    await call.message.answer('Пользователь разбанен', reply_markup = menu.close_markup())

@vip.callback_query_handler(text_startswith='adm_ban:')
async def adm_ban(call: types.CallbackQuery):
    await User(call.data.split(":")[1]).up_ban("yes")
    await call.message.answer('Пользователь забанен', reply_markup = menu.close_markup())

@vip.callback_query_handler(text_startswith='adm_send:')
async def adm_send(call: types.CallbackQuery, state: FSMContext):
    await call.message.answer('<i>✉️ Введите текст для ответа:</i> ', parse_mode='HTML')
    await state.set_state('admsending')
    await state.update_data(userid=call.data.split(":")[1])

@vip.message_handler(state='admsending')
async def adm_send_payload(m: types.Message, state: FSMContext):
    data = await state.get_data()
    print(f'[SEND] {data}')
    await bot.send_message(data['userid'], f'''<b>👾 Поддержка обработала ваш запрос! 

💬 Сообщение:</b> <code>{m.text}</code>
''', parse_mode='HTML')
    await m.answer('<b>☑️ Успешно ответили</b>', parse_mode='HTML')
    await state.finish()
@vip.callback_query_handler(text_startswith='adm_give_balance:')
async def adm_give(call: types.CallbackQuery, state: FSMContext):
    await AdmGiveBalance.amount.set()
    async with state.proxy() as data:
        data['user_id'] = call.data.split(":")[1]
    await call.message.answer('Введите значение, на которое изменится баланс пользователя:')

@vip.callback_query_handler(text_startswith='download_product:')
async def adm_add_product(call: types.CallbackQuery, state: FSMContext):
    await AdminDownloadProduct.file.set()
    async with state.proxy() as data:
        data['product_id'] = call.data.split(":")[1]
    await call.message.answer('Пришлите файл с товаром, я загружу его')