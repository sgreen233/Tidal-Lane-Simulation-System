# -*- coding: utf-8 -*-
from django.shortcuts import render

#首先存储一个全局时间，根据来车进行时间的变换
from datetime import datetime
from TidalLane.models import tidallane
# 首先是一个等待队列，需要计算时间的

Main_time = datetime.now()

# 数据库操作
def testdb(request):
    # 初始时间根据表格中数据进行修改
    queryset = tidallane.objects.all().order_by("arrivetime")
    # 遍历QuerySet
    for obj in queryset:
        # 访问并打印每个对象的字段值
        print(f"arrivetime: {type(obj.arrivetime)}, direct: {obj.direct}")
    first1000 = list(queryset[:1000])
    Main_time = first1000[0].arrivetime


    return render(request, 'hello.html', {'data':queryset})