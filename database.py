# database.py
import sqlite3
import json
import os
import time
import config  # 导入配置文件


"""

    请注意：
    如果运行该文件出现问题，可能是中文路径问题，因为英文路径运行是没有问题的，但是按照作业格式更改之后无法正常运行
    如果需要解决该问题，请讲路径全部修改为英文


"""



class DataManager:
    def __init__(self):
        self.ensure_files_exist()
        self.init_word_db()

    def ensure_files_exist(self):
        if not os.path.exists(config.IMG_DIR):
            try:
                os.makedirs(config.IMG_DIR)
            except:
                pass
        
        if not os.path.exists(config.DATA_FILE):
            with open(config.DATA_FILE, "w", encoding="utf-8") as f:
                json.dump({}, f)

    def init_word_db(self):
        with sqlite3.connect(config.DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS words (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    word TEXT NOT NULL UNIQUE
                )
            ''')
            
            cursor.execute('SELECT count(*) FROM words')
            if cursor.fetchone()[0] == 0:
                defaults = [
                    "Apple", "Banana", "Cherry", "Date", "Elderberry", "Fig", 
                    "Grape", "Honeydew", "Kiwi", "Lemon", "Mango", "Nectarine", 
                    "Orange", "Papaya", "Quince", "Raspberry", "Strawberry", "Tangerine",
                    "Ugli", "Vanilla", "Watermelon", "Xigua", "Yam", "Zucchini"
                ]
                data = [(w,) for w in defaults]
                cursor.executemany('INSERT INTO words (word) VALUES (?)', data)
                conn.commit()

    def load_words(self):
        with sqlite3.connect(config.DB_FILE) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT word FROM words')
            words = [row[0] for row in cursor.fetchall()]
        return words

    
    def load_users(self):
        with open(config.DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    def save_users(self, users):
        with open(config.DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(users, f, indent=4)

    def register(self, username, password):
        users = self.load_users()
        if username in users:
            return False, "用户名已存在"
        users[username] = {"password": password, "scores": []}
        self.save_users(users)
        return True, "注册成功"

    def login(self, username, password):
        users = self.load_users()
        if username not in users:
            return False, "用户不存在"
        if users[username]["password"] != password:
            return False, "密码错误"
        return True, "登录成功"

    def add_score(self, username, score, difficulty):
        users = self.load_users()
        if username in users:
            record = {
                "score": score,
                "difficulty": difficulty,
                "date": time.strftime("%Y-%m-%d %H:%M")
            }
            users[username]["scores"].append(record)
            self.save_users(users)

    def get_all_rankings(self):
        users = self.load_users()
        rank_list = []
        for u, data in users.items():
            if data["scores"]:
                scores = [s["score"] for s in data["scores"]]
                max_score = max(scores)
                total_score = sum(scores)
                rank_list.append((u, max_score, total_score))
            else:
                rank_list.append((u, 0, 0))
        rank_list.sort(key=lambda x: x[1], reverse=True)
        return rank_list