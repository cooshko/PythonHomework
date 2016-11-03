FTP：

1. 用户加密认证
```
在Server端，conf目录下，每个用户一个文件，保存着用户的md5密码和用户的磁盘配额
```
2. 多用户同时登陆
```
使用了TheadingTCPServer，可以支持并发访问
if __name__ == '__main__':
    myserver = socketserver.ThreadingTCPServer(("0.0.0.0", 9999), FtpServer)
    myserver.serve_forever()
```
3. 每个用户有自己的家目录且只能访问自己的家目录（公共函数，返回bool）
```
用户名：coosh
密码：123
服务器： 欢迎
>> cd ..
只允许访问你拥有目录
```
4. 对用户进行磁盘配额、不同用户配额可不同
```
>> du
你的配额是800000000，已使用1192658，剩余798807342
```
5. 用户可以登陆server后，可切换目录
```
>> cd 666
你正在访问666
>> ls
.
..
freetds.txt
```
6. 查看当前目录下文件
```
>> cd ..
你正在访问家目录
>> ls
.
..
666\
Bind_9.10_Manual.pdf
```
7. 上传下载文件，保证文件一致性
```
下载：
>> get Bind_9.10_Manual.pdf
==========> 100%
md5 from server:  77e519d9bc468075a4d7f3ac083f3bd1
md5 from local :  77e519d9bc468075a4d7f3ac083f3bd1

上传：
>> put loganalyzer-3.6.6.tar.gz
==========> 100%
md5 local:  979b25330b0a2bb35eb458f634335a76
md5 server: 979b25330b0a2bb35eb458f634335a76
DONE
```
8. 传输过程中现实进度条
```
参考7
```
9. 支持断点续传
```
>> get ubuntu-16.04.1-server-amd64.iso
===> 39%
Process finished with exit code 1

>> get ubuntu-16.04.1-server-amd64.iso
正在为你断点续传
==========> 100%
md5 from server:  f8fd0646b717a83f4b61bf749e909ea2
md5 from local :  f8fd0646b717a83f4b61bf749e909ea2

```