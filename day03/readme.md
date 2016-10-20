#作业要求：
HAproxy配置文件操作
> * 1. 根据用户输入输出对应的backend下的server信息
> * 2. 可添加backend 和sever信息
> * 3. 可修改backend 和sever信息
> * 4. 可删除backend 和sever信息
> * 5. 操作配置文件前进行备份
> * 6. 添加server信息时，如果ip已经存在则修改;如果backend不存在则创建；若信息与已有信息重复则不操作

让用户查找和编辑backend信息，用户的输入例子为
```
{"backend": "test.oldboy.org","record":{"server": "100.1.7.9","weight": 20,"maxconn": 30}}
```
在编辑haproxy.cfg时，程序能自动备份和切换文件
程序主入口为main.py，配置文件和备份文件放在conf目录下
每编辑一次，就会自动生产更高版本的备份文件，也可以在程序手工备份
