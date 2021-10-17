from nonebot import on_command
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp import Event, PrivateMessageEvent
from .utils import to_me
from .image_utils import *
import time
import requests


adjust_rate = 1    # 人工调整系数
limuid = Bot.config.limuid

live_prob = on_command('直播概率', priority=4)
@live_prob.handle()
async def predict_live(bot: Bot, event: Event, state: T_State):
    live_history = TinyDB(get_path('history.json'), encoding='utf-8').table("live_history")
    dynamic_history = TinyDB(get_path('history.json'), encoding='utf-8').table("dynamic_history")
    end_history = TinyDB(get_path('history.json'), encoding='utf-8').table("end_live_history")
    q = Query()
    last_live = sorted([i.get('time') for i in live_history.search(q.uid == str(limuid))], reverse=True)
    last_live = 0 if len(last_live) == 0 else last_live[0]
    last_end = sorted([i.get('time') for i in end_history.search(q.uid == str(limuid))], reverse=True)
    last_end = 0 if len(last_end) == 0 else last_end[0]
    if time.localtime(last_live).tm_yday == time.localtime().tm_yday:
        # 今天直播了就不用判断了
        prob = 1
    elif time.localtime(last_live).tm_yday == time.localtime().tm_yday - 1 and time.localtime(last_end).tm_yday == time.localtime().tm_yday and time.localtime(last_end).tm_hour >= 2:
        # 昨天播到2点之后 则今天必不播
        prob = 0
    else:
        # 节假日影响因子
        holiday_json = requests.get("http://api.haoshenqi.top/holiday?date=" + time.strftime("%Y-%m-%d", time.localtime())).json()
        if holiday_json[0]['status'] == 3:
            holiday_rate = 1
        elif holiday_json[0]['status'] == 2:
            holiday_rate = 0.7
        else:
            holiday_rate = 0.1
        # 是否寒暑假
        if 10 <= time.localtime().tm_yday < 20:
            holiday_rate = max(holiday_rate, 0.6)
        elif 20 <= time.localtime().tm_yday < 40:
            holiday_rate = max(holiday_rate, 1)
        elif 40 <= time.localtime().tm_yday < 50:
            holiday_rate = max(holiday_rate, 0.6)
        elif 180 <= time.localtime().tm_yday < 195:
            holiday_rate = max(holiday_rate, 0.7)
        elif 195 <= time.localtime().tm_yday < 235:
            holiday_rate = max(holiday_rate, 1)
        elif 235 <= time.localtime().tm_yday < 250:
            holiday_rate = max(holiday_rate, 0.7)
        # 是否周六日
        if time.localtime().tm_wday == 5:
            holiday_rate = 1
        elif time.localtime().tm_wday == 6:
            holiday_rate = 0.6
        # 上次直播距今影响因子
        live_rate = min(0.5 + (time.time() - last_live) / 1000000, 1)
        # 今日动态影响因子
        dynamic_rate = 0.9
        last_dynamic = sorted([i.get('time') for i in dynamic_history.search(q.uid == str(limuid))], reverse=True)
        last_dynamic = 0 if len(last_dynamic) == 0 else last_dynamic[0]
        if ((time.localtime(last_dynamic).tm_mday != time.localtime().tm_mday) or
            (time.localtime(last_dynamic).tm_mday == time.localtime().tm_mday and time.localtime(last_dynamic).tm_hour < 6)) and \
                12 <= time.localtime().tm_hour < 20:
            dynamic_rate += (time.time() - time.mktime(time.strptime(time.strftime("%Y-%m-%d", time.localtime()) + " 12:00:00", "%Y-%m-%d %H:%M:%S"))) / 300000
        # 迟到衰减因子
        delay_rate = 1
        if time.localtime().tm_hour >= 21 and adjust_rate <= 1:
            delay_rate = max((2000 - (time.time() - time.mktime(time.strptime(time.strftime("%Y-%m-%d", time.localtime()) + " 21:00:00", "%Y-%m-%d %H:%M:%S")))) / 2000, 0)
        prob = min(max(holiday_rate * live_rate * dynamic_rate * delay_rate * adjust_rate, 0), 1)
    await live_prob.finish(Message("莉姆丝今日直播概率：" + "%.2f%%" % (prob * 100)))


# 私聊bot调整系数
adjust_prob = on_command('setrate', rule=to_me(), permission=SUPERUSER, priority=4)
@adjust_prob.handle()
async def get_manage_args(bot: Bot, event: Event, state: T_State):
    if event.__class__ == PrivateMessageEvent:
        global adjust_rate
        adjust_rate = float(str(event.get_message()))
        await predict_live(bot, event, state)


# 0点重置调整系数
@scheduler.scheduled_job('cron', hour='0', minute='0', id='clear_adjust_rate')
async def clear_adjust_rate():
    global adjust_rate
    adjust_rate = 1


bailan_prob = on_command('摆烂概率', priority=4)
@bailan_prob.handle()
async def predict_bailan(bot: Bot, event: Event, state: T_State):
    await bailan_prob.finish(Message("莉姆丝今日摆烂概率：100%"))
