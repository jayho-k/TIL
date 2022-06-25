'''
n = 5
build_frame = [[1,0,0,1],[1,1,1,1],[2,1,0,1],[2,2,1,1],[5,0,0,1],[5,1,0,1],[4,2,1,1],[3,2,1,1]]

a = 기둥 보
b = 삭제하는 경우 아닌경우

'''
n = 5
build_frame = [[0,0,0,1],[2,0,0,1],[4,0,0,1],[0,1,1,1],[1,1,1,1],[2,1,1,1],[3,1,1,1],[2,0,0,0],[1,1,1,0],[2,2,0,1]]



build = []
store = []
# before = set(build_frame[0][:3])
for i in range(len(build_frame)):
    x,y,a,b = build_frame[i]

    if b:
        # 기둥
        if a==0:
            # 바닥
            if y==0:
                store.append((x,y+1))
                build.append([x,y,a])

            else:
                if (x,y) in store:
                    store.append((x,y+1))
                    build.append([x,y,a])
                else:
                    continue

        # 보
        else:
            if y==0:
                continue

            else:
                if (x,y) in store or (x+1,y) in store:
                    store.append((x,y))
                    store.append((x+1,y))
                    build.append([x,y,a])

                else:
                    continue
        # print(build)
        # print(store)
    # 삭제
    else:
        # 기둥
        if a==0:
            store.remove((x,y+1))
            build.remove([x,y,a])

        # 보
        else:
            store.remove((x,y))
            store.remove((x+1,y))
            build.remove([x,y,a])


    print(build)



    





















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




