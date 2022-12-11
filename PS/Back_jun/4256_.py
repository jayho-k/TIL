'''


4
3 2 1 4
2 3 4 1

8
3 6 5 4 8 7 1 2
5 6 8 4 3 1 2 7

'''
def findSomthing(pre,inor,idx):
    
    # if node == None:
    #     return
    
    if len(pre)==0:
        return

    elif len(pre)==1:
        print(pre[0], end=' ')
        return

    # 이부분이 문제가 있음
    elif len(pre) == 2:
        print(pre[1],pre[0],end=' ')
        return
    
    sp_idx = inor.index(pre[0])
    left_lst = inor[:sp_idx]
    left_pre = pre[1:len(left_lst)+1]
    
    right_lst = inor[sp_idx+1:]
    right_pre = pre[len(left_lst)+1:]

    # # left
    # for i in range(idx,len(pre)):
    #     if pre[i] in left_lst:
    #         left = pre[i]
    #         idx = i
    #         break
    # else:
    #     left = None

    # # right
    # if right_lst:
    #     right = right_lst[-1]
    # else:
    #     right = None

    findSomthing(left_pre,left_lst,idx)
    findSomthing(right_pre,right_lst,idx)
    print(pre[0], end=' ')
    # tmp.append(node)

T = int(input())
for _ in range(1,T+1):
    n = int(input())
    pre = list(map(int,input().split()))
    inor = list(map(int,input().split()))
    root = pre[0]
    tmp = []
    findSomthing(pre,inor,0)
    print()
    # print(*tmp)