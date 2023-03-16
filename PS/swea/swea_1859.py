'''
1. 원재는 연속된 N일 동안의 물건의 매매가를 예측하여 알고 있다.
2. 당국의 감시망에 걸리지 않기 위해 하루에 최대 1만큼 구입할 수 있다.
3. 판매는 얼마든지 할 수 있다.

예를 들어 3일 동안의 매매가가 1, 2, 3 이라면 처음 두 날에 원료를 구매하여 
마지막 날에 팔면 3의 이익을 얻을 수 있다.

==> max값을 계속해서 찾아야하는 문제
==> 두가지 방법
    1. 뒤에서 찾는 방법 
        => mx보다 작으면 저장해놓는 방식
        => mx보다 크면 mx값 저장해놓은 것 팔고 mx값 체인지

    2. 앞에서 찾는 방법

3
3
10 7 6
3
3 5 9
5
1 1 3 1 2

3
5
1 1 3 1 100
8
1 1 3 1 100 6 5 4
10
1 1 3 1 100 1 6 4 3 5

'''
# 
for tc in range(1,int(input())+1):
    n = int(input())
    lst = list(map(int,input().split()))
    mx = 0
    store = 0
    total = 0
    for i in range(n-1,-1,-1):
        if mx<lst[i]:
            mx = lst[i]
            total += store
            store = 0

        elif mx>lst[i]:
            store+=(mx-lst[i])

    if store:
        total+=store
    
    print(f"#{tc} {total}")














# def find_max(lst,slice_lst):
#     if slice_lst:
#         return lst.index(max(slice_lst))
    
#     return -1

# for tc in range(1,int(input())+1):
#     n = int(input())
#     lst = list(map(int,input().split()))
#     ans = 0
#     mx_idx = find_max(lst,lst[:])
#     for i in range(n):
#         if i < mx_idx and lst[mx_idx]>lst[i]:
#             ans+=lst[mx_idx]-lst[i]
#             # print("@@@@",lst[mx_idx],lst[i])
#         else:
#             mx_idx = find_max(lst,lst[i+1:])

#     print(f"#{tc}",ans)

# def make_biglist(lst):
#     big_lst = []
#     for i in range(len(lst)):
#         big_lst.append((lst[i],i))

#     big_lst.sort(key=lambda x : (-x[0],x[1]))
#     return big_lst

# for tc in range(1,int(input())+1):
#     n = int(input())
#     lst = list(map(int,input().split()))
#     big_lst = make_biglist(lst)
    
#     ans = 0
#     i = 0
#     # j = lst index
#     # i = big_lst index
#     for j in range(n):
#         if i>=n-1:
#             break
#         bv,bi = big_lst[i]
#         if j<bi and bv>lst[j]:
#             # print("@@@@",bv,lst[j])
#             ans += bv-lst[j]

#         elif j==bi and bv<=lst[j]:
#             while 1:
#                 wbv, wbi = big_lst[i]
#                 if j<wbi or i>=n-1:
#                     break
#                 i+=1

#     print(f"#{tc}",ans)