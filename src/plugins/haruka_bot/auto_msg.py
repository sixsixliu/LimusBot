from nonebot import on_command, on_message
from nonebot.adapters import Bot
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Message, GroupMessageEvent
from nonebot.permission import SUPERUSER
from .utils import to_me, get_path, scheduler
from tinydb import TinyDB, Query
import time
import random


d_lim = TinyDB(get_path('temp.json'), encoding='utf-8').table("d_lim")
limqq = Bot.config.limqq
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
                await repeat.finish(Message(msg))
        else:
            repeat_msg_dict[groupid] = [msg, 1]
    else:
        repeat_msg_dict[groupid] = [msg, 1]


# 每日每个群捕捉一次lim
catch_lim = on_message(priority=5)
@catch_lim.handle()
async def catch_lim_fun(bot: Bot, event: GroupMessageEvent, state: T_State):
    q = Query()
    if event.get_user_id() == str(limqq):
        if not(d_lim.contains(q.groupid == event.group_id) and d_lim.get(q.groupid == event.group_id)['d'] is True):
            msg = "[CQ:reply,id=" + str(event.message_id) + "]" + \
                  "莉姆🤤嘿嘿.......莉姆🤤嘿嘿......莉姆🤤嘿嘿.......莉姆🤤嘿嘿......莉姆🤤嘿嘿.......莉姆🤤嘿嘿......"
            if not d_lim.contains(q.groupid == event.group_id):
                d_lim.insert({'groupid': event.group_id, 'd': True})
            else:
                d_lim.update({'groupid': event.group_id, 'd': True})
            await catch_lim.finish(Message(msg))


# 5点重置dlim
@scheduler.scheduled_job('cron', hour='5', minute='0', id='clear_d_times')
async def clear_d_times():
    d_lim.update({'d': False})


# 晚安语音
good_night = on_command('晚安', rule=to_me(), priority=5)
@good_night.handle()
async def send_good_night(bot: Bot, event: GroupMessageEvent, state: T_State):
    hour = time.localtime().tm_hour
    if hour >= 22 or hour <= 2:
        message = event.sender.card + "，晚安。"
        message = Message('[CQ:tts,text=' + str(message) + ']')
        await good_night.finish(message)
    elif 17 <= hour < 22:
        message = "才" + str(hour - 12) + "点。"
        message = Message('[CQ:tts,text=' + str(message) + ']')
        await good_night.finish(message)


# 群友发消息时随机戳一戳
poke = on_message(priority=5)
@poke.handle()
async def random_poke(bot: Bot, event: GroupMessageEvent, state: T_State):
    if random.random() < 0.01:
        message = Message('[CQ:poke,qq=' + str(event.get_user_id()) + ']')
        time.sleep(10)
        await poke.finish(message)
