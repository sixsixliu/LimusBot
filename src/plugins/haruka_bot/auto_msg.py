from nonebot import on_command, on_message, on_notice
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp import Bot, Message, GroupMessageEvent, Event, PrivateMessageEvent
from .utils import to_me, get_path, scheduler
from tinydb import TinyDB, Query
import time
import random
import re


repeat_msg_dict = {}
keywords_db = TinyDB(get_path('keywords.json'), encoding='utf-8').table("keywords_1")
reply_keywords = keywords_db.all()

# 复读
repeat = on_message(priority=5)
@repeat.handle()
async def repeat_fun(bot: Bot, event: GroupMessageEvent, state: T_State):
    global repeat_msg_dict
    msg = str(event.get_message())
    groupid = event.group_id
    if groupid in repeat_msg_dict.keys():
        if repeat_msg_dict[groupid][0] == msg:
            repeat_msg_dict[groupid][1] += 1
            # 复读次数大于等于5 则加入复读
            if repeat_msg_dict[groupid][1] >= 5:
                del repeat_msg_dict[groupid]
                if msg == '打断复读！':
                    await repeat.finish('打断打断复读！')
                else:
                    if random.random() > 0.1:
                        await repeat.finish(Message(msg))
                    else:   # 有几率打断复读
                        await repeat.finish('打断复读！')
        else:
            repeat_msg_dict[groupid] = [msg, 1]
    else:
        repeat_msg_dict[groupid] = [msg, 1]


# 晚安语音
good_night = on_command('晚安', rule=to_me(), priority=5)
@good_night.handle()
async def send_good_night(bot: Bot, event: GroupMessageEvent, state: T_State):
    hour = time.localtime().tm_hour
    if hour >= 22 or hour <= 2:
        fil = re.compile(u'[^0-9a-zA-Z\u4e00-\u9fa5.，,。？“”]+', re.UNICODE)
        name = fil.sub(' ', event.sender.card) or fil.sub(' ', event.sender.nickname)
        message = fil.sub(' ', name) + "，晚安。"
        message = Message('[CQ:tts,text=' + str(message) + ']')
        await good_night.finish(message)
    elif 17 <= hour < 22:
        message = "才" + str(hour - 12) + "点。"
        message = Message('[CQ:tts,text=' + str(message) + ']')
        await good_night.finish(message)


# 群友发消息时随机戳一戳 & 随机关键词匹配回复
poke_and_reply = on_message(priority=5)
@poke_and_reply.handle()
async def random_poke(bot: Bot, event: GroupMessageEvent, state: T_State):
    if random.random() < 0.1:
        msg_list = set()
        msg = str(event.get_message())
        for keyword in reply_keywords:
            if re.match(keyword['regex'], msg, re.S):
                msg_list.update(eval(keyword['reply']))
        if len(msg_list) > 0:
            time.sleep(1)
            await poke_and_reply.finish(msg_list.pop())
    if random.random() < 0.006:
        message = Message('[CQ:poke,qq=' + str(event.get_user_id()) + ']')
        time.sleep(10)
        await poke_and_reply.finish(message)


# 获取回复关键词列表
get_all_keywords = on_command('keywords', rule=to_me(), permission=SUPERUSER, priority=4)
@get_all_keywords.handle()
async def get_keywords(bot: Bot, event: Event, state: T_State):
    if event.__class__ == PrivateMessageEvent:
        message = '现有关键词列表：'
        for keyword in reply_keywords:
            message += '\n' + str(keyword.doc_id) + ' ' + keyword['regex'] + ' ' + keyword['reply']
        await get_all_keywords.finish(message)


# 添加关键词  指令：add 正则表达式 [回复语]
add_keywords = on_command('add', rule=to_me(), permission=SUPERUSER, priority=4)
@add_keywords.handle()
async def save_add_keywords(bot: Bot, event: Event, state: T_State):
    if event.__class__ == PrivateMessageEvent:
        args = str(event.get_message()).strip().split(' ')
        if args and len(args) > 1:
            global reply_keywords
            q = Query()
            if keywords_db.contains(q.regex == args[0]):
                keywords = eval(keywords_db.get(q.regex == args[0])['reply'])
                keywords.update(args[1:])
                keywords_db.update({'reply': str(keywords)}, q.regex == args[0])
            else:
                keywords_db.insert({'regex': args[0], 'reply': str(set(args[1:]))})
            keyword = keywords_db.get(q.regex == args[0])
            reply_keywords = keywords_db.all()
            message = '已添加关键词：\n' + str(keyword.doc_id) + ' ' + keyword['regex'] + ' ' + keyword['reply']
            await add_keywords.finish(message)


# 删除关键词  指令：delete [序号]
delete_keywords = on_command('delete', rule=to_me(), permission=SUPERUSER, priority=4)
@delete_keywords.handle()
async def save_delete_keywords(bot: Bot, event: Event, state: T_State):
    if event.__class__ == PrivateMessageEvent:
        args = str(event.get_message()).strip().split(' ')
        if args and len(args) > 0:
            global reply_keywords
            keywords_db.remove(doc_ids=[int(i) for i in args])
            reply_keywords = keywords_db.all()
            message = '现有关键词列表：'
            for keyword in reply_keywords:
                message += '\n' + str(keyword.doc_id) + ' ' + keyword['regex'] + ' ' + keyword['reply']
            await delete_keywords.finish(message)
