from lib import itchat
from lib.itchat.content import *
import time
from datetime import datetime
import threading
import queue
from database import getJiancaiConfig
import os

# 获取当前进程的ID
pid = os.getpid()
# 将进程ID转换为字符串
pid_str = str(pid)

# 打开文件并写入进程ID
with open('wechat-jiancai.pid', 'w') as f:
    f.write(pid_str)

jiancaiConfigs = getJiancaiConfig()
if len(jiancaiConfigs) > 0:
    jiancaiConfig = jiancaiConfigs[0]
    keyWords = jiancaiConfig[0].split(",")
    keyWordsNotNeed = jiancaiConfig[1].split(",")
    targetContactName = jiancaiConfig[2]
    blacklist = jiancaiConfig[3].split(",")

    print("keyWords -> ", keyWords)
    print("keyWordsNotNeed -> ", keyWordsNotNeed)
    print("targetContactName -> ", targetContactName)
    print("blacklist -> ", blacklist)

targetContact = None

######################## heart 服务子线程 ########################
# 创建一个队列对象
heartQueue = queue.Queue()

# http服务子线程的回调函数
def heartCallback():
    if targetContact:
        targetContact.send("我还活着 (づ｡◕‿◕｡)づ")
    else:
        print('targetContact is None')

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

def datetimeFormat(timestamp):
    date_time = datetime.fromtimestamp(timestamp)
    return date_time.strftime('%Y-%m-%d %H:%M:%S')

@itchat.msg_register(TEXT, isGroupChat=True)
def text_reply(msg):
    initTarget()
    if msg.type != TEXT:
        return
    
    finalName = msg.ActualNickName
    for blackItem in blacklist:
        if blackItem.lower() in finalName.lower():
            return
    
    content = msg.text

    # 当内容过长，直接过滤
    if(len(content) > 50):
        return
    
    isKeyWords = False
    for keyword in keyWords:
        if keyword.lower() in content.lower():
            isKeyWords = True
            break
    if isKeyWords:
        for keyword in keyWordsNotNeed:
            if keyword.lower() in content.lower():
                isKeyWords = False
                return
            
        roomName = msg.user.NickName
        messageTime = datetimeFormat(msg.CreateTime)
        message = f"群名称：{roomName}\n发消息人：{ finalName }\n消息时间：{ messageTime }\n消息内容：{ content }"
        targetContact.send(message)


def initTarget():
    global targetContact, targetContactName
    if not targetContact:
        targetContacts = itchat.search_friends(nickName=targetContactName)
        if len(targetContacts) > 0:
            targetContact = targetContacts[0]
            print(f"找到了[{targetContactName}]")
    
def loginFinish():
    heartThread.start()
    initTarget()
    print('finish login')

def exit():
    print('-------exit-------')

itchat.auto_login(enableCmdQR=2, loginCallback=loginFinish, exitCallback=exit, hotReload=False)
itchat.run(True)
