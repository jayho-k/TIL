T = int(input())
for tc in range(1,T+1):
    num, n = input().split()
    lst = input().split()

    s = ["ZRO", "ONE", "TWO", "THR", "FOR", "FIV", "SIX", "SVN", "EGT", "NIN"]
    n = list(range(10))
    StoN = dict(zip(s, n))
    NtoS = dict(zip(n, s))

    lst1 = []
    for i in lst:
        number1 = StoN[i]
        lst1.append(number1)
    lst1.sort()

    lst2 = []
    for j in lst1:
        number2 = NtoS[j]
        lst2.append(number2)

    s = ' '.join(lst2)
    print(f'#{tc}')
    print(s)