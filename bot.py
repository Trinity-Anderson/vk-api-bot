import vk_api
import time
import sys
import random
import json

import colorama
colorama.init()

def print_box(title, content_lines):
    max_length = max(len(line) for line in content_lines + [title])
    border = '═' * (max_length + 4)
    colors = [
        '',             # без цвета
        '\033[91m',     # красный
        '\033[93m',     # желтый
        '\033[92m',     # зеленый
        '\033[94m',     # синий
        '\033[95m',     # фиолетовый
        '\033[96m',     # голубой
        '\033[97m',     # белый
    ]
    color = random.choice(colors)
    endc = '\033[0m' if color else ''

    print(f"{color}╔{border}╗{endc}")
    print(f"{color}║  {title.center(max_length)}  ║{endc}")
    print(f"{color}╠{border}╣{endc}")
    for line in content_lines:
        print(f"{color}║  {line.ljust(max_length)}  ║{endc}")
    print(f"{color}╚{border}╝{endc}\n")

def подтвердить_выполнение(desc):
    print_box("Подтверждение", [
        f"Вы уверены, что хотите выполнить: {desc}?",
        "1 - Да",
        "0 - Нет"
    ])
    while True:
        resp = input("Введите 1 для подтверждения или 0 для отмены: ").strip()
        if resp == '1':
            return True
        if resp == '0':
            return False
        print("Пожалуйста, введите 1 или 0.")

# Вначале выводим рамку один раз
print_box("Добро пожаловать в VK автоматизатор", [])

# Ввод токена
token = input("Введите ваш токен доступа: ")

# Создаем сессию
try:
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
except Exception as e:
    print(f"Ошибка при создании сессии: {e}")
    sys.exit(1)

def удалить_исходящие_заявки():
    print_box("Удаление исходящих заявок", [])
    try:
        requests = vk.friends.getRequests(out=1, need_viewed=0, suggested=0, count=1000)
        count_requests = requests['count']
        print(f"Найдено исходящих заявок: {count_requests}")
        for user_id in requests['items']:
            try:
                print(f"🔄 Удаляю заявку на user_id: {user_id}")
                vk.friends.delete(user_id=user_id)
                print(f"✔️ Заявка на {user_id} удалена")
                time.sleep(1)
            except vk_api.exceptions.ApiError as e:
                print(f"❌ Ошибка при удалении {user_id}: {e}")
            except Exception as e:
                print(f"❓ Неожиданная ошибка на {user_id}: {e}")
    except Exception as e:
        print(f"Ошибка при получении заявок: {e}")
    print()

def добавить_друзей():
    print_box("Добавление друзей из предложений", [])
    try:
        suggestions = vk.friends.getSuggestions()
        print(f"Получено предложений: {suggestions['count']}")
        print("Имена предложенных друзей:")
        if 'items' in suggestions:
            items = suggestions['items']
        else:
            items = suggestions
        if isinstance(items, list) and items and isinstance(items[0], dict):
            for user in items:
                print(f"{user['first_name']} {user['last_name']}")
        else:
            for name in items:
                print(name)
        for user in items:
            if isinstance(user, dict):
                user_id = user['id']
                try:
                    print(f"⏳ Готовлюсь добавить {user['first_name']} {user['last_name']} (ID: {user_id})")
                    time.sleep(3)
                    vk.friends.add(user_id=user_id)
                    print(f"✔️ {user['first_name']} {user['last_name']} добавлен")
                except vk_api.exceptions.ApiError as e:
                    print(f"❌ Ошибка при добавлении {user['first_name']} {user['last_name']}: {e}")
                except Exception as e:
                    print(f"❓ Неожиданная ошибка при добавлении {user['first_name']} {user['last_name']}: {e}")
    except Exception as e:
        print(f"Ошибка при получении предложений: {e}")
    print()

