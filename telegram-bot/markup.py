from telebot import types
from core import my_reqs, get_reqs, get_agents, get_passwords, get_files, get_icon_from_status, get_file_text
from locales import t


def markup_lang():
    markup_lang = types.InlineKeyboardMarkup(row_width=2)
    item1 = types.InlineKeyboardButton('English', callback_data='set_lang:en')
    item2 = types.InlineKeyboardButton('Русский', callback_data='set_lang:ru')
    markup_lang.add(item1, item2)
    return markup_lang


def page(markup, number, list, call, callback_cancel, lang='en'):
    if len(list) != 10:
        max_nums = number
    else:
        max_nums = 'None'

    if str(number) == '1':
        item1 = types.InlineKeyboardButton(f"⏹", callback_data=f'None')
    else:
        item1 = types.InlineKeyboardButton(f"◀️", callback_data=f'{call}:{int(number) - 1}')

    if str(number) == str(max_nums):
        item2 = types.InlineKeyboardButton(f"⏹", callback_data=f'None')
    else:
        item2 = types.InlineKeyboardButton(f"▶️", callback_data=f'{call}:{int(number) + 1}')

    item3 = types.InlineKeyboardButton(t(lang, 'back_btn'), callback_data=callback_cancel)

    if callback_cancel != 'None':
        markup.add(item1, item3, item2)
    else:
        if str(number) == '1' and str(number) == str(max_nums):
            pass
        else:
            markup.add(item1, item2)
    
    return markup 


def markup_main(lang='en'):
    markup_main = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton(t(lang, 'write_request_btn'))
    item2 = types.KeyboardButton(t(lang, 'my_requests_btn'))
    item3 = types.KeyboardButton(t(lang, 'change_language_btn'))
    markup_main.row(item1)
    markup_main.row(item2)
    markup_main.row(item3)

    return markup_main


def markup_agent(lang='en'):
    markup_agent = types.InlineKeyboardMarkup(row_width=1)
    item1 = types.InlineKeyboardButton(t(lang, 'waiting_support_btn'), callback_data='waiting_reqs:1')
    item2 = types.InlineKeyboardButton(t(lang, 'waiting_user_btn'), callback_data='answered_reqs:1')
    item3 = types.InlineKeyboardButton(t(lang, 'completed_btn'), callback_data='confirm_reqs:1')
    markup_agent.add(item1, item2, item3)

    return markup_agent


def markup_cancel(lang='en'):
    markup_cancel = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item1 = types.KeyboardButton(t(lang, 'cancel_btn'))
    markup_cancel.row(item1)

    return markup_cancel


def markup_admin(lang='en'):
    markup_admin = types.InlineKeyboardMarkup(row_width=1)
    item1 = types.InlineKeyboardButton(t(lang, 'add_agent_btn'), callback_data='add_agent')
    item2 = types.InlineKeyboardButton(t(lang, 'agents_btn'), callback_data='all_agents:1')
    item3 = types.InlineKeyboardButton(t(lang, 'passwords_btn'), callback_data='all_passwords:1')
    item4 = types.InlineKeyboardButton(t(lang, 'generate_pass_btn'), callback_data='generate_passwords')
    item5 = types.InlineKeyboardButton(t(lang, 'stop_bot_btn'), callback_data='stop_bot:wait')
    markup_admin.add(item1, item2, item3, item4, item5)

    return markup_admin


def markup_back(back, lang='en'):
    markup_back = types.InlineKeyboardMarkup(row_width=1)
    item1 = types.InlineKeyboardButton(t(lang, 'back_btn'), callback_data=f'back_{back}')
    markup_back.add(item1)

    return markup_back


def markup_reqs(user_id, callback, number, lang='en'):
    if callback == 'my_reqs':
        reqs = my_reqs(number, user_id)
        user_status = 'user'
        callback_cancel = 'None'
    else:
        reqs = get_reqs(number, callback)
        user_status = 'agent'
        callback_cancel = 'back_agent'

    markup_my_reqs = types.InlineKeyboardMarkup(row_width=3)
    for req in reqs:
        req_id = req[0]
        req_status = req[1]
        req_icon = get_icon_from_status(req_status, user_status)
        #❗️, ⏳, ✅

        item = types.InlineKeyboardButton(f'{req_icon} | ID: {req_id}', callback_data=f'open_req:{req_id}:{callback}-{number}')
        markup_my_reqs.add(item)
    
    markup_my_reqs = page(markup_my_reqs, number, reqs, callback, callback_cancel, lang)

    return markup_my_reqs, len(reqs)


