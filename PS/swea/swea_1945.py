'''
10  
6791400
1646400
1425600
8575
185625
6480
1185408
6561
25
330750

'''
def find_div(n):
    lst = [2,3,5,7,11]
    ans = [0,0,0,0,0]
    for i in range(len(lst)):
        while n%lst[i]==0 and n!=0:
            ans[i]+=1
            n=n//lst[i]

    return ans

for tc in range(1,int(input())+1):
    n = int(input())
    a = find_div(n)
    print(f"#{tc}",*a)

