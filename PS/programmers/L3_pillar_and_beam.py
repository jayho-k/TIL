'''
n = 5
build_frame = [[1,0,0,1],[1,1,1,1],[2,1,0,1],[2,2,1,1],[5,0,0,1],[5,1,0,1],[4,2,1,1],[3,2,1,1]]

a = 기둥 보
b = 삭제하는 경우 아닌경우

1. 기둥은 바닥 위에 있거나 보의 한쪽 끝 부분 위에 있거나, 또는 다른 기둥 위에 있어야 합니다.
2. 보는 한쪽 끝 부분이 기둥 위에 있거나, 또는 양쪽 끝 부분이 다른 보와 동시에 연결되어 있어야 합니다.


'''
n = 5
build_frame = [[0,0,0,1],[2,0,0,1],[4,0,0,1],[0,1,1,1],[1,1,1,1],[2,1,1,1],[3,1,1,1],[2,0,0,0],[1,1,1,0],[2,2,0,1]]

# for문으로 돌려서 check를 하는 것
def check(build):

    for bx,by,ba in build:
        pillar, beam = 0,1

        # pillar
        if ba==pillar:
            if by!=0 and (bx,by-1,pillar) not in build and (bx,by,beam) not in build and (bx-1,by,beam) not in build:
                return False
            else:
                return True
        # beam
        else:
            if (bx,by-1,pillar) not in build and (bx+1,by-1,pillar) not in build and (bx+1,by,beam) not in build and (bx-1,by,beam) not in build:
                return False
            else:
                return True
       

from collections import deque
build = set()

for x,y,a,b in build_frame:
    tmp = (x,y,a)
    
    # 설치
    if b:
        build.add(tmp)
        print(tmp,check(build))
        if check(build) == False:
            build.remove(tmp)
            
    # 삭제
    else:
        build.remove(tmp)
        print(tmp,check(build))
        if check(build)==False:
            build.add(tmp)

    print(build)

print(build)

ans = list(map(list,build))
ans.sort(key=lambda x : (x[0], x[1], x[2]))
print(ans)



































# n = 5
# build_frame = [[0,0,0,1],[2,0,0,1],[4,0,0,1],[0,1,1,1],[1,1,1,1],[2,1,1,1],[3,1,1,1],[2,0,0,0],[1,1,1,0],[2,2,0,1]]



# build = []
# store = []
# # before = set(build_frame[0][:3])
# for i in range(len(build_frame)):
#     x,y,a,b = build_frame[i]

#     if b:
#         # 기둥
#         if a==0:
#             # 바닥
#             if y==0:
#                 store.append((x,y+1))
#                 build.append([x,y,a])

#             else:
#                 if (x,y) in store:
#                     store.append((x,y+1))
#                     build.append([x,y,a])
#                 else:
#                     continue

#         # 보
#         else:
#             if y==0:
#                 continue

#             else:
#                 if (x,y) in store or (x+1,y) in store:
#                     store.append((x,y))
#                     store.append((x+1,y))
#                     build.append([x,y,a])

#                 else:
#                     continue
#         # print(build)
#         # print(store)
#     # 삭제
#     else:
#         # 기둥
#         if a==0:
#             store.remove((x,y+1))
#             build.remove([x,y,a])

#         # 보
#         else:
#             store.remove((x,y))
#             store.remove((x+1,y))
#             build.remove([x,y,a])


#     print(build)



    





















# before = [build_frame[0][:3]]
# # before = set(build_frame[0][:3])
# for i in range(1,len(build_frame)):

#     bx,by,ba = before[-1]
#     x,y,a,b = build_frame[i]

#     # 설치할 경우
#     if b==1:

#         # 기둥일 경우
#         if a==0:
#             # 바닥일 경우
#             if y==0:
#                 before.append([x,y,a])

#             else:
#                 # 전의 것이 기둥일경우
#                 if ba == 0:
#                     if by+1==y and bx==x:
#                         before.append([x,y,a])
#                     else:
#                         continue

#                 elif ba == 1:
#                     if by==y and (bx==x or bx+1==x):
#                         before.append([x,y,a])
#                     else:
#                         continue

#         # 보일 경우
#         else:
#             if y==0:
#                 continue

#             else:
               
#                 #전 기, 현 보
#                 if ba == 0:
#                     if by+1==y and (bx==x or bx==x+1):
#                         before.append([x,y,a])
#                     else:
#                         continue

#                 elif ba == 1:
#                     if by==y and (bx==x+1 or bx+1==x):
#                         before.append([x,y,a])
#                     else:
#                         continue

#     print(before)

# print(before)