def отписаться_от_всех_групп():
    print_box("Отписываюсь от всех групп", [])
    try:
        offset = 0
        total = None
        all_group_ids = []
        while True:
            resp = vk.groups.get(offset=offset, count=200)
            items = resp.get('items', [])
            total = resp.get('count', total)
            if not items:
                break
            for g in items:
                if isinstance(g, int):
                    gid = g
                elif isinstance(g, dict):
                    gid = g.get('id')
                else:
                    gid = None
                if gid is not None:
                    all_group_ids.append(gid)
            if total is not None and offset + len(items) >= total:
                break
            offset += len(items)
            time.sleep(0.2)
        print(f"Найдено групп для отписки: {len(all_group_ids)}")
        for gid in all_group_ids:
            try:
                vk.groups.leave(group_id=gid)
                print(f"✔️ Потребитель отписался от группы {gid}")
            except vk_api.exceptions.ApiError as e:
                print(f"❌ Ошибка при отписке от {gid}: {e}")
            except Exception as e:
                print(f"❓ Неожиданная ошибка при отписке от {gid}: {e}")
            time.sleep(0.5)
    except Exception as e:
        print(f"Ошибка при получении списков групп: {e}")
    print()

def удалить_всю_музыку():
    print_box("Удаление всей музыки", [])
    try:
        my_id = vk.users.get()[0]['id']
        offset = 0
        while True:
            resp = vk.audio.get(owner_id=my_id, count=200, offset=offset)
            items = resp.get('items', [])
            if not items:
                break
            for a in items:
                aid = a.get('id')
                owner_id = a.get('owner_id', my_id)
                title = a.get('title', '')
                try:
                    vk.audio.delete(owner_id=owner_id, audio_id=aid)
                    print(f"✔️ Удалена песня: {title} (ID: {aid})")
                except vk_api.exceptions.ApiError as e:
                    print(f"❌ Ошибка удаления '{title}' (ID: {aid}): {e}")
                except Exception as e:
                    print(f"❓ Неожиданная ошибка удаления '{title}' (ID: {aid}): {e}")
                time.sleep(0.2)
            offset += len(items)
    except Exception as e:
        print(f"Ошибка при получении аудио: {e}")
    print()

def поставить_лайки_в_ленте_группы():
    print_box("Поставить лайки в ленте группы", [])
    try:
        group_input = input("Введите URL группы VK или экранное имя (screen_name): ").strip()
        if not group_input:
            print("Не введено. Прерывание.")
            return

        screen_name = group_input
        if 'vk.com/' in group_input:
            screen_name = group_input.split('vk.com/')[-1].split('?')[0]

        resp = vk.utils.resolveScreenName(screen_name=screen_name)
        obj_type = resp.get('type')
        obj_id = resp.get('object_id')
        if obj_type not in ('group', 'public', 'page'):
            print(f"Указанная ссылка относится не к группе (type={obj_type}).")
            return

        group_id = obj_id
        owner_id = -group_id

        wall = vk.wall.get(owner_id=owner_id, count=100, filter='all')
        posts = wall.get('items', [])
        print(f"Найдено постов в группе: {len(posts)} (group_id={group_id})")

        for post in posts:
            post_id = post.get('id')
            if post_id is None:
                continue
            try:
                vk.likes.add(type='post', owner_id=owner_id, item_id=post_id)
                print(f"💙 Лайк поставлен: пост {post_id} в группе {group_id}")
                time.sleep(0.4)
            except vk_api.exceptions.ApiError as e:
                print(f"❌ Ошибка лайка поста {post_id}: {e}")
            except Exception as e:
                print(f"❓ Неожиданная ошибка лайка поста {post_id}: {e}")
    except Exception as e:
        print(f"Ошибка при обработке группы: {e}")
    print()

