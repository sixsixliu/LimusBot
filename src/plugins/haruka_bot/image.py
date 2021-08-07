from nonebot import on_command, on_keyword, on_message
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from .utils import to_me, is_lim_group, safe_send
from .mirage_tank import make_mirage
from .image_utils import *
import time
import requests


image_keywords = eval(Bot.config.image_keywords)
everyday_image_config = TinyDB(get_path('config.json'), encoding='utf-8').table("everyday_image_config")
ghs_path = './src/data/image/ghs/'


class SendImage:
    def __init__(self, folder, keywords):
        send_image = on_keyword(keywords, priority=4)
        @send_image.handle()
        async def send(bot: Bot, event: GroupMessageEvent, state: T_State):
            if check_query_permission(bot, event):
                message = Message("[CQ:reply,id=" + str(event.message_id) + "]你今天已经请求10张图了 请明天再来吧")
                await send_image.finish(message)
            else:
                base64_img, image_path, image_name = get_random_image(folder)
                message = "[CQ:reply,id=" + str(event.message_id) + "]"
                if image_name.startswith('save'):
                    message += '提供者：' + image_name.split('_-_')[1] + '\n保存者：' + image_name.split('_-_')[2] + '\n'
                message += "回复本条消息可增加此图评分" + f"[CQ:image,file={base64_img}]"
                await save_image_message_id(image_path, event.message_id)
                await counter(bot, event)
                if event.group_id not in bot.config.limgroup:
                    await promotion(bot, event)
                await send_image.finish(Message(message))


for key in image_keywords.keys():
    SendImage(key, image_keywords[key])


rating = on_message(rule=to_me(), priority=5)
@rating.handle()
async def get_rating(bot: Bot, event: GroupMessageEvent, state: T_State):
    if event.reply and '回复本条消息可增加此图评分' in str(event.reply.message):
        await plus_rating(str(event.reply.message), event.user_id)


# 幻影坦克
mirage = on_command('随机幻影坦克', permission=SUPERUSER, priority=5)
@mirage.handle()
async def mirage_tank(bot: Bot, event: GroupMessageEvent, state: T_State):
    path = os.path.join(image_dir, "ghs")
    imgs = []
    for x in os.listdir(path):
        if x.endswith('jpg') or x.endswith('jpeg') or x.endswith('png'):
            imgs.append(x)
    selected_imgs = random.sample(imgs, k=1)
    file1 = os.path.join(path, selected_imgs[0])

    path = os.path.join(image_dir, "yuki")
    imgs = []
    for x in os.listdir(path):
        if x.endswith('jpg') or x.endswith('jpeg') or x.endswith('png'):
            imgs.append(x)
    selected_imgs = random.sample(imgs, k=1)
    file2 = os.path.join(path, selected_imgs[0])
    base64_img = make_mirage(file1, file2)
    message = f"[CQ:image,file={base64_img}]"
    await mirage.finish(Message(message))


# 发送秀图
show_image = on_command('随机社死', rule=to_me(), priority=4)
@show_image.handle()
async def send_show_image(bot: Bot, event: GroupMessageEvent, state: T_State):
    if event.get_user_id() in bot.config.superusers or event.sender.role == "admin" or event.sender.role == "owner":
        base64_img, image_path, image_name = get_random_image("ghs")
        message = f"[CQ:image,file={base64_img},type=show,id=40001]"
        await show_image.finish(Message(message))
    else:
        await show_image.finish("权限不足，目前只有管理员才能使用")


# # 发送色图请求量统计
# ghs_count = on_command('色图统计', rule=to_me(), priority=5)
# @ghs_count.handle()
# async def send_count(bot: Bot, event: Event, state: dict):
#


# 大图模式发送当天评分最高的图
@scheduler.scheduled_job('cron', hour='0', minute='0', id='send_today_top')
async def send_today_top():
    image_list = image_rating_today.all()
    if len(image_list):
        image_list = [dict(i) for i in image_list]
        image_list.sort(key=lambda k: k['rating'], reverse=True)
        # 发送三张评分最高的
        for i in range(min(3, len(image_list))):
            base64_img = get_image(image_list[i]['image'])
            if base64_img is not None:
                message = f"[CQ:cardimage,file={base64_img},source=LimusBot每日精选第{i+1}名，指名人数：{image_list[i]['rating']}]"
                group_list = everyday_image_config.all()
                for group in group_list:
                    if group['status']:
                        await safe_send(group['bot_id'], 'group', group['groupid'], Message(message))
    image_rating.drop_table('today')
    temp.drop_table('image_message')
    temp.drop_table('image_rating_temp')


