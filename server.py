import html
import json
import os
import sys
import time
import urllib.request
import m3u8
import requests
from multiprocessing import Process, Queue
from Crypto.Cipher import AES
from flask_cors import CORS

from config import headers
from crawler import prepareCrawl
from merge import mergeMp4
from delete import deleteM3u8, deleteMp4
from flask import Flask, jsonify, request

app = Flask(__name__)
CORS(app)

task_queue = Queue()
data_file = "./task.json"


def load_data():
    with open(data_file, "r") as file:
        return json.load(file)


def save_data(data):
    with open(data_file, "w") as file:
        return json.dump(data, file, indent=2)


@app.route("/api/submit", methods=["POST"])
def task():
    data = request.get_json()
    print(f'收到下载请求: {data["code"]}')
    task_queue.put(data)

    persisted = load_data()
    persisted.append(data)
    save_data(persisted)

    result = {"message": "Success"}
    return jsonify(result)


def process_task(task):
    print(f'开始下载: {task["code"]}')
    download_m3u8(
        url=task["url"], code=task["code"], cover=task["cover"], title=get_valid_directory_name(task["title"])
    )
    print(f'结束下载: {task["code"]}')


def task_worker(queue):
    while True:
        if not queue.empty():
            t = queue.get()
            try:
                process_task(t)
                persisted = load_data()
                index = next(
                    (
                        index
                        for index, item in enumerate(persisted)
                        if item["code"] == t["code"]
                    ),
                    None,
                )
                if index is not None:
                    del persisted[index]
                save_data(persisted)
            except Exception as e:
                print("发生错误:", e)
        time.sleep(1)


def start_worker_process():
    worker_process = Process(target=task_worker, args=(task_queue,))
    worker_process.start()

def get_valid_directory_name(directory_name):
    invalid_chars = r'\/:*?"<>|'
    return ''.join(char if char not in invalid_chars else '_' for char in directory_name)

def download_m3u8(url, code, cover, title):
    folder_path = os.path.join(os.getcwd(), "downloads", title)

    if os.path.exists(f"{folder_path}/{code}.mp4"):
        print("番號資料夾已存在, 跳過...", file=sys.stdout)
        return

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    m3u8url = html.unescape(url)
    m3u8url_list = m3u8url.split("/")
    m3u8url_list.pop(-1)
    download_url = "/".join(m3u8url_list)

    m3u8file = os.path.join(folder_path, code + ".m3u8")
    urllib.request.urlretrieve(url, m3u8file)

    # 得到 m3u8 file裡的 URI和 IV
    m3u8obj = m3u8.load(m3u8file)
    m3u8uri = ""
    m3u8iv = ""

    for key in m3u8obj.keys:
        if key:
            m3u8uri = key.uri
            m3u8iv = key.iv

    # 儲存 ts網址 in tsList
    tsList = []
    for seg in m3u8obj.segments:
        tsUrl = download_url + "/" + seg.uri
        tsList.append(tsUrl)

    # 有加密
    if m3u8uri:
        m3u8keyurl = download_url + "/" + m3u8uri  # 得到 key 的網址
        # 得到 key的內容
        response = requests.get(m3u8keyurl, headers=headers, timeout=10)
        contentKey = response.content

        vt = m3u8iv.replace("0x", "")[:16].encode()  # IV取前16位

        ci = AES.new(contentKey, AES.MODE_CBC, vt)  # 建構解碼器
    else:
        ci = ""

    # 刪除m3u8 file
    deleteM3u8(folder_path)

    # 開始爬蟲並下載mp4片段至資料夾
    prepareCrawl(ci, folder_path, tsList)

    # 合成mp4
    mergeMp4(folder_path, tsList, video_name=code)

    # 刪除子mp4
    deleteMp4(folder_path, originFile=code + ".mp4")

    # 取得封面
    cover_name = f"{code}.jpg"
    cover_path = os.path.join(folder_path, cover_name)
    try:
        r = requests.get(cover)
        with open(cover_path, "wb") as cover_fh:
            r.raw.decode_content = True
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:
                    cover_fh.write(chunk)
    except Exception as e:
        print(f"unable to download cover: {e}")


def run():
    start_worker_process()
    app.run(host="0.0.0.0", port=3001)


if __name__ == "__main__":
    persist_data = load_data()
    print("恢复队列，剩余任务数量: ", len(persist_data))
    for i in persist_data:
        task_queue.put(i)

    run()
