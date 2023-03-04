def resume_write():
    cnt = 0
    with open('C:/Users/jayho/Developer/practice/PS/test/db_init_query/resume_init.txt', 'w') as f:
        f.write("INSERT INTO resume (resume_id,create_at,modified_at,resume_title, user_id) VALUES\n")
        for user in range(1,2001):
            for resume in range(5):
                cnt+=1
                f.write(f"({cnt},NOW(),NOW(),'user{user}/resume{resume}',{user}),\n")

resume_write()
