from django.http import JsonResponse
from django.shortcuts import render
# import mysql.connector
import random
import numpy as np
import pandas as pd
# from . import data_run
# from . import cal_flow
from TidalLane.models import tidallane
def runoob(request):
    context = {}
    context['hello'] = 'Hello World!'
    return render(request, 'hello.html', context)



def index(request):
    context = {}
    return render(request, 'index.html', context)


def rundata():
    # data_run.init()
    # oldvolume = []
    # for _ in range(24):
    #     oldvolume.append([400, 400, 400, 400])
    # data_run.run_data(2, 2, oldvolume)
    # data_run.run_data(2, 2, oldvolume, 1)
    # cal_flow.cal_flow()
    return JsonResponse({'message': 'operation is done'})


def getdata():
    # mydb = mysql.connector.connect(
    #     host="localhost",
    #     user="root",
    #     password="111111",
    #     database="trafficmanager"
    # )
    # cursor = mydb.cursor()
    #
    # delete_query = '''
    #                 TRUNCATE TABLE traffic_volume;
    #                 '''
    # cursor.execute(delete_query)
    # delete_query = '''
    #                     TRUNCATE TABLE orginal_car;
    #                     '''
    # cursor.execute(delete_query)
    #
    # # 设置随机种子以确保结果的可复现性
    # np.random.seed()
    #
    #
    # # 生成24小时的时间序列
    # hours = pd.date_range("00:00", "23:00", freq="H")
    # # 理论最大车流：单车道最大545，
    # hourly_traffic = {
    #     0: (100, 100),
    #     1: (150, 150),
    #     2: (150, 150),
    #     3: (300, 200),
    #     4: (400, 200),
    #     5: (400, 200),
    #     6: (500, 300),
    #     7: (600, 300),
    #     8: (800, 300),
    #     9: (600, 300),
    #     10: (300, 400),
    #     11: (100, 200),
    #     12: (500, 800),
    #     13: (800, 900),
    #     14: (300, 200),
    #     15: (500, 800),
    #     16: (500, 700),
    #     17: (500, 600),
    #     18: (500, 800),
    #     19: (300, 900),
    #     20: (200, 300),
    #     21: (100, 200),
    #     22: (200, 150),
    #     23: (100, 150)
    # }
    #
    # # 创建空列表来存储车流量数据
    # traffic_data = []
    #
    # # 填充每个小时的车流量数据
    # for hour, (in_traffic, out_traffic) in hourly_traffic.items():
    #     volume1 = np.random.randint(in_traffic, in_traffic + 100)
    #     volume2 = np.random.randint(out_traffic, out_traffic + 100)
    #     time = hours[hour].strftime('%Y-%m-%d %H:%M:%S')
    #     traffic_data.append((time, volume1, volume2))
    #
    # for data in traffic_data:
    #     insert_query = '''
    #                         INSERT INTO traffic_volume (time, volume1, volume2)
    #                         VALUES (%s, %s, %s)
    #                         '''
    #     cursor.execute(insert_query, data)
    # mydb.commit()
    #
    # # 生成数据方式：根据车流量数据进行生成，然后调整各个车辆的到达时间
    # # 用一个列表存储时间数据，同时使用
    # query = "SELECT * FROM traffic_volume"
    # # 执行查询
    # cursor.execute(query)
    # datas = cursor.fetchall()
    #
    # for data in datas:
    #     noise = random.randint(0, 50)
    #     proportion = 0
    #     # if data[0].hour >7 and data[0].hour < 8:
    #     #     proportion = (data[1]+data[2])//4
    #     # elif data[0].hour >17 and data[0].hour < 19:
    #     #     proportion = (data[1]+data[2])*3//4
    #
    #     for i in range(data[1] + noise):
    #         arrivetime = data[0].replace(second=random.randint(0, 59), minute=random.randint(0, 59))
    #         speed = random.randint(15, 18)
    #         direct = 'N'
    #         sql = "INSERT INTO orginal_car ( arrivetime, speed, direct) VALUES (%s, %s, %s)"
    #         val = (arrivetime, speed, direct)
    #
    #         # 执行插入语句
    #         cursor.execute(sql, val)
    #         print(f"{cursor.rowcount} 条记录插入成功。")
    #     for i in range(data[2] + noise):
    #         arrivetime = data[0].replace(second=random.randint(0, 59), minute=random.randint(0, 59))
    #         speed = random.randint(15, 18)
    #         direct = 'S'
    #         sql = "INSERT INTO orginal_car ( arrivetime, speed, direct) VALUES (%s, %s, %s)"
    #         val = (arrivetime, speed, direct)
    #         # 执行插入语句
    #         cursor.execute(sql, val)
    #         print(f"{cursor.rowcount} 条记录插入成功。")
    #
    #     # 提交到数据库
    # mydb.commit()
    # cursor.close()
    # mydb.close()
    return JsonResponse({'message': 'operation is done'})

def getTidal(request):
    traffic_data = tidallane.objects.all().order_by("arrivetime")
    times = [data.time for data in traffic_data]
    original_traffic = [data.ori_volume for data in traffic_data]
    tidal_traffic = [data.tid_volume for data in traffic_data]
    return JsonResponse({
        "labels":times,
        "original_traffic":original_traffic,
        "tidal_traffic":tidal_traffic,
    })
