"""
10 5
10 a
15 b
20 c
25 d
30 e
17 f
18 g
26 h
24 i
28 j

 가능한 방이 없다면 새로운 방을 생성
- 처음 입장한 플레이어의 레벨을 기준으로 -10부터 +10까지 입장 가능

입장 가능한 방이 있다면 입장시킨 후 방의 정원이 모두 찰 때까지 대기시킨다.
이때 입장이 가능한 방이 여러 개라면 먼저 생성된 방에 입장한다.

방의 정원이 모두 차면 게임을 시작시킨다.

1. 입장 가능한 방이 있는지 없는지 확인
    - 처음 lv +- 10 을 dic (처음 lv : [name, name ...])
    - room info dic (name : index, status)
    - 해당 플레이어 => 레벨 +- 10 으로 가능한 방 scan
    - start 하면 대기 heapq 에 넣고 index를 기준으로 넣는다
        - 그리고 삭제
    - 여러개가 나오면 index min으로 계산

12 5
10 a
15 b
20 c
25 d
30 e
17 f
18 g
26 h
24 i
28 j
30 asdf
1 asdfasdf


12 300
10 a
15 b
20 c
25 d
30 e
17 f
18 g
26 h
24 i
28 j
30 asdf
1 asdfasdf

"""
import heapq

# lv : [roomName, roomName ,,, ]
lvDic = {}

# name : [index, number ,status]
roomInfo  = {}

# roomName : [(name,lv),,,,]
roomMember = {}

# 방수 카운트
cnt = 1

def checkIfFull(roomName):
    if roomInfo[roomName][1] == m: 
        roomInfo[roomName][2] = 0 # 정원 다 차면 status starting으로 변경

def makeRoom(findName, findLv):
    global cnt

    # room 생성
    roomInfo[findName] = [cnt,1,1]
    cnt+=1

    # member 추가
    roomMember[findName] = []
    roomMember[findName].append((findName,findLv))

    # lv update
    if findLv in lvDic:
        lvDic[findLv].append(findName)
    else:
        lvDic[findLv] = []
        lvDic[findLv].append(findName)
    
    checkIfFull(findName)

def checkPossibleLv(minLv, maxLv):
    if (minLv<1):
        minLv = 1

    if (maxLv>500):
        maxLv = 500
    return minLv,maxLv

def findPossibleRoom(minLv,maxLv):

    minIndex = 100000
    minIndexRoom = ""

    for posibleLv in range(minLv,maxLv+1):
        
        # 참여 가능하다 => 존재하고, status가 waiting인 상태 / start:0, waiting:1 
        if posibleLv in lvDic:
            for roomName in lvDic[posibleLv]:
                if roomInfo[roomName][2]: # 참여 가능
                    
                    if minIndex > roomInfo[roomName][0]:
                        minIndex = roomInfo[roomName][0]
                        minIndexRoom = roomName

    return minIndexRoom

def play(findLv, findName):
    
    global cnt

    minLv, maxLv = checkPossibleLv(findLv-10, findLv+10)
    minIndexRoom = findPossibleRoom(minLv, maxLv)
    
    # 참여 가능한 방이 있는 경우 그 방에 들어간다.
    if minIndexRoom:
        #[index, number ,status]
        roomInfo[minIndexRoom][1]+=1
        roomMember[minIndexRoom].append((findName,findLv))

        checkIfFull(minIndexRoom)

    # 없는 경우 새로 방을 만든다.
    else:
        makeRoom(findName, findLv)


def main(p):
    
    for _ in range(p):
        lv,name = input().split()
        lv = int(lv)

        play(lv, name)
        
p, m = map(int,input().split())
main(p)

# name : [index, number ,status]
ans = []
for rName in roomInfo:
    ans.append((roomInfo[rName][0],rName, roomInfo[rName][2]))

ans.sort()
# print(ans)

for a in ans:
    if (a[2]):
        print('Waiting!')
    else:
        print('Started!')
    roomMember[a[1]].sort()
    for member in roomMember[a[1]]:
        print(member[1],member[0])

