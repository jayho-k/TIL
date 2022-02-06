'''
3 3  ==> 6
1 3  ==> 4
3 1  ==> 4
1 1  ==> 2

특징1: 짝수다

'''
n = int(input())

namuzi = n % 2

if namuzi == 1:
    print('SK')

elif namuzi == 0:
    print('CY')
