#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @Author  : Coosh
# @File    : main.py
import json, os, glob, shutil

APP_DIR = os.path.dirname(os.path.abspath(__file__))
CONF_DIR = os.path.join(APP_DIR, 'conf')
CONF_FILE = os.path.join(CONF_DIR, 'haproxy.cfg')
TMP_CONF_FILE = os.path.join(CONF_DIR, 'haproxy.cfg.tmp')


def display_backend_info():
    """
    用户输入backend名称，展示里面的信息
    如找不到backend，则显示提示信息
    """
    global CONF_FILE
    backend_name = input('请输入backend：').strip()
    keyword = "backend " + backend_name
    interest_flag = False
    result_str = ''
    with open(CONF_FILE) as conf_f:
        for line in conf_f:
            line = line.rstrip()
            if not interest_flag and line != keyword:
                # 如果既不感兴趣，也是不keyword行，将跳过
                continue
            elif interest_flag and not line:
                # 如果是感兴趣的行，且为空行，那么就是感兴趣区域的结束行，关闭感兴趣标记，并跳过
                interest_flag = False
                continue
            else:
                # 其他感兴趣且非空行，或者keyword行均打印，并且标记已找到结果
                interest_flag = True
                result_str += line + '\n'
    if result_str:
        print('结果如下'.center(60, '*'))
        print(result_str)
        print('*' * 64)
    else:
        print('没有您要的backend信息。'.center(64, '*'))


def add_record():
    """
    用户输入一个json格式的字符串，往haproxy.cfg里相应的backend添加record
    如果backend不存在，则创建并添加
    如果record不存在，则添加
    如果record已存在，则修改
    :return:
    """
    interest_flag = False
    has_updated_flag = False
    dict_json = input("请输入您要增加的信息（json格式）：").strip()
    try:
        new_record_dict = json.loads(dict_json)
        backend_line = "backend {backend_name}".format(backend_name=new_record_dict['backend'])
        new_record_line = "        server {r_server} {r_server} weight {r_wt} maxconn {r_mc}\n"\
            .format(r_server=new_record_dict['record']['server'],
                    r_wt=new_record_dict['record']['weight'],
                    r_mc=new_record_dict['record']['maxconn'])
        with open(CONF_FILE) as cfg, open(TMP_CONF_FILE, 'w') as tmp:
            for line in cfg:
                if not has_updated_flag:
                    # 如果没有更新过record则进行以下判断，
                    # 如果已更新过，则无需在对后续内容进行判断，可以提高效率
                    if line.rstrip() == backend_line:
                        # 如果该行是backend行，那么对接下来的内容感兴趣
                        interest_flag = True
                    elif interest_flag:
                        # 该行属于感兴趣
                        if not line.strip():
                            # 如果是感兴趣区域的空行，视为感兴趣的结束行
                            if not has_updated_flag:
                                # 如果在感兴趣区域结束时，仍没有更新过，那么将在结束行前，插入新record，并打上更新标记
                                line = new_record_line + '\n'
                                has_updated_flag = True
                            interest_flag = False
                        elif line.strip().startswith('server') and (new_record_dict['record']['server']+' ' in line):
                            # 如果该行是record行，且包含用户输入的record的ip地址，则替换line内容
                            line = new_record_line
                            # 打上更新标记
                            has_updated_flag = True
                # 将line内容写入haproxy.cfg.tmp
                tmp.write(line)

            if interest_flag and not has_updated_flag:
                # 如果感兴趣区域位于底部，需要补一刀
                tmp.write(new_record_line)
                has_updated_flag = True

            if not has_updated_flag:
                # 如果遍历过所有行，都没有找到backend，则在文件末尾添加
                tmp.write('\n\n' + backend_line + '\n' + new_record_line)
        # 切换配置文件
        switch_file()
        return True
    except json.JSONDecodeError:
        print("您的输入有误，请检查后重新输入".center(64, '*'))
        return False


