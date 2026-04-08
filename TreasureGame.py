import tkinter as tk
from tkinter import messagebox
import random
import pygame  # サウンド用に追加

class TreasureGame:
    def __init__(self, master):
        self.master = master
        self.master.title("THE TREASURE HUNTER - Sound Edition")
        self.master.geometry("400x550")
        
        # Pygame Mixerの初期化
        pygame.mixer.init()
        self.load_sounds()

        self.container = tk.Frame(self.master)
        self.container.pack(expand=True, fill="both")
        
        self.show_title_screen()
    def clear_screen(self):
        """現在の画面にあるウィジェット（ボタンやラベル）をすべて削除する"""
        for widget in self.container.winfo_children():
            widget.destroy()
    def load_sounds(self):
        """音源ファイルの読み込み（ファイルがない場合はエラーを防ぐ処理付き）"""
        try:
            # BGM
            # pygame.mixer.music.load("bgm.mp3") 
            # self.sound_win = pygame.mixer.Sound("win.wav")
            # self.sound_lose = pygame.mixer.Sound("lose.wav")
            # self.sound_trap = pygame.mixer.Sound("trap.wav")
            # self.sound_move = pygame.mixer.Sound("move.wav")
            self.has_sound = False # ファイルがない場合はFalseにしておく
            print("音源ファイルをセットすれば、よりリアルな音が鳴ります！")
        except:
            self.has_sound = False

    def play_bgm(self):
        if self.has_sound:
            pygame.mixer.music.play(-1) # ループ再生

    def stop_bgm(self):
        if self.has_sound:
            pygame.mixer.music.stop()

    def play_effect(self, effect_name):
        """効果音を鳴らす（実際にはファイルパスを指定してください）"""
        # ここでは簡易的に、OS標準のベル音を鳴らすか、ファイルを再生する処理を書きます
        if self.has_sound:
            # self.sound_move.play() などの処理
            pass
        else:
            self.master.bell() # ファイルがない場合の代用（OSの警告音）

    # --- 画面遷移部分は前回と同じですが、各アクションに音を追加 ---

    def start_game(self):
        self.play_bgm() # BGMスタート
        # （中略：ゲーム初期化ロジック）
        self.size = 5
        self.num_traps = 3
        self.time_left = 30
        self.start_pos = (random.randint(0, self.size - 1), random.randint(0, self.size - 1))
        self.player_pos = self.start_pos
        self.relocate_items()
        self.show_game_screen()
        self.update_timer()

    def move_player(self, x, y):
        dist = abs(self.player_pos[0] - x) + abs(self.player_pos[1] - y)
        if dist != 1: return

        self.play_effect("move") # 移動音
        self.player_pos = (x, y)
        self.history.add(self.player_pos)
        
        if self.player_pos == self.treasure:
            self.stop_bgm()
            self.play_effect("win") # 勝利音
            self.master.after_cancel(self.timer_id)
            self.show_ending_screen(True)
        elif self.player_pos in self.traps:
            self.play_effect("trap") # 罠の音
            self.time_left = max(0, self.time_left - 5)
            messagebox.showerror("TRAP", "😱 罠だ！！")
            self.player_pos = self.start_pos
            self.relocate_items()
            self.update_board()
        else:
            self.update_board()

