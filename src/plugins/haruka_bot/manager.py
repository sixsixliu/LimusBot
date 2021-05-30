from nonebot import on_command
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Message, GroupMessageEvent, PrivateMessageEvent
from nonebot.adapters.cqhttp.permission import PRIVATE_FRIEND
from nonebot.permission import SUPERUSER
from .utils import to_me, get_path, safe_send
import random
import os
import base64
from tinydb import TinyDB, Query

groupids = [0]
group_id_test = '736346227'
group_id_1 = '1056356647'
group_id_2 = '599594424'
group_id_jz = '849956869'

send_message_1 = on_command('send', rule=to_me(), permission=SUPERUSER, priority=5)
send_message_2 = on_command('', rule=to_me(), permission=SUPERUSER, priority=5)
# temp = TinyDB(get_path('temp.json'), encoding='utf-8')
# send_list = temp.table('send_list')


@send_message_1.handle()
async def get_args(bot: Bot, event: Event, state: T_State):
    if event.__class__ == PrivateMessageEvent:
        args = str(event.get_message()).strip()
        if args:
            global groupids
            if args == '1':
                message = "将发送消息至粉丝1群：{}".format(group_id_1)
                groupids = [group_id_1]
            elif args == '2':
                message = "将发送消息至粉丝2群：{}".format(group_id_2)
                groupids = [group_id_2]
            elif args == 'jz':
                message = "将发送消息至舰长群：{}".format(group_id_jz)
                groupids = [group_id_jz]
            elif args == 'test':
                message = "将发送消息至测试群：{}".format(group_id_test)
                groupids = [group_id_test]
            elif args == 'all':
                message = "将发送消息至所有已配置群"
                groupids = [group_id_1, group_id_2, group_id_jz]
            else:
                message = "将发送消息至群：{}".format(args)
                groupids = [args]
            await send_message_1.finish(Message(message))


@send_message_2.handle()
async def send_msg(bot: Bot, event: Event, state: T_State):
    global groupids
    if len(groupids) > 0:
        message = event.get_message()
        for groupid in groupids:
            if groupid != 0:
                if not str(message) == "cancel":
                    await bot.call_api('send_group_msg', **{
                        'message': message,
                        'group_id': groupid
                    })
        groupids = [0]
