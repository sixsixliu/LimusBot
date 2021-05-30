from nonebot import on_command, on_message
from nonebot.adapters import Bot
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Message, GroupMessageEvent
from nonebot.permission import SUPERUSER
from .utils import to_me, get_path, scheduler
from tinydb import TinyDB, Query


d_lim = TinyDB(get_path('temp.json'), encoding='utf-8').table("d_lim")
limqq = '2280883416'
repeat_msg_dict = {}
repeat = on_message(priority=5)
catch_lim = on_message(priority=5)


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
            repeat_msg_dict[groupid] = [msg, 0]
    else:
        repeat_msg_dict[groupid] = [msg, 0]


# 每日每个群捕捉一次lim
@catch_lim.handle()
async def catch_lim_fun(bot: Bot, event: GroupMessageEvent, state: T_State):
    q = Query()
    if event.get_user_id() == limqq:
        if not(d_lim.contains(q.groupid == event.group_id) and d_lim.get(q.groupid == event.group_id)['d'] is True):
            msg = "[CQ:reply,id=" + str(event.message_id) + "]" + \
                  "莉姆🤤嘿嘿.......莉姆🤤嘿嘿......莉姆🤤嘿嘿.......莉姆🤤嘿嘿......莉姆🤤嘿嘿.......莉姆🤤嘿嘿......"
            if not d_lim.contains(q.groupid == event.group_id):
                d_lim.insert({'groupid': event.group_id, 'd': True})
            else:
                d_lim.update({'groupid': event.group_id, 'd': True})
            await catch_lim.finish(Message(msg))


# 0点重置dlim
@scheduler.scheduled_job('cron', hour='0', minute='0', id='clear_d_times')
async def clear_d_times():
    d_lim.update({'d': False})
