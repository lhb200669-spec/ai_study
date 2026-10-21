import  multiprocessing as mp
import time
import os

def eat(time01, v):
    process = mp.current_process()
    pid = process.pid
    name = process.name
    print(f"当前进程的name为{name}, 进程号为{pid}")
    for _ in range(100):
        print(f"吃吃吃{v.value}")
        v.value += 1
        time.sleep(time01)

def sleep(time01, num, v):
    process = mp.current_process()
    pid = process.pid
    name = process.name
    print(f"当前进程的name为{name}, 进程号为{pid}")
    for _ in range(num):
        print(f"睡睡睡{v.value}")
        time.sleep(time01)

if __name__ == '__main__': #需要区分主进程和子进程, 必须要main
    v = mp.Value("i", 0)
    pid = os.getpid()
    ppid = os.getppid()
    print(f"主进程的pid为{pid}, ppid为{ppid}")
    process_eat = mp.Process(
        group = None, #固定为None
        target = eat, #这个进程要执行什么代码, 传入函数名
        name = "大胃王", #进程的名字
        args = (2, v), #函数位置传参
        # kwargs = {} #关键字传参
        daemon = False #子进程设置守护, 主进程代码执行完, 程序立刻结束(包括子进程)
    )

    process_sleep = mp.Process(
        group=None,  # 固定为None
        target=sleep,  # 这个进程要执行什么代码, 传入函数名
        name="懒虫",  # 进程的名字
        # args = (3, 10)
        kwargs = {"time01" : 3, "num" : 10, "v" : v}, #关键字传参
        # daemon = True
    )

    process_eat.start()
    process_sleep.start()

    time.sleep(10)

    process_eat.terminate()
    process_sleep.terminate() # 强制杀死进程

