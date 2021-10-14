import asyncio
import socketio
import logging
import subprocess
import time
import os
import json
from pathlib import Path

version = "Automatic 1.0"
interval = 20
save_position = "/home/automatic/log"
date = time.strftime("%Y-%m-%d", time.localtime())

sio = socketio.AsyncClient()


def runShell(command):
    return subprocess.run(command, stdout=subprocess.PIPE, shell=True, encoding="utf-8").stdout


def showData():
    ip = runShell("ifconfig | grep inet")
    UUID = runShell("dmidecode -t system | grep UUID")
    current_time = time.localtime()
    os = runShell("cat /etc/redhat-release")

    nvme_list = runShell("nvme list")
    lscpu = runShell("lscpu")
    lspci = runShell("lspci")
    lspci_vvv = runShell("lspci -vvv")
    lspci_xxx = runShell("lspci -xxx")
    fdisk_l = runShell("fdisk -l")
    dmidecode_bios = runShell("dmidecode -t bios")
    dmidecode_system = runShell("dmidecode -t system")
    dmidecode_baseboard = runShell("dmidecode -t baseboard")
    dmidecode_processor = runShell("dmidecode -t processor")
    dmidecode_memory = runShell("dmidecode -t memory")
    cat_cpuinfo = runShell("cat /proc/cpuinfo")

    return dict(ip=ip, UUID=UUID, version=version, current_time=current_time, interval=interval, os=os,
                baseData=dict(nvme_list=nvme_list, lscpu=lscpu, lspci=lspci, lspci_vvv=lspci_vvv, lspci_xxx=lspci_xxx,
                              fdisk_l=fdisk_l, dmidecode_bios=dmidecode_bios, dmidecode_system=dmidecode_system,
                              dmidecode_baseboard=dmidecode_baseboard, dmidecode_processor=dmidecode_processor,
                              dmidecode_memory=dmidecode_memory, cat_cpuinfo=cat_cpuinfo))


def saveData(data, filename):
    save_file = open(save_position + "/" + filename + "_" + date + ".txt", "a+")
    size = os.path.getsize(save_position + "/" + filename + "_" + date + ".txt")
    if size != 0:
        save_file.write("\n")
    save_file.write(json.dumps(data) + "\n")
    save_file.close()


@sio.event
async def connect():
    print('连接成功', sio.sid)
    for file_name in os.listdir(save_position):
        if file_name[:-15] == "failture":

            file = open(save_position + "/" + file_name, "a+")
            file.seek(0, os.SEEK_END)
            position = file.tell()
            line = ''
            while position >= 0:
                file.seek(position)
                next_char = file.read(1)
                if next_char == "\n":
                    if line[::-1] != "":
                        await sio.emit('receive', json.loads(line[::-1]))
                        await sio.sleep(5)
                        file.truncate(position)
                    line = ''
                else:
                    line += next_char
                position -= 1
            await sio.emit('receive', json.loads(line[::-1]))
            file.truncate(position + 1)
            file.close()

            size = os.path.getsize(save_position + "/" + file_name)
            if size == 0:
                os.remove(save_position + "/" + file_name)
            else:
                await sio.emit("receive", {"name": "error", "words": "读取数据发生错误"})


@sio.event
async def send(messageName):
    print("执行send")
    if messageName == "data":
        data = showData()
        data["name"] = messageName
        try:
            data["type"] = "success"
            await sio.emit('receive', data, callback=saveData(data, "all"))
        except Exception:
            data["type"] = "fail"
            saveData(data, "failture")
    if messageName == "error":
        print("error")


@sio.event
async def disconnect():
    print("断开连接")


async def main():
    await sio.connect('http://10.2.134.249:5000')

    async def timing():
        while True:
            await send("data")
            await sio.sleep(10)

    await timing()


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    logger.setLevel(level=logging.INFO)

    handler = logging.FileHandler(save_position + "/" + "log" + "_" + date + ".txt")
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    handler.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)

    logger.addHandler(handler)
    logger.addHandler(console)

    logger.info("程序开始执行")
    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except Exception:
        logger.error("程序执行中发生错误", exc_info=True)
    logger.info("程序执行完毕")