def markup_request_action(req_id, req_status, callback, lang='en'):
    formatted_callback = callback.replace('-', ':')

    markup_request_action = types.InlineKeyboardMarkup(row_width=1)

    if req_status == 'confirm':
        item1 = types.InlineKeyboardButton(t(lang, 'show_files_btn'), callback_data=f'req_files:{req_id}:{callback}:1')
        item2 = types.InlineKeyboardButton(t(lang, 'back_btn'), callback_data=formatted_callback)

        markup_request_action.add(item1, item2)

    elif req_status == 'answered' or req_status == 'waiting':
        if 'my_reqs:' in formatted_callback:
            status_user = 'user'
        else:
            status_user = 'agent'

        item1 = types.InlineKeyboardButton(t(lang, 'add_message_btn'), callback_data=f'add_message:{req_id}:{status_user}')
        item2 = types.InlineKeyboardButton(t(lang, 'show_files_btn'), callback_data=f'req_files:{req_id}:{callback}:1')

        if status_user == 'user':
            item3 = types.InlineKeyboardButton(t(lang, 'finish_request_btn'), callback_data=f'confirm_req:wait:{req_id}')

        item4 = types.InlineKeyboardButton(t(lang, 'back_btn'), callback_data=formatted_callback)

        if status_user == 'user':
            markup_request_action.add(item1, item2, item3, item4)
        else:
            markup_request_action.add(item1, item2, item4)

    return markup_request_action


def markup_confirm_req(req_id, lang='en'):
    markup_confirm_req = types.InlineKeyboardMarkup(row_width=1)
    item1 = types.InlineKeyboardButton(t(lang, 'confirm_btn'), callback_data=f'confirm_req:true:{req_id}')
    markup_confirm_req.add(item1)

    return markup_confirm_req


def markup_agents(number, lang='en'):
    agents = get_agents(number)

    markup_agents = types.InlineKeyboardMarkup(row_width=3)
    for agent in agents:
        agent_id = agent[0]

        item = types.InlineKeyboardButton(f'🧑‍💻 | {agent_id}', callback_data=f'delete_agent:{agent_id}')
        markup_agents.add(item)
    
    markup_agents = page(markup_agents, number, agents, 'all_agents', 'back_admin', lang)

    return markup_agents, len(agents)


def markup_passwords(number, lang='en'):
    passwords = get_passwords(number)

    markup_passwords = types.InlineKeyboardMarkup(row_width=3)
    for password in passwords:
        password_value = password[0]

        item = types.InlineKeyboardButton(password_value, callback_data=f'delete_password:{password_value}')
        markup_passwords.add(item)
    
    markup_passwords = page(markup_passwords, number, passwords, 'all_passwords', 'back_admin', lang)

    return markup_passwords, len(passwords)


def markup_files(number, req_id, callback, lang='en'):
    files = get_files(number, req_id)

    markup_files = types.InlineKeyboardMarkup(row_width=3)
    for file in files:
        id = file[0]
        file_name = file[1]
        type = file[2]

        file_text = get_file_text(file_name, type, lang)
        # 📷 | Фото 27.12.2020 14:21:50
        
        item = types.InlineKeyboardButton(file_text, callback_data=f'send_file:{id}:{type}')
        markup_files.add(item)
    
    markup_files = page(markup_files, number, files, f'req_files:{req_id}:{callback}', f'open_req:{req_id}:{callback}', lang)

    return markup_files, len(files)

def markup_confirm_stop(lang='en'):
    markup_confirm_stop = types.InlineKeyboardMarkup(row_width=1)
    item1 = types.InlineKeyboardButton(t(lang, 'yes_btn'), callback_data='stop_bot:confirm')
    item2 = types.InlineKeyboardButton(t(lang, 'no_btn'), callback_data='back_admin')
    markup_confirm_stop.add(item1, item2)

    return markup_confirm_stop
