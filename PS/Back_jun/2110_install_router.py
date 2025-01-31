'''
5 3
1
2
8
4
9

'''

def check(distance, c):
    # c개를 distance 간격으로 설치가 가능한지
    # distance간격으로 설치를 했을 때

    now = houses[0]
    cnt = 1
    for i in range(1,len(houses)):
        if distance <= houses[i]-now:
            cnt += 1
            now = houses[i]
    return cnt>=c

n,c = map(int,input().split())
houses = [int(input()) for _ in range(n)]
houses.sort()

start = 1
end = houses[-1]-houses[0]
while start <= end: # 이거 땜에 틀림 => start end가 거리라서 +1로 가면 틀림 => start <= end로 가는게 좋을 거가틍ㅁ = 
    mid = (start+end)//2
    #print("start, end, mid : " , start, end, mid)
    if check(mid,c):
        start = mid+1
    else:
        end = mid-1
        

print(end)

# print(start)
# print(end)
# print(mid)


# def caculate(mid):
#     cnt = 1
#     now = lst[0]
#     for i in range(1,len(lst)):
#         if lst[i]>=mid+now:
#             cnt+=1
#             now = lst[i]
#     return cnt


# n,c = map(int,input().split())
# lst = [int(input()) for _ in range(n)]
# lst.sort()

# # 초기화
# start = 1
# end = lst[-1]-lst[0]
# while start<=end:
#     mid = (start+end)//2
#     if caculate(mid)>=c:
#         start = mid+1

#     else:
#         end = mid-1

# print(end)

