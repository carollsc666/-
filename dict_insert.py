# dict_insert.py
import pymysql
import re

f = open('dict.txt')
db = pymysql.connect(\
    'localhost','root','123456',\
    'dict',charset='utf8')

cur = db.cursor()

for  line in f:
    l = re.split(r'\s+',line)
    word = l[0]
    interpret = ' '.join(l[1:])
    sql = "insert into words (word,interpret) \
    values('%s','%s')"%(word,interpret)
    try:
        cur.execute(sql)
        db.commit()
        print('插入成功')
    except Exception as e:
        db.rollback()
        print('出现错误，已回滚')

f.close()
