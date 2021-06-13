[![LimusBot](https://socialify.git.ci/sixsixliu/LimusBot/image?description=1&descriptionEditable=%E5%9F%BA%E4%BA%8EHarukaBot%E5%BC%80%E5%8F%91%E7%9A%84%E4%B9%90%E5%AD%90q%E7%BE%A4bot&font=Inter&forks=1&issues=1&logo=https%3A%2F%2Fi0.hdslb.com%2Fbfs%2Fface%2F44658dc2c46868a7e96d68d03eb3bf5cc811b2b4.jpg&owner=1&pattern=Floating%20Cogs&stargazers=1&theme=Light)](https://space.bilibili.com/664047468/)


名称来源：[@莉姆丝OvO](https://space.bilibili.com/664047468)

[![qq group](https://img.shields.io/badge/%E7%B2%89%E4%B8%9D%E7%BE%A4-1056356647-ff69b4)](https://qm.qq.com/cgi-bin/qm/qr?k=FKJxrfNNqHIHu-zpD-s7YDoyvZfnjhDP&amp;jump_from=webapi)
[![qq group](https://img.shields.io/badge/%E7%B2%89%E4%B8%9D%E7%BE%A4-599594424-ff69b4)](https://qm.qq.com/cgi-bin/qm/qr?k=pdseITovTpDBhBLPJ8t4fa1QqN8tNEOz&amp;jump_from=webapi)

## 简介

[HarukaBot](https://github.com/SK-415/HarukaBot)是一款将哔哩哔哩UP主的直播与动态信息推送至QQ的机器人，但缺乏传统群聊机器人的娱乐功能

LimusBot在其基础上做了修改，增加了如随机色图、复读机等功能

## 功能介绍

> HarukaBot的原有功能请参见[其项目README](https://github.com/SK-415/HarukaBot/blob/master/README.md)

- **随机色图、随机夸图、随机影图**：通过关键词匹配方式发送指定目录下的随机图片，关键词及目录在配置文件中设置

- **色图请求量记录**：记录了当天每个群员索取色图的次数，以及bot运行以来的总次数

- **复读机**：检测到群内复读次数超过5，则发送一条相同消息（有几率打断复读）

- **捕捉lim**：每日捕捉群内lim的第一条消息，并回复，可替换成其他qq

- **代发消息**：超级管理员通过指令私聊bot，bot会代发送消息到指定群，就不用来回切账号了

- **代发语音消息**：通过qq的tts将代发的文字转为语音发送

- **晚安语音条**：对bot说晚安会得到一句念出你群昵称的晚安语音条

- **发送秀图**：将随机色图以秀图方式发送出来

- **随机戳一戳**：群员说话小概率对其戳一戳

- **每日一d**：开启后每天发送一个随机vtuber的介绍 _(数据来源[vtbs.moe](https://github.com/dd-center/vtbs.moe))_

- **每日精选图**：群员回复发过的图可以增加其评分，精选图功能开启后每日24时以大图模式发送当天评分最高的图

## 后续计划

- 随机每日lim
- 随机lim语音条
- 发送色图请求量统计到群
- 刚发过的色图会降低随机权重
- 色图好坏反馈机制并影响随机权重
- 随机触发事件 如不定期发送消息
- 超级管理员在群内开启火力全开模式，如色图雨、播放五字母之歌等

## 特别感谢

- [`go-cqhttp`](https://github.com/Mrs4s/go-cqhttp)：整挺好

- [`NoneBot2`](https://github.com/nonebot/nonebot2)：整也挺好

- [`HarukaBot`](https://github.com/SK-415/HarukaBot)：整确实挺好

- [`vtbs.moe`](https://github.com/dd-center/vtbs.moe)：整得真的挺好

## 支持与贡献

关注[莉姆丝](https://space.bilibili.com/664047468)就是对我最好的支持
