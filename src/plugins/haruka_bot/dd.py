from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Message, GroupMessageEvent
from nonebot.adapters.cqhttp.permission import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER
from .utils import to_me, get_path, scheduler, safe_send
from tinydb import TinyDB, Query
import random
import requests
import base64


everyday_dd_config = TinyDB(get_path('config.json'), encoding='utf-8').table("everyday_dd_config")


def url2base64(url):
    return "base64://" + str(base64.b64encode(requests.get(url).content).decode('ascii'))


open_dd = on_command('开启每日一d', rule=to_me(), permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER, priority=5)
@open_dd.handle()
async def open_everyday_dd(bot: Bot, event: GroupMessageEvent, state: T_State):
    q = Query()
    if not everyday_dd_config.contains(q.groupid == event.group_id):
        everyday_dd_config.insert({'groupid': event.group_id, 'd': True, 'bot_id': str(event.self_id)})
    else:
        everyday_dd_config.update({'groupid': event.group_id, 'd': True, 'bot_id': str(event.self_id)},
                                  q.groupid == event.group_id)
    await open_dd.finish('已开启本群每日一d')


close_dd = on_command('关闭每日一d', rule=to_me(), permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER, priority=5)
@close_dd.handle()
async def open_everyday_dd(bot: Bot, event: GroupMessageEvent, state: T_State):
    q = Query()
    if not everyday_dd_config.contains(q.groupid == event.group_id):
        everyday_dd_config.insert({'groupid': event.group_id, 'd': False, 'bot_id': str(event.self_id)})
    else:
        everyday_dd_config.update({'groupid': event.group_id, 'd': False, 'bot_id': str(event.self_id)},
                                  q.groupid == event.group_id)
    await close_dd.finish('已关闭本群每日一d')


# 每日一d
@scheduler.scheduled_job('cron', hour='23', minute='0', id='everyday_dd')
async def everyday_dd():
    vtb_json = requests.get("https://api.vtbs.moe/v1/info").json()
    group_list = everyday_dd_config.all()
    if len(vtb_json):
        for group in group_list:
            if group['d']:
                print(group['groupid'])
                i = random.randint(0, len(vtb_json)-1)
                vtb = vtb_json[i]
                message = '[CQ:image,file=' + url2base64(vtb['topPhoto']) + ']' + '\n每日一d\n昵称：' + vtb['uname'] + '\n签名：' \
                          + vtb['sign'] + '\n粉丝数：' + str(vtb['follower']) + '\nb站空间：https://space.bilibili.com/' + \
                          str(vtb['mid']) + '/\n' + '[CQ:image,file=' + url2base64(vtb['face']) + ']'
                await safe_send(group['bot_id'], 'group', group['groupid'], Message(message))
