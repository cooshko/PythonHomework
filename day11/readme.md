作业
一个简单的RPC（远程调用模型）
1. server端将要执行的命令及参数发送到RabbitMQ，
2. client端从RabbitMQ获取要执行的命令，命令执行完成之后，将结果返回给server端
3. server端接受client端的命令执行结果，并处理，
4. 可选择指定主机或者主机组

> * rabbitmq需要自行安装并配置（下面有简单的配置）
> * 而本程序的rabbitmq的ip地址和认证，请在commons/conf/rabbit.conf目录中修改
> * 程序的入口均在各自的bin目录下的main.py
> * 由于commons为公共类库，所以使用时务必要带上这个目录
> * 管理端使用主线程来接收指令并推送，子线程来打印结果

特别说明：由于视频课程中没有讲述rabbitmq的安装和配置，所以在使用时，如果不是本机访问rabbitmq，可能会认证失败，这是因为rabbitmq默认用户guest是不允许远程访问的，但生产环境中，大多都是远程访问，因此这里附带上简单的配置（共5步）

1、使用apt-get install rabbitmq-server即可安装（centos貌似不能yum安装，只能源码安装了）

2、开启web管理页面（可选）
rabbitmq-plugins enable rabbitmq_management

3、rabbitmqctl add_user coosh coosh

4、rabbitmqctl set_user_tags coosh administrator

5、rabbitmqctl set_permissions -p "/" coosh ".*" ".*" ".*"