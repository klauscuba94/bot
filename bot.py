import telebot
import time
from telebot import types

TOKEN = "6232039281:AAGBT4pMdcjH4vA8enA5J4oulsTVvZ79d_g"
bot = telebot.TeleBot(TOKEN)

grupo_id = -1001800937998
insultos = ["tonto", "idiota", "imbécil", "estúpido", "pinga", "cojone", "repinga", "anormal", "guanajo", "come mierda", "mierda", "maricon", "singa", "cinga", "culo"]
infracciones = {}
usuarios_silenciados = []
usuarios_baneados = []

# Manejador para saludar a los nuevos miembros del grupo
@bot.message_handler(func=lambda m: True, content_types=['new_chat_members'])
def greet_new_members(message):
    for member in message.new_chat_members:
        user_name = member.first_name
        welcome_msg = f"🌟 ¡Hola {user_name}! ¡Bienvenid@ a ZapataNet! 🌟\n\n" \
                      f"👋 Para comenzar, presiona /start y nuestro asistente te ayudará en todo.\n\n" \
                      f"📢 Puedes enviarme mensajes y yo los publicaré en el chat.\n\n" \
                      f"✉️ Además, ten en cuenta que cualquier palabra ofensiva está prohibida aquí. " \
                      f"Si se detecta alguna, recibirás una advertencia.\n\n" \
                      f"😊 ¡Diviértete y participa en las conversaciones! ¡Estamos felices de tenerte aquí! 😊"
        bot.send_message(message.chat.id, welcome_msg)

# Manejador para el comando /start
@bot.message_handler(commands=['start'])
def start(message):
    user_name = message.from_user.first_name
    welcome_msg = f"🌟 ¡Hola {user_name}! ¡Bienvenid@ a ZapataNet! 🌟\n\n" \
                  f"✉️ Además, ten en cuenta que cualquier palabra ofensiva está prohibida aquí. " \
                  f"Si se detecta alguna, recibirás una advertencia.\n\n" \
                  f"😊 ¡Diviértete y participa en las conversaciones! ¡Estamos felices de tenerte aquí! 😊"
    bot.send_message(message.chat.id, welcome_msg)

# Manejador para detectar mensajes ofensivos
@bot.message_handler(func=lambda m: True)
def handle_offensive_message(message):
    text = message.text
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    if any(insulto in text.lower() for insulto in insultos):
        if user_id not in infracciones:
            infracciones[user_id] = 1
        else:
            infracciones[user_id] += 1
        num_infracciones = infracciones[user_id]
        if num_infracciones == 1:
            warn_msg = f"¡Cuidado, {user_name}! Has usado una palabra ofensiva. No lo vuelvas a hacer o serás silenciado durante dos horas."
            bot.send_message(message.chat.id, warn_msg)
        elif num_infracciones == 2:
            mute_msg = f"¡¡{user_name}!! Has usado otra palabra ofensiva. Has sido silenciado durante dos horas. No podrás enviar mensajes al grupo hasta que se te levante la restricción."
            bot.send_message(message.chat.id, mute_msg)
            now = int(time.time())
            until_date = now + 2 * 60 * 60 
            bot.restrict_chat_member(grupo_id, user_id, until_date=until_date, can_send_messages=False)
            usuarios_silenciados.append(user_id)

# Manejador para el comando /unsilence
@bot.message_handler(commands=['unsilence'])
def unsilence(message):
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
        if user_id in usuarios_silenciados:
            bot.restrict_chat_member(grupo_id, user_id, can_send_messages=True)
            usuarios_silenciados.remove(user_id)
            unsilence_msg = f"La sanción ha sido levantada para el usuario {message.reply_to_message.from_user.first_name}. ¡Ahora puede enviar mensajes nuevamente!"
            bot.send_message(grupo_id, unsilence_msg)
        else:
            unsilence_msg = "El usuario seleccionado no está silenciado."
            bot.send_message(grupo_id, unsilence_msg)

# Manejador para el comando /list_ban
@bot.message_handler(commands=['list_ban'])
def list_ban(message):
    if usuarios_baneados:
        ban_msg = "Usuarios baneados:\n"
        for user_id in usuarios_baneados:
            user_info = bot.get_chat_member(grupo_id, user_id)
            user_name = user_info.user.first_name
            ban_msg += f"- {user_name} (ID: {user_id})\n"
        bot.send_message(grupo_id, ban_msg)
    else:
        bot.send_message(grupo_id, "No hay usuarios baneados en este momento.")

# Manejador para el comando /unlock
@bot.message_handler(commands=['unlock'])
def unlock(message):
    if message.reply_to_message and message.reply_to_message.from_user:
        user_id = message.reply_to_message.from_user.id
        if user_id in usuarios_baneados:
            bot.unban_chat_member(grupo_id, user_id)
            usuarios_baneados.remove(user_id)
            unlock_msg = f"El usuario {message.reply_to_message.from_user.first_name} ha sido desbloqueado."
            bot.send_message(grupo_id, unlock_msg)
        else:
            unlock_msg = "El usuario seleccionado no está baneado."
            bot.send_message(grupo_id, unlock_msg)

# Manejador para el comando /menu
@bot.message_handler(commands=['menu'])
def menu(message):
    # Crear el teclado inline
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    # Crear los botones del menú
    btn_silence = types.InlineKeyboardButton("Silenciar Usuario", callback_data='silence')
    btn_unsilence = types.InlineKeyboardButton("Desilenciar Usuario", callback_data='unsilence')
    btn_list_ban = types.InlineKeyboardButton("Listar Usuarios Baneados", callback_data='list_ban')
    btn_unlock = types.InlineKeyboardButton("Desbloquear Usuario", callback_data='unlock')
    
    # Agregar los botones al teclado
    markup.add(btn_silence, btn_unsilence)
    markup.add(btn_list_ban, btn_unlock)
    
    # Enviar el mensaje del menú
    bot.send_message(message.chat.id, "Selecciona una opción:", reply_markup=markup)

# Manejador para los botones del menú
@bot.callback_query_handler(func=lambda call: True)
def handle_menu_buttons(call):
    user_id = call.from_user.id
    
    if call.data == 'silence':
        # Silenciar al usuario
        bot.send_message(call.message.chat.id, "Seleccionaste la opción 'Silenciar Usuario'.")
    elif call.data == 'unsilence':
        # Desilenciar al usuario
        bot.send_message(call.message.chat.id, "Seleccionaste la opción 'Desilenciar Usuario'.")
    elif call.data == 'list_ban':
        # Listar usuarios baneados
        bot.send_message(call.message.chat.id, "Seleccionaste la opción 'Listar Usuarios Baneados'.")
    elif call.data == 'unlock':
        # Desbloquear al usuario
        bot.send_message(call.message.chat.id, "Seleccionaste la opción 'Desbloquear Usuario'.")
    
    # Responder al callback query para evitar errores
    bot.answer_callback_query(call.id)

print("Bot iniciado")
bot.polling()
