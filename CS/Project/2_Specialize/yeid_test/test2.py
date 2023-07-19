
from yeild_test import somthing

i = 0
s = somthing.iter(10)
print(s)
while 1:
    p = next(s)
    if p == 'stop':
        print('it works')
        break
    else:
        print(p)