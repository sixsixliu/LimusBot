from nonebot import on_command
from nonebot.adapters import Bot, Event
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, Message, PrivateMessageEvent
from nonebot.permission import SUPERUSER
from .utils import to_me

groupids = ['0']
mode = 'text'
manage_group_dict = eval(Bot.config.manage_group_dict)

send_message_1 = on_command('send', rule=to_me(), permission=SUPERUSER, priority=5)
send_message_2 = on_command('', rule=to_me(), permission=SUPERUSER, priority=5)


# 给bot私发消息 bot会转发到指定群 指令：send test（发送到测试群）  send test voice（发送语音到测试群）
@send_message_1.handle()
async def get_args(bot: Bot, event: Event, state: T_State):
    if event.__class__ == PrivateMessageEvent:
        args = str(event.get_message()).strip().split(' ')
        if args:
            global groupids
            if args[0] in manage_group_dict.keys():
                message = "将发送消息至{}，群号{}".format(manage_group_dict[args[0]][1], manage_group_dict[args[0]][0])
                groupids = manage_group_dict[args[0]][0]
            else:
                message = "将发送消息至群：{}".format(args[0])
                groupids = [args[0]]
            if len(args) > 1:
                global mode
                mode = args[1]
            await send_message_1.finish(Message(message))


@send_message_2.handle()
async def send_msg(bot: Bot, event: Event, state: T_State):
    global groupids
    global mode
    if len(groupids) > 0:
        message = event.get_message()
        if not str(message) == "cancel":
            if mode == 'voice':
                message = Message('[CQ:tts,text=' + str(message) + ']')
            for groupid in groupids:
                if groupid != '0':
                    await bot.call_api('send_group_msg', **{
                        'message': message,
                        'group_id': groupid
                    })
        mode = 'text'
        groupids = ['0']
