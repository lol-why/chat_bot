import vk_api
import json
from datetime import datetime
import os
from pprint import pprint
from random import randint
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

commands = {'!помощь': 'help_b(vk, peer_id)',
            '!кик': 'kick(vk, chat_id, user_id2, peer_id)',
            '!пред': 'warn(vk, peer_id, user_id, user_id2, chat_id)',
            '!разбан': '', '!баннеактив': '',
            '!распред': 'un_warn(vk, peer_id, user_id, user_id2, chat_id)',
            '!мут': '', '!размут': '', '!списокпредов': '',
            '!участник': '', '!повысить': '', '!понизить': '', '!роль': '', '!админы': '',
            '!право': '', '!стата': '', '!правасброс': '', '!неактив': '',
            '!правила': '', '!самобан': '', '!онлайн': '', '!новыеправила': ''}


def main():
    vk_session = vk_api.VkApi(
        token='e5b5de92b44570487dc93fc1a0b75afd63909de12db8d831cba17ac80293898b7fc099c2ac502c011a173')
    longpoll = VkBotLongPoll(vk_session, '204029383')
    for event in longpoll.listen():
        #  получение сообщений из беседы  #
        if event.type == VkBotEventType.MESSAGE_NEW and event.from_chat:
            vk = vk_session.get_api()
            full_mes = event.obj
            message = full_mes['message']
            if not (os.path.exists(f'{message["peer_id"]}.json')):
                reg(message['peer_id'], vk.messages.getConversationMembers(peer_id=message['peer_id'],
                                                                           group_id=event.group_id))
            lol = vk.messages.getConversationMembers(peer_id=2000000001, group_id=204029383)['profiles']
            text = message['text'].split()
            try:
                if text[0] in commands:
                    peer_id = message['peer_id']
                    user_id = str(message['from_id'])
                    chat_id = event.chat_id
                    try:
                        user_id2 = message['reply_message']['from_id']
                    except KeyError:
                        try:
                            user_id2 = int(text[1][3:])
                        except ValueError:
                            user_id2 = (text[1].split('|')[0][3:])
                    user_id2 = str(user_id2)
                    eval(commands[text[0]])
                    # pprint(event.chat_id)
                    # pprint(lol)
                else:
                    pass
            except IndexError:
                try:
                    new_user(message['peer_id'], message['action']['member_id'], message['date'])
                except KeyError:
                    pass


def new_user(peer_id, member_id, date):
    with open(f"{peer_id}.json") as f:
        norm_f = json.load(f)
        dates = datetime.utcfromtimestamp(date).strftime('%Y-%m-%d')
        norm_f['members'][str(member_id)] = {
            'role': 60,
            'join_from': dates,
            'warns': 0,
            'count_messages': 0,
            'last_message': dates
        }
    os.remove(f'{peer_id}.json')
    with open(f'{peer_id}.json', 'w') as f:  # да, это очень большой костыль, да я быдлопе
        json.dump(norm_f, f)
    pass


def reg(peer_id, members):
    file_dump = {'members': {}, 'rules': "", 'laws': {
        "kick": 60,
        "mute": 60,
        "un_mute": 60,
        "warn": 60,
        "un_warn": 60,
        "warn_list": 60,
        "new_rules": 80
    }}
    for i, user in enumerate(members['items']):
        if user['member_id'] < 0:
            continue
        role_ = 60
        try:
            if user['is_admin']:
                role_ = 80
            try:
                if user['is_owner']:
                    role_ = 100
            except KeyError:
                pass
        except KeyError:
            pass

        dates = datetime.utcfromtimestamp(user['join_date']).strftime('%Y-%m-%d')
        file_dump['members'][user['member_id']] = {
            'role': role_,
            'join_from': dates,
            'warns': 0,
            'count_messages': 0,
            'last_message': dates
        }
    with open(f'{peer_id}.json', 'w') as f:
        json.dump(file_dump, f)


def help_b(vk, peer_id):
    vk.messages.send(peer_id=peer_id, message='все команды находятся здесь:'
                                              'https://vk.com/...00',
                     random_id=randint(0, 2 ** 64))
    pass


def kick(vk, chat_id, user_id, peer_id, **kwargs):
    """
    do with vk.messages.removeChatUser
    :return:
    """
    try:
        vk.messages.removeChatUser(chat_id=chat_id, user_id=user_id)
        vk.messages.send(peer_id=peer_id, message=f'здесь больше нет @id{user_id} )))',
                         random_id=randint(0, 2 ** 64))
    except vk_api.exceptions.ApiError:
        vk.messages.send(peer_id=peer_id, message=f'этого пользователя и так нет',
                         random_id=randint(0, 2 ** 64))


def warn(vk, peer_id, user_id, user_id2, chat_id):
    with open(f"{peer_id}.json") as f:
        norm_f = json.load(f)
        member_ = norm_f['members']
        if member_[user_id]['role'] > member_[user_id2]['role']:
            member_[user_id]['warns'] += 1
            if member_[user_id]['warns'] >= 3:
                kick(vk, chat_id, user_id2, peer_id)
            else:
                vk.messages.send(peer_id=peer_id,
                                 message=f'участнику @id{user_id2} было выдано предупреждение, '
                                         f'[{member_[user_id2]["warns"]}/ 3]',
                                 random_id=randint(0, 2 ** 64)

                                 )
    # os.remove(f'{peer_id}.json')
    with open(f"{peer_id}.json", 'w') as f:
        json.dump(norm_f, f)


def un_warn(vk, peer_id, user_id, user_id2, chat_id):
    with open(f"{peer_id}.json") as f:
        norm_f = json.load(f)
        member_ = norm_f['members']
        if member_[user_id]['role'] > member_[user_id2]['role']:
            member_[user_id]['warns'] = 0
            vk.messages.send(peer_id=peer_id,
                             message=f'участнику @id{user_id2} были сняты предупреждения, ',
                             random_id=randint(0, 2 ** 64))

    with open(f"{peer_id}.json", 'w') as f:
        json.dump(norm_f, f)


def ban_inactive():
    pass


def mute():
    pass


def un_mute():
    pass


def warns_list():
    pass


def member():
    pass


def rank_up():
    pass


def rank_down():
    pass


def role():
    pass


def admins():
    pass


def new_laws():
    pass


def default_law():
    pass


def inactive_list():
    pass


def rules():
    pass


def suicide():
    pass


def online():
    pass


def new_rules():
    pass


if __name__ == '__main__':
    main()
