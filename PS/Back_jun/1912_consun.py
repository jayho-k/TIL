'''
10
10 -4 3 1 5 6 -35 12 21 -1

'''

n = int(input())

lst = list(map(int,input().split()))

mx = lst[0]
sm = lst[0]












    # if sm+lst[end] < mx:
    #     mx = max(mx, sm+lst[end])
    #     sm += lst[end]
    #     end += 1

    # else:
    #     mx = max(mx, sm+lst[end])
    #     sm -= lst[st]
    #     st += 1

    print(mx)

print(mx)





# n = int(input())

# lst = list(map(int,input().split()))

# mx = lst[0]


# for i in range(1,len(lst)):
#     std = lst[i]
#     for j in range(i-1,-1,-1):
#         std += lst[j]
#         mx = max(mx, std)


# print(mx)