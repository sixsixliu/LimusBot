from nonebot import on_command, on_notice
from nonebot.adapters.cqhttp import Bot, Event, GroupDecreaseNoticeEvent
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp.permission import GROUP_ADMIN, GROUP_OWNER

from .bilireq import BiliReq
from .config import Config
from .utils import permission_check, to_me
from .version import __version__


add_uid = on_command('添加主播', rule=to_me() & permission_check, priority=5)

@add_uid.handle()
async def get_args(bot: Bot, event: Event, state: dict):
    args = str(event.message).strip()
    if args:
        state['uid'] = args

@add_uid.got('uid', prompt='请输入主播的 uid')
async def _(bot: Bot, event: Event, state: dict):
    uid = state['uid']
    with Config(event) as config:
        await add_uid.finish(await config.add_uid(uid))


delete_uid = on_command('删除主播', rule=to_me() & permission_check, priority=5)

@delete_uid.handle()
async def get_args(bot: Bot, event: Event, state: dict):
    args = str(event.message).strip()
    if args:
        state['uid'] = args

@delete_uid.got('uid', prompt='请输入主播的 uid')
async def _(bot: Bot, event: Event, state: dict):
    uid = state['uid']
    with Config(event) as config:
        await delete_uid.finish(await config.delete_uid(uid))


uid_list = on_command('主播列表', rule=to_me() & permission_check, priority=5)

@uid_list.handle()
async def _(bot: Bot, event: Event, state: dict):
    with Config(event) as config:
        await uid_list.finish(await config.uid_list())


dynamic_on = on_command('开启动态', rule=to_me() & permission_check, priority=5)

@dynamic_on.handle()
async def handle_first_recive(bot: Bot, event: Event, state: dict):
    args = str(event.message).strip()
    if args:
        state['uid'] = args

@dynamic_on.got('uid', prompt='请输入主播的 uid')
async def _(bot: Bot, event: Event, state: dict):
    uid = state['uid']
    with Config(event) as config:
        msg = await config.set('dynamic', uid, True)
    await dynamic_on.finish(msg.replace('name', '开启动态'))


dynamic_off = on_command('关闭动态', rule=to_me() & permission_check, priority=5)

@dynamic_off.handle()
async def handle_first_recive(bot: Bot, event: Event, state: dict):
    args = str(event.message).strip()
    if args:
        state['uid'] = args

@dynamic_off.got('uid', prompt='请输入主播的 uid')
async def _(bot: Bot, event: Event, state: dict):
    uid = state['uid']
    with Config(event) as config:
        msg = await config.set('dynamic', uid, False)
    await dynamic_off.finish(msg.replace('name', '关闭动态'))


live_on = on_command('开启直播', rule=to_me() & permission_check, priority=5)

@live_on.handle()
async def handle_first_recive(bot: Bot, event: Event, state: dict):
    args = str(event.message).strip()
    if args:
        state['uid'] = args

@live_on.got('uid', prompt='请输入主播的 uid')
async def _(bot: Bot, event: Event, state: dict):
    uid = state['uid']
    with Config(event) as config:
        msg = await config.set('live', uid, True)
    await live_on.finish(msg.replace('name', '开启直播'))
    

live_off = on_command('关闭直播', rule=to_me() & permission_check, priority=5)

@live_off.handle()
async def handle_first_recive(bot: Bot, event: Event, state: dict):
    args = str(event.message).strip()
    if args:
        state['uid'] = args

@live_off.got('uid', prompt='请输入主播的 uid')
async def _(bot: Bot, event: Event, state: dict):
    uid = state['uid']
    with Config(event) as config:
        msg = await config.set('live', uid, False)
    await live_off.finish(msg.replace('name', '关闭直播'))


at_on = on_command('开启全体', rule=to_me(), 
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER, 
    priority=5)

@at_on.handle()
async def handle_first_recive(bot: Bot, event: Event, state: dict):
    args = str(event.message).strip()
    if args:
        state['uid'] = args

