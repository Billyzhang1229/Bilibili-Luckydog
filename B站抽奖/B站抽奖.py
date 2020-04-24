"""
    Bilibili视频评论抽奖脚本 V0.1
    Bilibili账号:在英国的哔哩张
    https://space.bilibili.com/195006167
"""

import sys
import os
import math
import sqlite3
import webbrowser
import json
import random
import re
import time
import urllib
import urllib.request
LuckyDogNum = 0
urls = []

#验证视频网页是否有效并获取所有评论页网址
def verifyUrl():
    avid = getVid()
    firstPageDict = jsonToDict(getPage("http://api.bilibili.com/x/v2/reply?jsonp=jsonp&;pn=1&type=1&oid=" + str(avid)))
    if firstPageDict['code']== 0:
        print("获取网页中...")
        pageNum = math.ceil(firstPageDict['data']['page']['count'] / firstPageDict['data']['page']['size'])
        i = 0
        while i < int(pageNum):
            urls.append("http://api.bilibili.com/x/v2/reply?jsonp=jsonp&;pn=" + str(i+1) + "&type=1&oid=" + str(avid))
            i = i + 1
        print("获取网页完成！")
    else:
        print("获取视频网页出现异常，请检查输入的AV/BV号是否正确")
        verifyUrl()

#获取网页源码
def getPage(url):
    html = urllib.request.urlopen(url)
    content = html.read().decode("utf-8")
    return content

# 将 JSON 对象转换为 Python 字典
def jsonToDict(data_json):
    data_dict = json.loads(data_json)
    return data_dict

#获取评论信息
def getReplyInfo():
    conn = sqlite3.connect("Replies_bilibili.db")
    c = conn.cursor()
    print ("成功打开数据库！")
    try:
        print("正在写入数据...")
        for url in urls:
            for reply in jsonToDict(getPage(url))['data']['replies']:
                bilibili_uid = str(reply['mid'])
                bilibili_uname = reply['member']['uname']
                bilibili_message = reply['content']['message']
                bilibili_rpid = str(reply['rpid'])
                Bilibili_SQL = "INSERT into bilibili (uid, uname, message, rpid) VALUES (?,?,?,?)"
                insert_tuple = bilibili_uid, bilibili_uname, bilibili_message, bilibili_rpid
                c.execute(Bilibili_SQL, insert_tuple)
                conn.commit()
        conn.close()
    except:
        print("数据库保存失败！")
        conn.close()
        deleteDB()
    else:
        print("数据库保存成功！")

#获取用户ID
def getUserID():
    try:
        ReplyIDs = []
        UserIDs = []
        conn = sqlite3.connect("Replies_bilibili.db")
        c = conn.cursor()
        print ("成功打开数据库！")
        cursor = c.execute("SELECT uid from bilibili")
        print("获取用户ID中...")
        for row in cursor:
            ReplyIDs.append(row[0])
        for ID in ReplyIDs:
            if ID not in UserIDs:
                UserIDs.append(ID)
        conn.close()
    except:
        conn.close()
        print("获取用户ID失败!")
        deleteDB()
    else:
        print("获取用户ID成功！")
        print("成功关闭数据库！")
        return UserIDs


#获取av号
def getVid():
    vid = input("请输入AV/BV号：")
    searchBV = re.search('BV',vid)
    searchAV = re.search('av',vid,re.I)
    if searchBV:
        vid = (jsonToDict(getPage("https://api.bilibili.com/x/web-interface/view?bvid=" + vid)))['data']['aid']
    elif searchAV:
        vid =(''.join(list(filter(str.isdigit, vid))))
    return vid

#抽奖
def getLuckyDog(UserIDs):
    luckyDogs = []
    try:
        i = int(input("请输入抽奖的人数: "))
        if isinstance(i, int) and i >= 1 :
            print("抽奖中...")
            LuckyDogNum = i
            resultList = random.sample(range(0,len(UserIDs)-1),i)
            for num in resultList:
                luckyDogs.append(UserIDs[num])
        else:
            print("请输入有效数字")
            getLuckyDog(UserIDs)
    except:
        print("请输入有效数字")
        getLuckyDog(UserIDs)
    else:
        return luckyDogs
   

#创建数据库
def createDB():
    conn = sqlite3.connect("Replies_bilibili.db")
    c = conn.cursor()
    try:
        c.execute('''CREATE TABLE bilibili
        (uid INT NOT NULL,uname TEXT NOT NULL,message TEXT NOT NULL,rpid INT PRIMARY KEY NOT NULL)''')
        conn.commit()
        conn.close()
    except sqlite3.OperationalError:
        conn.commit()
        conn.close()
        print("发现遗留数据")
        deleteDB()
        createDB()
    else:
        print("数据库创建成功！")

#删除数据库
def deleteDB():
    DB_path = os.getcwd() + os.sep + "Replies_bilibili.db"
    os.remove(DB_path)
    print("清理缓存成功！")


#获取中奖人信息
def getLuckyDogInfo(luckyDogs):
    non_bmp_map = dict.fromkeys(range(0x10000, sys.maxunicode + 1), 0xfffd)
    conn = sqlite3.connect("Replies_bilibili.db")
    c = conn.cursor()
    for luckyDog in luckyDogs:
        c.execute("SELECT uid, uname, message from bilibili where uid=" + str(luckyDog))
        results = c.fetchall()
        for row in results:
            try:
                print("用户ID：", row[0])
                print("用户名：",row[1])
                print("用户评论：",row[2], "\n")
            except UnicodeEncodeError:
                print("用户评论：",row[2].translate(non_bmp_map), "\n")
    sendMessage = input("是否要给中奖用户发送私信: Y/N ")
    trueList = ["Y","y","Yes","yes","是","是的","好"]
    for condition in trueList:
        if sendMessage == condition:
            for u in luckyDogs:
                webbrowser.open("https://message.bilibili.com/#/whisper/mid" + str(u))
            conn.close()
    else:
        conn.close()


#主程序
print("+--------------------------- +")
print("|点击进入Bilibili视频页面     |")
print("|复制BV或者AV号，并粘贴在下方:|")
print("+----------------------------+\n")
verifyUrl()
createDB()
getReplyInfo()
luckyDogs = getLuckyDog(getUserID())
getLuckyDogInfo(luckyDogs)
deleteDB()
input("")
