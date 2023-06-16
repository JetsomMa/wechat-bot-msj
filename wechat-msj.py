from lib import itchat
from lib.itchat.content import *
from flask import Flask, request
from flask_cors import CORS
import requests
import json
import time
from datetime import datetime
import threading
import queue
import random
import os

# 获取当前进程的ID
pid = os.getpid()
# 将进程ID转换为字符串
pid_str = str(pid)

# 打开文件并写入进程ID
with open('wechat-msj.pid', 'w') as f:
    f.write(pid_str)

chatUrl = 'https://api.mashaojie.cn/api/chat-query'
# chatUrl = 'http://127.0.0.1:3002/api/chat-query'
port = 3012
targetRoom = None
targetRoomName = 'ChatGPT使用交流群'
botName = '@chat'
reply_prefix = '【chat】'
dingUser = None
dingUserName = 'A0000专业防水丁师'

######################## http 服务子线程 ########################
# 创建一个队列对象
httpQueue = queue.Queue()

# http服务子线程的回调函数
def httpCallback(url,  username, chatusername):
    fileUrl = '/home/jetsom/nginx/html/download/images/dalle/' + url.replace('https://download.mashaojie.cn/images/dalle/', '')
    print("开始发送照片: " + url)
    if chatusername:
        itchat.send("开始发送照片: " + url, toUserName=chatusername)
        time.sleep(random.randint(1, 3))  # 随机休眠（1~3）秒，用于防检测机器人
        itchat.send_image(fileDir = fileUrl, toUserName=chatusername)
    else:
        if targetRoom:
            targetRoom.send(f"{username}的画作: {url}")
            time.sleep(random.randint(1, 3))  # 随机休眠（1~3）秒，用于防检测机器人
            targetRoom.send_image(fileDir = fileUrl)
        else:
            print('targetRoom is None')

# http服务子线程
def httpWorker(httpQueue, httpCallback):
    """子线程执行体"""
    app = Flask(__name__)
    CORS(app)

    @app.route('/api/mdj', methods=['POST'])
    def mdj():
        try:
            url = request.json['url']
            print(url)
            username = request.json['username']
            print(username)
            chatusername = request.json['chatusername']
            print(chatusername)

            httpCallback(url,  username, chatusername)  # 调用回调函数，并将数据作为参数传递给它
            
            return 'ok'
        except Exception as e:
            print(e)
            return 'no'
    
    app.run(host='0.0.0.0', port=port)

# 创建一个 Thread 对象，并将 worker 函数、队列对象和回调函数作为参数传递给它
httpThread = threading.Thread(target=httpWorker, args=(httpQueue, httpCallback))
######################## http 服务子线程 结束 ########################

######################## heart 服务子线程 ########################
# 创建一个队列对象
heartQueue = queue.Queue()

# http服务子线程的回调函数
def heartCallback():
    if dingUser:
        dingUser.send("我还活着 (づ｡◕‿◕｡)づ")
    else:
        print('dingUser is None')

# http服务子线程
def heartWorker(heartQueue, httpCallback):
    """子线程执行体"""
    message_flag = True
    while True:
        if datetime.now().strftime('%M') == '00' and message_flag:
            httpCallback()
            message_flag = False
            time.sleep(60)
            message_flag = True
        time.sleep(50)

# 创建一个 Thread 对象，并将 worker 函数、队列对象和回调函数作为参数传递给它
heartThread = threading.Thread(target=heartWorker, args=(heartQueue, heartCallback))
######################## http 服务子线程 结束 ########################

@itchat.msg_register(FRIENDS)
def add_friend(msg):
    # msg.user.verify()
    time.sleep(random.randint(1, 3))  # 随机休眠（1~3）秒，用于防检测机器人
    itchat.add_friend(**msg['Text']) # 该操作会自动将新好友的消息录入，不需要重载通讯录
    userid = msg['RecommendInfo']['UserName']
    time.sleep(random.randint(1, 3))  # 随机休眠（1~3）秒，用于防检测机器人
    itchat.send('您好，很高兴认识您!', userid)  # 给刚交的朋友发送欢迎语句
    # msg.user.send('您好，很高兴认识您!')


