import config
import core
from core import sanitize_text
import telebot
import random
import datetime
import markup
from locales import t
import sys
from telebot import apihelper

if config.PROXY_URL:
    apihelper.proxy = {'https': config.PROXY_URL}

bot = telebot.TeleBot(config.TOKEN, skip_pending=True)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    lang = core.get_user_lang(user_id)
    if not lang:
        bot.send_message(message.chat.id, t('en', 'select_language'), reply_markup=markup.markup_lang())
        return
    bot.send_message(message.chat.id, t(lang, 'welcome'), parse_mode='html', reply_markup=markup.markup_main(lang))


@bot.message_handler(commands=['language'])
def language_cmd(message):
    lang = core.get_user_lang(message.from_user.id) or 'en'
    bot.send_message(message.chat.id, t(lang, 'select_language'), reply_markup=markup.markup_lang())


@bot.message_handler(commands=['agent'])
def agent(message):
    user_id = message.from_user.id
    lang = core.get_user_lang(user_id) or 'en'

    if core.check_agent_status(user_id) == True:
        bot.send_message(message.chat.id, t(lang, 'already_agent'), parse_mode='html', reply_markup=markup.markup_agent(lang))

    else:
        take_password_message = bot.send_message(message.chat.id, t(lang, 'not_in_db'), reply_markup=markup.markup_cancel(lang))

        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(take_password_message, get_password_message)


@bot.message_handler(commands=['admin'])
def admin(message):
    user_id = message.from_user.id
    lang = core.get_user_lang(user_id) or 'en'

    if str(user_id) == config.ADMIN_ID:
        bot.send_message(message.chat.id, t(lang, 'authorized_admin'), reply_markup=markup.markup_admin(lang))
    else:
        bot.send_message(message.chat.id, t(lang, 'admin_only'))


@bot.message_handler(content_types=['text'])
def send_text(message):
    user_id = message.from_user.id
    lang = core.get_user_lang(user_id) or 'en'

    if message.text == t(lang, 'write_request_btn'):
        take_new_request = bot.send_message(message.chat.id, t(lang, 'write_request_prompt'), reply_markup=markup.markup_cancel(lang))

        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(take_new_request, get_new_request)

    elif message.text == t(lang, 'my_requests_btn'):
        markup_and_value = markup.markup_reqs(user_id, 'my_reqs', '1', lang)
        markup_req = markup_and_value[0]
        value = markup_and_value[1]

        if value == 0:
            bot.send_message(message.chat.id, t(lang, 'no_requests'), reply_markup=markup.markup_main(lang))
        else:
            bot.send_message(message.chat.id, t(lang, 'your_requests'), reply_markup=markup_req)

    elif message.text == t(lang, 'change_language_btn'):
        bot.send_message(message.chat.id, t(lang, 'select_language'), reply_markup=markup.markup_lang())

    else:
        bot.send_message(message.chat.id, t(lang, 'main_menu_returned'), parse_mode='html', reply_markup=markup.markup_main(lang))


def get_password_message(message):
    password = message.text
    user_id = message.from_user.id
    lang = core.get_user_lang(user_id) or 'en'

    if password == None:
        send_message = bot.send_message(message.chat.id, t(lang, 'not_text_try_again'), reply_markup=markup.markup_cancel(lang))

        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(send_message, get_password_message)

    elif password.lower() == t(lang, 'cancel_btn').lower():
        bot.send_message(message.chat.id, t(lang, 'cancelled'), reply_markup=markup.markup_main(lang))
        return

    elif core.valid_password(password) == True:
        core.delete_password(password)
        core.add_agent(user_id)

        bot.send_message(message.chat.id, t(lang, 'already_agent'), parse_mode='html', reply_markup=markup.markup_main(lang))
        bot.send_message(message.chat.id, t(lang, 'choose_agent_section'), parse_mode='html', reply_markup=markup.markup_agent(lang))

    else:
        send_message = bot.send_message(message.chat.id, t(lang, 'wrong_password'), reply_markup=markup.markup_cancel(lang))

        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(send_message, get_password_message)


