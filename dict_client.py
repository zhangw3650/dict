#!/usr/bin/env python3
# coding=utf-8

from socket import *
import sys
import getpass


# 创建网络链接
def main():
    if len(sys.argv) == 0:
        print("argv is error")
        return
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])

    s = socket()
    try:
        s.connect((HOST, PORT))
    except Exception as e:
        print(e)
        return

    while True:
        print('''
            =========Welcome========
            --1.注册  2.登录  3.退出--
            ========================
            ''')
        try:
            cmd = int(input("输入选项>>"))
        except Exception as e:
            print("命令错误")
            continue
        if cmd not in [1, 2, 3]:
            print("请输入正确选项")
            sys.stdin.flush()  # 清楚标准输入缓冲区
            continue
        elif cmd == 1:
            r = do_regiter(s)
            if r == 0:
                print("注册成功")
                # login(s, name)  直接进入二级界面
            elif r == 1:
                print("用户存在")
            else:
                print("注册失败")
        elif cmd == 2:
            name = do_login(s)
            if name:
                print("登录成功")
                login(s, name)
            else:
                print("用户名或密码不正确")
        elif cmd == 3:
            msg = "E {}".format(name)
            s.send(msg.encode())
            sys.exit("谢谢使用")


def do_regiter(s):
    while True:
        name = input('User:')
        passwd = getpass.getpass()
        passwd1 = getpass.getpass('Again:')
        if (' ' in name) or (' ' in passwd):
            print("用户名和密码不能为空")
            continue
        if passwd != passwd1:
            print("两次密码不一致")
            continue
        msg = 'R {} {}'.format(name, passwd)
        s.send(msg.encode())
        data = s.recv(128).decode()
        if data == "OK":
            return 0
        elif data == 'EXISTS':
            return 1
        else:
            return


def do_login(s):
    name = input('User:')
    passwd = getpass.getpass()
    msg = 'L {} {}'.format(name, passwd)
    s.send(msg.encode())
    data = s.recv(128).decode()
    if data == 'OK':
        return name
    else:
        return


def login(s, name):
    while True:
        print('''
            ==========Welcome==========
            --1.查词  2.历史记录  3.退出--
            ===========================
            ''')
        try:
            cmd = int(input("输入选项>>"))
        except Exception:
            print("命令错误")
            continue
        if cmd not in [1, 2, 3]:
            print("请输入正确选项")
            sys.stdin.flush()  # 清楚标准输入缓冲区
            continue
        elif cmd == 1:
            do_query(s, name)
        elif cmd == 2:
            do_hist(s, name)
        elif cmd == 3:
            return


def do_query(s, name):
    while True:
        word = input('单词:')
        if word == '##':
            return
        msg = "Q {} {}".format(name, word)
        s.send(msg.encode())
        data = s.recv(128).decode()
        if data == 'OK':
            data = s.recv(2048).decode()
            print(data)
        else:
            print("sorry,没有该单词")


def do_hist(s, name):
    msg = "H {}".format(name)
    s.send(msg.encode())
    data = s.recv(128).decode()
    if data == 'OK':
        while True:
            data = s.recv(1024).decode()
            if data == '##':
                break
            print(data)
    else:
        print("没有历史记录")


if __name__ == "__main__":
    main()
