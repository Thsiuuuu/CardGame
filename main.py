# main.py
import tkinter as tk
import os
import config
from views import LoginFrame, DashboardFrame, GameFrame




class MemoryGameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Python 记忆翻牌游戏")
        self.geometry("800x600")
        self.resizable(True, True) # 允许调整大小
        
        self.current_user = None
        
        self.container = tk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        self.frames = {}
        
        # 循环初始化三个界面
        for F in (LoginFrame, DashboardFrame, GameFrame):
            page_name = F.__name__
            frame = F(self.container, self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame("LoginFrame")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()

    def show_game(self, difficulty):
        frame = self.frames["GameFrame"]
        frame.setup_game(difficulty)
        frame.tkraise()

if __name__ == "__main__":
    # 检查图片目录提示
    if not os.path.exists(config.IMG_DIR):
        print(f"提示: 请确保 '{config.IMG_DIR}' 目录下有图片文件。")
    
    app = MemoryGameApp()

    app.mainloop()
