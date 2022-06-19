'''
70828315762
1234567890
left
right
'''
def play(numbers,hand):
    tmp = ''
    l = ['*']
    r = ['#']

    for num in numbers:
        if num==1 or num==4 or num==7:
            tmp += 'L'
            l.append(num)

        elif num==3 or num==6 or num==9:
            tmp += 'R'
            r.append(num)

        else:
            l_dis = abs(loc[l[-1]][0]-loc[num][0]) + abs(loc[l[-1]][1]-loc[num][1])
            r_dis = abs(loc[r[-1]][0]-loc[num][0]) + abs(loc[r[-1]][1]-loc[num][1])
            if l_dis > r_dis:
                tmp += 'R'
                r.append(num)

            elif l_dis < r_dis:
                tmp += 'L'
                l.append(num)

            else:
                if hand == 'left':           
                    tmp += 'L'
                    l.append(num)
                else:
                    tmp += 'R'
                    r.append(num)
    return tmp


numbers = [1,3,4,5,8,2,1,4,5,9,5]
hand = 'left'
pad = [[1,2,3],[4,5,6],[7,8,9],['*',0,'#']]
loc = {1:[0,0],2:[0,1],3:[0,2],4:[1,0],5:[1,1],6:[1,2],7:[2,0],8:[2,1],9:[2,2]
        ,'*':[3,0],0:[3,1],'#':[3,2]}

ans = play(numbers,hand)
print(ans)