open_image = on_command('开启每日精选图', rule=to_me(), permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER, priority=5)
@open_image.handle()
async def open_everyday_image(bot: Bot, event: GroupMessageEvent, state: T_State):
    q = Query()
    if not everyday_image_config.contains(q.groupid == event.group_id):
        everyday_image_config.insert({'groupid': event.group_id, 'status': True, 'bot_id': str(event.self_id)})
    else:
        everyday_image_config.update({'groupid': event.group_id, 'status': True, 'bot_id': str(event.self_id)},
                                  q.groupid == event.group_id)
    await open_image.finish('已开启本群每日精选图 将在每日24时发送')


close_image = on_command('关闭每日精选图', rule=to_me(), permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER, priority=5)
@close_image.handle()
async def open_everyday_image(bot: Bot, event: GroupMessageEvent, state: T_State):
    q = Query()
    if not everyday_image_config.contains(q.groupid == event.group_id):
        everyday_image_config.insert({'groupid': event.group_id, 'status': False, 'bot_id': str(event.self_id)})
    else:
        everyday_image_config.update({'groupid': event.group_id, 'status': False, 'bot_id': str(event.self_id)},
                                  q.groupid == event.group_id)
    await close_image.finish('已关闭本群每日精选图')


save_ghs = on_command('保存色图', permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER, priority=5)
@save_ghs.handle()
async def save_ghs_image(bot: Bot, event: GroupMessageEvent, state: T_State):
    if event.reply and event.reply.message:
        message = event.reply.message
        count = 0
        if len(message) == 1 and message[0].type == 'forward':  # 回复消息是转发的
            message = (await bot.call_api(api='get_forward_msg', message_id=message[0].data['id']))['messages']
            for msg in message:
                if '[CQ:image,' in msg['content']:
                    url = msg['content'].split(',url=')[1].split(']')[0]
                    img_path = ghs_path + "save" + str(int(time.time()*1000)) + '_-_' + \
                               str(msg['sender']['nickname']) + '_-_' + \
                               str(event.sender.nickname) + '.jpg'
                    t = requests.get(url)
                    with open(img_path, 'wb')as f:
                        f.write(t.content)
                    f.close()
                    count += 1
        else:   # 回复消息是普通消息
            for msg in message:
                if '[CQ:image,' in str(msg):
                    url = msg.data['url']
                    img_path = ghs_path + "save" + str(int(time.time()*1000)) + '_-_' + \
                               str(event.reply.sender.nickname) + '_-_' + \
                               str(event.sender.nickname) + '.jpg'
                    t = requests.get(url)
                    with open(img_path, 'wb')as f:
                        f.write(t.content)
                    f.close()
                    count += 1
        await save_ghs.finish(f'已保存{count}张色图')


user_query_time = on_command('色图次数', rule=to_me(), priority=5)
@user_query_time.handle()
async def get_user_query_time(bot: Bot, event: GroupMessageEvent, state: T_State):
    qqid = int(event.user_id)
    groupid = int(event.group_id)
    q = Query()
    result_today = query_times_today.get((q.qqid == qqid) & (q.groupid == groupid))
    result_all = query_times_all.get((q.qqid == qqid) & (q.groupid == groupid))
    result_all_group = query_times_all.search(q.qqid == qqid)
    message = "[CQ:reply,id=" + str(event.message_id) + "]"
    if not result_all and not result_today and not result_all_group:
        message += '没有色图请求记录'
    else:
        if result_today:
            message += '今日请求次数：' + str(result_today['times']) + '\n'
        else:
            message += '今日请求次数：0\n'
        if result_all:
            message += '本群请求次数：' + str(result_all['times']) + '\n'
        else:
            message += '本群请求次数：0\n'
        if result_all_group:
            times_all_group = 0
            for i in result_all_group:
                times_all_group += i['times']
            message += '总请求次数：' + str(times_all_group)
        else:
            message += '总请求次数：0'
    await user_query_time.finish(Message(message))


group_query_time = on_command('色图总次数', permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER, rule=to_me(), priority=5)
@group_query_time.handle()
async def get_group_query_time(bot: Bot, event: GroupMessageEvent, state: T_State):
    groupid = int(event.group_id)
    q = Query()
    result_all = query_times_all.search(q.groupid == groupid)
    result_all_group = query_times_all.all()
    message = ''
    if not result_all and not result_all_group:
        message += '没有色图请求记录'
    else:
        if result_all:
            times_all = 0
            for i in result_all:
                times_all += i['times']
            message += '自2021年6月9日以来本群共请求色图' + str(times_all) + '次，'
        else:
            message += '自2021年6月9日以来本群共请求色图0次，'
        if result_all_group:
            times_all_group = 0
            for i in result_all_group:
                times_all_group += i['times']
            message += 'LimusBot加入的所有群共请求色图' + str(times_all_group) + '次。'
        else:
            message += 'LimusBot加入的所有群共请求色图0次。'
    await group_query_time.finish(Message(message))
