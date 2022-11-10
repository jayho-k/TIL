'''



'''
from pprint import pprint
ay,ax,k = map(int,input().split())
grid = [list(map(int,input().split())) for _ in range(3)]
ny = 3
nx = 3
ans = 0
while 1:
    if ay <= len(grid) and ax <= len(grid[0]):
        if grid[ay-1][ax-1] == k:
            break
    if ans == 100:
        ans = -1
        break
    mx = 0
    new_grid = []
    tmp_new_lst = []
    if ny >= nx:
        for y in range(len(grid)):
            tmp_store = dict()
            tmp = set()

            for x in range(len(grid[0])):
                if grid[y][x] == 0:
                    continue
                if grid[y][x] not in tmp:
                    tmp_store[grid[y][x]] = 1
                    tmp.add(grid[y][x])
                else:
                    tmp_store[grid[y][x]] += 1
            mx = max(mx,len(tmp)*2)
            sorted_lst = sorted(tmp_store.items(), key=lambda x : (x[1],x[0]))
            tmp_new_lst = []
            if len(sorted_lst) > 50:
                for i in range(50):
                    for j in range(2):
                        tmp_new_lst.append(sorted_lst[i][j])
            else:
                for i in range(len(sorted_lst)):
                    for j in range(2):
                        tmp_new_lst.append(sorted_lst[i][j])
            new_grid.append(tmp_new_lst)
            
        nx = mx
        for gy in range(len(new_grid)):
            if len(new_grid[gy]) < mx:
                new_grid[gy] += [0]*(mx-len(new_grid[gy]))
        # pprint(new_grid)
        grid = new_grid
        if len(grid)>100:
            grid = grid[:100]
            

    else:
        grid = list(map(list,zip(*grid)))
        for y in range(len(grid)):            
            tmp_store = dict()
            tmp = set()
            for x in range(len(grid[0])):
                if grid[y][x] == 0:
                    continue
                if grid[y][x] not in tmp:
                    tmp_store[grid[y][x]] = 1
                    tmp.add(grid[y][x])
                else:
                    tmp_store[grid[y][x]] += 1

            mx = max(mx,len(tmp)*2)
            sorted_lst = sorted(tmp_store.items(), key=lambda x : (x[1],x[0]))
            tmp_new_lst = []
            if len(sorted_lst) > 50:
                for i in range(50):
                    for j in range(2):
                        tmp_new_lst.append(sorted_lst[i][j])
            else:
                for i in range(len(sorted_lst)):
                    for j in range(2):
                        tmp_new_lst.append(sorted_lst[i][j])
            new_grid.append(tmp_new_lst)
        
        ny = mx
        for gy in range(len(new_grid)):
            if len(new_grid[gy]) < mx:
                new_grid[gy] += [0]*(mx-len(new_grid[gy]))
        
        grid = new_grid
        grid = list(map(list,zip(*grid)))
        if len(grid)>100:
            grid = grid[:100]

    
    ans +=1

print(ans)
