'''
key = [[0, 0, 0], [1, 0, 0], [0, 1, 1]]	
lock = [[1, 1, 1], [1, 1, 0], [1, 0, 1]]

'''
# 90도 회전 구현
def rotation(key):

    kn = len(key)
    r_key = [[0]*kn for _ in range(kn)]

    for y in range(kn):
        for x in range(kn):
            r_key[x][kn-y-1] = key[y][x]

    return r_key

def padding(lock):
    
    plock = []
    pn = len(lock)
    for l in lock:
        plock.append([-2]+l+[-2])
    plock = [[-2]*(pn+2)]+plock+[[-2]*(pn+2)]

    return plock

def check(new_lock):

    for nl in new_lock:
        for l in nl:
            if l != 1:
                return False
    
    return True


def extrt(lock,lock_n,pn):

    new_lock = []
    for i in range(pn,lock_n-pn):
        new_lock.append(lock[i][pn:lock_n-pn])

    return new_lock


def solution(key):
    ans = False
    for py in range(lock_n-kn+1):
        for px in range(lock_n-kn+1):

            # 이부분 수정 !!! (key로 넣는 것이 아니라 ==> 확인을 lcok padding지운 곳으로 해줘야함)
            new_lock = [[0]*(lock_n) for _ in range(lock_n)]
            for y in range(kn):
                for x in range(kn):
                    new_lock[y+py][x+px] = key[y][x] + lock[y+py][x+px]

            new_lock = extrt(new_lock,lock_n,pn)
            print(new_lock)

            ans  = check(new_lock)

            if ans == True:
                return ans
    return False


from pprint import pprint

key = [[0, 0, 0], [1, 0, 0], [0, 1, 1]]	
lock = [[1, 1, 1], [1, 1, 0], [1, 0, 1]]
# 키가 항상 더 작음

kn = len(key)
pn = kn-1

for _ in range(pn):

    plock = padding(lock)
    lock = plock

lock_n = len(lock)
ans = solution(key)
if ans == False:
    for _ in range(3):
        r_key = rotation(key)
        ans = solution(r_key)
        if ans == True:
            break

print(ans)




