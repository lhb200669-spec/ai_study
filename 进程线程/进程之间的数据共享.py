import multiprocessing as mp
import time
import random

def w1(queue):
    for _ in range(100):
        num = random.randint(1, 1000)
        queue.put(num)
        print(f"w1放入: {num}")
        time.sleep(1)

def w2(queue):
    while True:
        num = queue.get() #阻塞等待
        if num % 2 == 0:
            print(f"w2, 偶数: {num}")
        else:
            print(f"w2, 奇数: {num}")

if __name__ == '__main__':
    q = mp.Queue()
    mp.Process(target=w1, args=(q,)).start()
    mp.Process(target=w2, args=(q,)).start()