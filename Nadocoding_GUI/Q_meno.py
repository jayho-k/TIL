import os
from tkinter import *
root = Tk()
root.title('제목 없음 - window 메모장')
root.geometry('640x480')

menu = Menu(root)

filename = 'mynote.txt'

# 메뉴
def file_open():
    if os.path.isfile(filename):
        with open(filename, 'r', encoding = 'utf8') as file:
            txt.delete('0.1', END)
            txt.insert(END, file.read())

def file_save():
    with open(filename, 'w', encoding = 'utf8') as file:
        file.write(txt.get('1.0', END))


# File
menu_file = Menu(menu, tearoff = 0)

menu_file.add_command(label = 'open', command = file_open)
menu_file.add_command(label = 'save', command = file_save)
menu_file.add_separator()
menu_file.add_command(label = 'exit', command = root.quit)
menu_file

menu.add_cascade(label = 'file', menu = menu_file)

# Edit
menu_edit = Menu(menu, tearoff = 0)
menu.add_cascade(label = 'Edit', menu = menu_edit)


# Form
menu_form = Menu(menu, tearoff = 0)
menu.add_cascade(label = 'Form', menu = menu_form)


# View
menu_form = Menu(menu, tearoff = 0)
menu.add_cascade(label = 'Form', menu = menu_form)

# Help
menu_form = Menu(menu, tearoff = 0)
menu.add_cascade(label = 'Form', menu = menu_form)


root.config(menu = menu)



# Scrollbar
scrollbar = Scrollbar(root)
scrollbar.pack(side = 'right', fill = 'y')

# Add Text  + 창에 따라 크기를 변하게 만들어야 함
txt = Text(root, yscrollcommand = scrollbar.set)
txt.pack(side = 'left', fill = 'both', expand = True) 

scrollbar.config(command = txt.yview)






root.mainloop()