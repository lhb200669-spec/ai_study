import multiprocessing as mp
import time
from multiprocessing.synchronize import Lock


def w1(v: mp.Value, lock:Lock):
    for i in range(100000):
        lock.acquire()
        v.value += 1
        lock.release()

def w2(v: mp.Value, lock:Lock):
    for i in range(100000):
        lock.acquire()
        v.value += 1
        lock.release()

if __name__ == '__main__':
    v = mp.Value("i", 0)
    lock = mp.Lock() #上锁, 可以保证数据安全
    w1_p = mp.Process(target=w1, args=(v, lock))
    w2_p = mp.Process(target=w2, args=(v, lock))

    s = time.time()
    w1_p.start()
    w2_p.start()

    w1_p.join()
    w2_p.join()
    e = time.time()

    print(v.value)
    print(f"时间: {e - s}")
