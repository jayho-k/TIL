# 1번 열어 ==> 읽어 ==> md에 써

import re

path = 'C:\ProgramData\Anaconda3\Python Workspace\Nadocoding_Python\Nadocoding_craping\webscraping_basic'
typora ='C:\Program Files\Typora\Typora.exe'
for num in range(1,3):
    with open(path +re.compile('\^{}_'.format(num)), 'r', encoding = 'uft-8') as f: python = f.read()


    with open(typora) as f: f.write('python'+ '\n\n\n\n\n\n\n\n\n')