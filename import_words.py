import sqlite3
import os

"""

    使用说明：
        该文件用于导入单词
        确保本脚本、words.txt 和 game.db 都在同一个文件夹下
        导入单词的文件请修改为words.txt并放入PYHOMEWORK文件夹当中
        之后点击运行该脚本就可以


"""


# 获取当前脚本文件所在的绝对路径 (也就是 实验1 文件夹的路径)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 使用 os.path.join 拼接路径，不管你在哪里运行，都能找到正确的文件
DB_FILE = os.path.join(BASE_DIR, "game.db")
TXT_FILE = os.path.join(BASE_DIR, "words.txt")

def import_txt_to_db():
    if not os.path.exists(TXT_FILE):
        print(f"找不到{TXT_FILE},无法导入。")
        return 
    
    with open(TXT_FILE,"r",encoding="utf-8") as f:
        words=[line.strip() for line in f if line.strip()]

    if not words:
        print("txt 文件是空的，没有单词可以导入。")
        return
    

    try:
        conn=sqlite3.connect(DB_FILE)
        cursor=conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL UNIQUE
            )
        ''')

        data_to_insert=[(w,) for w in words]
        cursor.executemany('INSERT OR IGNORE INTO words (word) VALUES (?)', data_to_insert)

        conn.commit()
        print(f"成功导入了{len(words)}个单词到数据库（重复的已经跳过）")

        cursor.execute("SELECT count(*) FROM words")
        count=cursor.fetchone()[0]
        print(f"当前数据库共有{count}个单词")


    except Exception as e:
        print(f"导入出错：{e}")

    finally:
        conn.close()

if __name__=="__main__":

    import_txt_to_db()
