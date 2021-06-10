from nonebot import on_command, on_keyword, on_message
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Message, GroupMessageEvent, GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER
from .utils import to_me, get_path, safe_send, scheduler, is_lim_group
import random
import os
import base64
from tinydb import TinyDB, Query

image_dir = "./src/data/image/"

query_times = TinyDB(get_path('query_times.json'), encoding='utf-8')
query_times_today = query_times.table('today')
query_times_all = query_times.table('all')
other_group_count = 0   # 非lim群请求的色图数量


image_keywords = eval(Bot.config.image_keywords)


class SendImage:
    def __init__(self, folder, keywords):
        send_image = on_keyword(keywords, priority=5)
        @send_image.handle()
        async def send(bot: Bot, event: GroupMessageEvent, state: T_State):
            if check_query_permission(bot, event):
                message = Message("[CQ:reply,id=" + str(event.message_id) + "]你今天已经请求10张图了 请明天再来吧")
                await send_image.finish(message)
            else:
                base64_img = get_random_image(folder)
                message = "[CQ:reply,id=" + str(event.message_id) + f"][CQ:image,file={base64_img}]"
                # message = f"[CQ:cardimage,file={base64_img},source=来自LimusBot]"
                await counter(bot, event)
                if event.group_id not in bot.config.limgroup:
                    await promotion(bot, event)
                await send_image.finish(Message(message))


for key in image_keywords.keys():
    SendImage(key, image_keywords[key])


# 0点删除今日请求记录
@scheduler.scheduled_job('cron', hour='0', minute='0', id='clear_query_times')
async def clear_query_times():
    query_times.drop_table('today')


# 每日请求色图上限
def check_query_permission(bot: Bot, event: GroupMessageEvent):
    qqid = event.user_id
    groupid = event.group_id
    q = Query()
    return str(qqid) not in bot.config.superusers and \
           query_times_today.contains((q.qqid == qqid) & (q.groupid == groupid)) and \
           query_times_today.get((q.qqid == qqid) & (q.groupid == groupid))['times'] >= 10


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
    if not str(qqid) in bot.config.superusers:
        # 如果不是超级管理员 则计数+1
        if not query_times_today.contains((q.qqid == qqid) & (q.groupid == groupid)):
            query_times_today.insert({'qqid': qqid, 'groupid': groupid, 'times': 1})
        else:
            query_times_today.update({'qqid': qqid, 'groupid': groupid,
                                      'times': query_times_today.get((q.qqid == qqid) & (q.groupid == groupid))['times'] + 1},
                                     (q.qqid == qqid) & (q.groupid == groupid))
        if not query_times_all.contains((q.qqid == qqid) & (q.groupid == groupid)):
            query_times_all.insert({'qqid': qqid, 'groupid': groupid, 'times': 1})
        else:
            query_times_all.update({'qqid': qqid, 'groupid': groupid,
                                    'times': query_times_all.get((q.qqid == qqid) & (q.groupid == groupid))['times'] + 1},
                                   (q.qqid == qqid) & (q.groupid == groupid))


# 发送秀图
show_image = on_command('随机社死', rule=to_me() & is_lim_group(), priority=5)
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


async def promotion(bot: Bot, event: GroupMessageEvent):
    global other_group_count
    other_group_count += 1
    # 非lim群发送30张图就推广一次lim
    if other_group_count > 30:
        await bot.call_api('send_group_msg', **{
            'message': "发了这么多色图了，麻烦各位点个关注吧！",
            'group_id': event.group_id
        })
        message = '[CQ:json,data={"app":"com.tencent.structmsg"&#44;"config":{"autosize":true&#44;' \
                  '"ctime":1622947362&#44;"forward":true&#44;"token":"4b43064926a8881bba3a2547dd8ad4e1"&#44;' \
                  '"type":"normal"}&#44;"desc":"新闻"&#44;"extra":{"app_type":1&#44;"appid":100951776&#44;' \
                  '"msg_seq":6970505831977544528&#44;"uin":""}&#44;"meta":{"news":{"action":""&#44;' \
                  '"android_pkg_name":""&#44;"app_type":1&#44;"appid":100951776&#44;"desc":"你感兴趣的视频都在B站"&#44;' \
                  '"jumpUrl":"https://b23.tv/8tU8fQ?share_medium=android&amp;share_source=qq&amp;bbid=97BC6A17-CE5F-4980-8C81-E23467D5C03618604infoc&amp;ts=1622947347467"&#44;' \
                  '"preview":"https://external-30160.picsz.qpic.cn/3572cc74832728cdbdde623efbb3769b/jpg1"&#44;' \
                  '"source_icon":""&#44;"source_url":""&#44;"tag":"哔哩哔哩"&#44;"title":"莉姆丝OvO的个人空间"}}&#44;' \
                  '"prompt":"&#91;分享&#93;莉姆丝OvO的个人空间"&#44;"ver":"0.0.0.1"&#44;"view":"news"}]'
        await bot.call_api('send_group_msg', **{
            'message': Message(message),
            'group_id': event.group_id
        })
        other_group_count = 0
