查看帮助
```
>python main.py

main.py [option] ["command"]
OPTIONS:
--list  查看主机列表
--groups 查看组
-H <"command"> 对所有主机执行命令
-G GROUPNAME <"command"> 对指定组的所有主机执行命令

COMMANDS:
get REMOTE-FILE-PATH 尝试获取远程主机指定路径的文件
put LOCAL-FILE-PATH  将本地文件上传到远程主机
其他指令直接发往远程主机上执行
```
验证失败
```
Connected to pydev debugger (build 162.1628.8)
[192.168.5.41:9991] 验证失败
[192.168.5.138:9992] 验证失败
2016-11-09 13:30:42 - ERROR - [192.168.5.41:9991] 验证失败
2016-11-09 13:30:42 - ERROR - [192.168.5.138:9992] 验证失败
[192.168.5.142:9993] 验证失败
2016-11-09 13:30:42 - ERROR - [192.168.5.142:9993] 验证失败

Process finished with exit code 0
```

执行命令
```
>python main.py -H "hostname"

===START===
[192.168.5.138:9992]  >>> hostname
Lab2.jscan

===END===
===START===
[192.168.5.41:9991]  >>> hostname
Lab1.jscan

===END===
===START===
[192.168.5.37:9994]  >>> hostname
ntp1.jscan

===END===

===START===
[192.168.5.142:9993]  >>> hostname
Lab3.jscan

===END===
```

查看组
```
>python main.py --
groups
共2组
PRODUCTION 组
      ntp1 192.168.5.37:9994 coosh4 123
UAT 组
      lab1 192.168.5.41:9991 coosh1 123
      lab2 192.168.5.138:9992 coosh2 123
      lab3 192.168.5.142:9993 coosh3 123
```

查看所有主机
```
>python main.py --groups
共2组
PRODUCTION 组
      ntp1 192.168.5.37:9994 coosh4 123
UAT 组
      lab1 192.168.5.41:9991 coosh1 123
      lab2 192.168.5.138:9992 coosh2 123
      lab3 192.168.5.142:9993 coosh3 123
```

上传文件
```
>python main.py -G UAT "put F:\README.HTM"
2016-11-09 13:40:02 - INFO - [192.168.5.41:9991] 尝试发送文件：F:\README.HTM
2016-11-09 13:40:02 - INFO - [192.168.5.138:9992] 尝试发送文件：F:\README.HTM
2016-11-09 13:40:02 - INFO - [192.168.5.142:9993] 尝试发送文件：F:\README.HTM
2016-11-09 13:40:02 - INFO - [192.168.5.142:9993] 成功
===START===
[192.168.5.142:9993]  >>> put F:\README.HTM
成功！
===END===
2016-11-09 13:40:02 - INFO - [192.168.5.138:9992] 成功

2016-11-09 13:40:02 - INFO - [192.168.5.41:9991] 成功
===START===
[192.168.5.138:9992]  >>> put F:\README.HTM
成功！
===END===
===START===
[192.168.5.41:9991]  >>> put F:\README.HTM
成功！
===END===
```

下载文件
```
>python main.py -G UAT "get /tmp/ip.txt"
2016-11-09 13:40:52 - INFO - [192.168.5.41:9991] 成功！文件保存到 E:\PycharmProjects\PythonHomework\day10\MyFabricManager\data\192.168.5.41\ip.txt
===START===
[192.168.5.41:9991]  >>> get /tmp/ip.txt
成功！文件保存到 E:\PycharmProjects\PythonHomework\day10\MyFabricManager\data\192.168.5.41\ip.txt
===END===

2016-11-09 13:40:52 - INFO - [192.168.5.142:9993] 成功！文件保存到 E:\PycharmProjects\PythonHomework\day10\MyFabricManager\data\192.168.5.142\ip.txt
===START===
[192.168.5.142:9993]  >>> get /tmp/ip.txt
成功！文件保存到 E:\PycharmProjects\PythonHomework\day10\MyFabricManager\data\192.168.5.142\ip.txt
===END===
2016-11-09 13:40:52 - INFO - [192.168.5.138:9992] 成功！文件保存到 E:\PycharmProjects\PythonHomework\day10\MyFabricManager\data\192.168.5.138\ip.txt

===START===
[192.168.5.138:9992]  >>> get /tmp/ip.txt
成功！文件保存到 E:\PycharmProjects\PythonHomework\day10\MyFabricManager\data\192.168.5.138\ip.txt
===END===
```