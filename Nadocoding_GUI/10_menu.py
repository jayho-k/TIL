
from tkinter import*

root =Tk()
root.title('Nadp GUI')
root.geometry('640x480')

def create_new_file():
    print('새 파일을 만듭니다.')

menu = Menu(root)

# file 메뉴
menu_file = Menu(menu, tearoff=0)
menu_file.add_command(label = 'new file', command = create_new_file)
menu_file.add_command(label = 'new window')
menu_file.add_separator()  # 선을 그어주는 것 
menu_file.add_command(label= 'open file')
menu_file.add_separator()
menu_file.add_command(label = 'save all', state = 'disable')
menu_file.add_separator()
menu_file.add_command(label = 'Exit', command = root.quit)  # 나가기 버튼 

menu.add_cascade(label = 'file', menu= menu_file)


# edit 메뉴 추가 (빈 것)
menu.add_cascade(label = 'edit')

# Language 버튼 추가 (radiator를 이용 체크버튼이 사라지지는 않음)
menu_lang = Menu(menu, tearoff=0) # tear off는 하위 메뉴 오픈 가능 여부 0일때 없음
menu_lang.add_radiobutton(label = 'Python')
menu_lang.add_radiobutton(label = 'Jaba')
menu_lang.add_radiobutton(label = 'C++')
menu.add_cascade(label = 'language', menu = menu_lang)

# view 메뉴 (check버튼이 한번 누르면 생기고 사라짐)
menu_view = Menu(menu, tearoff = 0)
menu_view.add_checkbutton(label = 'show minimap')
menu.add_cascade(label = 'view', menu = menu_view)




root.config(menu = menu)


root.mainloop()   # 창이 닫히지 않게 해주는 것
