"""
python中的线程比较特殊,由于gil的原因
python中的多线程不能享受多核cpu的服务, 只能单核cpu并发执行
"""
import time
import threading

def eat():
    print("吃")
    time.sleep(5)
    print("吃完了")

def sleep():
    print("要睡了")
    time.sleep(7)
    print("爽了")

if __name__ == '__main__':
    thread_eat = threading.Thread(target=eat, name = "食神")
    thread_sleep = threading.Thread(target=sleep, name = "睡神")

    thread_eat.start()
    thread_sleep.start()