import mysql.connector
from datetime import datetime, timedelta


mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="111111",
  database="trafficmanager"
)

def cal_flow():



    cursor = mydb.cursor()

    query = "SELECT * FROM run_data WHERE type = 'original' ORDER BY passtime ASC"
    # 执行查询
    cursor.execute(query)
    original_datas = cursor.fetchall()

    query = "SELECT * FROM run_data WHERE type = 'tidal' ORDER BY passtime ASC"
    cursor.execute(query)
    tidal_datas = cursor.fetchall()


    res = []
    passcar = 0
    sumofwait = 0
    print(original_datas)
    Main_time = original_datas[0][5]
    print(original_datas[0])
    print(len(original_datas))
    datalist = [Main_time.replace(hour=0,minute=0,second=0) + timedelta(hours=x) for x in range(0,24)]
    index = 0
    for car in original_datas:
        if index > 23:
            print("car",car)
            break
        if car[5] > datalist[index] + timedelta(hours=1) or passcar >= len(original_datas) - 1:
            arwait = sumofwait//passcar if passcar else 0
            res.append([datalist[index], passcar,arwait])
            passcar = 0
            sumofwait = 0
            index += 1
        else:
            passcar+=1
            sumofwait += car[8]
    index = 0
    passcar = 0
    sumofwait = 0
    for car in tidal_datas:
        if index > 23:
            print("car",car)
            break
        if car[5] > original_datas[0][5]:
            if car[5] > datalist[index] + timedelta(hours=1) or passcar >= len(original_datas) - 1:
                arwait = sumofwait//passcar if passcar else 0
                res[index].append(passcar)
                res[index].append(arwait)
                passcar = 0
                sumofwait = 0
                index += 1
            else:
                passcar+=1
                sumofwait += car[8]



    for i in res:
        print(i)
        delete_query = '''
                                   TRUNCATE TABLE tidallane_tidallane;
                                   '''
        cursor.execute(delete_query)

    sql_insert_query = """
        INSERT INTO tidallane_tidallane (time, ori_volume, ori_wait, tid_volume, tid_wait)
        VALUES (%s, %s, %s, %s, %s)
        """
    for item in res:
        data_tuple = (item[0], item[1], item[2], item[3], item[4])
        cursor.execute(sql_insert_query, data_tuple)
    mydb.commit()
    cursor.close()
    mydb.close()




cal_flow()