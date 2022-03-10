'''
3가지 연산 가능
1. 첫번째 원소 뽑아냄
2. 외쪽이동
3. 오른쪽 이동

2, 3의 연산을 최소로 = 최대한 1을 많이 사용(순서대로)

n m 
10 3
2 9 5 
==> 8
뽑아내려고 하는 수의 위치

1,2,3,4,5,6,7,8,9,10

더 짧은 쪽으로 로데이션을 돌릴것이기 때문에
1. fornt <= rear
    왼쪽으로
    맨 앞이 있는 것을 맨 뒤에 붙히고
    맨 앞이 있는 것을 지운다 ==> del[0]

2. front > rear
    오른쪽으로
    맨 뒤에 있는 것을 지우고 ==> s= pop()
    맨 앞에 붙힌다 s를 앞에 붙혀준다 ==> insert

'''
def l_rot(lst):
    p = lst[0]
    lst.append(p)
    lst.remove(p)

def r_rot(lst):
    s = lst.pop()
    lst.insert(0,s)

n, m = map(int, input().split())
# n은 가지고 있는 큐의 크기 , m은 뽑아내려고 하는 개수

t_lst = list(map(int, input().split()))
lst = list(range(1, n+1))
q_lst = []
oolst = []

cnt = 0
for i in range(len(t_lst)):

    t = t_lst[i]

    t_lo = lst.index(t) + 1
    front = lst.index(t)
    rear = len(lst) - t_lo

    if front <= rear:
        while lst[0] != t:
            l_rot(lst)
            cnt += 1
        del lst[0]


    elif front > rear:
        while lst[0] !=t:
            cnt += 1
            r_rot(lst)
        del lst[0]

print(cnt)













