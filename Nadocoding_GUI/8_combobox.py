import tkinter.ttk as ttk
from tkinter import*

root =Tk()
root.title('Nadp GUI')
root.geometry('640x480')

values = [str(i) + '일' for i in range(1, 32)]
combobox1 = ttk.Combobox(root, height = 5, values = values)
combobox1.pack()
combobox1.set('카드 결제일') # 최초목록, 버튼 클릭을 통한 값 설정도 가능

combobox2 = ttk.Combobox(root, height = 10, values = values, state = 'readonly') # state readonly는 타자를 칠 수 없게 만드는 것
combobox2.current(0) # 0번째 인덱스 값 선택
combobox2.pack()
combobox2.set('카드 결제일') 




def btncmd():
    print(combobox1.get()) 
    print(combobox2.get())   




btn = Button(root, text='주문', command=btncmd)
btn.pack()



root.mainloop()   # 창이 닫히지 않게 해주는 것
