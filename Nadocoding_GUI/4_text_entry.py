from tkinter import *

root =Tk()
root.title('Nadp GUI')
root.geometry('640x480')

txt=Text(root, width=30, height=5) 
txt.pack()

txt.insert(END, '글자를 입력하세요')

e = Entry(root, width=30)  # 한줄로 받는 것 마치 id, password 처럼
e.pack()
e.insert(0, '한줄만 입력해요')

# 내용 출력
def btncmd():
    print(txt.get('1.0',END)) # 라인 1부터 가져와라, 커서 위치에서 0번째 인댁스부터 가져와라- 끝까지
    print(e.get())

    #내용 삭제
    txt.delete('1.0', END)
    e.delete(0,END)



btn = Button(root, text = '클릭', command = btncmd)
btn.pack()



root.mainloop()   # 창이 닫히지 않게 해주는 것