@at_on.got('uid', prompt='请输入主播的 uid')
async def _(bot: Bot, event: Event, state: dict):
    uid = state['uid']
    with Config(event) as config:
        msg = await config.set('at', uid, True)
    await at_on.finish(msg.replace('name', '开启全体'))


at_off = on_command('关闭全体', rule=to_me(), 
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER, 
    priority=5)

@at_off.handle()
async def handle_first_recive(bot: Bot, event: Event, state: dict):
    args = str(event.message).strip()
    if args:
        state['uid'] = args

@at_off.got('uid', prompt='请输入主播的 uid')
async def _(bot: Bot, event: Event, state: dict):
    uid = state['uid']
    with Config(event) as config:
        msg = await config.set('at', uid, False)
    await at_off.finish(msg.replace('name', '关闭全体'))


permission_on = on_command('开启权限', rule=to_me(), 
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER, 
    priority=5)

@permission_on.handle()
async def _(bot: Bot, event: Event, state: dict):
    with Config(event) as config:
        msg = await config.set_permission(True)
    await permission_on.finish(msg.replace('name', '开启权限'))


func_list = [
    '主播列表', '开启权限', '关闭权限', '添加主播', '删除主播', '开启动态',
    '关闭动态', '开启直播', '关闭直播', '开启全体', '关闭全体', '版本信息']

permission_off = on_command('关闭权限', rule=to_me(), 
    permission=GROUP_OWNER | GROUP_ADMIN | SUPERUSER, 
    priority=5)

@permission_off.handle()
async def _(bot: Bot, event: Event, state: dict):
    with Config(event) as config:
        msg = await config.set_permission(False)
    await permission_on.finish(msg.replace('name', '关闭权限'))

get_version = on_command('版本信息', rule=to_me(), priority=5)

@get_version.handle()
async def _(bot: Bot, event: Event, state: dict):
    message = f"当前 HarukaBot 版本：{__version__}\n" +\
        "\n使用中遇到问题欢迎加群反馈，\n" +\
        "群号：629574472\n" +\
        "\n常见问题：https://www.haruka-bot.live/usage/faq.html\n" +\
        "\n当前刘六六修改的版本：0.4" +\
        "\n有问题直接群里at刘六六反馈"
    await get_version.finish(message)

no_permission = on_command(func_list[0],
    aliases=set(func_list[1:]), rule=to_me(), priority=20)

@no_permission.handle()
async def _(bot: Bot, event: Event, state: dict):
    await permission_on.finish("权限不足，目前只有管理员才能使用")


help = on_command('帮助', rule=to_me(), priority=5)

@help.handle()
async def _(bot: Bot, event: Event, state: dict):
    message = "什么是LimusBot？\n" + \
              "LimusBot由刘六六在HarukaBot基础上修改，增加了新功能的bot\n\n" + \
              "HarukaBot原有功能：\n\n"
    for name in func_list:
        message += name
        if not name.endswith(('列表', '权限', '版本信息')):
            message += " uid"
        message += '、'
    message += "\n命令中的uid需要替换为对应主播的uid，注意是uid不是直播间id\n" + \
        "\n刘六六增加的功能有：\n" + \
        "随机色图\n" + \
        "随机夸图\n" + \
        "随机影图\n" + \
        "（无需@bot 关键词可自行尝试）\n" + \
        "\n后续计划：\n" \
        "增加自动爬虫更新色图、" \
        "刚发过的色图会降低随机权重、" \
        "增加随机每日lim、" \
        "色图请求量统计、" \
        "lim辱骂语音（待定）"
    await help.finish(message)


group_decrease = on_notice(priority=5)

@group_decrease.handle()
async def _(bot: Bot, event: GroupDecreaseNoticeEvent, state: dict):
    if event.self_id == event.user_id:
        event.message_type = 'group'
        c = Config(event)
        await c.delete_push_list()


# login = on_command('测试登录', rule=to_me(), permission=SUPERUSER, 
#     priority=5)

# @login.handle()
# async def _(bot: Bot, event: Event, state: dict):
#     b = BiliReq()
#     await login.send(f"[CQ:image,file=base64://{await b.get_qr()}]")
#     await login.send(str(await b.qr_login()))