def remove_record():
    """
    用户输入一个json格式的字符串，往haproxy.cfg里相应的backend删除record
    如果record不存在，则不做任何事情，并返回false
    如果record存在且仅有一条，则删除整个backend信息，返回True
    如果record存在但仍有其他record，则只删除用户指定的record，其他不管，返回True
    :return:
    """
    interest_flag = False
    removed_flag = False
    truncated_flag = False
    backend_has_other_record = False
    dict_json = input("请输入您要删除的信息（json格式）：").strip()
    try:
        remove_record_dict = json.loads(dict_json)
        remove_record_line = "        server {r_server} {r_server} weight {r_wt} maxconn {r_mc}"\
            .format(r_server=remove_record_dict['record']['server'],
                    r_wt=remove_record_dict['record']['weight'],
                    r_mc=remove_record_dict['record']['maxconn'])
        with open(CONF_FILE) as cfg, open(TMP_CONF_FILE, 'w') as tmp:
            for line in cfg:
                if line.startswith('backend ' + remove_record_dict['backend']):
                    # 接下里的内容是感兴趣区域
                    interest_flag = True
                    # 记录tmp文件的当前指针位置，如果没有record，则需要删除整个backend
                    tmp_backend_pointer = tmp.tell()
                if interest_flag and line.strip().startswith('server'):
                    # 如果感兴趣区域里，行首以server开头则判断
                    if remove_record_line in line:
                        # 如果该行是要移除的record字符串，则不进行记录，并标记已进行移除工作
                        removed_flag = True
                        continue
                    else:
                        # 如果改行是另外的record记录，则代表该backend还有其他的record
                        backend_has_other_record = True
                if interest_flag and not line.strip():
                    # 感兴趣区域的空行代表感兴趣区域的结束
                    interest_flag = False
                    # 感兴趣区域的结束，需要进行清理工作
                    if not backend_has_other_record:
                        # 如果backend没有其他record，则清理整个backend
                        tmp.seek(tmp_backend_pointer)
                        tmp.truncate()
                        truncated_flag = True
                # 将line写入临时文件
                tmp.write(line)

            if removed_flag and not backend_has_other_record and not truncated_flag:
                # 针对感兴趣区域在文件末尾的清理工作
                # 如果移除过记录，backend没有其他record，并且未进行truncate
                tmp.seek(tmp_backend_pointer)
                tmp.truncate()

        # 切换配置文件
        switch_file()
        return removed_flag
    except json.JSONDecodeError:
        print("您的输入有误，请检查后重新输入".center(64, '*'))
        return False


def switch_file():
    """
    用于切换新旧haproxy.cfg，原有的haproxy.cfg改名类似为haproxy.cfg.v1（版本号结尾）
    新文件（haproxy.cfg.tmp）如果存在，就更名为haproxy.cfg
    :return: 切换成功后返回True
    """
    try:
        # 获取conf目录下的已有备份文件版本，并生成新版本号new_version_num
        new_version_num = 1
        common_str = os.path.join(CONF_DIR, 'haproxy.cfg.v')
        for fn in glob.glob(common_str + '*'):
            ver = fn.replace(common_str, '')
            if ver.isdigit():
                ver = int(ver)
                if ver >= new_version_num:
                    new_version_num = ver + 1
        # 新的备份文件绝对路径
        new_backup_fn = "{conf_fn}.v{ver}".format(conf_fn=CONF_FILE, ver=str(new_version_num))
        # 进行备份
        shutil.copy(CONF_FILE, new_backup_fn)
        # 如果haproxy.cfg.tmp文件存在，则替换原有配置文件
        if os.path.isfile(TMP_CONF_FILE):
            shutil.move(TMP_CONF_FILE, CONF_FILE)
        return True
    except:
        return False


if __name__ == '__main__':
    while True:
        print("""
============================
    1、获取ha记录
    2、增加ha记录
    3、删除ha记录
    4、切换配置文件

    (q)退出""")
        user_choice = input('请选择：')
        if user_choice == '1':
            display_backend_info()
        elif user_choice == '2':
            if add_record():
                print("增加成功！")
            else:
                print("增加失败...")
        elif user_choice == '3':
            if remove_record():
                print("删除成功!")
            else:
                print("删除失败...")
        elif user_choice == '4':
            switch_file()
        elif user_choice == 'q':
            exit()
        else:
            print("您的输入有误，请重新输入")
