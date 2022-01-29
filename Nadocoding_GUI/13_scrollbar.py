from tkinter import*

root =Tk()
root.title('Nadp GUI')
root.geometry('640x480')

frame = Frame(root)
frame.pack()

scrollbar = Scrollbar(frame)
scrollbar.pack(side = 'right', fill = 'y')

listbox = Listbox(frame, selectmode = 'extended', height = 10, yscrollcommand = scrollbar.set)
# scrollbar.set 이 없으면 다시 스크롤이 올라온다.

scrollbar.config(command = listbox.yview) #리스트와 스크롤이 서로 연동이 되어야함 

for i in range(1,32):
    listbox.insert(END, str(i) + '일')
listbox.pack(side = 'left')

root.mainloop()   # 창이 닫히지 않게 해주는 것
