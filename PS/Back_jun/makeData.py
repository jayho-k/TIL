import string

def asdf(table):
    for i in range(20):
        sql = "INSERT INTO {3}.AGV VALUES({0},{1},{2});".format(i,i,i+1,table)
        print(sql)

        
asdf("sprout_db")
asdf("spring_batch")
