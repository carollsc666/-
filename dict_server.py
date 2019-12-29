# dict_server.py
from socket import *
import os,sys
import time
import signal
import pymysql

class DictServer(object):
    def __init__(self,c,db):
        self.c = c
        self.db = db

    def do_login(self,data):
        print('登录操作')
        l = data.split(' ')
        name = l[1]
        passwd = l[2]
        cursor = self.db.cursor()
        sql = "select * from user where\
        name='%s' and passwd='%s'"%(name,passwd)
        cursor.execute(sql)
        r = cursor.fetchone()
        if r:
            self.c.send(b'OK')
        else:
            self.c.send(b'FAIL')

    def do_register(self,data):
        print('注册操作')
        l = data.split(' ')
        name = l[1]
        passwd = l[2]
        cursor = self.db.cursor()
        sql = "select * from user where name = '%s'"
        cursor.execute(sql)
        r = cursor.fetchone()
        if r != None:
            self.c.send(b'EXISTS')
            return
        sql = "insert into user (name,passwd) \
        values('%s','%s')"%(name,passwd)
        try:
            cursor.execute(sql)
            self.db.commit()
            self.c.send(b'OK')
        except:
            self.db.rollback()
            self.c.send('FAIL')
        else:
            print('%s注册成功'%name)
    def do_query(self,data):
        print('查询操作')
        l = data.split(' ')
        name = l[1]
        word = l[2]
        cursor = self.db.cursor()
        def insert_hist():
            tm = time.ctime()
            sql = "insert into hist (name,word,time) \
            values('%s','%s','%s')"%(name,word,tm)
            try:
                cursor.execute(sql)
                self.db.commit()
            except:
                self.db.rollback()
        #文本查询
        try:
            f = open(DICT_TEXT)
        except:
            c.send(b'FALL')
            return
        for line in f:
            tmp = line.split(' ')[0]
            if tmp > word:
                self.c.send(b'FALL')
                f.close()
                return
            elif tmp == word:
                self.c.send(b'OK')
                time.sleep(0.1)
                self.c.send(line.encode())
                f.close
                insert_hist()
                return
        self.c.send(b'FAIL')
        f.close()

    def do_hist(self,data):
        print('历史记录')
        l = data.split(' ')
        name = l[1]
        cursor = self.db.cursor()
        sql = "select * from hist where name='%s'"%name
        cursor.execute(sql)
        r = cursor.fetchall()
        if not r:
            self.c.send(b'FALL')
        else:
            self.c.send(b'OK')
        for i in r:
            time.sleep(0.1)
            msg = '%s    %s    %s'%(i[1],i[2],i[3])
            self.c.send(msg.encode()) 
        time.sleep(0.1)
        self.c.send(b'##') 
# 定义全局变量
DICT_TEXT = './dict.txt'
HOST = '127.0.0.1'
PORT = 8888
ADDR = (HOST,PORT)

def client_handle(c,ftp):
    data = c.recv(128).decode()
    print(c.getpeername(),':',data)
    if (not data) or data[0] == 'E':
        c.close()
        sys.exit('客户端退出！')
    elif data[0] == 'R':
        ftp.do_register(data)
    elif data[0] == 'L':
        ftp.do_login(data)
    elif data[0] == 'Q':
        ftp.do_query(data)
    elif data[0] == 'H':
        ftp.do_hist(data)


# 流程控制
def main():
    # 创建数据库连接
    db = pymysql.connect(\
    'localhost','root','123456',\
    'dict',charset='utf8')

    # 创建套接字
    s = socket()
    s.setsockopt(SOL_SOCKET,SO_REUSEADDR,1)
    s.bind(ADDR)
    s.listen(5)

    # 忽略子进程退出
    signal.signal(signal.SIGCHLD,\
        signal.SIG_IGN)

    while True:
        try:
            c,addr = s.accept()
            print('Connect from',addr)
        except KeyboardInterrupt:
            s.close()
            sys.exit('服务器退出！')
        except Exception as e:
            print(e)
            continue

        pid = os.fork()
        if pid == 0:
            s.close()
            print('子进程准备处理请求')
            ftp = DictServer(c,db)
            while True:
                client_handle(c,ftp)

        else:
            c.close()
            continue

if __name__ == '__main__':
    main()