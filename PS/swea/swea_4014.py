'''

1
6 2
3 3 3 2 1 1
3 3 3 2 2 1
3 3 3 3 3 2
2 2 3 2 2 2
2 2 3 2 2 2
2 2 2 2 2 2


1. left, right => 이전까지 연속된 개수가 몇개인지 누적합을 나타낸것
    ex) 3 3 3 2 1 1 
        left  => 1 2 3 1 1 2
        right => 3 2 1 1 2 1

2. 앞에 부터 차례대로 확인
    1) 이전 값이 더 작으면 left[이전 값] >= 길이
        => 좌측을 봤을 때 length만큼의 공간이 있는지 확인하는 것
        => check표시

    2) 이전 값이 더 크면 right[자기자신] >= 길이
        => 우측을 봤을 때 length만큼의 공간이 있는지 확인하는 것


'''
from pprint import pprint

def left_right(lst):

    left = [0]*n
    left[0] = 1
    for lx in range(1,n):
        if lst[lx-1]==lst[lx]:
            left[lx]=left[lx-1]+1
        else:
            left[lx]=1

    right = [0]*n
    right[n-1] = 1
    for rx in range(n-2,-1,-1):
        if lst[rx]==lst[rx+1]:
            right[rx]=right[rx+1]+1
        else:
            right[rx]=1

    return left,right

def play():
    cnt=0
    for y in range(n):
        lst = grid[y]
        left,right = left_right(lst)
        check = [0]*n
        flag = False

        for x in range(1,n):
            if abs(lst[x-1]-lst[x])>=2:
                break

            if lst[x-1] < lst[x] and left[x-1]>=length:
                for l in range(x-1,x-1-length,-1):
                    if check[l]:
                        flag=True
                        break
                    check[l]=1

            elif lst[x-1]>lst[x] and right[x]>=length:
                for r in range(x,x+length):
                    if check[r]:
                        flag=True
                        break
                    check[r]=1
            
            elif lst[x-1]==lst[x]:
                continue
            
            else:
                break

            if flag:
                break

        else:
            cnt+=1

    return cnt


for tc in range(1,int(input())+1):

    n,length = map(int,input().split())
    grid = [list(map(int,input().split())) for _ in range(n)]
    total = 0
    total+=play()

    grid = list(map(list,zip(*grid)))
    total+=play()

    print(f"#{tc} {total}")