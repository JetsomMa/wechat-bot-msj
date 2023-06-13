from flask import Flask
from flask import render_template
from flask import request
import subprocess
import time
import os
import base64

app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/execute', methods=['POST'])
def restartWechatJiancai():
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

    if command == 'restart wechat-jiancai':
        if os.path.exists('wechat-jiancai.pid'):
            # 打开文件并读取内容
            with open('wechat-jiancai.pid', 'r') as f:
                pid_str = f.read()
            
            command2 = 'kill -9 ' + pid_str
            # subprocess.run(command2.split(' '))
            os.system(command2)
          
        command3 = 'nohup python wechat-jiancai.py > wechat-jiancai.out 2>&1 &'
        # subprocess.run(command3.split(' '))
        os.system(command3)

        time.sleep(2)
        # 打开照片文件并读取其内容
        with open('QR.png', 'rb') as f:
            photo_data = f.read()

        # 将照片数据转换为Base64编码
        photo_base64 = base64.b64encode(photo_data)

        message = f'重启 wechat-jiancai 成功\n<img src="data:image/jpeg;base64,{photo_base64.decode()}" alt="Photo">'

        return {
            "code": 200,
            "data": {
                "message": message
            },
        }
    elif command == 'restart wechat-msj':
        if os.path.exists('wechat-msj.pid'):
            # 打开文件并读取内容
            with open('wechat-msj.pid', 'r') as f:
                pid_str = f.read()
            
            command2 = 'kill -9 ' + pid_str
            # subprocess.run(command2.split(' '))
            os.system(command2)
          
        command3 = 'nohup python wechat-msj.py > wechat-msj.out 2>&1 &'
        # subprocess.run(command3.split(' '))
        os.system(command3)

        time.sleep(2)
        # 打开照片文件并读取其内容
        with open('QR.png', 'rb') as f:
            photo_data = f.read()

        # 将照片数据转换为Base64编码
        photo_base64 = base64.b64encode(photo_data)

        message = f'重启 wechat-msj 成功\n<img src="data:image/jpeg;base64,{photo_base64.decode()}" alt="Photo">'

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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3013)
