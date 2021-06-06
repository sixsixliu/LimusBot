from nonebot import on_command, on_keyword, on_message
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Message, GroupMessageEvent, GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER
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
        # message = f"[CQ:cardimage,file={base64_img},source=来自LimusBot]"
        await ghs.finish(Message(message))
        await counter(bot, event)


@aqua.handle()
async def send_ghs(bot: Bot, event: GroupMessageEvent, state: T_State):
    if check_query_permission(bot, event):
        message = Message("[CQ:at,qq={}]你今天已经请求10张图了 请明天再来吧".format(event.get_user_id()))
        await ghs.finish(message)
    else:
        base64_img = get_random_image("aqua")
        message = f"[CQ:image,file={base64_img}]"
        # message = f"[CQ:cardimage,file={base64_img},source=来自LimusBot]"
        await ghs.finish(Message(message))
        await counter(bot, event)


@echo.handle()
async def send_ghs(bot: Bot, event: GroupMessageEvent, state: T_State):
    if check_query_permission(bot, event):
        message = Message("[CQ:at,qq={}]你今天已经请求10张图了 请明天再来吧".format(event.get_user_id()))
        await ghs.finish(message)
    else:
        base64_img = get_random_image("echo")
        message = f"[CQ:image,file={base64_img}]"
        # message = f"[CQ:cardimage,file={base64_img},source=来自LimusBot]"
        await ghs.finish(Message(message))
        await counter(bot, event)


# 0点删除今日请求记录
@scheduler.scheduled_job('cron', hour='0', minute='0', id='clear_query_times')
async def clear_query_times():
    query_times.drop_table('today')


# 每日请求色图上限
def check_query_permission(bot: Bot, event: GroupMessageEvent):
    qqid = event.user_id
    groupid = event.group_id
    q = Query()
    return event.get_user_id() not in bot.config.superusers and query_times_today.contains(q.qqid == qqid) and \
           query_times_today.get(q.qqid == qqid and q.groupid == groupid)['times'] >= 10


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
    qqid = event.user_id
    groupid = event.group_id
    q = Query()
    if not qqid in bot.config.superusers:
        # 如果不是超级管理员 则计数+1
        if not query_times_today.contains(q.qqid == qqid and q.groupid == groupid):
            query_times_today.insert({'qqid': qqid, 'groupid': event.group_id, 'times': 1})
        else:
            query_times_today.update({'qqid': qqid, 'groupid': event.group_id,
                                      'times': query_times_today.get(q.qqid == qqid and q.groupid == groupid)['times'] + 1})
        if not query_times_all.contains(q.qqid == qqid and q.groupid == groupid):
            query_times_all.insert({'qqid': qqid, 'groupid': event.group_id, 'times': 1})
        else:
            query_times_all.update({'qqid': qqid, 'groupid': event.group_id,
                                    'times': query_times_all.get(q.qqid == qqid and q.groupid == groupid)['times'] + 1})


# 发送秀图
show_image = on_command('随机社死', rule=to_me(), priority=5)
@show_image.handle()
async def send_show_image(bot: Bot, event: GroupMessageEvent, state: T_State):
    if event.get_user_id() in bot.config.superusers or event.sender.role == "admin" or event.sender.role == "owner":
        base64_img = get_random_image("ghs")
        message = f"[CQ:image,file={base64_img},type=show,id=40001]"
        await show_image.finish(Message(message))
    else:
        await show_image.finish("权限不足，目前只有管理员才能使用")


# # 发送色图请求量统计
# ghs_count = on_command('色图统计', rule=to_me(), priority=5)
# @ghs_count.handle()
# async def send_count(bot: Bot, event: Event, state: dict):
#