from nonebot import on_command, on_message, on_notice
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp import Bot, Message, GroupMessageEvent, Event, PrivateMessageEvent
from .utils import to_me, get_path, scheduler
from tinydb import TinyDB, Query
import time
import random


available_times = TinyDB(get_path('available_times.json'), encoding='utf-8').table("ghs_times")
sign_history = TinyDB(get_path('available_times.json'), encoding='utf-8').table("sign_history")

ghs_reward = on_message(priority=5)
@ghs_reward.handle()
async def reward(bot: Bot, event: GroupMessageEvent, state: T_State):
    rand = random.random()
    if rand < 0.01:
        qqid = event.user_id
        if not str(qqid) in bot.config.superusers:
            q = Query()
            if not available_times.contains(q.qqid == qqid):
                available_times.insert({'qqid': qqid, 'times': 10})
            else:
                available_times.update({'qqid': qqid, 'times': available_times.get(q.qqid == qqid)['times'] + 10},
                                       q.qqid == qqid)
            message = f'[CQ:at,qq={qqid}]运气太好了，奖励你10张色图，快发指令召唤吧'
            await ghs_reward.finish(Message(message))
    # elif rand < 0.1:


sign = on_command("签到", priority=4)
@sign.handle()
async def qiandao(bot: Bot, event: GroupMessageEvent, state: T_State):
    qqid = event.user_id
    q = Query()
    message = f'[CQ:reply,id={str(event.message_id)}]'
    if not sign_history.contains(q.qqid == qqid):
        times = random.randint(1, 6)
        if not available_times.contains(q.qqid == qqid):
            available_times.insert({'qqid': qqid, 'times': times})
        else:
            available_times.update({'qqid': qqid, 'times': available_times.get(q.qqid == qqid)['times'] + times},
                                   q.qqid == qqid)
        message += f'签到成功，获得{times}张色图，快发指令召唤吧'
        sign_history.insert({'qqid': qqid})
    else:
        message += '签到过了捏'
    await sign.finish(Message(message))


# 0点重置签到
@scheduler.scheduled_job('cron', hour='0', minute='0', id='clear_qd_times')
async def clear_qd_times():
    TinyDB(get_path('available_times.json'), encoding='utf-8').drop_table("sign_history")
