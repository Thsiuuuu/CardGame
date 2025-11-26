# config.py
import os


"""

    请注意：
    如果运行该文件出现问题，可能是中文路径问题，因为英文路径运行是没有问题的，但是按照作业格式更改之后无法正常运行
    如果需要解决该问题，请讲路径全部修改为英文


"""


# 基础路径配置
# 建议使用相对路径，确保在不同电脑上也能运行
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(BASE_DIR, "users.json")
DB_FILE = os.path.join(BASE_DIR, "game.db")
WORDS_FILE = os.path.join(BASE_DIR, "words.txt")
IMG_DIR = os.path.join(BASE_DIR, "images")

# 游戏难度配置
DIFFICULTY_CONFIG = {
    "简单": {"pairs": 6, "time": 60, "preview": 2, "cols": 4},
    "中等": {"pairs": 8, "time": 70, "preview": 3, "cols": 4},
    "困难": {"pairs": 12, "time": 80, "preview": 4, "cols": 6},
    "专家": {"pairs": 18, "time": 90, "preview": 5, "cols": 6}
}