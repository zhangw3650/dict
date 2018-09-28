#!/usr/bin/env python3
# coding=utf-8

'''
name:  zhangw
email: 297960393@qq.com
date:  2018-9
introduce: dict server
env : python3.6
'''

from socket import *
import os
import time
import signal
import pymysql
import sys


# 定义需要的全局变量
DICT_TEXT = './dict.txt'
HOST = '0.0.0.0'
PORT = 8888
ADDR = (HOST, PORT)


# 控制流程
def main():
    # 创建数据库连接
    db = pymysql.connect('localhost', 'zhangw', '123456', 'dict')

    # 创建套接字
    s = socket()
    s.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    s.bind(ADDR)
    s.listen(5)

    # 忽略子进程退出信号 避免僵尸进程产生
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    # 循环等待连接
    print("Waiting for connect...")
    while True:
        try:
            c, addr = s.accept()
            print("connect from", addr)
        except Exception as e:
            print(e)
            continue

        # 连接成功，创建子进程
        pid = os.fork()
        if pid == 0:
            # 子进程关闭通讯服务端套接字
            s.close()
            do_child(c, db)
        else:
            # 父进程关闭客户端套接字，继续等待客户连接
            c.close()
            continue


def do_child(c, db):
    # 循环接收客户端请求
    while True:
        data = c.recv(1024).decode()
        if not data:
            c.close()
            sys.exit("未知客户端异常退出")
        elif data[0] == 'E':
            c.close()
            sys.exit("%s已退出" % data.split(' ')[1])
        elif data[0] == 'R':
            do_register(c, db, data)
        elif data[0] == 'L':
            do_login(c, db, data)
        elif data[0] == 'Q':
            do_query(c, db, data)
        elif data[0] == 'H':
            do_hist(c, db, data)


def do_login(c, db, data):
    print("登录操作")
    L = data.split(' ')
    name = L[1]
    passwd = L[2]
    cursor = db.cursor()
    sql = "select * from user where name='%s' and \
        passwd='%s';" % (name, passwd)
    cursor.execute(sql)
    r = cursor.fetchone()
    if not r:
        c.send(b'FALL')
    else:
        c.send(b'OK')
        print("%s登录成功" % name)


def do_register(c, db, data):
    print("注册操作")
    L = data.split(' ')
    name = L[1]
    passwd = L[2]
    cursor = db.cursor()

    # 查询用户是否存在
    sql = "select * from \
        user where name='%s';" % name
    cursor.execute(sql)
    r = cursor.fetchone()
    if r:
        c.send(b'EXISTS')
        return

    sql = "insert into user(name,passwd) \
            values('%s', '%s');" % (name, passwd)
    try:
        cursor.execute(sql)
        db.commit()
        c.send(b'OK')
    except Exception:
        db.rollback()
        c.send(b'FALL')
    else:
        print("%s注册成功" % name)


def do_query(c, db, data):
    print("查词操作")
    L = data.split(' ')
    name = L[1]
    word = L[2]
    cursor = db.cursor()

    def insert_histor():
        tmp = time.ctime()
        sql = "insert into hist(name,word,time) \
        values('%s','%s','%s');" % (name, word, tmp)
        try:
            cursor.execute(sql)
            db.commit()
        except Exception:
            db.rollback()

    # 文本查询
    try:
        f = open(DICT_TEXT)
    except Exception:
        c.send(b'FALL')
        return
    for line in f:
        tmp = line.split(' ')[0]
        if tmp > word:
            c.send(b'FALL')
            f.close()
            return
        elif tmp == word:
            c.send(b'OK')
            time.sleep(0.1)
            c.send(line.encode())
            f.close()
            insert_histor()
            return
    else:
        c.send(b'FALL')
        f.close()


def do_hist(c, db, data):
    print("查历史操作")
    name = data.split(' ')[1]
    cursor = db.cursor()
    sql = "select * from hist where name='%s';" % name
    cursor.execute(sql)
    r = cursor.fetchall()
    if not r:
        c.send(b'FALL')
        return
    else:
        c.send(b'OK')

    for i in r:
        time.sleep(0.1)
        msg = "%s\t%s\t%s" % (i[1], i[2], i[3])
        c.send(msg.encode())
    time.sleep(0.1)
    c.send(b'##')


if __name__ == "__main__":
    main()
