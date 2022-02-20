'''
우선순위 세기

'''

r = int(input())
# r = 1

for _ in range(r):
    al = list(map(int, input().split()))
    bl = list(map(int, input().split()))
    mn_cnt = min(al[0], bl[0])

    alst = sorted(al[1:], reverse=True)
    blst = sorted(bl[1:], reverse=True)

    for i in range(mn_cnt):
        if alst[i] > blst[i]:
            print('A')
            break

        elif alst[i] < blst[i]:
            print('B')
            break

    else:
        if al[0] > bl[0]:
            print('A')

        elif al[0] < bl[0]:
            print('B')
        else:
            print('D')

















