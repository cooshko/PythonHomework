/**
* Created by Coosh on 2017/2/14.
*/
/* ajax检查数据是否已被注册使用 */
function check_exist(ele) {
    var t = ele.getAttribute("name");
    var v = ele.value;
    v = $.trim(v);
    if(v.length>0){
        $.post({
            url: "/app01/check_exist/",
            data: {"check_type": t, "check_value": v},
            dataType: "json",
            success: function (response) {
                // console.log(response);
                var check_result = "";
                if(response.status=='ok'){
                    // 没有重复
                    check_result = "√";
                }else{
                    check_result = "已存在";
                    ele.setAttribute("duplicate", "duplicate");
                }
                $(ele).parent().parent().find('td:last-child').text(check_result);
            }
        });
    }
}

function register(ele) {
    // 数据检查
    var check_pass = true;
    var check_list = {
        'login_name': '用户名',
        'email': '邮箱',
        'password': '密码',
        'password2': '确认密码',
        'verify_code': '验证码'
    };
    for(var key in check_list){
        var val = $.trim($('.reg_frm #' + key).val());
        if(val.length==0){
            // 如果要检查的input值为空，提醒用户
            check_pass = false;
            $(".reg_frm #" + key).parent().parent().find('td:last-child').text("不能为空");
        }
    }
    if(!check_pass){
        return false;
    }

    // 通过检查后
    var login_name = $.trim($('.reg_frm #login_name').val());
    var email = $.trim($('.reg_frm #email').val());
    var password = $.trim($('.reg_frm #password').val());
    var password2 = $.trim($('.reg_frm #password2').val());
    var verify_code = $.trim($('.reg_frm #verify_code').val());

    // 提交前，先将按钮置为不可点击
    $("div.reg_shelter").removeClass("hide");
    var data = $('#register_frm').serialize();
    console.log(data);
    $.post({
        url: "/app01/register/",
        data: data,
        dataType: "json",
        success: function (response) {
            console.log(response);
            if(response.hasOwnProperty("status")){
                if(response.status=='ok'){
                    //console.log("注册成功");
                    $("div.register_result").text("注册成功");
                    setTimeout(function () {
                        $("div.login_reg_frm").addClass("hide");
                        $("div.shelter").addClass("hide");
                    }, 2000);
                }else{
                    $("div.reg_shelter").addClass("hide");
                    $("div.register_result").text(response.msg);
                }
            }else{
                var ul = document.createElement('ul');
                for(var key in response){
                    var li = document.createElement('li');
                    li.innerText = response[key][0].message;
                    ul.appendChild(li);
                }
                $("div.register_result").html(ul.outerHTML);
                $("div.reg_shelter").addClass("hide");
            }
        },
        error: function (xhr) {
            $("div.reg_shelter").addClass("hide");
        }
    });
    reload_verify_code();   // 无论结果如何，都刷新验证码
}

/* 检查两次密码是否一致 */
function confirm_password() {
    if($('.reg_frm #password').val()!=$('#password2').val()){
        $('.reg_frm #password2').parent().parent().find('td:last-child').text("两次密码不一致");
    }else{
        $('.reg_frm #password').parent().parent().find('td:last-child').text("√");
        $('.reg_frm #password2').parent().parent().find('td:last-child').text("√");
    }
}

/* 创建验证码图片标签 */
function create_verify_code_img() {
    // 创建验证码图片标签，插入到验证码输入框后面
    if(!document.getElementById('verify_code_img')){
        var img = document.createElement('img');
        img.id = 'verify_code_img';
        img.src = '/app01/verify_code/';
        img.className = 'verify_code';
        img.onclick = reload_verify_code;
        $("input.verify_code").after(img);
    }
}

/* 刷新验证码函数 */
function reload_verify_code() {
    var img = $('img.verify_code')[0];
    img.src += '?';
}

/* 显示登录、注册页面 */
function show_login_reg_frm() {
    $("div.login_reg_frm").removeClass("hide");
    $("div.shelter").removeClass("hide");
}

/* 用户下拉菜单显示开关 */
function show_user_menu(flag) {
    if(flag){
        $("div.user_menu").removeClass("hide");
    }else{
        $("div.user_menu").addClass("hide");
    }
}

