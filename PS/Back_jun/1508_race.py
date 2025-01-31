"""

11 3 4
0 5 10 11

20 3 4
0 5 10 15

1110
"""


def person_cnt(dist):

    cnt = 1
    now = possible[0]
    position_lst = ["1"]

    for i in range(1,len(possible)):
        # dist <= 심판 앞뒤 간격 and 이미 cnt 넘겼는지 확인
        if dist <= possible[i]-now and cnt < m:
            cnt += 1
            now = possible[i]
            position_lst.append("1")
        else:
            position_lst.append("0")
    
    return cnt, ''.join(position_lst)


def compare(cnt,dist,position, ans):

    # 심판사이의 거리 max 구하기, cnt = 심판 수, m : 요구한 심판 수
    if cnt==m and ans[1] < dist:
        ans = (position, dist)

    return ans

# 포지션, 심판사이 거리
ans = ("",0)

n,m,k = map(int,input().split())
possible = list(map(int,input().split()))

start = 0
end = possible[-1]-possible[0]

while start <= end:
    mid = (start+end)//2
    cnt,position = person_cnt(mid)
    ans = compare(cnt,mid,position,ans)

    if cnt>=m:
        start = mid+1
    else:
        end = mid-1

print(ans[0])
