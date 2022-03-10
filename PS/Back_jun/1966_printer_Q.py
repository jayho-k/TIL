'''
1. 현재 큐의 가장 앞에 있는 문서의 중요도를 확인한다
2. 나머지 문서들 중 중요도가 높은 문서가 하나라도 있음 ==> 가장 뒤로 보냄//
3. 없으면 바로 인쇄

숫자가 높을 수록 중요함

어떠한 문서가 몇번째로 인쇄되는지

입력: 
테스트케이스의 수가 주어짐

테케의
1번째: 문서의 개수 , 궁금한 문서의 놓인 위치[0부터 시작]
2번째: N개 문서의 중요도가 찰로 주어짐


1 0 : 문서개수 1개 / 궁금한거 위치 [0]
5   : 

4 2 : 문서개수 4개 / 궁금한거 위치 [2] 
1 2 3 4
1 2 3 4에서 

6 0 : 문서개수 6개 / 궁금한거 위치 [0]  ==> 6  
1 9 1 1 1 *
1 1 1 * 1
1 1 * 1
1 * 1
* 1

언제까지 돌려야 하니???
궁금한 것이 remove 될때 까지// 
궁금한 것의 위치가 0이고
max가 궁금한것일 때
멈춰야함

1. lst에서 max값을 찾아
2. 그것이 인덱스 0이 될때까지 rot을 돌려
3. max값이 인덱스0이면 del을 한다

문제는 궁금한거 위치가 계속 변할때 마다 그 위치를 어떻게 파악하지??
1. 인덱스가 0이되면 ==> len(lst) -1을 더해준다
2. else: -1

아.. 이래서 popleft가 편하구나
'''
# 로직은 금방 짰음 ==> 그러나 인덱스 -1를 어디서 해주어야 하는지 오래걸림 ==> remove를 했으면 인덱스도 같이 줄여줬어야 하나
# 줄여주지 않아서 인덱스의 위치가 꼬이기 시작했음

def rot(lst):
    p = lst[0]
    lst.append(p)
    lst.remove(p)

n = int(input())


for i in range(n):
    tx_num, tg_lo = map(int, input().split())
    imp_lst = list(map(int, input().split()))
    tg = imp_lst[tg_lo]
    cnt = 0

    while 1:       
        mx = max(imp_lst)

        while mx != imp_lst[0]:
            rot(imp_lst)
            if tg_lo == 0:
                tg_lo += len(imp_lst) -1
                
            else:
                tg_lo -= 1
    
        cnt += 1

        if tg_lo == 0 and imp_lst[0] == mx:
            print(cnt)
            break

        del imp_lst[0]
        tg_lo -= 1

        

        
        