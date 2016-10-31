作业需求：
FTP：

1. 用户登陆
```
请输入用户名：coosh
请输入密码：dsfasfds
验证失败...
请输入用户名：coosh
请输入密码：123
验证通过...
```
2. 上传/下载文件
```
>> get Desert.jpg
接收完毕
>> put Desert.jpg
DONE
>> ls
.
..
666\
Desert.jpg
haproxy1.6.x Configuration Manual.txt
>> 
```
3. 不同用户家目录不同
```
请输入用户名：coosh
请输入密码：123
验证通过...
>> ls
.
..
666\
Desert.jpg
haproxy1.6.x Configuration Manual.txt
>> exit
已连接到服务器...
NEED AUTH
请输入用户名：panny
请输入密码：123
验证通过...
>> ls
.
..
示例图片_02.jpg
>> 
```
4. 用户登陆server后，可切换目录
```
>> mkdir testdir
DONE
>> ls
.
..
testdir\
示例图片_02.jpg
>> cd testdir
DONE
>> ls
.
..
>> cd ..
DONE
>> ls
.
..
testdir\
示例图片_02.jpg
>> 
```
5. 查看当前目录下文件
```
>> cd ..
DONE
>> ls
.
..
testdir\
示例图片_02.jpg
>> 
```