/* 登录 */
function login() {
    var login_name = $(".login_frm input.login_name").val();
    var password = $(".login_frm input.password").val();
    $.post({
        url: '/app01/login/',
        data: {'login_name': login_name, 'password': password},
        dataType: "json",
        success: function (response) {
            if(response.status=='ok'){
                // 登录成功，读取用户昵称和头像
                $("div.login_result").text("登录成功");
                var display_name = response.display_name;
                var head_pic = response.head_pic;
                $("span#display_name").text(display_name);
                $("img.head_pic").attr("src", head_pic);
                $("div.login_reg_frm").addClass("hide");
                $("div.shelter").addClass("hide");
                $(".user_info #display_name").attr("is_login", "");
                $(".user_info").removeClass("hide");
                $(".login_or_register").addClass("hide");
                get_online_users();
            }else{
                $("div.login_result").text(response.error);
            }
        },
        error: function (xhr) {

        }
    });
}

/* 注销 */
function logout() {
    $.get({
        url: "/app01/logout/",
        dataType: "json",
        success:function (response) {
            if(response.status=='ok'){
                window.location.href="/app01/";
            }
        }
    })
}

/* 检查是否登录 */
function is_login() {
    return document.getElementById('display_name').hasAttribute('is_login');
}

/* 隐藏登录框 */
function close_login_reg_frm() {
    $("div.login_reg_frm").addClass("hide");
    $("div.shelter").addClass("hide");
}

/* 展示发布框 */
function show_publish_frm(flag) {
    if(!is_login()){
        show_login_reg_frm();
        return false;
    }
    if(flag){
        $("div.shelter").removeClass("hide");
        $("div.publish_frm").removeClass("hide");
    }else{
        $("div.shelter").addClass("hide");
        $("div.publish_frm").addClass("hide");
    }
}

function clear_publish_form() {
            $("textarea.publish_text").val("");
            $(".publish_frm a.current").removeClass("current");
            $("#fo")[0].reset();
            $("div.uploaded_preview").children().remove();
        }

        function publish() {
            var data = {};
            data['pub_text'] = $.trim($("textarea.publish_text").val());
            // 检查文本内容是否为空
            if(data['pub_text'].length==0){
                alert("文字内容不能为空。");
                return false;
            }

            // 检查是否有选择类别
            data['catalog'] = $("div.publish_catalog a.current").attr("cid");
            if(!data['catalog']){
                alert("请选择一个分类");
                return false;
            }

            // 获取图片
            var img = $("div.uploaded_preview img")[0];
            if(img){
                data['img_link'] = $(img).attr("src");
            }

            $.post({
                url:"/app01/publish/",
                data: data,
                dataType: "json",
                success: function (response) {
                    if(response.status=='ok'){
                        alert("发布成功！");
                        clear_publish_form();
                        show_publish_frm(false);
                        $("div.shelter").addClass("hide");
                    }
                },
                error: function (xhr) {

                }
            });
        }

function upload_img() {
    document.getElementById('if').onload=callback;
    document.getElementById('fo').submit();
}

/* 上传完毕后的回调函数 */
function callback() {
    var t = $("#if").contents().find('body').text();
    var result = JSON.parse(t);
    console.log(result);
    if(result.status=='ok'){
        var a = document.createElement('a');
        a.href = result.link;
        a.target = '_blank';
        var img = document.createElement('img');
        img.src = result.link;
        a.appendChild(img);
        $("div.uploaded_preview").html(a.outerHTML);
    }
}

