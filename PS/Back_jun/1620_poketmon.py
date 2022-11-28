'''
26 5
Bulbasaur
Ivysaur
Venusaur
Charmander
Charmeleon
Charizard
Squirtle
Wartortle
Blastoise
Caterpie
Metapod
Butterfree
Weedle
Kakuna
Beedrill
Pidgey
Pidgeotto
Pidgeot
Rattata
Raticate
Spearow
Fearow
Ekans
Arbok
Pikachu
Raichu
25
Raichu
3
Pidgey
Kakuna

'''
n,m = map(int,input().split())

nums = set(map(str,range(1,10)))
diclist = [input() for _ in range(n)]
anslist = [input() for _ in range(m)]

for al in anslist:
    
    if al[0] in nums:
        al_num = int(al)
        print(diclist[al_num-1])

    else:
        print(diclist.index(al)+1)




