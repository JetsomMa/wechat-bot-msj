from flask import Flask
from flask import render_template
from flask import request
import subprocess
import time
import os
import base64

app = Flask(__name__)

WechatServerList = ['jiancai', 'jiancai2', 'msj']

def startWechat(wechatName):
    if os.path.exists(f'{wechatName}.pid'):
        # 打开文件并读取内容
        with open(f'{wechatName}.pid', 'r') as f:
            pid_str = f.read()
        
        command2 = 'kill -9 ' + pid_str
        os.system(command2)
    
    command3 = f'nohup python {wechatName}.py > {wechatName}.out 2>&1 &'
    os.system(command3)

    time.sleep(3)
    # 打开照片文件并读取其内容
    with open('QR.png', 'rb') as f:
        photo_data = f.read()

    # 将照片数据转换为Base64编码
    photo_base64 = base64.b64encode(photo_data)

    message = f'重启 {wechatName} 成功\n<img src="data:image/jpeg;base64,{photo_base64.decode()}" alt="Photo">'
    return message


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/execute', methods=['POST'])
def restartWechatJiancai():
    try:
        data = request.get_json()
        print(data)
        admin = data['admin']
        command = data['command']

        if admin != '19901017':
            return {
                "code": 200,
                "data": {
                    "message": "你不是管理员，无法执行该操作"
                },
            }
        
        if command.startswith("restart"):
            wechatName = command.replace("restart", "").strip()
            if wechatName not in WechatServerList:
                return {
                    "code": 200,
                    "data": {
                        "message": "你输入的微信服务有误"
                    },
                }
            
            message = startWechat(wechatName)

            return {
                "code": 200,
                "data": {
                    "message": message
                },
            }
        
        else:
            if command in WechatServerList:
                wechatName = command
                message = startWechat(wechatName)
                return {
                    "code": 200,
                    "data": {
                        "message": message
                    },
                }

            else:
                output = subprocess.check_output(command.split(' '))

                print(output.decode())

                return {
                    "code": 200,
                    "data": {
                        "message": output.decode()
                    },
                }
    except Exception as e:
        return {
            "code": 500,
            "data": {
                "message": "服务器异常: " + str(e)
            },
        }


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3013)