def поставить_лайки_на_странице_пользователя():
    print_box("Поставить лайки на странице пользователя", [])
    user_input = input("Введите ссылку на профиль или его экранное имя: ").strip()
    if not user_input:
        print("Не введено. Возврат к меню.")
        return
    if 'vk.com/' in user_input:
        sname = user_input.split('vk.com/')[-1].split('?')[0]
    else:
        sname = user_input

    try:
        resp = vk.utils.resolveScreenName(screen_name=sname)
        if not resp:
            print("Не удалось разрешить профиль. Проверьте ввод.")
            return
        obj_type = resp.get('type')
        obj_id = resp.get('object_id')
        if obj_type != 'user':
            print(f"Указанный профиль не является пользователем (тип: {obj_type}).")
            return
        user_id = obj_id
        owner_id = user_id

        # Получаем последние посты пользователя, например, 1-3
        posts = vk.wall.get(owner_id=owner_id, count=3)
        post_items = posts.get('items', [])
        if not post_items:
            print("Постов на стене пользователя нет.")
            return
        for post in post_items:
            post_id = post['id']
            try:
                vk.likes.add(type='post', owner_id=owner_id, item_id=post_id)
                print(f"💙 Лайк поставлен на пост {post_id} этого пользователя.")
                time.sleep(0.5)
            except vk_api.exceptions.ApiError as e:
                print(f"Ошибка при лайке поста {post_id}: {e}")
            except Exception as e:
                print(f"Неожиданная ошибка при лайке поста {post_id}: {e}")
    except Exception as e:
        print(f"Ошибка при разрешении пользователя: {e}")

def убрать_лайки_с_группы():
    print_box("Убрать лайки с постов группы", [])
    try:
        group_input = input("Введите URL группы VK или экранное имя: ").strip()
        if not group_input:
            print("Не введено. Возврат к меню.")
            return
        if 'vk.com/' in group_input:
            sname = group_input.split('vk.com/')[-1].split('?')[0]
        else:
            sname = group_input
        resp = vk.utils.resolveScreenName(screen_name=sname)
        if not resp:
            print("Не удалось разрешить группу.")
            return
        if resp.get('type') not in ('group', 'public', 'page'):
            print("Указано не группа.")
            return
        group_id = resp.get('object_id')
        owner_id = -group_id
        posts = vk.wall.get(owner_id=owner_id, count=100)
        for post in posts.get('items', []):
            post_id = post['id']
            try:
                vk.likes.delete(type='post', owner_id=owner_id, item_id=post_id)
                print(f"✔️ Убран лайк с поста {post_id}")
                time.sleep(0.4)
            except vk_api.exceptions.ApiError as e:
                print(f"Ошибка при удалении лайка с поста {post_id}: {e}")
            except Exception as e:
                print(f"Неожиданная ошибка при удалении лайка с поста {post_id}: {e}")
    except Exception as e:
        print(f"Ошибка: {e}")

def убрать_лайки_с_страницы_пользователя():
    print_box("Убрать лайки с постов пользователя", [])
    user_input = input("Введите ссылку на профиль или его экранное имя: ").strip()
    if not user_input:
        print("Не введено. Возврат к меню.")
        return
    if 'vk.com/' in user_input:
        sname = user_input.split('vk.com/')[-1].split('?')[0]
    else:
        sname = user_input
    try:
        resp = vk.utils.resolveScreenName(screen_name=sname)
        if not resp:
            print("Не удалось разрешить пользователя.")
            return
        if resp.get('type') != 'user':
            print(f"Это не профиль пользователя (тип: {resp.get('type')}).")
            return
        user_id = resp.get('object_id')
        owner_id = user_id
        posts = vk.wall.get(owner_id=owner_id, count=3)
        for post in posts.get('items', []):
            post_id = post['id']
            try:
                vk.likes.delete(type='post', owner_id=owner_id, item_id=post_id)
                print(f"✔️ Убран лайк с поста {post_id}")
                time.sleep(0.4)
            except vk_api.exceptions.ApiError as e:
                print(f"Ошибка при удалении лайка с поста {post_id}: {e}")
            except Exception as e:
                print(f"Неожиданная ошибка при удалении лайка с поста {post_id}: {e}")
    except Exception as e:
        print(f"Ошибка: {e}")

