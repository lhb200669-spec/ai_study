from collections import deque

def max_sliding_window(nums: list[int], k: int) -> list[int]:
    dq = deque()
    res = []
    for i in range(len(nums)):
        # 1. 如果队首元素的下标已经不在当前窗口内（滑出去了），则弹出
        if dq and dq[0] < i - k + 1:
            dq.popleft()
        # 2. 维护单调递减：如果当前元素大于等于队尾元素，则把队尾元素弹出
        while dq and nums[dq[-1]] <= nums[i]:
            dq.pop()
        # 3. 将当前元素的下标加入队尾
        dq.append(i)
        # 4. 当遍历到第 k 个元素时（也就是窗口形成时），开始记录结果
        if i >= k - 1:
            res.append(nums[dq[0]])
    return res



