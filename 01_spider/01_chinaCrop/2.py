#coding=utf-8
import requests
import time, json, re
import math
import pymongo

url_root = 'http://www.cgris.net/query/do.php#粮食作物,小麦'
url_data = 'http://www.cgris.net/query/o.php'
session = requests.session()
response = session.get(url_root)

# 初始化请求， 请求作物类别的属性和下拉框的key value 对应关系
r1 = session.post(url_data, data={'action': 'init', 'croptype': ['粮食作物', '小麦'], '_': ''})
result1 = r1.text[r1.text.rfind('>') + 1: len(r1.text)]

time.sleep(2)
#连接Mongo数据库
client = pymongo.MongoClient(host='localhost', port=27017)
db = client.spider
collection = db.chinaCrop

total = 1  # 假设类别下共有1条数据
pageSize = 100  # 每页100个
s = 0  # 当前第几页查询，初始0

# 如果当前页码小于等于总页码，则进行查询，否则跳出循环
while s <= math.floor(total / pageSize):

    # 查询请求， 查询类别下作物总数和当前页码下的作物ID列表
    r2 = session.post(url_data, data={'action': 'query', 'p': {}, 's': s, 'croptype': ['粮食作物', '小麦'], '_': ''})
    # 返回结果去除没用信息
    result2 = r2.text[r2.text.rfind('>') + 1: len(r2.text)]
    # 作物的总数量
    total = int(result2[2: result2.find(',')])
    # 当前页面下的作物ID列表
    tags = re.findall(r"(\d{2})[-](\d{5})", result2)

    # 循环作物列表，分别根据作物ID查询作物的详细信息
    for index in range(len(tags)):
        # 解析作物的ID
        tag_str = tags[index][0] + "-" + tags[index][1]
        # 查询作物的详细信息
        r3 = session.post(url_data, data={'action': 'item', 'p': tag_str, 'croptype': ['粮食作物', '小麦'], '_': ''})
        # 解析返回结果
        item_content = r3.text[r3.text.rfind('>') + 1:len(r3.text)]
        # 组装成json 对象
        item = json.loads(item_content, encoding='utf-8')
        # 插入到数据库
        collection.insert(item)
        # 暂停一秒钟，继续执行下一次循环
        time.sleep(1)

    #页码加1， 查询下100条数据
    s += 1