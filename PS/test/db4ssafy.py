'''
'''
def user_write():
    
    with open('C:/Users/jayho/Developer/practice/PS/test/db4ssafy_init/user_init.txt', 'w') as f:
        f.write("INSERT INTO homterviewssafy.user (user_no, user_email, user_id, user_img, user_name, user_pw, user_type) VALUES\n")
        for user in range(1,2001):
            f.write(f"({user},'sox{user}@naver.com','user{user}','img','user{user}','user','USER'),\n")



def resume_write():
    cnt = 0
    with open('C:/Users/jayho/Developer/practice/PS/test/db4ssafy_init/resume_init.txt', 'w') as f:
        f.write("INSERT INTO homterviewssafy.resume (resume_no, resume_title, user_no) VALUES\n")
        for user in range(1,2001):
            for resume in range(5):
                cnt+=1
                f.write(f"({cnt},'user{user}/resume{resume}',{user}),\n")

def resume_detail_write():
    cnt = 0
    with open('C:/Users/jayho/Developer/practice/PS/test/db4ssafy_init/resume_detail_init.txt', 'w') as f:
        f.write("INSERT INTO homterviewssafy.resume_detail (detail_no, answer, item, item_no, resume_no) VALUES\n")
        for resume in range(1,10001):
            for resume_detail in range(1,6):
                cnt+=1
                f.write(f"({cnt},'resume{resume}/detail{resume_detail}','content',{resume_detail}, {resume}),\n")


def study_write():
    with open('C:/Users/jayho/Developer/practice/PS/test/db4ssafy_init/study_init.txt', 'w') as f:
        f.write("INSERT INTO homterviewssafy.study (std_no, com_name, end_date, start_date, std_day, std_detail, std_img, std_limit, std_name, std_notice, std_type) VALUES\n")
        for study in range(1,401):
            f.write(f"({study},'smasung','2022','2022','Mon','detail','image',5,'study_name','std_notation','FREE'),\n")


def study_join_write():
    with open('C:/Users/jayho/Developer/practice/PS/test/db4ssafy_init/study_join_init.txt', 'w') as f:
        f.write("INSERT INTO homterviewssafy.study_join (join_no, join_type, resume_no, std_no, user_no) VALUES\n")
        study = 1
        join_type = 'NORMAL'

        for study_join in range(1,2001):
            if study_join%5==1:
                join_type='LEADER'

            f.write(f"({study_join},'{join_type}',{(study_join-1)*5+1},{study},{study_join}),\n")

            join_type='NORMAL'
            if study_join%5==0:
                study+=1


def common_question_write():
    with open('C:/Users/jayho/Developer/practice/PS/test/db4ssafy_init/common_question_init.txt', 'w') as f:
        f.write("INSERT INTO homterviewssafy.common_question (question_no, contents, question_type, writer_no, std_no) VALUES\n")
        study = 1
        for common_question in range(1,2001):
            
            f.write(f"({common_question},'contents','PERSONALITY',{common_question},{study}),\n")

            if common_question%5==0:
                study+=1


def recruit_write():
    with open('C:/Users/jayho/Developer/practice/PS/test/db4ssafy_init/recruit_init.txt', 'w') as f:
        f.write("INSERT INTO homterviewssafy.recruit (recruit_no, com_name, end_date, recruit_status, recruit_title, start_date, std_day, std_detail, std_img, std_limit, std_name, std_no, std_type) VALUES\n")
        for recruit in range(1,2001):
            if recruit%2==1:
                f.write(f"({recruit},'smasung','2022','RECRUITING','recurit_title','2020','Mon','detail','image',5,'study_name',null,'FREE'),\n")
            else:
                f.write(f"({recruit},'smasung','2022','COMPLETED','recurit_title','2020','Mon','detail','image',5,'study_name',null,'COM'),\n")



def apply_write():
     with open('C:/Users/jayho/Developer/practice/PS/test/db4ssafy_init/apply_init.txt', 'w') as f:
        f.write("INSERT INTO homterviewssafy.apply (apply_no, apply_type, recruit_no, user_no) VALUES\n")
        recruit = 1
        user = 0
        join_type = 'NORMAL'
        for apply in range(1,10001):
            if apply%5==1:
                join_type = 'LEADER'
            
            user+=1
            f.write(f"({apply},'{join_type}',{recruit},{user}),\n")

            join_type = 'NORMAL'
            if apply%5==0:
                recruit+=1

            if apply%2000==0:
                user=0
apply_write()