被控节点加入组
```
[root@localhost bin]# python3 main.py  
请输入当前主机名：new sys
不能包含空格！
请输入当前主机名：newsys
要加入哪个组（留空则为workgroup）：
开始运行。。。
```
管理端对一个节点执行命令

```
请输入要执行的主机或组，空格后，加上要执行的命令
>> newsys ip addr|grep 192.168
>> ================= From newsys =================
    inet 192.168.199.223/24 brd 192.168.199.255 scope global eth0
```
管理端对一个组执行命令
```
>> workgroup dir
>> ================= From newsys =================
__init__.py  main.py

================= From node1 =================
 驱动器 E 中的卷是 新加卷
 卷的序列号是 6C14-E465

 E:\PycharmProjects\PythonHomework\day11\node\bin 的目录

2016/11/20  23:24    <DIR>          .
2016/11/20  23:24    <DIR>          ..
2016/11/20  23:24               959 main.py
2016/11/20  23:23               100 __init__.py
               2 个文件          1,059 字节
               2 个目录 18,450,554,880 可用字节
```