# ---------- НОВЫЕ ФУНКЦИИ ДЛЯ ЭКСПОРТА ----------
def получить_список_диалогов():
    """Получает первые 200 диалогов и возвращает список с информацией для выбора."""
    try:
        convs = vk.messages.getConversations(count=200, extended=1)
        items = convs.get('items', [])
        profiles = convs.get('profiles', [])
        groups = convs.get('groups', [])
        if not items:
            return []

        profiles_dict = {p['id']: p for p in profiles}
        groups_dict = {g['id']: g for g in groups}

        dialog_list = []
        for idx, item in enumerate(items, 1):
            conversation = item.get('conversation', {})
            peer = conversation.get('peer', {})
            peer_id = peer.get('id')
            if peer_id is None:
                continue  # пропускаем диалоги без peer_id

            conv_type = peer.get('type')
            title = ""

            if conv_type == 'user':
                user = profiles_dict.get(peer_id, {})
                title = f"{user.get('first_name', '')} {user.get('last_name', '')}".strip()
                if not title:
                    title = f"Пользователь {peer_id}"
            elif conv_type == 'chat':
                chat_settings = conversation.get('chat_settings', {})
                title = chat_settings.get('title', f"Беседа {peer_id}")
            else:
                title = f"Диалог {peer_id}"

            dialog_list.append({
                'number': idx,
                'peer_id': peer_id,
                'title': title,
                'type': conv_type
            })
        return dialog_list
    except Exception as e:
        print(f"Ошибка при получении списка диалогов: {e}")
        return []

def экспортировать_чат_полностью(peer_id, title):
    """Выгружает все сообщения из диалога peer_id и сохраняет в JSON."""
    print_box("Экспорт чата", [f"Выгружаем все сообщения из диалога: {title}"])
    all_messages = []
    offset = 0
    count_per_request = 200
    retrieved = 0

    try:
        while True:
            history = vk.messages.getHistory(
                peer_id=peer_id,
                count=count_per_request,
                offset=offset,
                extended=1
            )
            items = history.get('items', [])
            if not items:
                break

            # Подготовка данных об отправителях
            profiles = history.get('profiles', [])
            profiles_dict = {p['id']: p for p in profiles}

            for msg in items:
                msg_copy = {
                    'id': msg['id'],
                    'date': msg['date'],
                    'text': msg.get('text', ''),
                    'from_id': msg['from_id'],
                    'peer_id': msg['peer_id'],
                    'attachments': []
                }
                # Информация об отправителе
                sender = profiles_dict.get(msg['from_id'])
                if sender:
                    msg_copy['from_name'] = f"{sender['first_name']} {sender['last_name']}"
                    msg_copy['from_link'] = f"https://vk.com/id{sender['id']}"
                else:
                    msg_copy['from_name'] = f"User {msg['from_id']}"
                    msg_copy['from_link'] = ""

                # Вложения (кратко)
                if 'attachments' in msg:
                    for att in msg['attachments']:
                        att_type = att['type']
                        att_info = {'type': att_type}
                        if att_type == 'photo':
                            sizes = att['photo'].get('sizes', [])
                            if sizes:
                                att_info['url'] = sizes[-1]['url']
                        elif att_type == 'video':
                            att_info['title'] = att['video'].get('title', '')
                            att_info['url'] = f"https://vk.com/video{att['video']['owner_id']}_{att['video']['id']}"
                        elif att_type == 'audio':
                            att_info['title'] = f"{att['audio'].get('artist', '')} - {att['audio'].get('title', '')}"
                        elif att_type == 'doc':
                            att_info['title'] = att['doc'].get('title', '')
                            att_info['url'] = att['doc'].get('url', '')
                        elif att_type == 'link':
                            att_info['url'] = att['link'].get('url', '')
                        msg_copy['attachments'].append(att_info)

                all_messages.append(msg_copy)

            retrieved += len(items)
            offset += len(items)
            print(f"Загружено {retrieved} сообщений...")
            time.sleep(0.34)  # задержка для соблюдения лимитов API

            # Если получено меньше, чем запрошено, значит сообщения закончились
            if len(items) < count_per_request:
                break

        if not all_messages:
            print("Сообщений не найдено.")
            return

        # Формируем имя файла
        safe_title = title.replace('/', '_').replace('\\', '_').replace(':', '_')
        filename = f"chat_export_{peer_id}_{safe_title}_{time.strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump({
                'peer_id': peer_id,
                'title': title,
                'export_date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_messages': len(all_messages),
                'messages': all_messages
            }, f, ensure_ascii=False, indent=2)

        print_box("Готово", [f"Экспорт завершён. Сохранено {len(all_messages)} сообщений в файл:", filename])
    except vk_api.exceptions.ApiError as e:
        print(f"Ошибка API при получении сообщений: {e}")
    except Exception as e:
        print(f"Неожиданная ошибка при экспорте: {e}")

