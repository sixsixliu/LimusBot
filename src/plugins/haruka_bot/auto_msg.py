from nonebot import on_command, on_message, on_notice
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Message, GroupMessageEvent, Event
from .utils import to_me, get_path, scheduler
from tinydb import TinyDB, Query
import time
import random
import re


reply_keywords = eval(Bot.config.reply_keywords)
repeat_msg_dict = {}

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
        msg_list = []
        for key in reply_keywords.keys():
            if key in str(event.get_message()):
                msg_list.extend(reply_keywords[key])
        if len(msg_list) > 0:
            time.sleep(1)
            await poke_and_reply.finish(random.choice(msg_list))
    if random.random() < 0.006:
        message = Message('[CQ:poke,qq=' + str(event.get_user_id()) + ']')
        time.sleep(10)
        await poke_and_reply.finish(message)