def get_agent_id_message(message):
    agent_id = message.text
    lang = core.get_user_lang(message.from_user.id) or 'en'

    if agent_id == None:
        take_agent_id_message = bot.send_message(message.chat.id, t(lang, 'not_text_try_again'), reply_markup=markup.markup_cancel(lang))

        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(take_agent_id_message, get_agent_id_message)

    elif agent_id.lower() == t(lang, 'cancel_btn').lower():
        bot.send_message(message.chat.id, t(lang, 'cancelled'), reply_markup=markup.markup_main(lang))
        return

    else:
        core.add_agent(agent_id)
        bot.send_message(message.chat.id, t(lang, 'agent_added'), reply_markup=markup.markup_main(lang))
        bot.send_message(message.chat.id, t(lang, 'choose_admin_section'), reply_markup=markup.markup_admin(lang))


def get_new_request(message):
    request = message.text
    user_id = message.from_user.id
    lang = core.get_user_lang(user_id) or 'en'
    check_file = core.get_file(message)

    #Если пользователь отправляет файл
    if check_file != None:
        file_id = check_file['file_id']
        file_name = check_file['file_name']
        type = check_file['type']
        request = check_file['text']

        if str(request) == 'None':
            take_new_request = bot.send_message(message.chat.id, t(lang, 'no_request_text'), reply_markup=markup.markup_cancel(lang))

            bot.clear_step_handler_by_chat_id(message.chat.id)
            bot.register_next_step_handler(take_new_request, get_new_request)

        else:
            req_id = core.new_req(user_id, request)
            core.add_file(req_id, file_id, file_name, type)

            bot.send_message(message.chat.id, t(lang, 'request_created', req_id=req_id), parse_mode='html', reply_markup=markup.markup_main(lang))
    
    #Если пользователь отправляет только текст
    else:
        if request == None:
            take_new_request = bot.send_message(message.chat.id, t(lang, 'unsupported_type_request'), reply_markup=markup.markup_cancel(lang))

            bot.clear_step_handler_by_chat_id(message.chat.id)
            bot.register_next_step_handler(take_new_request, get_new_request)

        elif request.lower() == t(lang, 'cancel_btn').lower():
            bot.send_message(message.chat.id, t(lang, 'cancelled'), reply_markup=markup.markup_main(lang))
            return

        else:
            req_id = core.new_req(user_id, request)
            bot.send_message(message.chat.id, t(lang, 'request_created', req_id=req_id), parse_mode='html', reply_markup=markup.markup_main(lang))


def get_additional_message(message, req_id, status):
    additional_message = message.text
    check_file = core.get_file(message)
    lang = core.get_user_lang(message.from_user.id) or 'en'
    
    #Если пользователь отправляет файл
    if check_file != None:
        file_id = check_file['file_id']
        file_name = check_file['file_name']
        type = check_file['type']
        additional_message = check_file['text']

        core.add_file(req_id, file_id, file_name, type)

    if additional_message == None:
        take_additional_message = bot.send_message(chat_id=message.chat.id, text=t(lang, 'unsupported_type_message'), reply_markup=markup.markup_cancel(lang))

        bot.clear_step_handler_by_chat_id(message.chat.id)
        bot.register_next_step_handler(take_additional_message, get_additional_message, req_id, status)

    elif additional_message.lower() == t(lang, 'cancel_btn').lower():
        bot.send_message(message.chat.id, t(lang, 'cancelled'), reply_markup=markup.markup_main(lang))
        return

    else:
        if additional_message != 'None':
            core.add_message(req_id, additional_message, status)

        if check_file != None:
            if additional_message != 'None':
                text = t(lang, 'file_and_message_sent')
            else:
                text = t(lang, 'file_sent')
        else:
            text = t(lang, 'message_sent')
        
        bot.send_message(message.chat.id, text, reply_markup=markup.markup_main(lang))

        if status == 'agent':
            user_id = core.get_user_id_of_req(req_id)
            user_lang = core.get_user_lang(user_id) or 'en'
            try:
                if additional_message == 'None':
                    additional_message = ''

                bot.send_message(user_id, t(user_lang, 'new_answer', req_id=req_id, text=additional_message), reply_markup=markup.markup_main(user_lang))

                if type == 'photo':
                    bot.send_photo(user_id, photo=file_id, reply_markup=markup.markup_main(user_lang))
                elif type == 'document':
                    bot.send_document(user_id, data=file_id, reply_markup=markup.markup_main(user_lang))
                elif type == 'video':
                    bot.send_video(user_id, data=file_id, reply_markup=markup.markup_main(user_lang))
                elif type == 'audio':
                    bot.send_audio(user_id, audio=file_id, reply_markup=markup.markup_main(user_lang))
                elif type == 'voice':
                    bot.send_voice(user_id, voice=file_id, reply_markup=markup.markup_main(user_lang))
                else:
                    bot.send_message(user_id, additional_message, reply_markup=markup.markup_main(user_lang))
            except:
                pass
        

