from tkinter import*

root =Tk()
root.title('Nadp GUI')
root.geometry('640x480')

listbox = Listbox(root, selectmode='extended', height=0) # extended 여러개 선택 가능, single 하나만 선택 가능
listbox.insert(0, '사과')
listbox.insert(1, '딸기')
listbox.insert(2, '바나나')

listbox.insert(END, '수박')
listbox.insert(END, '포도')
listbox.pack()


def btncmd():
    # listbox.delete(END) # 맨 뒤에꺼를 삭제
    # listbox.delete(0) # 맨 앞에꺼

    # # 갯 수 확인
    # print('리스트에는', listbox.size(), '개 있어요')

    # # 항목 확인
    # print('1번째 부터 3번째 까지의 항목 : ', listbox.get(0, 2))

    # 선택된 항목 확인 (위치로 반환 ex) 123)
    print('선택된 항목 :', listbox.curselection())



btn = Button(root, text='클릭', command=btncmd)
btn.pack()



root.mainloop()   # 창이 닫히지 않게 해주는 것
