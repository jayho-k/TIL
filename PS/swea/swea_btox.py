'''
16진수를 2진수로 만들기
3
4 47FE
5 79E12
8 41DA16CD
'''
def b(i):
    s = ''
    for j in range(3,-1,-1):
        if i & (1<<j):
            s+='1'
        else:
            s+='0'
    return s

dic = {'A':10,'B':11,'C':12,'D':13,'E':14,'F':15}
T = int(input())
for tc in range(1,T+1):

    n, lst = input().split()
    n = int(n)
    lst = list(lst)

    tmp = []
    for l in lst:
        if l in dic:
            tmp.append(dic[l])
        else:
            tmp.append(int(l))

    ans = ''
    for t in tmp:
        ans += b(t)

    print(f'#{tc} {ans}')

