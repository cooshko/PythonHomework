初始化数据库
```
day12\bin>python main.py sync-db
这个操作会清空整个数据库，如确定请输入YES：YES
mysql> show tables;
+---------------------+
| Tables_in_baoleiji  |
+---------------------+
| host                |
| host2group          |
| host2host_user      |
| host_group          |
| host_user           |
| user                |
| user2group          |
| user2host2host_user |
| user_group          |
+---------------------+
9 rows in set (0.00 sec)
```
添加用户组
```
day12\bin>python main.py add-user-groups -f ../samples/new_user_groups.txt

mysql> select * from user_group;
+----+-------+-------------+
| id | name  | description |
+----+-------+-------------+
|  1 | ops1  |             |
|  2 | ops2  |             |
|  3 | admin |             |
+----+-------+-------------+
3 rows in set (0.00 sec)
```

添加主机组
```
day12\bin>python main.py add-host-groups -f ../samples/new_host_groups.txt

mysql> select * from host_group;
+----+------------+--------------------+
| id | name       | description        |
+----+------------+--------------------+
|  1 | www        | 网页服务器组       |
|  2 | db         | 数据库组           |
|  3 | cache      | 缓存服务器组       |
|  4 | lb         | 负载均衡组         |
|  5 | lab        | 测试机组           |
|  6 | production | 生产组             |
+----+------------+--------------------+
6 rows in set (0.00 sec)
```
添加用户（提示的错误是我故意，用于展示异常情况）
```
day12\bin>python main.py add-users -f ../samples/new_users.txt
ops3 组不存在
lisi 用户已经添加，但没有加入任何的组

mysql> select * from user;      
+----+----------+----------------------------------+--------+
| id | name     | password                         | enable |
+----+----------+----------------------------------+--------+
|  1 | coosh    | 5b7fc268816e6f4dc2673b6a087e7d72 |      1 |
|  2 | panny    | 122d089aed3e3ab8386c139c81d02555 |      1 |
|  3 | alex     | b75bd008d5fecb1f50cf026532e8ae67 |      1 |
|  4 | zhangsan | 4e7bdb88640b376ac6646b8f1ecfb558 |      1 |
|  5 | lisi     | c3cb6d12c40908943b64bc0681af47db |      1 |
+----+----------+----------------------------------+--------+
5 rows in set (0.00 sec)

mysql> select user.name, user_group.name from user, user_group, user2group where user.id = user2group.uid and user_group.id =  user2group.gid;
+----------+-------+
| name     | name  |
+----------+-------+
| coosh    | admin |
| panny    | ops1  |
| panny    | ops2  |
| alex     | ops2  |
| zhangsan | ops2  |
+----------+-------+
5 rows in set (0.00 sec)
```
添加主机
```
day12\bin>python main.py add-hosts -f ../samples/real_hosts.txt

mysql> select h.name, h.ip, h.port, hg.name as 'group' from host h, host_group hg, host2group h2g where h2g.hid = h.id and h2g.hgid = hg.id; 
+------+---------------+------+------------+
| name | ip            | port | group      |
+------+---------------+------+------------+
| lab2 | 192.168.5.138 |   22 | lab        |
| lab3 | 192.168.5.142 |   22 | lab        |
| lab1 | 192.168.5.41  |   22 | production |
+------+---------------+------+------------+
3 rows in set (0.00 sec)

mysql> select h.name, h.ip, h.port, hu.auth_user, hu.using_key, hu.auth_pass, hu.auth_key  
from host h, host_user hu, host2host_user h2u 
where h.id = h2u.hid and hu.id=h2u.huid;       
+------+---------------+------+-----------+-----------+-----------+-----------------------------------+
| name | ip            | port | auth_user | using_key | auth_pass | auth_key                          |
+------+---------------+------+-----------+-----------+-----------+-----------------------------------+
| lab2 | 192.168.5.138 |   22 | root      |         0 | coosh123  |                                   |
| lab3 | 192.168.5.142 |   22 | root      |         0 | coosh123  |                                   |
| lab1 | 192.168.5.41  |   22 | coosh     |         1 |           | C:\Users\Coosh\Documents\Identity |
+------+---------------+------+-----------+-----------+-----------+-----------------------------------+
3 rows in set (0.00 sec)
```

重设堡垒机用户密码
```
bin>python main.py reset-user-password -u coosh new1234
```

用户管理整个主机组
```
E:\PycharmProjects\PythonHomework\day12\bin>python main.py user-manage-host-group -u coosh -g lab -r NONE
失败，请检查用户或组是否存在

E:\PycharmProjects\PythonHomework\day12\bin>python main.py user-manage-host-group -u coosh -g lab -r root
OK

mysql> select u.name as 'user', h.name as 'host', hg.name as 'host_group', hu.auth_user  from user u, host h, host_group hg, host_user hu, user2host2host_user hhhh where hhhh.uid=u.id and hhhh.hid=h.id and hhhh.hgid=hg.id and hhhh.huid=hu.id;     
+-------+------+------------+-----------+
| user  | host | host_group | auth_user |
+-------+------+------------+-----------+
| coosh | lab2 | lab        | root      |
| coosh | lab3 | lab        | root      |
+-------+------+------------+-----------+
2 rows in set (0.00 sec)
```

用户不再管理整个主机组
```
day12\bin>python main.py user-leave-host-group -u coosh -g lab -r root
OK

mysql> select u.name as 'user', h.name as 'host', hg.name as 'host_group', hu.auth_user  from user u, host h, host_group hg, host_user hu, user2host2host_user hhhh where hhhh.uid=u.id and hhhh.hid=h.id and hhhh.hgid=hg.id and hhhh.huid=hu.id;
Empty set (0.00 sec)

```

