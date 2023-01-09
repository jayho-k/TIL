'''
문자열 검색 트리 : Resursive

Trie
- add
- search

time complexity : O(M)
'''

# Resursive
class TrieNode:
    def __init__(self):
        self.isEnd = False
        self.links = {}

class Trie:
    def __init__(self):
        self._root = TrieNode()
        self.saved_word = []

    # ADD
    # python : 타입 설정가능
    def _recurAdd(self, node:TrieNode, word:str) ->None:
        if len(word)==0:
            node.isEnd = True
            return

        ch = word[0]
        next_link = node.links.get(ch) # 다음 dictionary 저장

        # add : 새로운 노드 생성
        if next_link is None:
            node.links[ch] = TrieNode()
            next_link = node.links[ch] # ch를 저장함
        # print('word',word)
        # print('cur :',node.links)
        self._recurAdd(next_link,word[1:])

    def add(self, word:str) -> None:
        if len(word)==0:
            return

        self._recurAdd(self._root, word)


    # SEARCH
    def _recurSearch(self, node:TrieNode, word:str)-> bool:
        
        if len(word)==0:
            isEnd = node.isEnd
            return isEnd

        ch = word[0]
        if ch == '.':
            letters = node.links.keys()
            for key in letters:
                ret = self._recurSearch(node.links[key],word[1:])
                if ret is True:
                    return True

            return False
            
        else:
            next_link = node.links.get(ch)
            if next_link:
                return self._recurSearch(next_link,word[1:])  
            return False

    def search(self,word:str)->bool:
        if len(word)==0:
            return True
        
        return self._recurSearch(self._root,word)


    # FIND
    def _recurFind(self,node:TrieNode, word:str, savedWord, flag)->str:

        if node.isEnd == True:
            self.saved_word.append(savedWord)
            return
        
        if flag==True or word[0] == '_':
            flag = True
            letters = node.links.keys()
            for key in letters:
                self._recurFind(node.links[key],word[1:],savedWord+key,flag)

        else:
            ch = word[0]
            next_link = node.links.get(ch)
            if next_link:
                return self._recurFind(next_link,word[1:],savedWord+ch,flag)
            
    def find(self,word:str)->list:
        self.saved_word = []
        self._recurFind(self._root,word,'',False)
        return self.saved_word


if __name__=="__main__":
    trie = Trie()
    trie.add('baby')
    trie.add('ballgame')
    trie.add('batch')
    trie.add('bank')
    trie.add('charge')
    print('ballgame',trie.search('ballgame'))
    print('baby',trie.search('baby'))
    print('ba..',trie.search('ba..'))

    print(trie.find('ba_'))
    print(trie.find('ch_'))
