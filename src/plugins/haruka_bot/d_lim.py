from nonebot import on_command, on_message, on_notice
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Message, GroupMessageEvent, Event
from .utils import to_me, get_path, scheduler
from tinydb import TinyDB, Query
import time
import random
import re


d_lim = TinyDB(get_path('temp.json'), encoding='utf-8').table("d_lim")
dynamic_history = TinyDB(get_path('history.json'), encoding='utf-8').table("dynamic_history")
live_history = TinyDB(get_path('history.json'), encoding='utf-8').table("live_history")
limqq = Bot.config.limqq
limuid = Bot.config.limuid
catch_lim_keywords = eval(Bot.config.catch_lim_keywords)


# 每日每个群捕捉一次lim
catch_lim = on_message(priority=5)
@catch_lim.handle()
async def catch_lim_fun(bot: Bot, event: GroupMessageEvent, state: T_State):
    q = Query()
    if event.get_user_id() == str(limqq):
        if not(d_lim.contains(q.groupid == event.group_id) and d_lim.get(q.groupid == event.group_id)['d'] is True):
            msg = "[CQ:reply,id=" + str(event.message_id) + "]" + generate_dlim_message(str(event.get_message()))
            if not d_lim.contains(q.groupid == event.group_id):
                d_lim.insert({'groupid': event.group_id, 'd': True})
            else:
                d_lim.update({'groupid': event.group_id, 'd': True}, q.groupid == event.group_id)
            await catch_lim.finish(Message(msg))


# 5点重置dlim
@scheduler.scheduled_job('cron', hour='5', minute='0', id='clear_d_times')
async def clear_d_times():
    d_lim.update({'d': False})


def generate_dlim_message(lim_msg: str):
    msg_list = []
    q = Query()

    if len(dynamic_history.search(q.uid == str(limuid))) > 0:
        # 上次发动态时间
        last_dynamic = sorted([i.get('time') for i in dynamic_history.search(q.uid == str(limuid))], reverse=True)[0]
        if time.localtime(last_dynamic).tm_mday != time.localtime().tm_mday and time.localtime().tm_hour >= 17:
            # 已经下午5点了且今天没发过动态
            msg_list.append('莉姆今天咋还没发动态捏')

    if len(live_history.search(q.uid == str(limuid))) > 0:
        # 上次直播时间
        last_live = sorted([i.get('time') for i in live_history.search(q.uid == str(limuid))], reverse=True)[0]
        if time.localtime(last_live).tm_yday == time.localtime().tm_yday - 1:
            # 昨天直播过
            msg_list.append('昨天直播辛苦了！')

    if 6 <= time.localtime().tm_hour < 10:
        # 时间在早6到10之间
        msg_list.append('今天咋起这么早')
    elif time.localtime().tm_hour >= 10 and '早' in lim_msg:
        # 10点之后发早安
        msg_list.append('都几点了还早')

    # 上面这些权重高一些所以复制一遍
    msg_list.extend(msg_list)

    for key in catch_lim_keywords.keys():
        if key in lim_msg:
            msg_list.extend(catch_lim_keywords[key])
    return random.choice(msg_list)
