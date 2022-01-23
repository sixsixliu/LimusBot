import re

from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Message, GroupMessageEvent, Event
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


open_dd = on_command('开启每日一d', rule=to_me(), permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER, priority=4)
@open_dd.handle()
async def open_everyday_dd(bot: Bot, event: GroupMessageEvent, state: T_State):
    q = Query()
    if not everyday_dd_config.contains(q.groupid == event.group_id):
        everyday_dd_config.insert({'groupid': event.group_id, 'd': True, 'bot_id': str(event.self_id)})
    else:
        everyday_dd_config.update({'groupid': event.group_id, 'd': True, 'bot_id': str(event.self_id)},
                                  q.groupid == event.group_id)
    await open_dd.finish('已开启本群每日一d')


close_dd = on_command('关闭每日一d', rule=to_me(), permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER, priority=4)
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
                i = random.randint(0, len(vtb_json)-1)
                vtb = vtb_json[i]
                message = '[CQ:image,file=' + url2base64(vtb['topPhoto']) + ']' + '\n每日一d\n昵称：' + vtb['uname'] + '\n签名：' \
                          + vtb['sign'] + '\n粉丝数：' + str(vtb['follower']) + '\nb站空间：https://space.bilibili.com/' + \
                          str(vtb['mid']) + '/\n' + '[CQ:image,file=' + url2base64(vtb['face']) + ']'
                await safe_send(group['bot_id'], 'group', group['groupid'], Message(message))


# 查牌子
medal = on_command('查牌子', priority=4)
@medal.handle()
async def get_bili_medal(bot: Bot, event: GroupMessageEvent, state: dict):
    args = str(event.message).strip().split(' ')
    if args:
        state['name'] = args[0]
        state['fuzzy'] = False
        if len(args) > 1:
            if args[1] == "模糊":
                state['fuzzy'] = True
        message = "[CQ:reply,id=" + str(event.message_id) + "]"
        await safe_send(bot.self_id, 'group', event.group_id, Message("[CQ:reply,id=" + str(event.message_id) + "]查询较慢请稍等"))
        response = requests.get("https://bili.jjnnnh.website/medal/?querylx=" + ("xzmh" if state['fuzzy'] else "") + "&query=" + state['name'])
        html = response.content.decode("utf-8")
        tr_content = re.findall("<th>开通人</th></tr>(.+?)</table>", html)
        # trs = re.findall()
        if len(tr_content) <= 0:
            message += "没有查到捏"
            await medal.finish(Message(message))
        else:
            trs = re.findall("<tr>(.+?)</tr>", tr_content[0])
            if len(trs) <= 0:
                message += "没有查到捏"
                await medal.finish(Message(message))
            else:
                if state['fuzzy']:
                    message += "查询到以下粉丝牌子：\n"
                    for tr in trs:
                        tds = re.findall("<td>(.+?)</td>", tr)
                        message += "牌子：" + tds[1] + "，up主：" + re.findall(">(.+?)</", tds[3])[0] + "\n"
                else:
                    tds = re.findall("<td>(.+?)</td>", trs[0])
                    message += "开通粉丝牌子" + re.findall(">(.+?)</", tds[1])[0] + "的up主是：" + re.findall(">(.+?)</", tds[3])[0] + "\n"
                message += "\n数据来源：粉丝勋章库 by jjnnnh"
                await medal.finish(Message(message))
