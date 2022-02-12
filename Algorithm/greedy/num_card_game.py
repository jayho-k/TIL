'''
N x M 카드

행(lst)를 뽑고 열(인덱스)를 뽑는다
열에서는 가장 낮은 카드를 뽑아야한다.

이때 가장 높은 수를 뽑는 방법은??

max 구현 함수를 사용하면 될듯?

3 3
3 1 2
4 1 4
2 2 2

'''

n, m = map(int, input().split())

mx_num =0

for i in range(n):
    lst = map(int, input().split())
    mn_num = min(lst)
    
    if mx_num < mn_num:
        mx_num = mn_num

print(mx_num)