def экспорт_чата_интерактивный():
    """Показывает список диалогов, даёт выбрать и экспортирует полностью."""
    print_box("Экспорт чата", ["Получение списка диалогов..."])
    dialogs = получить_список_диалогов()
    if not dialogs:
        print("Нет доступных диалогов. Возврат в меню.")
        return

    # Вывод списка
    print("Ваши диалоги:")
    for d in dialogs:
        print(f"{d['number']}. {d['title']} (peer_id: {d['peer_id']})")

    # Выбор
    while True:
        try:
            choice = input("Введите номер диалога для экспорта (или 0 для отмены): ").strip()
            if choice == '0':
                print("Отмена.")
                return
            idx = int(choice) - 1
            if 0 <= idx < len(dialogs):
                selected = dialogs[idx]
                break
            else:
                print("Неверный номер. Попробуйте снова.")
        except ValueError:
            print("Введите число.")

    # Подтверждение и экспорт
    if подтвердить_выполнение(f"Экспортировать чат '{selected['title']}' (все сообщения)"):
        экспортировать_чат_полностью(selected['peer_id'], selected['title'])
    else:
        print_box("Отмена", ["Операция отменена."])

# ---------- КОНЕЦ НОВЫХ ФУНКЦИЙ ----------

def главное_меню():
    print("Что вы хотите сделать?")
    print("1 - Удалить исходящие заявки")
    print("2 - Посмотреть имена предложенных друзей и добавить их")
    print("3 - Отписаться от всех групп")
    print("4 - Удалить всю музыку")
    print("5 - Поставить лайки в ленте группы")
    print("6 - Поставить лайки на странице пользователя")
    print("7 - Убрать лайки с постов группы")
    print("8 - Убрать лайки с постов пользователя")
    print("9 - Экспортировать чат в JSON")
    print("0 - Выход")
    choice = input("Введите число (0-9): ").strip()
    return choice

# Цикл
while True:
    try:
        choice = главное_меню()
        if choice == '1':
            if подтвердить_выполнение("Удаление исходящих заявок"):
                удалить_исходящие_заявки()
            else:
                print_box("Отмена", ["Операция отменена."])
        elif choice == '2':
            if подтвердить_выполнение("Добавление друзей из предложений"):
                добавить_друзей()
            else:
                print_box("Отмена", ["Операция отменена."])
        elif choice == '3':
            if подтвердить_выполнение("Отписаться от всех групп"):
                отписаться_от_всех_групп()
            else:
                print_box("Отмена", ["Операция отменена."])
        elif choice == '4':
            if подтвердить_выполнение("Удалить всю музыку"):
                удалить_всю_музыку()
            else:
                print_box("Отмена", ["Операция отменена."])
        elif choice == '5':
            if подтвердить_выполнение("Поставить лайки в ленте группы"):
                поставить_лайки_в_ленте_группы()
            else:
                print_box("Отмена", ["Операция отменена."])
        elif choice == '6':
            if подтвердить_выполнение("Поставить лайки на странице пользователя"):
                поставить_лайки_на_странице_пользователя()
            else:
                print_box("Отмена", ["Операция отменена."])
        elif choice == '7':
            if подтвердить_выполнение("Убрать лайки с постов группы"):
                убрать_лайки_с_группы()
            else:
                print_box("Отмена", ["Операция отменена."])
        elif choice == '8':
            if подтвердить_выполнение("Убрать лайки с постов пользователя"):
                убрать_лайки_с_страницы_пользователя()
            else:
                print_box("Отмена", ["Операция отменена."])
        elif choice == '9':
            экспорт_чата_интерактивный()
        elif choice == '0':
            print("Выход. До свидания.")
            break
        else:
            print("Неверный выбор. Попробуйте снова.")
        print()
    except KeyboardInterrupt:
        print("\nПрерывание. Выход.")
        break