function get_online_users() {
        if(is_login()){
            var online_users_container = $("div.online_users_container");
            // 清理工作
            online_users_container.children().remove();
            online_users_container.text("");

            // 获取在线用户
            $.get({
                url:"/app01/get_online_users/",
                dataType:"json",
                success:function (response) {
                    if(response.status=='ok'){
                        console.log(response);
                        var users = response.data;
                        online_users_container.text("在线用户列表：");
                        for(var key in users){
                            var user_a = document.createElement('a');
                            user_a.innerText=users[key]['display_name'];
                            user_a.setAttribute("user_id", users[key]['id']);
                            user_a.href = "javascript:void(0);";
                            online_users_container.append(user_a);
                        }
                    }
                }
            });

        }
    }
    function create_post_list(posts, cls) {
        if(posts.length>0){
            var big_div = document.createElement('div');
            big_div.className = cls;
            for(var i=0;i<posts.length;i++){
                var post_div = document.createElement('div'); // 包裹着整个帖子的div
                post_div.className="post_container clearfix";
                post_div.setAttribute("post_id", posts[i].id);
                var left_div = document.createElement('div');
                left_div.className="left_container fl";
                var right_div = document.createElement('div');
                right_div.className="right_container fl";
                var content_div = document.createElement('div');
                content_div.className="post_content";
                var bar_div = document.createElement('div');
                bar_div.className="post_bar";
                var comment_div = document.createElement('div');
                comment_div.className="comment_container hide";

                content_div.innerText = posts[i].content;
                var like = posts[i].like?"已赞":"赞";
                var like_a = document.createElement('a');
                var comment_a = document.createElement('a');
                var displayname_span = document.createElement("span");
                var create_i = document.createElement('i');
                like_a.href = comment_a.href = "javascript:void(0);";
                like_a.className="like_btn";
                like_a.setAttribute("onclick", "like(this," + posts[i].id + ")");
                like_a.setAttribute("like_count", posts[i].like_count);
                like_a.innerText = like+ '(' + posts[i].like_count + ')';
                comment_a.className="show_comments_btn";
                comment_a.setAttribute("onclick", "show_comments(this,"+ posts[i].id +")");
                comment_a.innerText = '评('+posts[i].comment_count+')';
                displayname_span.innerText = posts[i].user__display_name;
                create_i.innerText='在 '+posts[i].create_on+' 发布';
                bar_div.appendChild(like_a);
                bar_div.appendChild(comment_a);
                bar_div.appendChild(displayname_span);
                bar_div.appendChild(create_i);

                // comment_div.innerText = "这里是评论";
                var comment_text_container = document.createElement('div');
                var comment_content_container = document.createElement('div');
                comment_text_container.className="comment_text_container";
                comment_content_container.className="comment_content_container";
                comment_div.appendChild(comment_text_container);
                comment_div.appendChild(comment_content_container);


                left_div.appendChild(content_div);
                left_div.appendChild(bar_div);

                if(posts[i].hasOwnProperty("img_link")){
                    var img = document.createElement('img');
                    img.src = posts[i].img_link;
                    right_div.appendChild(img);
                }

                var row_container = document.createElement('div');
                row_container.className="row_container clearfix";
                row_container.appendChild(left_div);
                row_container.appendChild(right_div);

                post_div.appendChild(row_container);
                post_div.appendChild(comment_div);

                big_div.appendChild(post_div);
            }
            $("div.post_list").append(big_div);
        }
    }

    function view_posts(ele, catalog, page) {
        $(ele).siblings('a').removeClass("current");
        $(ele).addClass("current");
        $("div.paginator").children().remove();
        $.get({
            url:"/app01/posts/",
            data:{"catalog":catalog, "page":page},
            dataType:"json",
            success:function (response) {
                if(response.status=='ok'){
                    // 服务器返回数据
                    // console.log(response);
                    var posts = response['data']['posts'];
                    var current_page = response['data']['current_page'];
                    var page_count = response['data']['page_count'];

                    if(posts.length>0){
                        // 有帖子数据
                        // 区分置顶和普通帖子
                        var top_post_list = [];
                        var normal_post_list = [];
                        for(var key in posts){
                            var post = posts[key];
                            if(post.top){
                                // 帖子有置顶属性
                                if(post.catalog_id==response['data']['current_catalog']){
                                    // 帖子是当前类别
                                    post.content = '【置顶】'+ post.content;
                                    top_post_list.push(post);
                                }else{
                                    // 推入非置顶帖子
                                    normal_post_list.push(post);
                                }
                            }else{
                                // 非置顶帖子
                                normal_post_list.push(post);
                            }
                        }

                        // 分好之后交给对应的函数处理
                        $("div.post_list").html("");
                        create_post_list(top_post_list,"top_posts");
                        create_post_list(normal_post_list,"normal_posts");
                        create_paginator(page_count, current_page);
                    }else {
                        // 没有帖子
                        $("div.post_list").text("还没有帖子喲，要不你发一个:)");
                    }
                }
            }
        });
    }

    /* 分页 */
    function create_paginator(total, current) {
        if(total>0){
            var paginator_container = $("div.paginator");
            paginator_container.children().remove();
            for(var i=1;i<=total;i++){
                var a = document.createElement('a');
                a.innerText=i;
                if(i==current) a.className="current";
                a.href="javascript:void(0);";
                var cid = $("div.nav a.current").attr("cid");
                a.setAttribute("onclick", "view_posts(this,"+cid+","+i+")");
                paginator_container.append(a);
            }
        }
    }
    /* 点赞 */
    function like(ele, post_id) {
        if(!is_login()){
            show_login_reg_frm();
            return false;
        }
        $.get({
            url:"/app01/like_post/",
            data:{'post':post_id},
            dataType:"json",
            success: function (response) {
                console.log(response);
                if(response.status="ok"){
                    var like_count = parseInt($(ele).attr("like_count"));
                    if(response.msg=='liked'){
                        // 已赞
                        alert("已赞");
                        like_count++;
                        $(ele).text("已赞("+like_count+")");
                    }else if(response.msg=='unliked'){
                        // 已取消赞
                        alert("已取消赞");
                        like_count--;
                        $(ele).text("赞("+like_count+")");
                    }
                    $(ele).attr("like_count", like_count);
                }
            }
        });
    }

    /* 获取指定帖子的评论 */
    function get_comments(post_id) {
        var comments;
        $.get({
            url:"/app01/get_comments/",
            data:{"post": post_id},
            dataType: "json",
            async: false,
            success:function (response) {
                if(response.status=='ok'){
                    comments = response['data'];
                }
            }
        });
        return comments;
    }

    /* 展示该帖子的所有评论 */
    function show_comments(ele, post_id) {
        // 先隐藏所有帖子的评论div，然后展示用户点击的帖子的评论div
        $("div.comment_container").addClass("hide");

        var current_comment_container = $(ele).parent().parent().parent().siblings(".comment_container").removeClass("hide");
        var comment_text_container = current_comment_container.children(".comment_text_container");

        // 清理评论编辑器和评论列表
        $("div.comment_text_container").children().remove();
        $("div.comment_content_container").children().remove();


        // 插入一个textarea
        // var comment_text = document.createElement('textarea');
        // comment_text.className = "comment_text";
        // comment_text_container.append(comment_text);

        // 插入富文本编辑框
        var editor_container = document.createElement("div");
        editor_container.id = "editor-container";
        editor_container.className = "container";
        var editor_trigger = document.createElement("div");
        editor_trigger.id = "editor-trigger";
        var p = document.createElement("p");
        editor_trigger.appendChild(p);
        editor_container.appendChild(editor_trigger);
        comment_text_container.append(editor_container);
        create_rte();

        var send_btn = document.createElement('a');
        send_btn.className="send_btn";
        send_btn.innerText = "发送";
        send_btn.href = "javascript:void(0)";
        send_btn.setAttribute("onclick", "post_comment(this,"+post_id+")");
        comment_text_container.append(send_btn);

        // 获取这个帖子的所有评论
        var posts = get_comments(post_id);
        var comment_content_container = current_comment_container.find(".comment_content_container")[0];
        build_comment_tree(posts,comment_content_container);
    }

    /* 创建评论的HTML */
    function build_comment_tree(posts, comment_content_container) {
        if(posts.length>0){
            // 先进行清理工作

            $(comment_content_container).text("").children().remove();

            // 添加一个根ul
            var root_ul = document.createElement('ul');
            comment_content_container.appendChild(root_ul);

            // 循环每个帖子
            for(var key in posts){
                // 生成一个li节点，带comment_id，该li中也带一个ul用于存放子评论
                var li = document.createElement('li');
                li.setAttribute("comment_id", posts[key]['id']);
                li.setAttribute("display_name", posts[key]['user__display_name']);
                li.setAttribute("user_id", posts[key]['user_id']);

                // li的内容
                var comment_content_div = document.createElement('div'); // 评论的具体内容
                comment_content_div.className="comment_content_div";
                comment_content_div.setAttribute("onmouseover","show_reply_btn(this,true)");
                comment_content_div.setAttribute("onmouseout","show_reply_btn(this,false)");
                var display_name = posts[key]['user__display_name']==$("div.user_info #display_name").text() ? "我" : posts[key]['user__display_name'];
                comment_content_div.innerHTML = display_name +
                    ": " +
                    posts[key]['content']+
                    "　　"+
                    posts[key]['create_on'];

                var comment_bar = document.createElement('div');    // 针对该评论的工具栏
                var reply_a = document.createElement('a');
                reply_a.className="reply_btn hide";
                reply_a.innerText = "回复";
                reply_a.href = "javascript:void(0);";
                reply_a.setAttribute("onclick", "reply("+posts[key]['id']+",this)");
                //comment_bar.appendChild(reply_a);
                comment_content_div.innerHTML += reply_a.outerHTML;

                var comment_row = document.createElement('div');    // 一条评论的div，包括了以上两个div
                comment_row.className="comment_row";
                comment_row.appendChild(comment_content_div);
                comment_row.appendChild(comment_bar);

                li.appendChild(comment_row);    // 将整条评论+工具添加到li中

                // 用于存放子评论的ul，下方可以没有任何子评论
                var sub_ul = document.createElement('ul');
                li.appendChild(sub_ul);

                if(posts[key]['reply_to']){
                    // 评论有reply_to
                    $(comment_content_container).find("li[comment_id="+posts[key]['reply_to']+"]").children("ul").append(li);
                }else {
                    // 评论没有reply_to，将li加到根部的ul
                    root_ul.appendChild(li);
                }
            }

        }else{
            $(comment_content_container).text("暂时还没有评论");
        }
    }

    /**/
    function show_reply_btn(ele,show) {
        show?$(ele).find(".reply_btn:first").removeClass("hide"):$(ele).find(".reply_btn:first").addClass("hide")
    }

    /* 提交评论的内容 */
    function post_comment(ele, post_id) {
        var comment_obj = {};
        comment_obj['post']=post_id;
        // var ta = $(ele).siblings('textarea');   // 获取textarea的文本
        // comment_obj['comment_text'] = $.trim(ta.val());
        // comment_obj['comment_text'] = $.trim(ta.html());
        comment_obj['comment_text'] = "";
        var ta = $(ele).siblings("#editor-container").find("p");
        $(ta).each(function (k,p) {
            var html = p.innerHTML;
            if(html.length>0 && html!='<br>'){
                if(comment_obj['comment_text'].length>0){
                    comment_obj['comment_text'] += '<br>' + html;
                }else{
                    comment_obj['comment_text'] = html;
                }
            }
        });

        // alert(comment_obj['comment_text']);
        // return null;
        if(comment_obj['comment_text'].length==0){
            alert("请输入评论内容再提交");
            return false;
        }
        var reply_to = $(ele).siblings('#editor-container').attr("reply_to");
        if(reply_to){
            comment_obj['reply_to'] = reply_to;
        }
        // console.log(comment_obj);
        // return false;

        // ajax上传评论
        $.post({
            url:"/app01/post_comment/",
            data:comment_obj,
            dataType:"json",
            success:function (response) {
                if(response.status=='ok'){
                    // 评论成功
                    alert("评论成功");
                    var show_comments_btn = $(ele).parent().parent().parent().find('.show_comments_btn')[0];
                    show_comments(show_comments_btn, post_id)
                }
            }
        });
    }

    // //点击某个评论的回复按钮后，修改textarea的comment_id属性并让其得到焦点
    // function reply(comment_id, ele) {
    //     if(!is_login()){
    //         show_login_reg_frm();
    //         return false;
    //     }
    //     var reply_to_user = $(ele).parent().parent().parent().attr("display_name");
    //     $("textarea.comment_text").val("").attr("reply_to",comment_id).attr("placeholder","回复 "+reply_to_user).focus();
    // }

    // 点击某个评论的回复按钮后，修改富文本编辑器的comment_id属性并让其得到焦点
    function reply(comment_id, ele) {
        if(!is_login()){
            show_login_reg_frm();
            return false;
        }
        var reply_to_user = $(ele).parent().parent().parent().attr("display_name");
        $("div#editor-container").attr("reply_to",comment_id);
        $("div#editor-container p:gt(1)").remove();
        $("div#editor-container p:eq(1)").html("[回复 "+reply_to_user+"]&nbsp;");


        // .attr("placeholder","回复 "+reply_to_user).focus();
    }