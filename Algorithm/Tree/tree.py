'''
4
1 2 1 3 3 4 3 5

'''
def pre(v):
    if v:
        print(v)
        pre(ch1[v])
        pre(ch2[v])


e = int(input())
grid = list(map(int, input().split()))
v = e+1 # 정점 수

# 부모번호를 인덱스로 자식번호 저장
ch1 = [0]*(v+1)
ch2 = [0]*(v+1)
for i in range(e):
    p,c = grid[i*2], grid[i*2+1]
    if ch1[p] ==0:
        ch1[p] = c
    else:
        ch2[p] = c

# 부모 찾기
par = [0]*(v+1)
for i in range(e):
    p,c = grid[i*2], grid[i*2+1]
    par[c] = p


# root노드 찾기
root = 0
for i in range(1,+v+1):
    if p[i] ==0:
        root = i
        break

# 조상 찾기
c = 5
anc = []
while par[c] != 0:
    anc.append(par[c])
    c = par[c]
print(*anc)