用户管理指定组的某一主机
```
E:\PycharmProjects\PythonHomework\day12\bin>python main.py user-manage-host -u panny -g lab -h lab2 -r root
OK

mysql> select u.name as 'user', h.name as 'host', hg.name as 'host_group', hu.auth_user  from user u, host h, host_group hg, host_user hu, user2host2host_user hhhh where hhhh.uid=u.id and hhhh.hid=h.id and hhhh.hgid=hg.id and hhhh.huid=hu.id;
+-------+------+------------+-----------+
| user  | host | host_group | auth_user |
+-------+------+------------+-----------+
| panny | lab2 | lab        | root      |
| coosh | lab1 | production | coosh     |
+-------+------+------------+-----------+
2 rows in set (0.00 sec)
```

用户不再管理指定组的某一主机
```
day12\bin>python main.py user-leave-host -u panny -g lab -h lab2 -r root
OK
mysql> select u.name as 'user', h.name as 'host', hg.name as 'host_group', hu.auth_user  from user u, host h, host_group hg, host_user hu, user2host2host_user hhhh where hhhh.uid=u.id and hhhh.hid=h.id and hhhh.hgid=hg.id and hhhh.huid=hu.id;
+-------+------+------------+-----------+
| user  | host | host_group | auth_user |
+-------+------+------------+-----------+
| coosh | lab1 | production | coosh     |
+-------+------+------------+-----------+
1 row in set (0.00 sec)
```

普通用户的交互shell
```
day12\bin>python main.py interactive

用户名：coosh
密码：new1234
1) production

请输入你要访问的组：1
--> production
1) lab1 coosh@192.168.5.41

选择主机或者输入[ g ]对该组主机操作
>>1
-->选择的是 lab1
请选择：
1) 访问shell
2) 上传文件
3) 下载文件

>>1

Line-buffered terminal emulation. Press F6 or ^Z to send EOF.

Last login: Tue Nov 29 14:46:47 2016 from 192.168.5.6
[coosh@Lab1 ~]$ ifconfig eth0
ifconfig eth0
eth0      Link encap:Ethernet  HWaddr 00:0C:29:56:24:89
          inet addr:192.168.5.41  Bcast:192.168.5.255  Mask:255.255.255.0
          inet6 addr: fe80::20c:29ff:fe56:2489/64 Scope:Link


```

下载
```
请输入你要访问的组：2
--> lab
1) lab2 root@192.168.5.138
2) lab3 root@192.168.5.142

选择主机或者输入g对该组主机操作
>> g
对 lab 组进行的操作
1) 上传文件
2) 下载文件

>> 2
远程文件路径：/tmp/test.txt  
正在下载 lab2(192.168.5.138) 的远程文件 /tmp/test.txt
正在下载 lab3(192.168.5.142) 的远程文件 /tmp/test.txt
全部完毕


[root@Lab1 modules]# tree ../data/by_group/
../data/by_group/
├── lab2
│   └── test.txt
└── lab3
    └── test.txt

2 directories, 2 files
```




上传
```

请输入你要访问的组：1
--> lab
1) lab2 root@192.168.5.138
2) lab3 root@192.168.5.142

选择主机或者输入g对该组主机操作
>> g
对 lab 组进行的操作
1) 上传文件
2) 下载文件

>> 1
本地文件的绝对路径：/tmp/hello.txt
远程目录：/tmp
正在上传 /tmp/hello.txt 到 lab2 (192.168.5.138) 的 /tmp
正在上传 /tmp/hello.txt 到 lab3 (192.168.5.142) 的 /tmp
全部完毕

对 lab 组进行的操作
1) 上传文件
2) 下载文件
3) 执行一条命令

>> 3
请输入命令：cat /tmp/hello.txt
[192.168.5.138]
Hello from lab1


[192.168.5.142]
Hello from lab1

```

访问日志（位于log目录下的access.log）
```
2016-11-29 10:07:03 - INFO - coosh on 192.168.5.138 download_file []{"remote_file": "/tmp/test.txt", "secondary_dir": "lab2"}
2016-11-29 10:07:57 - INFO - coosh on 192.168.5.138 download_file []{"remote_file": "/tmp/test.txt", "secondary_dir": "lab2"}
2016-11-29 10:43:46 - INFO - coosh on 192.168.5.138 download_file []{"secondary_dir": "lab2", "toplevel_dir": "by_group", "remote_file": "/tmp/test.txt"}
2016-11-29 10:43:46 - INFO - coosh on 192.168.5.142 download_file []{"secondary_dir": "lab3", "toplevel_dir": "by_group", "remote_file": "/tmp/test.txt"}
2016-11-29 10:48:16 - INFO - coosh on 192.168.5.138 upload_file []{"remote_path": "/tmp", "local_file": "/tmp/hello.txt"}
2016-11-29 10:48:16 - INFO - coosh on 192.168.5.142 upload_file []{"remote_path": "/tmp", "local_file": "/tmp/hello.txt"}
```

用户输入的指令日志（位于log目录下的cmd.log）
```
[root@Lab1 modules]# cat ../log/cmd.log       
2016-11-29 10:41:35 - INFO - coosh: ls
2016-11-29 10:41:38 - INFO - coosh: df -h
2016-11-29 10:41:42 - INFO - coosh: ifconfig 
2016-11-29 10:41:45 - INFO - coosh: ifconfig eth0
2016-11-29 10:41:58 - INFO - coosh: ifconfig eth0
2016-11-29 10:42:06 - INFO - coosh: exit
```