# ---
# @Software: PyCharm
# @File: BlackList_Fw.py
# @Author: jojoli
# @Site: 启明防火墙批量黑名单脚本
# @Time: 4月 12, 2021
# ---
import time
import paramiko
import argparse
from colorama import init

init(autoreset=True)
# 发送paramiko日志到syslogin.log文件
paramiko.util.log_to_file('syslogin.log')
userinfo = {}

def main():
    global userinfo

    # 初始化argparse对象
    parse = argparse.ArgumentParser()
    # 获取登录IP
    parse.add_argument("-i", "--ip", type=str, dest="Hosts", help="Please input hosts")
    # 获取登录端口，默认22
    parse.add_argument("-p", "--port", type=int, dest="Port", help="Please input ssh port", default=22)
    #获取登录账号，默认root
    parse.add_argument("-u", "--user", type=str, dest="User", help="Please input username", default="root")
    # 获取登录密码
    parse.add_argument("-s", "--password", type=str, dest="Password", help="Please input password")
    # 获取黑名单文件,默认blacklist.txt
    parse.add_argument("-f", "--file", type=str, dest="File", help="Please input file path", default='blacklist.txt')
    options = parse.parse_args()
    IP = options.Hosts
    Port = options.Port
    User = options.User
    Pass = options.Password
    File = options.File
    print("\033[1;37;40m\t请核对输入信息\033[0m\n")
    print('\033[1;37;40m\t登录IP为{}:\033[0m\n'.format(IP))
    print("\033[1;37;40m\t登录端口为{}:\033[0m\n".format(Port))
    print("\033[1;37;40m\t登录账号为{}:\033[0m\n".format(User))
    print("\033[1;37;40m\t登录密码为{}:\033[0m\n".format(Pass))
    print("\033[1;37;40m\t获取黑名单文件为{}:\033[0m\n".format(File))
    userinfo['host'] = IP
    userinfo['port'] = Port
    userinfo['user'] = User
    userinfo['passwd'] = Pass
    userinfo['file'] = File
    return userinfo

def remote_login(userinfo):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(userinfo['host'], userinfo['port'], userinfo['user'], userinfo['passwd'], timeout=2)
        return ssh
    except Exception as e:
        print(e)
        return None

def get_info(userinfo):
    #登录防火墙
    client = remote_login(userinfo)
    if client is None:
        print(u'\033[31m登录失败，跳过\033[0m')
        return None
    # 获取防火墙规则
    print(u'\033[37;44m\t防火墙登录成功，请稍后\033[0m')
    result = ""
    time2 = time.time()
    try:
        #交换机等设备使用SSHClient().invoke_shell()
        remote_conn = client.invoke_shell()
        time.sleep(4)
        #抓取记录超过屏幕长度的命令输出
        remote_conn.send('terminal length 0\n')
        time.sleep(1)
        result1 = str(remote_conn.recv(1024))
        print(result1)
        remote_conn.send('enable\n')
        time.sleep(1)
        result2 = str(remote_conn.recv(1024))
        print(result2)
        remote_conn.send('conf t\n')
        time.sleep(1)
        result3 = str(remote_conn.recv(1024))
        print(result3)
        b = 0
        with open(userinfo['file'], 'r') as f:
            for a in f.readlines():
                a = a.split()
                a = a[0]
                command = 'blacklist-ip '+a+' timeout 0\n'
                if a is None:
                    print('请输入正确IP')
                    pass
                else:
                    print('\033[37;42m\t开始添加黑名单{}\033[0m'.format(command))
                    remote_conn.send(command)
                    result += str(remote_conn.recv(1024))+'\n'
                    b = b+1
            print('\033[37;46m\t黑名单添加完成，共添加{}个黑名单\033[0m'.format(b))
            print(result)
        # 当前时间
        time1 = time.localtime()

        time_start = time.strftime("%Y%m%d%H%M", time1)
        with open(time_start + '_黑名单添加结果.txt', 'w') as a:
            print(result, file=a)
    except Exception as e:
        print(e)
    finally:
        client.close()
        print('\033[37;46m\t共耗时{}秒\033[0m'.format(time.time()-time2))

if __name__ == '__main__':
    userinfo = main()
    get_info(userinfo)
