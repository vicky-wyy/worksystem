import sys
from flask import Flask, request
from flask_socketio import SocketIO
from flask_pymongo import PyMongo

app = Flask(__name__)
app.config['SECRET_KEY'] = 'shuguang'
mongo = PyMongo(app, uri="mongodb://localhost:27017/stone")
socketio = SocketIO(app)


@socketio.on('connect')
def connect():
    print('已连接到ip为{0}客户端'.format(request.remote_addr))


@socketio.on('disconnect')
def disconnect():
    print('客户端断开连接')


@socketio.on('receive')
def receive(message):
    if message["name"] == "data":
        if request.remote_addr == message["ip"].split("\n")[0].strip().split(" ")[1]:  # 判断二者ip是否一致
            print("确认是测试机")
            need_keys = ["name", "ip", "UUID", "current_time", "os", "type", "version", "interval", "baseData"]
            match_times = 0
            for each_key in message.keys():
                for each_value in need_keys:
                    if each_key == each_value:
                        match_times = match_times + 1
            if match_times == len(message.keys()):  # 判断传递数据与所需数据字段是否一致，避免中间篡改
                print("所需字段与传递字段完全匹配")
                if sys.getsizeof(message) <= 104857600:  # 判断传递数据大小是否符合要求，100M
                    print("数据大小符合要求")
                    mongo.db.original.insert_one(message)
                else:
                    print("数据容量过大")
            else:
                print("传递数据可能发生更改")
        else:
            print("测试机IP被篡改")
    if message["name"] == "error":
        print(message["words"])


if __name__ == '__main__':
    socketio.run(app, host='10.2.134.249', port=5000, debug=True)
