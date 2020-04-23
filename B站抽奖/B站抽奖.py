"""
    Bilibili视频评论抽奖脚本 V0.1
    Bilibili账号:在英国的哔哩张
    https://space.bilibili.com/195006167
"""

import os
import sqlite3
import json
import random
import re
import time
import urllib
import urllib.request

UserIDs = []
urls = []
luckyDogs = []
CommentUserData = []

#获取所有评论页网址
def getUrls(avid, pageNum):
    i = 0
    while i < int(pageNum):
        urls.append("http://api.bilibili.com/x/v2/reply?jsonp=jsonp&;pn=" + str(i+1) + "&type=1&oid=" + str(avid))
        i = i + 1

#获取网页源码
def getPage(url):
    html = urllib.request.urlopen(url)
    content = html.read().decode("utf-8")
    return content

# 将 JSON 对象转换为 Python 字典
def json_to_dict(data_json):
    data_dict = json.loads(data_json)
    return data_dict
    
#获取所有回复用户ID
def getUserID(allData):
    vidData = allData['data']['replies']
    for CommentData in vidData:
        UserID = CommentData['mid']
        UserIDs.append(UserID)

#获取评论信息
def getReplyInfo():
    conn = sqlite3.connect("Replies_bilibili.db")
    c = conn.cursor()
    for url in urls:
        for reply in json_to_dict(getPage(url))['data']['replies']:
            CommentUserData.append(reply['member'])

#获取av号
def getVid():
    vid = input("请输入AV/BV号：")
    searchBV = re.search('BV',vid)
    searchAV = re.search('av',vid,re.I)
    if searchBV:
        vid = (json_to_dict(getPage("https://api.bilibili.com/x/web-interface/view?bvid=" + vid)))['data']['aid']
    elif searchAV:
        vid =(''.join(list(filter(str.isdigit, vid))))
    print(vid)
    return vid

#抽奖
def getLuckyDog(LuckyDogNum):
    random.shuffle(UserIDs)
    return UserIDs[0:int(LuckyDogNum)]

#创建数据库
def createDB():
    conn = sqlite3.connect("Replies_bilibili.db")
    print("数据库创建成功！")
    c = conn.cursor()
    c.execute('''CREATE TABLE bilibili
    (uid INT PRIMARY KEY NOT NULL，uname TEXT NOT NULL, message TEXT NOT NULL, rpid INT NOT NULL)''')
    conn.commit()
    conn.close()

#删除数据库
def deleteDB():
    DB_path = os.getcwd() + os.sep + "Replies_bilibili.db"
    os.remove(DB_path)
    print("清理缓存成功！")

"""
#获取中奖人信息
def getLuckyDogInfo(luckyDogs):
"""


#主程序
vid = getVid()
pageNum = input("请输入评论的页数：")
LuckyDogNum = input("请输入抽奖的人数: ")
getUrls(vid, pageNum)
luckyDogs = getLuckyDog(LuckyDogNum)
print(luckyDogs)
