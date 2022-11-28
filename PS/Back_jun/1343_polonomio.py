'''
XXXXXX
XXXX....XXX.....XX
XX.XXXXXXXXXX..XXXXXXXX...XXXXXX
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

        elif not c_cnt%2:
            mok4 = c_cnt-(c_cnt%4)
            namuzi4 = c_cnt%4
            board_copy[i] = 'A'*mok4+'B'*namuzi4
        else:
            print(-1)
            break
else:
    print('.'.join(board_copy))