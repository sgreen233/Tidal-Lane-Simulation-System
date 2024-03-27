# 首先存储一个全局时间，根据来车进行时间的变换
from datetime import datetime, timedelta
import mysql.connector
from queue import Queue


def transfer_data(source_queues, target_queues, count=None):
    """从source_queues中平均分配数据到target_queues中"""
    index = 0
    for source_queue in source_queues:
        while not source_queue.empty():
            item = source_queue.get()
            target_queues[index % len(target_queues)].put(item)
            index +=1
            if count is not None and source_queue.qsize() <= count:
                break


# 一共有来两车道去两车道，转化方式是来车道转化为去车道
def run_data(inqueue, outqueue, oldvolumes, tidal = None):

    # 首先是一个等待队列，需要计算时间的
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="111111",
        database="trafficmanager"
    )

    # 道路通行时间和等待时间
    road = [20, 90]

    cursor = mydb.cursor()

    query = "SELECT * FROM orginal_car ORDER BY arrivetime ASC"
    # 执行查询
    cursor.execute(query)

    # 获取所有查询结果
    data = cursor.fetchall()

    carnum = len(data)
    Main_time = data[0][0]

    Passtime = Main_time
    res = []

    # carnum = carnum % 234

    # 队列数量
    queue = []
    pass_times = []
    pass_nums = []
    volumes = []
    for _ in range(inqueue + outqueue):
        queue.append(Queue())
        pass_times.append(0)
        pass_nums.append(0)
        volumes.append(0)

    # 计算得到的实时车流量
    print("carnum", carnum)
    waitcar = 0
    passcar = 0

    hour = 0
    # 如何确定实时车流和固定车流 实时车流，当前出去车的总数/度过的时间
    while waitcar < carnum or passcar < carnum:
        # 在此进行潮汐车道设置，先计算实时车流 顺序，先是入车道，然后是出车道
        #要避免一开始进入循环
        for i in range(inqueue + outqueue):
            pass_times[i] = 0
        if  tidal is not None and waitcar > 1:
            for i in range(inqueue + outqueue):
                volumes[i] = (queue[i].qsize()) * 3600 // 110
                pass_nums[i] = 0
            # 进行调换
            # 计算平均车流差，确定调换的车道
            # 计算调换次数和阈值
            # 进行车道调换，将转化车道空出，平均分配到其他车道，要转化的车道取出一半的数据，放到其他车道中
            mals_in = 0
            mals_out = 0
            for i in range(inqueue):
                mals_in += volumes[i] - oldvolumes[int(hour)][i]
            for i in range(inqueue, inqueue+outqueue):
                mals_out += volumes[i] - oldvolumes[int(hour)][i]
            change_num = 0
            # 预处理信息确定调换车道,减少到mals_in < mals_out 或者另一个车道只有一个的时候
            if mals_in > 0 or mals_out > 0:
                if mals_in/inqueue > mals_out/outqueue:
                    while outqueue > 1 and mals_in/inqueue > mals_out/outqueue:
                        inqueue += 1
                        outqueue -= 1
                        change_num += 1
                else:
                    while inqueue > 1 and mals_in/inqueue < mals_out/outqueue:
                        inqueue -= 1
                        outqueue += 1
                        change_num -= 1
            for q in queue:
                print("qsize：", q.qsize(), end="   ")
            print()
            print("通过车辆：", passcar, end="   ")
            print("时间差:", Passtime.timestamp() - Main_time.timestamp(), end="    ")
            print("Main_time", Main_time)
            # 进行车道调换，将转化车道空出，平均分配到其他车道，要转化的车道取出一半的数据，放到其他车道中
            if change_num > 0:
                in_queue = queue[:inqueue - change_num]
                out_queue = queue[inqueue:inqueue + outqueue]
                change_queue = queue[inqueue - change_num: inqueue]
                transfer_data(change_queue, out_queue)
                total_in_length = sum(queue.qsize() for queue in in_queue)
                transfer_data(in_queue, change_queue, total_in_length//inqueue)
            elif change_num < 0:
                in_queue = queue[:inqueue]
                out_queue = queue[inqueue - change_num:inqueue + outqueue]
                change_queue = queue[inqueue : inqueue - change_num]
                transfer_data(change_queue, in_queue)
                total_in_length = sum(queue.qsize() for queue in in_queue)
                transfer_data(out_queue, change_queue, total_in_length//outqueue)
            print("inqueue, outqueque,change_num", inqueue, outqueue,change_num)
            print("潮汐车道调控")
            for q in queue:
                print("qsize：", q.qsize(), end="   ")
            print()

            print("通过车辆：",passcar, end= "   ")
            print("时间差:",Passtime.timestamp() - Main_time.timestamp(),end="    ")
            print("Main_time",Main_time)


        # 等待时间，车辆入栈
        while waitcar < carnum and data[waitcar][0] < Passtime + timedelta(seconds=road[0]):
            if data[waitcar][2] == 'N':
                min_queue = min(queue[0:inqueue], key=lambda q:q.qsize())
                min_queue.put(data[waitcar])
                waitcar += 1
            elif data[waitcar][2] == 'S':
                min_queue = min(queue[inqueue:inqueue+outqueue], key=lambda q: q.qsize())
                min_queue.put(data[waitcar])
                waitcar += 1





        # 通过时间车辆出栈，并持续走
        for i in range(inqueue + outqueue):
            while (not queue[i].empty() and pass_times[i] < road[0]):
                res.append(list(queue[i].get()))
                pass_nums[i] += 1
                passcar += 1
                pass_times[i] = max((res[-1][0] -Passtime).total_seconds(), pass_times[i])
                pass_times[i] += 30 / res[-1][1]
                res[-1].append(Passtime + timedelta(seconds=pass_times[i]))
                waittime = res[-1][3].timestamp() - res[-1][0].timestamp()
                res[-1].append(waittime)

        hour = Passtime.hour
        Passtime = Passtime + timedelta(seconds=road[0])
        hour = Passtime.hour
        Passtime =Passtime + timedelta(seconds=road[1])

        print("res", len(res))
    index = 0
    for d in res[:200]:
        index+=1
        print(index, d[0], d[1], d[2],d[3])

    # 存储数据
    # delete_query = '''
    #                        TRUNCATE TABLE run_data;
    #                        '''
    # cursor.execute(delete_query)
    sql_insert_query = """
    INSERT INTO run_data (type, arrivetime, speed, direct, passtime, roadwait, roadpass, waittime)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    str = "original"
    if tidal is not None:
        str = "tidal"
    cursor = mydb.cursor()
    for item in res:
        data_tuple = (str,item[0], item[1], item[2], item[3], road[0], road[1], item[4])
        cursor.execute(sql_insert_query, data_tuple)
    mydb.commit()
    cursor.close()
    mydb.close()
# 关闭cursor和连接
oldvolume = []
for _ in range(24):
    oldvolume.append([400, 400, 400, 400])
run_data(2, 2, oldvolume)
run_data(2, 2, oldvolume, 1)





























# def run_data(inqueue, outqueue):
#     global Main_time
#     global carnum
#     global data
#     global road
#
#     Passtime = Main_time
#     res = []
#
#     carnum = carnum % 234
#
#     # 队列数量
#     qins = []
#     qouts = []
#     carin_times = []
#     carout_times = []
#     inpass = []
#     outpass = []
#     involume = []
#     outvolume = []
#     for _ in range(inqueue + outqueue):
#         qins.append(Queue())
#         carin_times.append(0)
#         inpass.append(0)
#         involume.append(0)
#     for _ in range(outqueue):
#         qouts.append(Queue())
#         carout_times.append(0)
#         outpass.append(0)
#
#     # 计算得到的实时车流量和固定车流量
#
#     for _ in range(inqueue+ outqueue):
#         involume.append(0)
#     tidallane = []
#     print("carnum", carnum)
#     waitcar = 0
#     passcar = 0
#
#
#     # 如何确定实时车流和固定车流 实时车流，当前出去车的总数/度过的时间
#     while waitcar < carnum or passcar < carnum:
#
#         # 确定时间和车的数量，确定当前是什么时间
#
#         # 在此进行潮汐车道设置，先计算实时车流 顺序，先是入车道，然后是出车道
#         trafficvolume = (passcar*3600)//(Passtime - Main_time)
#
#
#         while waitcar < carnum and data[waitcar][0] < Passtime + timedelta(seconds=road[0]):
#             if data[waitcar][2] == 'N':
#                 min_queue = min(qins[0:inqueue], key=lambda q:q.qsize())
#                 min_queue.put(data[waitcar])
#                 waitcar += 1
#             elif data[waitcar][2] == 'S':
#                 min_queue = min(qouts[inqueue:outqueue], key=lambda q: q.qsize())
#                 min_queue.put(data[waitcar])
#                 waitcar += 1
#         for i in range(inqueue):
#             carin_times[i] = 0
#         for i in range(outqueue):
#             carout_times[i] = 0
#         # 每个车道两辆可以走，那么可以同时释放4辆车，同时每个时间都需要重新计算，current_time
#         # current_time时间其实是上一辆车走的时间
#         for i in range(inqueue):
#             while (not qins[i].empty() and carin_times[i] < road[0]):
#                 res.append(list(qins[i].get()))
#                 inpass[i] += 1
#                 passcar += 1
#                 carin_times[i] += 30 / res[-1][1]
#                 res[-1][1] = Passtime + timedelta(seconds=carin_times[i])
#
#         for i in range(outqueue):
#             while (not qouts[i].empty() and carout_times[i] < road[0]):
#                 res.append(list(qouts[i].get()))
#                 outpass[i] += 1
#                 passcar += 1
#                 carout_times[i] += 30 / res[-1][1]
#                 res[-1][1] = Passtime + timedelta(seconds=carout_times[i])
#
#         Passtime = Passtime + timedelta(seconds=road[0] + road[1])
#
#     print("res", len(res))
#     index = 0
#     for d in res[:200]:
#         index+=1
#         print(index, d[0], d[1], d[2])