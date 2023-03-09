'''
뒤에서 부터


1
5 2
1 3
2 4	
// Test Case 개수
// 첫 번째 Test Case, N=5, Q=2
// i = 1일 때, L=1, R=3
// i = 2일 때, L=2, R=4
'''

for tc in range(1,int(input())+1):

    n,q = map(int,input().split())
    lst = [0]*(n+1)
    for i in range(1,q+1):
        l,r = map(int,input().split())
        for j in range(l,r+1):
            lst[j]=i
    print(f"#{tc}",*lst[1:])



    # tmp = []
    # for i in range(1,q+1):
    #     l,r = map(int,input().split())
    #     tmp.append((i,l,r))
    # print(tmp)






