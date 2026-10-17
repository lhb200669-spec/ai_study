
def find_anagrams(s: str, p: str) -> list[int]:
    res = []
    if len(s) < len(p):
        return res
    # 用大小为 26 的数组代替字典（只包含小写字母时更高效）
    p_count = [0] * 26
    s_count = [0] * 26
    # 统计 p 的字符频次
    for char in p:
        p_count[ord(char) - ord('a')] += 1
    left = 0
    for right in range(len(s)):
        # 1. 右边字符进入窗口
        right_idx = ord(s[right]) - ord('a')
        s_count[right_idx] += 1
        # 2. 窗口长度超过 p，左边字符移出窗口
        if right - left + 1 > len(p):
            left_idx = ord(s[left]) - ord('a')
            s_count[left_idx] -= 1
            left += 1
        # 3. 长度相等时直接比较两个数组（O(26) 很快）
        if s_count == p_count:
            res.append(left)
    return res
