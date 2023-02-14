'''
Mississipi
'''
from collections import Counter
def play(cnt):
    mx = 0
    for c in cnt:
        if mx < cnt[c]:
            mx = cnt[c]
        elif mx==cnt[c]:
            return "?"
    return mx
s = input()
cnt = Counter(s.lower())
print(cnt)
print(play(cnt))