@itchat.msg_register(TEXT, isFriendChat=True)
def text_reply(msg):
    initTarget()

    if msg.type != TEXT:
        return
    
    content = msg.text
    querymethod = 'ChatGPT'
    if content.startswith('@chat ') or content.startswith('@mdj '):
        if content.startswith('@mdj '):
            querymethod = '画画'
        content = content.replace('@chat ', '').replace('@mdj ', '')
        finalName = msg.user.RemarkName if msg.user.RemarkName else msg.user.NickName

        username = finalName
        if "-" in finalName:
            splitArray = finalName.split("-")
            if len(splitArray) >= 2:
                telephoneTarget = splitArray[1]
            else:
                telephoneTarget = ''
        else:
            telephoneTarget = ''

        # 自己发的消息，直接忽略
        if(msg.user.UserName == msg.ToUserName):
            username = '马少杰'
            telephone = '18514665919'
            if content == '充值':
                if telephoneTarget:
                    content = '/操作 充值' + telephoneTarget
                else:
                    msg.user.send(f"{reply_prefix} 请先设置充值手机号")
                    return
            elif content == '查询':
                if telephoneTarget:
                    content = '/查询 用户信息' + telephoneTarget
                else:
                    msg.user.send(f"{reply_prefix} 请先设置充值手机号")
                    return
        else:
            telephone = telephoneTarget

        print(f"收到了{username}的消息：{content}")
        data = {
            'prompt': content,
            'username': username,
            'telephone': telephone,
            'querymethod': querymethod,
            'chatusername': msg.user.UserName
        }
        headers = {
            'Content-Type': 'application/json'
        }
        result = requests.post(chatUrl, data=json.dumps(data), headers=headers)

        if querymethod == '画画':
            if result.text == 'error':
                msg.user.send(f"[{content}]的画作结果：画画失败")
            else:
                # fileUrl = '/home/jetsom/nginx/html/download/images/dalle/' + result.text.replace('https://download.mashaojie.cn/images/dalle/', '')
                msg.user.send(f"[{content}]的画作完成！")
                # time.sleep(random.randint(1, 3))  # 随机休眠（1~3）秒，用于防检测机器人
                # msg.user.send_image(fileDir = fileUrl)
                # itchat.send_image(fileDir = fileUrl, toUserName=msg.user.UserName)

        else:
            result_final = f"{content}\n---------------------\n{str(result.text) if isinstance(result.text, str) else json.dumps(result.text)}"
            msg.user.send(result_final)


@itchat.msg_register(TEXT, isGroupChat=True)
def text_reply(msg):
    initTarget()
    roomName = msg.user.NickName
    if(roomName != targetRoomName):
        return
    
    if msg.type != TEXT:
        return
    
    content = msg.text
    querymethod = 'ChatGPT'
    if content.startswith('@chat ') or content.startswith('@mdj '):
        if content.startswith('@mdj '):
            querymethod = '画画'
        finalName = msg.ActualNickName
        print(f"收到了{finalName}的消息：{content}")
        data = {
            'prompt': content.replace('@chat ', ''),
            'username': finalName,
            'telephone': '',
            'querymethod': querymethod,
            'chatusername': msg.user.UserName
        }
        headers = {
            'Content-Type': 'application/json'
        }
        result = requests.post(chatUrl, data=json.dumps(data), headers=headers)

        if querymethod == '画画':
            if result.text == 'error':
                msg.user.send(f"[{content}]的画作结果：画画失败")
            else:
                # fileUrl = '/home/jetsom/nginx/html/download/images/dalle/' + result.text.replace('https://download.mashaojie.cn/images/dalle/', '')
                msg.user.send(f"[{content}]的画作完成！")
                # time.sleep(random.randint(1, 3))  # 随机休眠（1~3）秒，用于防检测机器人
                # msg.user.send_image(fileDir = fileUrl)
                # itchat.send_image(fileDir = fileUrl, toUserName=msg.user.UserName)
        else:
            result_final = f"{content}\n---------------------\n{str(result.text) if isinstance(result.text, str) else json.dumps(result.text)}"
            msg.user.send(result_final)


def initTarget():
    global dingUser, targetRoom, dingUserName, targetRoomName
    if not dingUser:
        dingUsers = itchat.search_friends(nickName=dingUserName)
        if len(dingUsers) > 0:
            dingUser = dingUsers[0]
            print(f"找到了[{dingUserName}]")
    if not targetRoom:
        targetRooms = itchat.search_chatrooms(name=targetRoomName)
        if len(targetRooms) > 0:
            targetRoom = targetRooms[0]
            print(f"找到了[{targetRoomName}]")
    

def loginFinish():
    httpThread.start()
    heartThread.start()
    initTarget()
    print('finish login')


def exit():
    print('exit')

itchat.auto_login(enableCmdQR=2, loginCallback=loginFinish, exitCallback=exit)
itchat.run(True)
