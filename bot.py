from os import path

import nonebot
from nonebot.adapters.cqhttp import Bot
from nonebot.log import default_format, logger


nonebot.init()
driver = nonebot.get_driver()
driver.register_adapter('cqhttp', Bot)
app = nonebot.get_asgi()

nonebot.load_builtin_plugins()
nonebot.load_plugin('nonebot_plugin_apscheduler')
nonebot.load_plugins("src/plugins")
nonebot.load_plugin("nonebot_plugin_apscheduler")
nonebot.load_plugin("haruka_bot")

# Modify some config / config depends on loaded configs
# 
# config = nonebot.get_driver().config
# do something...

logger.add(path.join('log', "error.log"),
           rotation="00:00",
           retention='1 week',
           diagnose=False,
           level="ERROR",
           format=default_format,
           encoding='utf-8'
           )
           

if __name__ == "__main__":
    nonebot.run(app="bot:app", reload_dirs="src")
