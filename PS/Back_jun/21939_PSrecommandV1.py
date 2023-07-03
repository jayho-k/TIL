'''
5
1000 1
1001 2
19998 78
2667 37
2042 55
8
add 1402 59
recommend 1
solved 1000
solved 19998
recommend 1
recommend -1
solved 1001
recommend -1


2
1000 1
2000 1
4
recommend -1
solved 1000
add 1000 1000
recommend -1


2
1000 1
2000 1
2
recommend -1
recommend 1

이전에 추천 문제 리스트에 있던 문제 번호가 다른 난이도로 다시 들어 올 수 있다.
=> 1000:1 => slove => 1000:2 ==> solve ==> 1000:1
==> add될할때 remove에서 같은 번호 + 같은 난이도가 있다면 remove

'''

# 다시 풀기 

import sys
import heapq
from collections import defaultdict

def setting():
    for _ in range(n):
        pnum,lnum = map(int,input().split())
        heapq.heappush(small,lnum)
        heapq.heappush(big,-lnum)
        big_l2p[lnum].append(pnum)
        small_l2p[lnum].append(pnum)
        p2l[pnum]=lnum
        p_dic[lnum]+=1


    for nd in big_l2p:
        big_l2p[nd].sort()
        small_l2p[nd].sort(reverse=True)

def play():
    for _ in range(int(input())):
        order,*tmp = input().split()
        
        if order=='recommend':
            if int(tmp[0])== 1:

                # big => 이미 지워진 난이도가 존재할 수 있음
                while big and p_dic[-big[0]]<=0:
                    heapq.heappop(big)
                h_lv = -big[0]

        
                # big_l2p => 이미 지워진 문제가 존재할 수 있음
                # big_l2p[h_lv] => 문제 p_lst
                while big_l2p[h_lv] and big_l2p[h_lv][-1] in remove_dic and \
                        h_lv in remove_dic[big_l2p[h_lv][-1]]:
                    big_l2p[h_lv].pop()

                print(big_l2p[h_lv][-1])


            else:
                while small and p_dic[small[0]]<=0:
                    heapq.heappop(small)
                s_lv = small[0]

                while small_l2p[s_lv] and small_l2p[s_lv][-1] in remove_dic and \
                        s_lv in remove_dic[small_l2p[s_lv][-1]]:
                    small_l2p[s_lv].pop()

                print(small_l2p[s_lv][-1])


        elif order =='add':
            p,l = int(tmp[0]),int(tmp[1])

            # l2p, p2l => 값 삽입
            big_l2p[l].append(p)
            big_l2p[l].sort()

            small_l2p[l].append(p)
            small_l2p[l].sort(reverse=True)

            p2l[p]=l
            p_dic[l]+=1

            heapq.heappush(big,-l)
            heapq.heappush(small,l)

            # remove에서 같은 번호 + 같은 난이도가 있다면 remove
            if p in remove_dic and l in remove_dic[p]:
                remove_dic[p].remove(l)
            

        else:
            p=int(tmp[0])
            l=p2l[p]
            remove_dic[p].add(l)
            p_dic[l]-=1


# main
input = sys.stdin.readline

n = int(input())
big = []
small = []
big_l2p = defaultdict(list)
small_l2p = defaultdict(list)
p2l = defaultdict(int)
remove_dic = defaultdict(set)
p_dic = defaultdict(int)

# setting
setting()

# paly
play()