from nonebot import on_command, on_keyword, on_message
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from .utils import to_me, is_lim_group, safe_send
from .mirage_tank import make_mirage
from .image_utils import *
from .auto_msg import repeat_msg_dict


image_keywords = eval(Bot.config.image_keywords)
everyday_image_config = TinyDB(get_path('config.json'), encoding='utf-8').table("everyday_image_config")


class SendImage:
    def __init__(self, folder, keywords):
        send_image = on_keyword(keywords, priority=5)
        @send_image.handle()
        async def send(bot: Bot, event: GroupMessageEvent, state: T_State):
            if check_query_permission(bot, event):
                message = Message("[CQ:reply,id=" + str(event.message_id) + "]你今天已经请求10张图了 请明天再来吧")
                await send_image.finish(message)
            else:
                base64_img, image_path = get_random_image(folder)
                message = "[CQ:reply,id=" + str(event.message_id) + "]回复本条消息可增加此图评分" + f"[CQ:image,file={base64_img}]"
                await save_image_message_id(image_path, event.message_id)
                await counter(bot, event)
                if event.group_id not in bot.config.limgroup:
                    await promotion(bot, event)
                del repeat_msg_dict[event.group_id]
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


# 大图模式发送当天评分最高的图
@scheduler.scheduled_job('cron', hour='0', minute='0', id='send_today_top')
async def send_today_top():
    image_list = image_rating_today.all()
    if len(image_list):
        top = image_list[0]
        for image in image_list:
            if image['rating'] > top['rating']:
                top = image
        base64_img = get_image(top['image'])
        message = f"[CQ:cardimage,file={base64_img},source=LimusBot每日精选]"
        group_list = everyday_image_config.all()
        for group in group_list:
            if group['status']:
                await safe_send(group['bot_id'], 'group', group['groupid'], Message(message))
    image_rating.drop_table('today')


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
