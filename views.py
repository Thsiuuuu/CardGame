# views.py
import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import random
import os
import config 
from database import DataManager  # 导入数据类

class LoginFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.data_manager = DataManager()
        self._setup_ui()

    def _setup_ui(self):
        tk.Label(self, text="记忆翻牌游戏 - 登录", font=("Arial", 20, "bold")).pack(pady=30)
        form_frame = tk.Frame(self)
        form_frame.pack(pady=10)
        tk.Label(form_frame, text="用户名:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_user = tk.Entry(form_frame)
        self.entry_user.grid(row=0, column=1, padx=5, pady=5)
        tk.Label(form_frame, text="密码:").grid(row=1, column=0, padx=5, pady=5)
        self.entry_pass = tk.Entry(form_frame, show="*")
        self.entry_pass.grid(row=1, column=1, padx=5, pady=5)
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20)
        tk.Button(btn_frame, text="登录", command=self.login, width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="注册", command=self.register, width=10).pack(side=tk.LEFT, padx=10)
        tk.Button(self, text="退出游戏", command=self.master.quit, bg="#FFCCCC").pack(pady=10)

    def login(self):
        u = self.entry_user.get()
        p = self.entry_pass.get()
        success, msg = self.data_manager.login(u, p)
        if success:
            self.controller.current_user = u
            self.controller.show_frame("DashboardFrame")
            self.entry_pass.delete(0, tk.END)
        else:
            messagebox.showerror("错误", msg)

    def register(self):
        u = self.entry_user.get()
        p = self.entry_pass.get()
        if not u or not p:
            messagebox.showwarning("提示", "用户名和密码不能为空")
            return
        success, msg = self.data_manager.register(u, p)
        if success:
            messagebox.showinfo("成功", msg)
        else:
            messagebox.showerror("错误", msg)



class DashboardFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.data_manager = DataManager()
        
        self.lbl_welcome = tk.Label(self, text="", font=("Arial", 16))
        self.lbl_welcome.pack(pady=20)
        
        frame_diff = tk.LabelFrame(self, text="开始游戏 (选择难度)", padx=10, pady=10)
        frame_diff.pack(pady=10, fill="x", padx=50)
        
        for diff in ["简单", "中等", "困难", "专家"]:
            tk.Button(frame_diff, text=diff, 
                      command=lambda d=diff: self.start_game(d)).pack(side=tk.LEFT, expand=True, fill="x", padx=2)
        
        tk.Button(self, text="查看排行榜", command=self.show_rankings, height=2).pack(fill="x", padx=50, pady=10)
        tk.Button(self, text="返回登录", command=self.logout, bg="#FFCCCC").pack(pady=20)

    def tkraise(self, aboveThis=None):
        if self.controller.current_user:
            self.lbl_welcome.config(text=f"欢迎回来, {self.controller.current_user}!")
        super().tkraise(aboveThis)

    def start_game(self, difficulty):
        self.controller.show_game(difficulty)

    def show_rankings(self):
        rankings = self.data_manager.get_all_rankings()
        top_win = tk.Toplevel(self)
        top_win.title("玩家排行榜")
        top_win.geometry("400x400")
        tk.Label(top_win, text="玩家积分榜", font=("Arial", 14, "bold")).pack(pady=10)
        cols = ("排名", "玩家", "最高分", "历史总得分")
        tree = ttk.Treeview(top_win, columns=cols, show='headings')
        tree.heading("排名", text="排名")
        tree.heading("玩家", text="玩家")
        tree.heading("最高分", text="单局最高分")
        tree.heading("历史总得分", text="历史总得分")
        tree.column("排名", width=50, anchor="center")
        tree.column("玩家", width=100, anchor="center")
        tree.column("最高分", width=80, anchor="center")
        tree.column("历史总得分", width=100, anchor="center")
        for idx, (user, max_score, total_score) in enumerate(rankings, 1):
            tree.insert("", "end", values=(idx, user, max_score, total_score))
        tree.pack(expand=True, fill="both", padx=10, pady=10)

    def logout(self):
        self.controller.current_user = None
        self.controller.show_frame("LoginFrame")


