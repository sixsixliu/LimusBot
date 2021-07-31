from nonebot import on_command, on_message, on_notice
from nonebot.typing import T_State
from nonebot.permission import SUPERUSER
from nonebot.adapters.cqhttp import Bot, Message, GroupMessageEvent, Event, PrivateMessageEvent
from .utils import to_me, get_path, scheduler
from tinydb import TinyDB, Query
import requests
import json
import time

repeat_msg_dict = {}
keywords_db = TinyDB(get_path('keywords.json'), encoding='utf-8').table("keywords_1")
reply_keywords = keywords_db.all()

# 小作文查重
asoulcnki = on_command('枝网查重', priority=4)
@asoulcnki.handle()
async def check_duplicate(bot: Bot, event: GroupMessageEvent, state: T_State):
    if event.reply:
        text = str(event.reply.message)
        if len(text) < 10:
            await asoulcnki.finish('小作文字数太少了捏')
        else:
            data = json.dumps({'text': text})
            headers = {'Content-Type': 'application/json;charset=UTF-8'}
            result_json = requests.post(url='https://asoulcnki.asia/v1/api/check', data=data, headers=headers).json()
            if result_json['message'] == 'success':
                related = result_json['data']['related']
                if len(related) > 0:
                    message = '[CQ:reply,id=' + str(event.reply.message_id) + ']'
                    message += '枝网查重结果：\n' \
                              '总文字复制比：' + str(round(related[0]['rate']*100, 2)) + '%\n' + \
                              '原文地址：' + related[0]['reply_url'] + \
                              '\n作者：' + related[0]['reply']['m_name'] + \
                              '\n发表时间：' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(related[0]['reply']['ctime']))
                    await asoulcnki.finish(Message(message))
                else:
                    await asoulcnki.finish('没有查到重复小作文捏')
            else:
                await asoulcnki.finish('查重出错了捏')