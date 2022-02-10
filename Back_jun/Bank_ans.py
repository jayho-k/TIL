# import sys
# input = sys.stdin.readline

# def is_Circle(tar_pos,  em_pos):
#     a = tar_pos[0] - em_pos[0]
#     b = tar_pos[1] - em_pos[1]
#     if r*r < (a*a) + (b*b):
#         return False
#     return True


# n, r = map(int, input().split())
# tar = list()
# for i in range(n):
#     temp = list(map(int, input().split()))
#     if temp not in tar:
#         tar.append(temp)

# guest = list()
# m = int(input())
# for i in range(m):
#     guest.append(list(map(int, input().split())))

# cnt = 0
# # 로봇으로 먼저 탐색
# for i in tar:
#     for s in guest:
#         if is_Circle(i, s):
#             guest.remove(s)