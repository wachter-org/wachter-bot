import re

_texts = {
    "msg__set_new_message": "Обновил сообщение.",
    "msg__success_set_kick_timeout_response": "Обновил время до удаления.",
    "msg__sucess_set_notify_timeout_response": "Обновил время до напоминания.",
    "msg__failed_set_kick_timeout_response": "Время должно быть целым положительным числом.",
    "msg__failed_kick_response": "Я не справился.",
    "msg__start_command": "Выберите чат:",
    "msg__select_chat": "Выбран чат {chat_name}. Теперь выберите действие:",
    "msg__help": """Привет! Я - бот Вахтер. Я слежу, чтобы в твоем чате были только представившиеся пользователи. Для начала работы добавь меня в чат и сделай меня администратором.
После этого для настройки бота тебе нужно написать мне в личных сообщениях /start.
По умолчанию я не удаляю из чата непредставившихся, а лишь записываю все сообщения с хэштегом #whois.
Если ты хочешь автоматически удалять непредставившихся, то установи время ожидания до удаления из чата в значение больше нуля (в минутах).
По умолчанию за 10 минут до удаления я отправляю сообщение с напоминанием.""",
    "msg__add_bot_to_chat": "Привет, я Вахтёр. Я буду следить за тем, чтобы все люди в чате были представившимися. Дайте мне админские права, чтобы я мог это делать.",
    "msg__make_admin": "Спасибо, теперь я могу видеть сообщения. Пожалуйста, представьтесь, используя хэштег #whois.",
    "msg__make_admin_direct": "Есть новый чат {chat_name}",
    "msg__new_chat_member": "Добро пожаловать! Пожалуйста, представьтесь с использованием хэштега #whois и поздоровайтесь с сообществом.",
    "msg__known_new_chat_member": "Добро пожаловать снова!",
    "msg__introduce": "Спасибо и добро пожаловать!",
    "msg__kick": "%USER\_MENTION% не представился и покидает чат.",
    "msg__notify": "%USER\_MENTION%, пожалуйста, представьтесь с использованием хэштега #whois.",
    "msg__introduce_update": "%USER\_MENTION%, если вы хотите обновить существующий #whois, пожалуйста добавьте тег #update к сообщению.",
    "msg__no_chats_available": "У вас нет доступных чатов.",
    "msg__sucess_whois_length": "Обновил необходимую длину #whois.",
    "msg__failed_whois_response": "Длина должна быть целым положительным числом.",
    "msg__need_hashtag_update_response": "Сообщение должно содержать #update.",
    "btn__intro": "Приветствия",
    "btn__kicks": "Удаление и блокировка",
    "btn__back_to_chats": "Назад к списку чатов",
    "btn__current_settings": "Посмотреть текущие настройки",
    "btn__change_welcome_message": "Изменить сообщение при входе в чат",
    "btn__change_rewelcome_message": "Изменить сообщение при перезаходе в чат",
    "btn__change_notify_message": "Изменить сообщение напоминания",
    "btn__change_sucess_message": "Изменить сообщение после представления",
    "btn__change_notify_timeout": "Изменить время напоминания",
    "btn__change_whois_length": "Изменить необходимую длину #whois",
    "btn__change_whois_message": "Изменить сообщение для обновления #whois",
    "btn__back": "Назад",
    "btn__change_kick_timeout": "Изменить время до удаления",
    "btn__change_kick_message": "Изменить сообщение после удаления",
    "msg__set_new_welcome_message": "Отправьте новый текст сообщения при входе в чат. Используйте `%USER_MENTION%`, чтобы тегнуть адресата.",
    "msg__set_new_kick_timout": "Отправьте новое время до удаления в минутах",
    "msg__set_new_rewelcome_message": "Отправьте новый текст сообщения при перезаходе в чат. Используйте `%USER_MENTION%`, чтобы тегнуть адресата.",
    "msg__set_new_notify_message": "Отправьте новый текст сообщения напоминания. Используйте `%USER_MENTION%`, чтобы тегнуть адресата.",
    "msg__set_new_sucess_message": "Отправьте новый текст сообщения после представления. Используйте `%USER_MENTION%`, чтобы тегнуть адресата.",
    "msg__set_new_whois_length": "Отправьте новую необходимую длину #whois (количество символов).",
    "msg__set_new_kick_message": "Отправьте новый текст сообщения после удаления. Используйте `%USER_MENTION%`, чтобы тегнуть адресата.",
    "msg__set_new_notify_timeout": "Отправьте новое время до напоминания в минутах.",
    "msg__set_new_whois_message": "Отправьте новый текст сообщения для обновления #whois (должно содержать хэштег #update). Используйте `%USER_MENTION%`, чтобы тегнуть адресата.",
    "msg__get_intro_settings": """
Выбран чат {chat_name}.
---
Сообщение для нового участника чата: `{on_new_chat_member_message}`
---
Сообщение при перезаходе в чат: `{on_known_new_chat_member_message}`
---
Сообщение после успешного представления: `{on_introduce_message}`
---
Сообщение напоминания: `{notify_message}`
---
Необходимая длина представления с хэштегом #whois для новых пользователей: {whois_length}
---
Время до напоминания в минутах (целое положительное число): {notify_timeout}
---
Сообщение для обновления информации в #whois: `{on_introduce_message_update}`
""",
    "msg__get_kick_settings": """
Выбран чат {chat_name}.
---
Время до удаления в минутах (целое положительное число): {kick_timeout}
---
Сообщение после удаления: `{on_kick_message}`
""",
    "msg__short_whois": "%USER\_MENTION%, напишите про себя побольше, хотя бы {whois_length} символов. Спасибо!",
    "msg__skip_new_chat_member": "%SKIP%",
}

def escape_markdown(text):
    """
    Escapes special characters in a Markdown string to prevent Markdown rendering issues,
    excluding text within curly brackets.
    
    Args:
        text (str): The input string that may contain special Markdown characters.
        
    Returns:
        str: A string with special Markdown characters escaped, excluding text within curly brackets.
    """
    # Regex to find text outside curly brackets
    def escape_outside_braces(match):
        text_outside = match.group(1)
        if text_outside:
            # Escape special characters in text outside curly brackets
            special_characters = r"([\\`*_{}\[\]()#+\-.!|>~^])"
            return re.sub(special_characters, r"\\\1", text_outside)
        return match.group(0)
    
    # Match and process text outside curly brackets
    escaped_text = re.sub(r"([^{}]+(?=\{)|(?<=\})([^{}]+)|^[^{]+|[^}]+$)", escape_outside_braces, text)
    return escaped_text

def _(text):
    """
    Retrieve and escape a predefined message text based on a unique key.
    
    Args:
        text (str): A unique key representing the desired message.
        
    Returns:
        str: The escaped message text associated with the input key, or None if not found.
    """
    return _texts.get(text)
    # if raw_message is not None:
    #     return escape_markdown(raw_message)
    # return None
