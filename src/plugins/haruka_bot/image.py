from nonebot import on_command
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

ghs = on_command('随机色图', rule=to_me(), priority=5)
aqua = on_command('随机夸图', rule=to_me(), priority=5)
echo = on_command('随机影图', rule=to_me(), priority=5)


@ghs.handle()
async def send_ghs(bot: Bot, event: GroupMessageEvent, state: T_State):
    qqid = event.get_user_id()
    q = Query()
    if query_times_today.contains(q.qqid == qqid) and query_times_today.get(q.qqid == qqid)['times'] >= 5:
        message = Message("[CQ:at,qq={}]你今天已经请求5张图了 请明天再来吧".format(qqid))
        await ghs.finish(message)
    else:
        path = os.path.join(image_dir, "ghs")
        imgs = []
        for x in os.listdir(path):
            if x.endswith('jpg') or x.endswith('jpeg') or x.endswith('png'):
                imgs.append(x)
        selected_imgs = random.sample(imgs, k=1)
        for img in selected_imgs:
            f = open(os.path.join(path, img), 'rb')  # 二进制方式打开图文件
            base64_img = "base64://" + str(base64.b64encode(f.read()).decode('ascii'))  # 读取文件内容，转换为base64编码
            message = f"[CQ:image,file={base64_img}]"
            message = Message(message)
            if not query_times_today.contains(q.qqid == qqid):
                query_times_today.insert({'qqid': qqid, 'times': 1})
            else:
                query_times_today.update({'qqid': qqid, 'times': query_times_today.get(q.qqid == qqid)['times'] + 1})
            if not query_times_all.contains(q.qqid == qqid):
                query_times_all.insert({'qqid': qqid, 'times': 1})
            else:
                query_times_all.update({'qqid': qqid, 'times': query_times_all.get(q.qqid == qqid)['times'] + 1})
            await ghs.finish(message)


@aqua.handle()
async def send_aqua(bot: Bot, event: GroupMessageEvent, state: T_State):
    qqid = event.get_user_id()
    q = Query()
    if query_times_today.contains(q.qqid == qqid) and query_times_today.get(q.qqid == qqid)['times'] >= 5:
        message = Message("[CQ:at,qq={}]你今天已经请求5张图了 请明天再来吧".format(qqid))
        await aqua.finish(message)
    else:
        path = os.path.join(image_dir, "aqua")
        imgs = []
        for x in os.listdir(path):
            if x.endswith('jpg') or x.endswith('jpeg') or x.endswith('png'):
                imgs.append(x)
        selected_imgs = random.sample(imgs, k=1)
        for img in selected_imgs:
            f = open(os.path.join(path, img), 'rb')  # 二进制方式打开图文件
            base64_img = "base64://" + str(base64.b64encode(f.read()).decode('ascii'))  # 读取文件内容，转换为base64编码
            message = f"[CQ:image,file={base64_img}]"
            message = Message(message)
            if not query_times_today.contains(q.qqid == qqid):
                query_times_today.insert({'qqid': qqid, 'times': 1})
            else:
                query_times_today.update({'qqid': qqid, 'times': query_times_today.get(q.qqid == qqid)['times'] + 1})
            if not query_times_all.contains(q.qqid == qqid):
                query_times_all.insert({'qqid': qqid, 'times': 1})
            else:
                query_times_all.update({'qqid': qqid, 'times': query_times_all.get(q.qqid == qqid)['times'] + 1})
            await aqua.finish(message)


@echo.handle()
async def send_echo(bot: Bot, event: GroupMessageEvent, state: T_State):
    qqid = event.get_user_id()
    q = Query()
    if query_times_today.contains(q.qqid == qqid) and query_times_today.get(q.qqid == qqid)['times'] >= 5:
        message = Message("[CQ:at,qq={}]你今天已经请求5张图了 请明天再来吧".format(qqid))
        await echo.finish(message)
    else:
        path = os.path.join(image_dir, "echo")
        imgs = []
        for x in os.listdir(path):
            if x.endswith('jpg') or x.endswith('jpeg') or x.endswith('png'):
                imgs.append(x)
        selected_imgs = random.sample(imgs, k=1)
        for img in selected_imgs:
            f = open(os.path.join(path, img), 'rb')  # 二进制方式打开图文件
            base64_img = "base64://" + str(base64.b64encode(f.read()).decode('ascii'))  # 读取文件内容，转换为base64编码
            message = f"[CQ:image,file={base64_img}]"
            message = Message(message)
            if not query_times_today.contains(q.qqid == qqid):
                query_times_today.insert({'qqid': qqid, 'times': 1})
            else:
                query_times_today.update({'qqid': qqid, 'times': query_times_today.get(q.qqid == qqid)['times'] + 1})
            if not query_times_all.contains(q.qqid == qqid):
                query_times_all.insert({'qqid': qqid, 'times': 1})
            else:
                query_times_all.update({'qqid': qqid, 'times': query_times_all.get(q.qqid == qqid)['times'] + 1})
            await echo.finish(message)


@scheduler.scheduled_job('cron', hour='0', minute='0', id='clear_query_times')
async def clear_query_times():
    query_times.drop_table('today')