class GameFrame(tk.Frame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.data_manager = DataManager()
        
        info_frame = tk.Frame(self, bg="#DDD")
        info_frame.pack(fill="x", pady=5)
        self.lbl_time = tk.Label(info_frame, text="时间: 0s", font=("Arial", 12), bg="#DDD")
        self.lbl_time.pack(side=tk.LEFT, padx=10)
        self.lbl_score = tk.Label(info_frame, text="得分: 0", font=("Arial", 12, "bold"), fg="blue", bg="#DDD")
        self.lbl_score.pack(side=tk.LEFT, padx=10)
        self.lbl_combo = tk.Label(info_frame, text="连击: 0 (加分: 0)", font=("Arial", 12), fg="red", bg="#DDD")
        self.lbl_combo.pack(side=tk.LEFT, padx=10)
        tk.Button(info_frame, text="退出游戏", command=self.quit_game_early, font=("Arial", 10)).pack(side=tk.RIGHT, padx=10)

        self.card_frame = tk.Frame(self)
        self.card_frame.pack(expand=True, pady=10)
        
        self.cards = []
        self.buttons = []
        self.difficulty = ""
        self.time_left = 0
        self.timer_id = None
        self.game_active = False
        self.selected_indices = []
        self.score = 0
        self.combo_count = 0
        self.combo_bonus = 0
        self.card_attempts = {}
        self.matched_pairs = 0
        self.total_pairs = 0
        self.card_back_photo = None
        
    def load_images(self):
        valid_extensions = ('.png', '.jpg', '.jpeg', '.gif', '.GIF', '.PNG', '.JPG')
        if os.path.exists(config.IMG_DIR):
            try:
                all_files = os.listdir(config.IMG_DIR)
                image_files = [f for f in all_files if f.endswith(valid_extensions)]
                if image_files:
                    chosen_file = random.choice(image_files)
                    full_path = os.path.join(config.IMG_DIR, chosen_file)
                    pil_image = Image.open(full_path)
                    if hasattr(Image, 'Resampling'):
                        resample_method = Image.Resampling.LANCZOS
                    else:
                        resample_method = Image.ANTIALIAS
                    pil_image = pil_image.resize((80, 80), resample_method)
                    self.card_back_photo = ImageTk.PhotoImage(pil_image)
                    print(f"随机图片: {chosen_file}")
                else:
                    self.card_back_photo = None
            except Exception as e:
                print(f"图片错误: {e}")
                self.card_back_photo = None
        else:
            self.card_back_photo = None

    def setup_game(self, difficulty):
        self.load_images()
        self.difficulty = difficulty
        cfg = config.DIFFICULTY_CONFIG[difficulty] # 使用配置文件的配置
        
        self.score = 0
        self.combo_count = 0
        self.combo_bonus = 0
        self.matched_pairs = 0
        self.total_pairs = cfg["pairs"]
        self.time_left = cfg["time"]
        self.game_active = False
        self.selected_indices = []
        self.card_attempts = {}
        
        self.update_labels()
        
        all_words = self.data_manager.load_words()
        if len(all_words) < cfg["pairs"]:
            messagebox.showerror("错误", "单词库不足")
            self.controller.show_frame("DashboardFrame")
            return

        chosen_words = random.sample(all_words, cfg["pairs"])
        game_cards_content = chosen_words * 2
        random.shuffle(game_cards_content)
        self.cards = game_cards_content
        for i in range(len(self.cards)):
            self.card_attempts[i] = 0

        for widget in self.card_frame.winfo_children():
            widget.destroy()
        self.buttons = []
        
        cols = cfg["cols"]
        for i, word in enumerate(self.cards):
            btn = tk.Button(self.card_frame, text="???", width=10, height=4, font=("Arial", 10, "bold"),
                            command=lambda idx=i: self.on_card_click(idx))
            if self.card_back_photo:
                btn.config(image=self.card_back_photo, text="", width=80, height=80)
            
            row = i // cols
            col = i % cols
            btn.grid(row=row, column=col, padx=5, pady=5)
            self.buttons.append(btn)
        
        self.start_preview(cfg["preview"])

    def start_preview(self, duration):
        for i, btn in enumerate(self.buttons):
            btn.config(text=self.cards[i], image="", bg="#FFFFAA", width=10, height=4)
        self.lbl_time.config(text=f"记忆时间: {duration}s")
        self.controller.update() 
        self.after(duration * 1000, self.end_preview)

    def end_preview(self):
        for btn in self.buttons:
            if self.card_back_photo:
                btn.config(image=self.card_back_photo, text="", width=80, height=80)
            else:
                btn.config(text="", bg="SystemButtonFace", width=10, height=4)
        self.game_active = True
        self.start_timer()

    def start_timer(self):
        if self.time_left > 0 and self.game_active:
            self.lbl_time.config(text=f"剩余时间: {self.time_left}s", fg="black" if self.time_left > 10 else "red")
            self.time_left -= 1
            self.timer_id = self.after(1000, self.start_timer)
        elif self.time_left <= 0 and self.game_active:
            self.game_over(win=False)

    def on_card_click(self, index):
        if not self.game_active: return
        if index in self.selected_indices: return
        if self.buttons[index]['state'] == 'disabled': return
        
        if len(self.selected_indices) < 2:
            self.buttons[index].config(text=self.cards[index], image="", bg="#FFFFFF", width=10, height=4)
            self.selected_indices.append(index)
            self.card_attempts[index] += 1
            if len(self.selected_indices) == 2:
                self.game_active = False 
                self.after(500, self.check_match)

    def check_match(self):
        idx1, idx2 = self.selected_indices
        word1 = self.cards[idx1]
        word2 = self.cards[idx2]
        
        if word1 == word2:
            self.buttons[idx1].config(bg="#90EE90", state="disabled") 
            self.buttons[idx2].config(bg="#90EE90", state="disabled")
            max_attempts = max(self.card_attempts[idx1], self.card_attempts[idx2])
            base_score = 0
            if max_attempts == 1: base_score = 5
            elif max_attempts == 2: base_score = 3
            elif max_attempts == 3: base_score = 1
            if self.combo_count > 0: self.combo_bonus += 5
            self.score += base_score + self.combo_bonus
            self.combo_count += 1
            self.combo_bonus += 5 
            self.matched_pairs += 1
            if self.matched_pairs == self.total_pairs:
                self.game_over(win=True)
            else:
                self.game_active = True 
        else:
            if self.card_back_photo:
                self.buttons[idx1].config(image=self.card_back_photo, text="", width=80, height=80)
                self.buttons[idx2].config(image=self.card_back_photo, text="", width=80, height=80)
            else:
                self.buttons[idx1].config(text="", bg="SystemButtonFace", width=10, height=4)
                self.buttons[idx2].config(text="", bg="SystemButtonFace", width=10, height=4)
            self.combo_count = 0
            self.combo_bonus = 0
            self.game_active = True 

        self.selected_indices = []
        self.update_labels()

    def update_labels(self):
        self.lbl_score.config(text=f"得分: {self.score}")
        self.lbl_combo.config(text=f"连击: {self.combo_count} (下一次加分: {self.combo_bonus})")

    def quit_game_early(self):
        if self.timer_id: self.after_cancel(self.timer_id)
        self.controller.show_frame("DashboardFrame")

    def game_over(self, win):
        if self.timer_id: self.after_cancel(self.timer_id)
        final_score = self.score
        msg = ""
        if win:
            time_bonus = self.time_left * 1
            final_score += time_bonus
            msg = f"恭喜完成！\n基础得分: {self.score}\n时间奖励: {time_bonus}\n总分: {final_score}"
        else:
            msg = f"时间到！挑战失败。\n总分: {self.score}"
        messagebox.showinfo("游戏结束", msg)
        self.data_manager.add_score(self.controller.current_user, final_score, self.difficulty)

        self.controller.show_frame("DashboardFrame")
