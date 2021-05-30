from nonebot import on_command, on_keyword, on_message
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Message, GroupMessageEvent
from .utils import to_me, get_path, safe_send, scheduler
import random
import os
import base64
from tinydb import TinyDB, Query

image_dir = "./src/data/image/"

query_times = TinyDB(get_path('query_times.json'), encoding='utf-8')
query_times_today = query_times.table('today')
query_times_all = query_times.table('all')

ghs = on_keyword({'随机色图', '随机涩图', '来点色图', '来点涩图', '来张色图', '来张涩图', '给张色图', '给张涩图',
                  '色图time', '涩图time'}, priority=5)
aqua = on_keyword({'随机夸图', '来点夸图', '来张夸图', '给张夸图', 'crew', '随机阿夸', '来点阿夸', '来张阿夸',
                   '给张阿夸'}, priority=5)
echo = on_keyword({'随机影图', '来点影图', '来张影图', '给张影图', '口口口', '因为echo很色'}, priority=5)


@ghs.handle()
async def send_ghs(bot: Bot, event: GroupMessageEvent, state: T_State):
    if check_query_permission(bot, event):
        message = Message("[CQ:at,qq={}]你今天已经请求10张图了 请明天再来吧".format(event.get_user_id()))
        await ghs.finish(message)
    else:
        base64_img = get_random_image("ghs")
        message = f"[CQ:image,file={base64_img}]"
        await counter(bot, event)
        await ghs.finish(Message(message))


@aqua.handle()
async def send_ghs(bot: Bot, event: GroupMessageEvent, state: T_State):
    if check_query_permission(bot, event):
        message = Message("[CQ:at,qq={}]你今天已经请求5张图了 请明天再来吧".format(event.get_user_id()))
        await ghs.finish(message)
    else:
        base64_img = get_random_image("aqua")
        message = f"[CQ:image,file={base64_img}]"
        await counter(bot, event)
        await ghs.finish(Message(message))


@echo.handle()
async def send_ghs(bot: Bot, event: GroupMessageEvent, state: T_State):
    if check_query_permission(bot, event):
        message = Message("[CQ:at,qq={}]你今天已经请求5张图了 请明天再来吧".format(event.get_user_id()))
        await ghs.finish(message)
    else:
        base64_img = get_random_image("echo")
        message = f"[CQ:image,file={base64_img}]"
        await counter(bot, event)
        await ghs.finish(Message(message))


# 0点删除今日请求记录
@scheduler.scheduled_job('cron', hour='0', minute='0', id='clear_query_times')
async def clear_query_times():
    query_times.drop_table('today')


# 每日请求色图上限
def check_query_permission(bot: Bot, event: GroupMessageEvent):
    qqid = event.get_user_id()
    q = Query()
    return event.get_user_id() not in bot.config.superusers and query_times_today.contains(q.qqid == qqid) and \
           query_times_today.get(q.qqid == qqid)['times'] >= 10


# 获取目录下的随机图片
def get_random_image(folder):
    path = os.path.join(image_dir, folder)
    imgs = []
    for x in os.listdir(path):
        if x.endswith('jpg') or x.endswith('jpeg') or x.endswith('png'):
            imgs.append(x)
    selected_imgs = random.sample(imgs, k=1)
    f = open(os.path.join(path, selected_imgs[0]), 'rb')  # 二进制方式打开图文件
    return "base64://" + str(base64.b64encode(f.read()).decode('ascii'))  # 读取文件内容，转换为base64编码


# 请求量计数
async def counter(bot: Bot, event: GroupMessageEvent):
    qqid = event.get_user_id()
    q = Query()
    if not event.get_user_id() in bot.config.superusers:
        # 如果不是超级管理员 则计数+1
        if not query_times_today.contains(q.qqid == qqid):
            query_times_today.insert({'qqid': qqid, 'times': 1})
        else:
            query_times_today.update({'qqid': qqid, 'times': query_times_today.get(q.qqid == qqid)['times'] + 1})
        if not query_times_all.contains(q.qqid == qqid):
            query_times_all.insert({'qqid': qqid, 'times': 1})
        else:
            query_times_all.update({'qqid': qqid, 'times': query_times_all.get(q.qqid == qqid)['times'] + 1})
