from collections import deque
for i in range(1,5):
    locals()['g{}'.format(i)] = deque([])