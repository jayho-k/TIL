'''
4
123 1 1
356 1 0
327 2 0
489 0 1


'''
def strike(s,h_lst,l):

        state = False
        tmp = l[:]
        if s == 1:
            if (h_lst[0]==l[0] and h_lst[1]!=l[1] and h_lst[2]!=l[2]):
                tmp[0] = 0
                state = True

            elif (h_lst[0]!=l[0] and h_lst[1]==l[1] and h_lst[2]!=l[2]):
                tmp[1] = 0
                state = True

            elif (h_lst[0]!=l[0] and h_lst[1]!=l[1] and h_lst[2]==l[2]):
                tmp[2] = 0
                state = True

        elif s == 2:
            if (h_lst[0]==l[0] and h_lst[1]==l[1] and h_lst[2]!=l[2]):
                tmp[0] = 0
                tmp[1] = 0
                state = True

            elif (h_lst[0]==l[0] and h_lst[1]!=l[1] and h_lst[2]==l[2]):
                tmp[0] = 0
                tmp[2] = 0
                state = True

            elif (h_lst[0]!=l[0] and h_lst[1]==l[1] and h_lst[2]==l[2]):
                tmp[1] = 0
                tmp[2] = 0
                state = True

        elif s == 3:
            if (h_lst[0]==l[0] and h_lst[1]==l[1] and h_lst[2]==l[2]):
                tmp[1] = 0
                tmp[2] = 0
                tmp[3] = 0
                state = True

        else:
            if (h_lst[0]!=l[0] and h_lst[1]!=l[1] and h_lst[2]!=l[2]):
                state = True

        return state,tmp


def ball(b,h_lst,l):
    state = False

    cnt = 0
    for h in h_lst:
        if h in l:
            cnt += 1

    if b == cnt:
        state = True

    return state


from itertools import permutations
n = int(input())

hint = []

for _ in range(n):
    num,s,b = input().split()
    num_lst = list(map(int,list(num)))
    s = int(s)
    b = int(b)
    hint.append([num_lst,s,b])

lst = list(range(1,10))
lst = list(map(list,permutations(lst,3)))

store = []

for l in lst:
    cnt = 0
    for hi in hint:
        h_lst,s,b = hi
        s_state,tmp = strike(s,h_lst,l)
        b_state = ball(b,h_lst,tmp)

        if s_state == True and b_state == True:
            cnt += 1

    if cnt == n:
        store.append(l)

print(len(store))
