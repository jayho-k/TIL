'''
'''
import os

class InsertData2DB:

    def __init__(self,save_dir_name):
        self.save_dir = save_dir_name
        
    def make_dir(self):
        CUR_DIR=os.getcwd()
        SAVE_DIR = self.save_dir
        self.PATH = os.path.join(CUR_DIR,SAVE_DIR)
        try:
            os.mkdir(self.PATH)
            return self.PATH
        except:
            return '디렉토리가 만들어지지 않았습니다.'


def user_write():
    
    with open('C:/Users/jayho/Developer/practice/PS/test/db_init_query/user_init.txt', 'w') as f:
        f.write("INSERT INTO user (user_id, create_at, modified_at, user_delete, user_email, user_img, user_name, user_pw, user_type) VALUES\n")
        for user in range(1,2001):
            f.write(f"({user},NOW(),NOW(),0,'sox{user}@naver.com','img','user{user}','user{user}','USER'),\n")

def user_email_write():
    
    with open('C:/Users/jayho/Developer/practice/PS/test/db_init_query/user_init.txt', 'w') as f:
        
        for user in range(1,2001):
            f.write(f"UPDATE user SET user_email='sox{user}@naver.com' WHERE user_id = {user};\n")

user_email_write()

def resume_write():
    cnt = 0
    with open('C:/Users/jayho/Developer/practice/PS/test/db_init_query/resume_init.txt', 'w') as f:
        f.write("INSERT INTO resume (resume_id,create_at,modified_at,resume_title, user_id) VALUES\n")
        for user in range(1,2001):
            for resume in range(5):
                cnt+=1
                f.write(f"({cnt},NOW(),NOW(),'user{user}/resume{resume}',{user}),\n")

def resume_detail_write():
    cnt = 0
    with open('C:/Users/jayho/Developer/practice/PS/test/db_init_query/resume_detail_init.txt', 'w') as f:
        f.write("INSERT INTO resume_detail (resume_detail_id, create_at, modified_at, detail_contents,item_no,resume_id) VALUES\n")
        for resume in range(1,10001):
            for resume_detail in range(1,6):
                cnt+=1
                f.write(f"({cnt},NOW(),NOW(),'resume{resume}/detail{resume_detail}',{resume_detail}, {resume}),\n")

def room_session_write():
    with open('C:/Users/jayho/Developer/practice/PS/test/db_init_query/room_session_init_init.txt', 'w') as f:
        f.write("INSERT INTO room_session (dtype, std_id, create_at, modified_at, com_name, end_date, start_date, std_day, std_detail, std_img, std_limit, std_name, std_notation, std_type) VALUES\n")
        for study in range(1,401):
            f.write(f"('study',{study},NOW(),NOW(),'smasung','2022','2022','Mon','detail','image',5,'study_name','std_notation','FREE'),\n")


def study_write():
    with open('C:/Users/jayho/Developer/practice/PS/test/db_init_query/study_init.txt', 'w') as f:
        f.write("INSERT INTO study (std_id) VALUES\n")
        for study in range(1,401):
            f.write(f"({study}),\n")


def study_join_write():
    with open('C:/Users/jayho/Developer/practice/PS/test/db_init_query/study_join_init.txt', 'w') as f:
        f.write("INSERT INTO study_join (study_join_id, join_status, join_type, resume_id, study_id, user_id) VALUES\n")
        study = 1
        join_type = 'NORMAL'

        for study_join in range(1,2001):
            if study_join%5==1:
                join_type='LEADER'

            f.write(f"({study_join},0,'{join_type}',{(study_join-1)*5+1},{study},{study_join}),\n")

            join_type='NORMAL'
            if study_join%5==0:
                study+=1

def common_question_write():
    with open('C:/Users/jayho/Developer/practice/PS/test/db_init_query/common_question_init.txt', 'w') as f:
        f.write("INSERT INTO common_question (id, create_at, modified_at, contents, question_type, study_id, user_id) VALUES\n")
        study = 1
        for common_question in range(1,2001):
            
            f.write(f"({common_question},NOW(),NOW(),'contents','PERSONALITY',{study},{common_question}),\n")

            if common_question%5==0:
                study+=1

def room_session4recruit_write():
    with open('C:/Users/jayho/Developer/practice/PS/test/db_init_query/room_session4recruit_init_init.txt', 'w') as f:
        f.write("INSERT INTO room_session (dtype, std_id, create_at, modified_at, com_name, end_date, start_date, std_day, std_detail, std_img, std_limit, std_name, std_notation, std_type) VALUES\n")
        for recruit in range(401,2401):
            if recruit%2==1:
                f.write(f"('recruit',{recruit},NOW(),NOW(),'smasung','2022','2022','Mon','detail','image',5,'study_name','std_notation','FREE'),\n")
            else:
                f.write(f"('recruit',{recruit},NOW(),NOW(),'smasung','2022','2022','Mon','detail','image',5,'study_name','std_notation','COM'),\n")

def recruit_write():
    with open('C:/Users/jayho/Developer/practice/PS/test/db_init_query/recruit_init.txt', 'w') as f:
        f.write("INSERT INTO recruit (recruit_status, recruit_title, std_id) VALUES\n")
        for recruit in range(401,2401):
            if recruit%2==1:
                f.write(f"('ING','title',{recruit}),\n")
            else:
                f.write(f"('COMPLETE','title',{recruit}),\n")