@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    user_id = call.message.chat.id
    lang = core.get_user_lang(user_id) or 'en'

    if call.message:
        if call.data.startswith('set_lang:'):
            lang_selected = call.data.split(':')[1]
            core.set_user_lang(user_id, lang_selected)
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=t(lang_selected, 'welcome'), parse_mode='html', reply_markup=markup.markup_main(lang_selected))
            bot.answer_callback_query(call.id)
            return
        if ('my_reqs:' in call.data) or ('waiting_reqs:' in call.data) or ('answered_reqs:' in call.data) or ('confirm_reqs:' in call.data):
            """
            Обработчик кнопок для:

            ✉️ Мои запросы
            ❗️ Ожидают ответа от поддержки,
            ⏳ Ожидают ответа от пользователя
            ✅ Завершенные запросы  
            """

            parts = call.data.split(':')
            callback = parts[0]
            number = parts[1]
            markup_and_value = markup.markup_reqs(user_id, callback, number, lang)
            markup_req = markup_and_value[0]
            value = markup_and_value[1]

            if value == 0:
                bot.send_message(chat_id=call.message.chat.id, text=t(lang, 'requests_not_found'), reply_markup=markup.markup_main(lang))
                bot.answer_callback_query(call.id)
                return

            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=t(lang, 'press_request'), reply_markup=markup_req)
            except:
                bot.send_message(chat_id=call.message.chat.id, text=t(lang, 'your_requests'), reply_markup=markup_req)

            bot.answer_callback_query(call.id)

        #Открыть запрос
        elif 'open_req:' in call.data:
            parts = call.data.split(':')
            req_id = parts[1]
            callback = ':'.join(parts[2:])

            req_status = core.get_req_status(req_id)
            request_data = core.get_request_data(req_id, callback, lang)
            len_req_data = len(request_data)

            i = 1
            for data in request_data:
                data = sanitize_text(data)
                if i == len_req_data:
                    markup_req = markup.markup_request_action(req_id, req_status, callback, lang)
                else:
                    markup_req = None

                bot.send_message(chat_id=call.message.chat.id, text=data, parse_mode='html', reply_markup=markup_req)

                i += 1

            bot.answer_callback_query(call.id)

        #Добавить сообщение в запрос
        elif 'add_message:' in call.data:
            parts = call.data.split(':')
            req_id = parts[1]
            status_user = parts[2]

            take_additional_message = bot.send_message(chat_id=call.message.chat.id, text=t(lang, 'unsupported_type_message'), reply_markup=markup.markup_cancel(lang))

            bot.register_next_step_handler(take_additional_message, get_additional_message, req_id, status_user)

            bot.answer_callback_query(call.id)

        #Завершить запрос
        elif 'confirm_req:' in call.data:
            parts = call.data.split(':')
            confirm_status = parts[1]
            req_id = parts[2]

            if core.get_req_status(req_id) == 'confirm':
                bot.send_message(chat_id=call.message.chat.id, text=t(lang, 'request_already_finished'), reply_markup=markup.markup_main(lang))
                bot.answer_callback_query(call.id)

                return
            
            #Запросить подтверждение завершения
            if confirm_status == 'wait':
                bot.send_message(chat_id=call.message.chat.id, text=t(lang, 'confirm_finish'), parse_mode='html', reply_markup=markup.markup_confirm_req(req_id, lang))
            
            #Подтвердить завершение
            elif confirm_status == 'true':
                core.confirm_req(req_id)
                
                try:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=t(lang, 'request_finished'), reply_markup=markup.markup_main(lang))
                except:
                    bot.send_message(chat_id=call.message.chat.id, text=t(lang, 'request_finished'), reply_markup=markup.markup_main(lang))

                bot.answer_callback_query(call.id)

        #Файлы запроса
        elif 'req_files:' in call.data:
            parts = call.data.split(':')
            req_id = parts[1]
            callback = ':'.join(parts[2:-1])
            number = parts[-1]

            markup_and_value = markup.markup_files(number, req_id, callback, lang)
            markup_files = markup_and_value[0]
            value = markup_and_value[1]

            if value == 0:
                bot.send_message(chat_id=call.message.chat.id, text=t(lang, 'files_not_found'), reply_markup=markup.markup_main(lang))
                bot.answer_callback_query(call.id)
                return

            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=t(lang, 'press_file'), reply_markup=markup_files)
            except:
                bot.send_message(chat_id=call.message.chat.id, text=t(lang, 'press_file'), reply_markup=markup_files)

            bot.answer_callback_query(call.id)

        #Отправить файл
        elif 'send_file:' in call.data:
            parts = call.data.split(':')
            id = parts[1]
            type = parts[2]

            file_id = core.get_file_id(id)

            if type == 'photo':
                bot.send_photo(call.message.chat.id, photo=file_id, reply_markup=markup.markup_main(lang))
            elif type == 'document':
                bot.send_document(call.message.chat.id, data=file_id, reply_markup=markup.markup_main(lang))
            elif type == 'video':
                bot.send_video(call.message.chat.id, data=file_id, reply_markup=markup.markup_main(lang))
            elif type == 'audio':
                bot.send_audio(call.message.chat.id, audio=file_id, reply_markup=markup.markup_main(lang))
            elif type == 'voice':
                bot.send_voice(call.message.chat.id, voice=file_id, reply_markup=markup.markup_main(lang))
            
            bot.answer_callback_query(call.id)

        #Вернуться назад в панель агента
        elif call.data == 'back_agent':
            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=t(lang, 'already_agent'), parse_mode='html', reply_markup=markup.markup_agent(lang))
            except:
                bot.send_message(call.message.chat.id, t(lang, 'already_agent'), parse_mode='html', reply_markup=markup.markup_agent(lang))

            bot.answer_callback_query(call.id)

        #Вернуться назад в панель админа
        elif call.data == 'back_admin':
            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=t(lang, 'authorized_admin'), parse_mode='html', reply_markup=markup.markup_admin(lang))
            except:
                bot.send_message(call.message.chat.id, t(lang, 'authorized_admin'), parse_mode='html', reply_markup=markup.markup_admin(lang))

            bot.answer_callback_query(call.id)

        #Добавить агента
        elif call.data == 'add_agent':
            take_agent_id_message = bot.send_message(chat_id=call.message.chat.id, text=t(lang, 'add_agent_prompt'), reply_markup=markup.markup_cancel(lang))
            bot.register_next_step_handler(take_agent_id_message, get_agent_id_message)

        #Все агенты
        elif 'all_agents:' in call.data:
            number = call.data.split(':')[1]
            markup_and_value = markup.markup_agents(number, lang)
            markup_agents = markup_and_value[0]
            len_agents = markup_and_value[1]

            if len_agents == 0:
                bot.send_message(chat_id=call.message.chat.id, text=t(lang, 'agents_not_found'), reply_markup=markup.markup_main(lang))
                bot.answer_callback_query(call.id)
                return

            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=t(lang, 'press_agent_delete'), parse_mode='html', reply_markup=markup_agents)
            except:
                bot.send_message(call.message.chat.id, t(lang, 'press_agent_delete'), parse_mode='html', reply_markup=markup_agents)

            bot.answer_callback_query(call.id)

        #Удалить агента
        elif 'delete_agent:' in call.data:
            agent_id = call.data.split(':')[1]
            core.delete_agent(agent_id)

            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Нажмите на агента поддержки, чтобы удалить его', parse_mode='html', reply_markup=markup.markup_agents('1')[0])
            except:
                bot.send_message(call.message.chat.id, 'Нажмите на агента поддержки, чтобы удалить его', parse_mode='html', reply_markup=markup.markup_agents('1')[0])

            bot.answer_callback_query(call.id)

        #Все пароли
        elif 'all_passwords:' in call.data:
            number = call.data.split(':')[1]
            markup_and_value = markup.markup_passwords(number, lang)
            markup_passwords = markup_and_value[0]
            len_passwords = markup_and_value[1]

            if len_passwords == 0:
                bot.send_message(chat_id=call.message.chat.id, text=t(lang, 'passwords_not_found'), reply_markup=markup.markup_main(lang))
                bot.answer_callback_query(call.id)
                return

            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=t(lang, 'press_password_delete'), parse_mode='html', reply_markup=markup_passwords)
            except:
                bot.send_message(call.message.chat.id, t(lang, 'press_password_delete'), parse_mode='html', reply_markup=markup_passwords)

            bot.answer_callback_query(call.id)

        #Удалить пароль
        elif 'delete_password:' in call.data:
            password = call.data.split(':')[1]
            core.delete_password(password)

            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Нажмите на пароль, чтобы удалить его', parse_mode='html', reply_markup=markup.markup_passwords('1')[0])
            except:
                bot.send_message(call.message.chat.id, 'Нажмите на пароль, чтобы удалить его', parse_mode='html', reply_markup=markup.markup_passwords('1')[0])

            bot.answer_callback_query(call.id)

        #Сгенерировать пароли
        elif call.data == 'generate_passwords':
            #10 - количество паролей, 16 - длина пароля
            passwords = core.generate_passwords(10, 16)
            core.add_passwords(passwords)

            text_passwords = ''
            i = 1
            for password in passwords:
                text_passwords += f'{i}. {password}\n'
                i += 1
            
            bot.send_message(call.message.chat.id, t(lang, 'generated_passwords', count=i-1, passwords=text_passwords), parse_mode='html', reply_markup=markup.markup_main(lang))
            bot.send_message(call.message.chat.id, t(lang, 'press_password_delete'), parse_mode='html', reply_markup=markup.markup_passwords('1', lang)[0])

            bot.answer_callback_query(call.id)

        #Остановить бота
        elif 'stop_bot:' in call.data:
            status = call.data.split(':')[1]

            #Запросить подтверждение на отключение
            if status == 'wait':
                try:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=t(lang, 'sure_stop_bot'), parse_mode='html', reply_markup=markup.markup_confirm_stop(lang))
                except:
                    bot.send_message(call.message.chat.id, t(lang, 'sure_stop_bot'), parse_mode='html', reply_markup=markup.markup_confirm_stop(lang))

            #Подтверждение получено
            elif status == 'confirm':
                try:
                    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=t(lang, 'bot_stopped'))
                except:
                    bot.send_message(chat_id=call.message.chat.id, text=t(lang, 'bot_stopped'))

                bot.answer_callback_query(call.id)
                bot.stop_polling()
                sys.exit()


if __name__ == "__main__":
    bot.polling(none_stop=True)