依赖：redis、sqlalchemy、tornado
执行项目目录下的app.py即可。如需重建数据库，请执行modules下的models.py

作业需求：项目实战 开发一个WEB聊天室
>* 用户可以与好友一对一聊天
>* 可以搜索、添加某人为好友
>> 点击左下角的“添加好友”按钮，输入好友的昵称，点击"搜"，找到用户就可以添加；
>> 成功添加后，在左侧菜单中会自动出现好友的对话按钮


>* 用户可以搜索和添加群
>> 类似添加好友，但输入的应该是群号，群号可以在右侧对话框的标题看到（括号中的号码）
>> 当然，只有群里的成员才能看到群号，这点请注意了。


>* 每个群有管理员可以审批用户的加群请求，群管理员可以用多个，群管理员可以删除、添加、禁言群友
>> 任何人都可以发起加群的请求，这些请求会以管理消息形式出现在管理员的对话框中，普通成员是不会接收到的。管理员只需要点击“批准”即可允许新人加群
>> 群管理员可以有多个，但必须由群主任命。
>> 管理员和群主均可以禁言解禁、移除、邀请普通成员，而管理员之间无法禁言解禁、移除，群主则可以。
>> 当群成员剩下3人时，如果再减员，则自动解散该群


>* 可以与聊天室里的人进行临时会话(与qq群一样)
>> 可以在群成员列表中点击其他成员的名字，打开一对一会话，如果双方已经是好友，则打开好友会话，否则会创建并打开一个临时会话。

>* 可以在群中发图片＼文件
>* 可以与好友一对一发文件
>> 由于原理上是一致的，所以任何会话都可以上传图片或者文件，此类消息会以特殊的（FileType）形式进行展示。如果是图片，会有小图，如点击则在新窗口查看大图；其他类型的文件，则会显示文件名和下载路径
 

已有测试帐号如下
coosh panny mingming alex dan ，密码均为123

>* db目录下的数据库文件和statics目录下的upload文件夹里的内容，都是为了做DEMO展示，可以把他们删掉。执行一下modules目录下的models.py可以重建数据库
>* 由于整个系统会用到redis作为聊天记录的存储，为了方便测试，我提供了一个redis服务器，但该服务器只是临时的，因此打算自行执行的话请自行搭建redis服务器。

>* 已知问题，开发的环境是windows，测试环境是Linux，发现原本在开发时的上传文件名在Linux中变成了乱码，重新上传即可。