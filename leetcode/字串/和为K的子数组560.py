from collections import defaultdict

def subarray_sum(nums: list[int], k: int) -> int:
    count = 0
    prefix = 0
    # 记录每个前缀和出现的次数
    seen = defaultdict(int)
    seen[0] = 1  # 空前缀，处理从下标 0 开始的子数组
    for x in nums:
        prefix += x
        # 若存在 prefix - k，说明有一段子数组和为 k
        count += seen[prefix - k]
        seen[prefix] += 1
    return count