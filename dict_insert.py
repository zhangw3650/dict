# 将dict.txt导入Mysql数据库

import pymysql
import re


db = pymysql.connect('localhost', 'zhangw', '123456', 'dict')
cursor = db.cursor()

with open('dict.txt') as f:
    for line in f:
        L = re.split(r'\s+', line)
        word = L[0]
        interpret = ' '.join(L[1:])

        sql = "insert into words(word,interpret) \
        values('%s','%s');" % (word, interpret)

        try:
            cursor.execute(sql)
            db.commit()
        except Exception:
            db.rollback()

cursor.close()
db.close()
