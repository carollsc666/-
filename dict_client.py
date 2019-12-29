# dict_client.py
from socket import *
import sys
import getpass
'''getpass模块用于隐藏密码输入'''

def Argv():
    if len(sys.argv) < 3:
        HOST = input('请输入连接的地址：')
        PORT = int(input('请输入端口号：'))
        ADDR = (HOST,PORT)
        return ADDR
    elif len(sys.argv) == 3:
        HOST = sys.argv[1]
        PORT = int(sys.argv[2])
        ADDR = (HOST,PORT)
        return ADDR
    else:
        print('argv is error!')
        sys.exit(0)

def first_page():
    print('''
        =============welcome============
        １．注册　　２．登录　　３．退出
        ================================
        ''')

def second_page():
    print('''
        =============查询界面============
        １．查词　　２．历史记录　　３．退出
        ================================
        ''')

def do_register(s):
    while True:
        name = input('Username:')
        passwd = getpass.getpass('Password:')
        passwd1 = getpass.getpass('Again:')
        if passwd1 != passwd:
            print('两次密码不一致！')
            continue
        elif (' ' in name) or (' ' in passwd):
            print('不允许有空格！')
            continue
        msg = 'R {} {}'.format(name,passwd)
        # 发送请求
        s.send(msg.encode())
        # 等待回复
        data = s.recv(128).decode()
        print(data)
        if data == 'OK':
            return 0
        elif data == 'EXISTS':
            return 1
        else:
            return 2

def do_login(s):
    name = input('User:')
    passwd = getpass.getpass()
    msg = "L {} {}".format(name,passwd)
    s.send(msg.encode())
    data = s.recv(128).decode()
    if data == 'OK':
        return name
    else:
        return

def do_query(s,name):
    while True:
        word = input('请输入要查的单词(输入##退出)：')
        if word == '##':
            break
        msg = 'Q {} {}'.format(name,word)
        s.send(msg.encode())
        data = s.recv(1024).decode()
        if data == 'OK':
            data = s.recv(2048).decode()
            print(data)
        else:
            print('没有查到该单词') 

def do_hist(s,name):
    msg = 'H {}'.format(name)
    s.send(msg.encode())
    data = s.recv(1024).decode()
    if data == "OK":
        while True:
            data = s.recv(1024).decode()
            if data == '##':
                break
            print(data)
    else:
        print('没有历史记录')
    

def login(s,name):
    while True:
        second_page()
        try:
            cmd = int(input('请输入选项>>'))
        except Exception as e:
            print('命令错误')
            continue
        if cmd not in [1,2,3]:
            print('请输入正确选项')
            # 清理标准输入
            sys.stdin.flush()
            continue
        elif cmd == 1:
            do_query(s,name)
        elif cmd == 2:
            do_hist(s,name)
        else:
            return

def main():
    ADDR = Argv()
    s = socket()
    try:
        s.connect(ADDR)
    except Exception as e:
        print(e)
        return

    while True:
        first_page()
        try:
            cmd = int(input('请输入选项>>'))
        except Exception as e:
            print('命令错误')
            continue
        if cmd not in [1,2,3]:
            print('请输入正确选项')
            # 清理标准输入
            sys.stdin.flush()
            continue
        elif cmd == 1:
            r = do_register(s)
            if r == 0:
                print('注册成功！')
                #直接进入二级界面
                # login(s,name) 
            elif r == 1:
                print('用户存在')
            else:
                print('注册失败')
        elif cmd == 2:
            name = do_login(s)
            if name:
                print('登录成功')
                login(s,name)
            else:
                print('用户名或密码不正确')
        elif cmd == 3:
            s.send(b'E')
            sys.exit('退出')



if __name__ == '__main__':
    main()