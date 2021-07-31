from nonebot.adapters.cqhttp import Bot, Message, GroupMessageEvent, GROUP_ADMIN, GROUP_OWNER
from .utils import get_path, scheduler
import random
import os
import base64
from tinydb import TinyDB, Query


image_dir = "./src/data/image/"
query_times = TinyDB(get_path('query_times.json'), encoding='utf-8')
query_times_today = query_times.table('today')
query_times_all = query_times.table('all')
other_group_count = 0   # 非lim群请求的色图数量
image_rating = TinyDB(get_path('image_rating.json'), encoding='utf-8')
image_rating_today = image_rating.table('today')
image_rating_all = image_rating.table('all')
image_message = TinyDB(get_path('temp.json'), encoding='utf-8').table("image_message")
image_rating_temp = TinyDB(get_path('temp.json'), encoding='utf-8').table("image_rating_temp")


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
    return "base64://" + str(base64.b64encode(f.read()).decode('ascii')), \
           os.path.join(folder, selected_imgs[0]), os.path.splitext(selected_imgs[0])[0]  # 读取文件内容，转换为base64编码


# 获取指定图片
def get_image(path):
    try:
        path = os.path.join(image_dir, path)
        f = open(path, 'rb')  # 二进制方式打开图文件
    except IOError:
        return None
    else:
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


# 0点删除今日请求记录
@scheduler.scheduled_job('cron', hour='0', minute='0', id='clear_query_times')
async def clear_query_times():
    query_times.drop_table('today')


# 推广lim
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


# 保存图片路径与message_id的对应关系
async def save_image_message_id(image_path, message_id):
    image_message.insert({'image': image_path, 'message': message_id})


# 处理回复事件
async def plus_rating(reply_message, user_id):
    message_id = int(reply_message.split('[CQ:reply,id=')[1].split(']回复本条消息')[0])
    q = Query()
    # 同一条消息同一个人回复只记录一次
    if not image_rating_temp.contains((q.qqid == user_id) & (q.messageid == message_id)):
        image_rating_temp.insert({'qqid': user_id, 'messageid': message_id})
        image_path = str(image_message.get(q.message == message_id)['image'])
        if not image_rating_today.contains(q.image == image_path):
            image_rating_today.insert({'image': image_path, 'rating': 1})
        else:
            image_rating_today.update({'image': image_path,
                                       'rating': image_rating_today.get(q.image == image_path)['rating'] + 1},
                                      q.image == image_path)
        if not image_rating_all.contains(q.image == image_path):
            image_rating_all.insert({'image': image_path, 'rating': 1})
        else:
            image_rating_all.update({'image': image_path,
                                     'rating': image_rating_all.get(q.image == image_path)['rating'] + 1},
                                    q.image == image_path)
