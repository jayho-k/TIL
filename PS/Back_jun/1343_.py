'''
XXXXXX
XXXX....XXX.....XX
'''
board = input().split('.')
board_copy=board[:]
ans = -1
for i in range(len(board)):
    if board[i]:
        c_cnt = len(list(board[i]))
        # 짝수 => 4배수 => 나머지
        if not c_cnt%4:
            board_copy[i]='A'*c_cnt
            
        elif not c_cnt%6:
            mok4 = c_cnt//4
            namuzi4 = c_cnt%4
            board_copy[i] = 'A'*mok4+'B'*namuzi4

        elif not c_cnt%2:
            board_copy[i]='B'*c_cnt
        else:
            print(-1)
            break
else:
    print(board_copy)