# --- 1. タイトル画面 ---
    def show_title_screen(self):
        self.clear_screen()
        frame = tk.Frame(self.container)
        frame.pack(expand=True)

        tk.Label(frame, text="THE TREASURE\nHUNTER", font=("MS Gothic", 30, "bold"), fg="gold", bg="black").pack(pady=20)
        tk.Label(frame, text="～ 呪われたシャッフル迷宮 ～", font=("MS Gothic", 12)).pack(pady=10)
        
        tk.Button(frame, text="探索を開始する", font=("MS Gothic", 14), command=self.start_game, width=20, height=2).pack(pady=30)
        tk.Label(frame, text="[ルール]\n30秒以内に宝を探せ。罠を踏むと\n位置が全シャッフル＆残り時間-5秒！", justify="center").pack()

    # --- 2. ゲーム本編の準備 ---
    def start_game(self):
        self.size = 5
        self.num_traps = 3
        self.time_left = 30
        self.start_pos = (random.randint(0, self.size - 1), random.randint(0, self.size - 1))
        self.player_pos = self.start_pos
        self.relocate_items()
        
        self.show_game_screen()
        self.update_timer()

    def relocate_items(self):
        self.treasure = (random.randint(0, self.size - 1), random.randint(0, self.size - 1))
        while self.treasure == self.start_pos:
            self.treasure = (random.randint(0, self.size - 1), random.randint(0, self.size - 1))
        
        self.map_fragment = (random.randint(0, self.size - 1), random.randint(0, self.size - 1))
        while self.map_fragment in [self.start_pos, self.treasure]:
            self.map_fragment = (random.randint(0, self.size - 1), random.randint(0, self.size - 1))
            
        self.traps = []
        while len(self.traps) < self.num_traps:
            t = (random.randint(0, self.size - 1), random.randint(0, self.size - 1))
            if t not in [self.start_pos, self.treasure, self.map_fragment] and t not in self.traps:
                self.traps.append(t)
        self.history = {self.player_pos}

    def show_game_screen(self):
        self.clear_screen()
        
        # ヘッダー（タイマー）
        self.label_timer = tk.Label(self.container, text=f"TIME: {self.time_left}", font=("Arial", 16, "bold"), fg="red")
        self.label_timer.pack(pady=10)

        # マップ
        self.map_frame = tk.Frame(self.container)
        self.map_frame.pack(pady=10)
        self.buttons = {}
        for y in range(self.size):
            for x in range(self.size):
                btn = tk.Button(self.map_frame, width=6, height=3, command=lambda x=x, y=y: self.move_player(x, y))
                btn.grid(row=self.size-1-y, column=x)
                self.buttons[(x, y)] = btn
        
        # フッター（ヒント）
        self.label_info = tk.Label(self.container, text="", font=("MS Gothic", 10))
        self.label_info.pack(pady=10)
        self.update_board()

    def update_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.label_timer.config(text=f"TIME: {self.time_left}")
            self.timer_id = self.master.after(1000, self.update_timer)
        else:
            self.show_ending_screen(False)

    def move_player(self, x, y):
        dist = abs(self.player_pos[0] - x) + abs(self.player_pos[1] - y)
        if dist != 1: return

        self.player_pos = (x, y)
        self.history.add(self.player_pos)
        
        if self.player_pos == self.treasure:
            self.master.after_cancel(self.timer_id)
            self.show_ending_screen(True)
        elif self.player_pos == self.map_fragment:
            messagebox.showinfo("INFO", f"📜 古びた地図を入手！\n罠の場所: {self.traps}")
            self.map_fragment = (-1, -1)
            self.update_board()
        elif self.player_pos in self.traps:
            self.time_left = max(0, self.time_left - 5)
            messagebox.showerror("TRAP", "😱 罠だ！(TIME-5秒)\n全てが書き換えられた！")
            self.player_pos = self.start_pos
            self.relocate_items()
            self.update_board()
        else:
            self.update_board()

    def update_board(self):
        for coord, btn in self.buttons.items():
            btn.config(text="", bg="#f0f0f0")
            if coord in self.history: btn.config(bg="#dcdcdc")
            if coord == self.map_fragment: btn.config(text="M", fg="blue")
            if coord == self.player_pos: btn.config(text="YOU", bg="yellow")
        
        t_dist = abs(self.player_pos[0] - self.treasure[0]) + abs(self.player_pos[1] - self.treasure[1])
        warn = "⚠️ 嫌な予感がする... " if any(abs(self.player_pos[0]-tx) + abs(self.player_pos[1]-ty) == 1 for tx, ty in self.traps) else ""
        self.label_info.config(text=f"{warn}\n宝まであと {t_dist} マス")

    # --- 3. エンディング画面 ---
    def show_ending_screen(self, won):
        self.clear_screen()
        frame = tk.Frame(self.container)
        frame.pack(expand=True)

        if won:
            title = "GAME CLEAR!"
            color = "orange"
            msg = f"見事に宝を手に入れた！\n残り時間: {self.time_left}秒"
        else:
            title = "GAME OVER"
            color = "gray"
            msg = "あなたは迷宮の塵となった..."

        tk.Label(frame, text=title, font=("Arial", 30, "bold"), fg=color).pack(pady=20)
        tk.Label(frame, text=msg, font=("MS Gothic", 12)).pack(pady=20)
        
        tk.Button(frame, text="もう一度挑戦する", command=self.start_game).pack(pady=10)
        tk.Button(frame, text="タイトルへ戻る", command=self.show_title_screen).pack()

if __name__ == "__main__":
    root = tk.Tk()
    app = TreasureGame(root)
    root.mainloop()
