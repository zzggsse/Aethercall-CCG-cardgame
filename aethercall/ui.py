"""图形界面：主菜单选择英雄，Canvas 绘制战场，鼠标点击操作。"""

from __future__ import annotations

import tkinter as tk
from tkinter import font as tkfont

from .ai import SimpleAI
from .cards import HEROES, Card
from .engine import Game, HeroEntity, Minion

WIDTH, HEIGHT = 1180, 760
BG = "#1b2230"
PANEL = "#252f42"
GOLD = "#d9b166"
TEXT = "#e9eef7"
DIM = "#8a97ad"
GREEN = "#4caf6a"
RED = "#d1584c"
BLUE = "#3f7fd1"

CARD_W, CARD_H = 132, 186
MINION_W, MINION_H = 106, 118

# 布局：右侧日志栏之外的战场宽度
BOARD_W = WIDTH - 250
# 手牌收起时只露出顶部一角，抬升后完整展开
HAND_VISIBLE = 42
HAND_REST_Y = HEIGHT - HAND_VISIBLE
HAND_LIFT_Y = HEIGHT - CARD_H - 12
# 英雄面板与随从排的纵向位置，均在手牌上方，互不遮挡
ENEMY_HERO_Y = 56
ENEMY_ROW_Y = 168
BOARD_MID = 300
MY_ROW_Y = 312
MY_HERO_Y = 444


class CardGameApp:
    """游戏主窗口，负责菜单、渲染与交互。"""

    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("灵契战歌 · Aethercall")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)
        self.f_title = tkfont.Font(family="Microsoft YaHei", size=30, weight="bold")
        self.f_head = tkfont.Font(family="Microsoft YaHei", size=15, weight="bold")
        self.f_body = tkfont.Font(family="Microsoft YaHei", size=10)
        self.f_small = tkfont.Font(family="Microsoft YaHei", size=8)
        self.f_stat = tkfont.Font(family="Microsoft YaHei", size=13, weight="bold")
        self.canvas = tk.Canvas(self.root, width=WIDTH, height=HEIGHT, bg=BG,
                                highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_motion)
        self.root.bind("<space>", lambda _e: self.on_end_turn())
        self.root.bind("<Escape>", lambda _e: self.show_menu())

        self.game: Game | None = None
        self.hitboxes: list[tuple[tuple[int, int, int, int], str, object]] = []
        self.selected_card: Card | None = None
        self.selected_minion: Minion | None = None
        self.pending_target_mode: str | None = None
        self.pending_kind: str | None = None
        self.hover: object | None = None
        self.hover_index: int | None = None
        self.selected_index: int | None = None
        self.status = ""
        self.player_hero = "mage"
        self.enemy_hero = "hunter"
        self.ai_busy = False
        self.show_menu()

    # ---------- 通用绘制工具 ----------

    def rrect(self, x1, y1, x2, y2, r=12, **kw):
        points = [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
            x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        ]
        return self.canvas.create_polygon(points, smooth=True, **kw)

    def wrap(self, text: str, width: int) -> str:
        lines, line = [], ""
        for ch in text:
            if self.f_small.measure(line + ch) > width:
                lines.append(line)
                line = ch
            else:
                line += ch
        lines.append(line)
        return "\n".join(lines[:4])

    def add_hit(self, box, kind, ref):
        self.hitboxes.append((box, kind, ref))

    # ---------- 菜单 ----------

    def show_menu(self) -> None:
        self.game = None
        self.ai_busy = False
        self.render_menu()

    def render_menu(self) -> None:
        c = self.canvas
        c.delete("all")
        self.hitboxes = []
        c.create_rectangle(0, 0, WIDTH, HEIGHT, fill=BG, outline="")
        c.create_text(WIDTH // 2, 90, text="灵 契 战 歌", fill=GOLD, font=self.f_title)
        c.create_text(WIDTH // 2, 138, text="AETHERCALL · 单机 CCG 卡牌对战",
                      fill=DIM, font=self.f_body)
        c.create_text(WIDTH // 2, 196, text="选择你的英雄", fill=TEXT, font=self.f_head)
        keys = list(HEROES)
        gap, w, h = 30, 240, 200
        total = len(keys) * w + (len(keys) - 1) * gap
        x = (WIDTH - total) // 2
        for key in keys:
            hero = HEROES[key]
            chosen = key == self.player_hero
            self.rrect(x, 230, x + w, 230 + h, r=16,
                       fill=PANEL, outline=GOLD if chosen else "#39435c",
                       width=3 if chosen else 1)
            c.create_text(x + w // 2, 268, text=hero.class_name, fill=GOLD, font=self.f_head)
            c.create_text(x + w // 2, 300, text=hero.name, fill=TEXT, font=self.f_body)
            c.create_text(x + w // 2, 340, text=f"技能：{hero.power_name}（{hero.power_cost}费）",
                          fill=TEXT, font=self.f_small)
            c.create_text(x + w // 2, 372, text=self.wrap(hero.power_text, w - 40),
                          fill=DIM, font=self.f_small, justify="center")
            c.create_text(x + w // 2, 408, text="✓ 已选择" if chosen else "点击选择",
                          fill=GREEN if chosen else DIM, font=self.f_small)
            self.add_hit((x, 230, x + w, 230 + h), "menu_hero", key)
            x += w + gap

        c.create_text(WIDTH // 2, 476, text="选择对手英雄", fill=TEXT, font=self.f_head)
        bx = (WIDTH - (len(keys) * 150 + (len(keys) - 1) * 20)) // 2
        for key in keys:
            hero = HEROES[key]
            chosen = key == self.enemy_hero
            self.rrect(bx, 502, bx + 150, 552, r=10, fill="#2f3a52" if chosen else PANEL,
                       outline=RED if chosen else "#39435c", width=2 if chosen else 1)
            c.create_text(bx + 75, 527, text=f"AI · {hero.class_name}",
                          fill=TEXT if chosen else DIM, font=self.f_body)
            self.add_hit((bx, 502, bx + 150, 552), "menu_enemy", key)
            bx += 170

        self.rrect(WIDTH // 2 - 130, 592, WIDTH // 2 + 130, 652, r=14, fill=GOLD, outline="")
        c.create_text(WIDTH // 2, 622, text="开 始 对 战", fill="#1b2230", font=self.f_head)
        self.add_hit((WIDTH // 2 - 130, 592, WIDTH // 2 + 130, 652), "menu_start", None)
        c.create_text(WIDTH // 2, 700,
                      text="操作：点击手牌出牌 → 点击目标；点击随从再点敌方单位进行攻击；空格结束回合，ESC 返回菜单",
                      fill=DIM, font=self.f_small)

    # ---------- 开局 ----------

    def start_game(self) -> None:
        self.game = Game(self.player_hero, self.enemy_hero, ai_second=True)
        self.selected_card = None
        self.selected_minion = None
        self.selected_index = None
        self.hover_index = None
        self.pending_target_mode = None
        self.pending_kind = None
        self.status = "你的回合，开始行动吧！"
        self.render()

    # ---------- 战场渲染 ----------


    def render(self) -> None:
        if self.game is None:
            self.render_menu()
            return
        game = self.game
        c = self.canvas
        c.delete("all")
        self.hitboxes = []
        c.create_rectangle(0, 0, WIDTH, HEIGHT, fill=BG, outline="")
        c.create_rectangle(0, ENEMY_ROW_Y - 16, BOARD_W, MY_ROW_Y + MINION_H + 16,
                           fill="#202a3c", outline="")
        c.create_line(0, BOARD_MID, BOARD_W, BOARD_MID, fill="#2d3a4f")

        me = game.players[0]
        foe = game.players[1]
        self.draw_hero(foe, ENEMY_HERO_Y, enemy=True)
        self.draw_hero(me, MY_HERO_Y, enemy=False)
        self.draw_board(foe, ENEMY_ROW_Y, enemy=True)
        self.draw_board(me, MY_ROW_Y, enemy=False)
        self.draw_side_panel(game)
        self.draw_status()
        self.draw_hand(me)
        if game.finished:
            self.draw_result(game)

    def draw_hero(self, player, y: int, enemy: bool) -> None:
        """绘制英雄面板与英雄技能，两者并排居中，不与手牌重叠。"""
        c = self.canvas
        hero = player.hero_entity
        w, h = 200, 88
        pw = 116
        group = w + 20 + pw
        x = (BOARD_W - group) // 2
        border = RED if enemy else BLUE
        active = (self.game.current == player.index) and not self.game.finished
        targetable = self.is_targetable(hero)
        outline, width = (GOLD, 3) if active else (border, 2)
        if targetable:
            outline, width = "#ffd166", 4
        self.rrect(x, y, x + w, y + h, r=14, fill=PANEL, outline=outline, width=width)
        c.create_text(x + w // 2, y + 22, text=hero.hero.name, fill=TEXT, font=self.f_body)
        c.create_text(x + w // 2, y + 44, text=hero.hero.class_name, fill=DIM, font=self.f_small)
        c.create_text(x + 34, y + 68, text=f"♥ {max(0, hero.health)}", fill=RED, font=self.f_stat)
        if hero.armor:
            c.create_text(x + 100, y + 68, text=f"🛡 {hero.armor}", fill="#9fb6d8",
                          font=self.f_stat)
        c.create_text(x + w - 42, y + 68, text=f"牌库 {len(player.deck)}", fill=DIM,
                      font=self.f_small)
        if hero.frozen:
            c.create_text(x + w - 22, y + 18, text="❄", fill="#7fd6ff", font=self.f_stat)
        label = "对手" if enemy else "你"
        c.create_text(x - 34, y + h // 2, text=label, fill=GOLD if not enemy else RED,
                      font=self.f_body)
        self.add_hit((x, y, x + w, y + h), "hero", hero)

        px = x + w + 20
        usable = (not self.game.finished and self.game.current == player.index
                  and self.game.can_use_power(player) and not player.is_ai)
        used = player.power_used and not player.is_ai
        self.rrect(px, y, px + pw, y + h, r=12, fill="#2c3a52",
                   outline=GOLD if usable else "#3a4659", width=2 if usable else 1)
        c.create_text(px + pw // 2, y + 20, text="英雄技能", fill=DIM, font=self.f_small)
        c.create_text(px + pw // 2, y + 44, text=hero.hero.power_name,
                      fill=TEXT if usable else DIM, font=self.f_small, width=pw - 12)
        note = "已使用" if used else f"{hero.hero.power_cost} 费"
        c.create_text(px + pw // 2, y + 70, text=note,
                      fill=GOLD if usable else DIM, font=self.f_small)
        if not player.is_ai:
            self.add_hit((px, y, px + pw, y + h), "power", player)

    def draw_board(self, player, y: int, enemy: bool) -> None:
        c = self.canvas
        board = [m for m in player.board if not m.dead]
        if not board:
            c.create_text(BOARD_W // 2, y + MINION_H // 2,
                          text="（空场）", fill="#48536b", font=self.f_small)
            return
        gap = 12
        step = min(MINION_W + gap, (BOARD_W - 80) // max(1, len(board)))
        total = step * (len(board) - 1) + MINION_W
        x = (BOARD_W - total) // 2
        for minion in board:
            self.draw_minion(minion, x, y, enemy)
            x += step

    def draw_minion(self, minion: Minion, x: int, y: int, enemy: bool) -> None:
        c = self.canvas
        game = self.game
        attack = game.display_attack(minion)
        selected = minion is self.selected_minion
        ready = (not enemy and game.current == 0 and game.minion_can_attack(minion)
                 and not game.finished)
        targetable = self.is_targetable(minion)
        outline, width = "#3a4659", 1
        if minion.taunt:
            outline, width = "#b98a3f", 2
        if ready:
            outline, width = GREEN, 2
        if targetable:
            outline, width = "#ffd166", 3
        if selected:
            outline, width = GOLD, 4
        self.rrect(x, y, x + MINION_W, y + MINION_H, r=12, fill="#2b3550",
                   outline=outline, width=width)
        c.create_text(x + MINION_W // 2, y + 22, text=minion.name, fill=TEXT,
                      font=self.f_small, width=MINION_W - 12)
        tags = []
        if minion.taunt:
            tags.append("嘲讽")
        if minion.divine_shield:
            tags.append("圣盾")
        if "charge" in minion.keywords:
            tags.append("冲锋")
        if minion.frozen:
            tags.append("冻结")
        c.create_text(x + MINION_W // 2, y + 58, text=" · ".join(tags), fill="#9db2d6",
                      font=self.f_small, width=MINION_W - 8)
        c.create_text(x + 18, y + MINION_H - 18, text=str(attack),
                      fill=GOLD if attack != minion.card.attack else "#ffe6a7", font=self.f_stat)
        hp_color = RED if minion.health < minion.max_health else "#7fe08a"
        c.create_text(x + MINION_W - 18, y + MINION_H - 18, text=str(minion.health),
                      fill=hp_color, font=self.f_stat)
        if ready:
            c.create_text(x + MINION_W // 2, y + MINION_H - 18, text="可攻击", fill=GREEN,
                          font=self.f_small)
        self.add_hit((x, y, x + MINION_W, y + MINION_H), "minion", minion)

    # ---------- 手牌：默认只露出顶部一角，悬停/选中时抬升展开 ----------

    def hand_layout(self, player) -> list[tuple[int, Card, int, int, bool]]:
        """返回手牌布局：(序号, 卡牌, x, y, 是否抬升)。抬升的牌完整展开。"""
        hand = player.hand
        if not hand:
            return []
        gap = 10
        avail = BOARD_W - 40
        step = min(CARD_W + gap, (avail - CARD_W) // max(1, len(hand) - 1)) if len(hand) > 1 \
            else CARD_W
        total = step * (len(hand) - 1) + CARD_W
        start = (avail - total) // 2 + 20
        layout = []
        for index, card in enumerate(hand):
            lifted = index in (self.hover_index, self.selected_index)

            y = HAND_LIFT_Y if lifted else HAND_REST_Y
            layout.append((index, card, start + index * step, y, lifted))
        return layout

    def draw_hand(self, player) -> None:
        """先画未抬升的牌，再画抬升的牌，保证放大的牌显示在最上层。"""
        layout = self.hand_layout(player)
        if not layout:
            return
        self.canvas.create_rectangle(0, HAND_REST_Y - 14, BOARD_W, HEIGHT,
                                     fill="#161d29", outline="")
        self.canvas.create_line(0, HAND_REST_Y - 14, BOARD_W, HAND_REST_Y - 14,
                                fill="#333e54")
        for index, card, x, y, lifted in layout:
            if not lifted:
                self.draw_card(index, card, x, y, player, lifted=False)
        for index, card, x, y, lifted in layout:
            if lifted:
                self.draw_card(index, card, x, y, player, lifted=True)

    def draw_card(self, index: int, card: Card, x: int, y: int, player,
                  lifted: bool) -> None:
        c = self.canvas
        game = self.game
        playable = (game.current == 0 and not game.finished and game.can_play(player, card))
        selected = index == self.selected_index
        w, h = CARD_W, CARD_H
        fill = "#2f3b56" if playable else "#242c3d"
        outline = GOLD if selected else (GREEN if playable else "#39435c")
        width = 3 if selected else (2 if playable else 1)
        if lifted:
            c.create_rectangle(x + 4, y + 8, x + w + 6, y + h, fill="#0d1219", outline="")
        self.rrect(x, y, x + w, y + h, r=12, fill=fill, outline=outline, width=width)
        # 费用宝石始终位于卡牌顶部，收起状态下也能看清
        c.create_oval(x + 4, y + 4, x + 36, y + 36,
                      fill="#2f6fd0" if card.cost <= player.mana else "#4a5268", outline=GOLD)
        c.create_text(x + 20, y + 20, text=str(card.cost), fill="#ffffff", font=self.f_body)
        c.create_text(x + w // 2 + 14, y + 20, text=card.name, fill=TEXT, font=self.f_small,
                      width=w - 48)
        if lifted:
            kind = "随从" if card.is_minion else "法术"
            c.create_text(x + w // 2, y + 52, text=kind, fill=DIM, font=self.f_small)
            c.create_text(x + w // 2, y + 96, text=self.wrap(card.text, w - 16),
                          fill="#c2cee4", font=self.f_small, justify="center")
            if card.is_minion:
                c.create_text(x + 18, y + h - 18, text=str(card.attack), fill="#ffe6a7",
                              font=self.f_stat)
                c.create_text(x + w - 18, y + h - 18, text=str(card.health), fill="#7fe08a",
                              font=self.f_stat)
            hint = "点击目标生效" if selected else ("可打出" if playable else "无法打出")
            c.create_text(x + w // 2, y + 70, text=hint,
                          fill=GOLD if selected else (GREEN if playable else DIM),
                          font=self.f_small)
        bottom = y + h if lifted else y + HAND_VISIBLE
        self.add_hit((x, y, x + w, bottom), "hand", (index, card))
    def draw_side_panel(self, game: Game) -> None:
        c = self.canvas
        x0 = WIDTH - 240
        self.rrect(x0, 10, WIDTH - 10, HEIGHT - 10, r=14, fill="#1f2736", outline="#39435c")
        c.create_text(x0 + 115, 36, text="对战日志", fill=GOLD, font=self.f_head)
        y = 62
        for line in game.log[-26:]:
            c.create_text(x0 + 14, y, text=self.wrap(line, 200), anchor="nw", fill="#b9c6dd",
                          font=self.f_small, width=200)
            y += 12 * (1 + line.__len__() // 22) + 8
            if y > HEIGHT - 150:
                break
        me = game.players[0]
        c.create_text(x0 + 115, HEIGHT - 128,
                      text=f"法力水晶 {me.mana} / {me.max_mana}", fill="#7fb2ff",
                      font=self.f_body)
        crystals = "◆ " * me.mana + "◇ " * max(0, me.max_mana - me.mana)
        c.create_text(x0 + 115, HEIGHT - 106, text=crystals.strip(), fill="#5b8fd6",
                      font=self.f_small)
        end_ready = game.current == 0 and not game.finished
        self.rrect(x0 + 30, HEIGHT - 88, WIDTH - 40, HEIGHT - 40, r=12,
                   fill=GOLD if end_ready else "#3a4356", outline="")
        c.create_text(x0 + 115, HEIGHT - 64,
                      text="结束回合" if end_ready else "AI 思考中…",
                      fill="#1b2230" if end_ready else DIM, font=self.f_head)
        if end_ready:
            self.add_hit((x0 + 30, HEIGHT - 88, WIDTH - 40, HEIGHT - 40), "end_turn", None)

    def draw_status(self) -> None:
        self.canvas.create_text(18, 14, text=self.status, anchor="nw", fill=GOLD,
                                font=self.f_body, width=300)
        if self.pending_target_mode:
            self.canvas.create_text(18, 58, text="请选择目标（点击空白处取消）", anchor="nw",
                                    fill="#ffd166", font=self.f_small)

    def draw_result(self, game: Game) -> None:
        c = self.canvas
        c.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#000000", stipple="gray50", outline="")
        if game.winner is None:
            text, color = "平局！", DIM
        elif game.winner == 0:
            text, color = "胜利！你击败了对手", GREEN
        else:
            text, color = "失败…再来一局吧", RED
        self.rrect(WIDTH // 2 - 240, HEIGHT // 2 - 120, WIDTH // 2 + 240, HEIGHT // 2 + 120,
                   r=18, fill=PANEL, outline=GOLD, width=3)
        c.create_text(WIDTH // 2, HEIGHT // 2 - 50, text=text, fill=color, font=self.f_title)
        self.rrect(WIDTH // 2 - 190, HEIGHT // 2 + 20, WIDTH // 2 - 10, HEIGHT // 2 + 76,
                   r=12, fill=GOLD, outline="")
        c.create_text(WIDTH // 2 - 100, HEIGHT // 2 + 48, text="再来一局", fill="#1b2230",
                      font=self.f_head)
        self.add_hit((WIDTH // 2 - 190, HEIGHT // 2 + 20, WIDTH // 2 - 10, HEIGHT // 2 + 76),
                     "again", None)
        self.rrect(WIDTH // 2 + 10, HEIGHT // 2 + 20, WIDTH // 2 + 190, HEIGHT // 2 + 76,
                   r=12, fill="#3a4356", outline=GOLD)
        c.create_text(WIDTH // 2 + 100, HEIGHT // 2 + 48, text="返回菜单", fill=TEXT,
                      font=self.f_head)
        self.add_hit((WIDTH // 2 + 10, HEIGHT // 2 + 20, WIDTH // 2 + 190, HEIGHT // 2 + 76),
                     "menu", None)

    # ---------- 交互 ----------

    def is_targetable(self, entity) -> bool:
        if not self.pending_target_mode or self.game is None:
            return False
        return entity in self.game.valid_targets(self.game.players[0], self.pending_target_mode)

    def hit_test(self, x, y):
        for box, kind, ref in reversed(self.hitboxes):
            x1, y1, x2, y2 = box
            if x1 <= x <= x2 and y1 <= y <= y2:
                return kind, ref
        return None, None

    def on_motion(self, event) -> None:
        kind, ref = self.hit_test(event.x, event.y)
        cursor = "hand2" if kind else ""
        self.canvas.configure(cursor=cursor)
        hovered = ref[0] if kind == "hand" else None
        if hovered != self.hover_index:
            self.hover_index = hovered
            if self.game is not None:
                self.render()

    def on_click(self, event) -> None:
        kind, ref = self.hit_test(event.x, event.y)
        if self.game is None:
            if kind == "menu_hero":
                self.player_hero = ref
            elif kind == "menu_enemy":
                self.enemy_hero = ref
            elif kind == "menu_start":
                self.start_game()
                return
            self.render_menu()
            return
        if self.game.finished:
            if kind == "again":
                self.start_game()
            elif kind == "menu":
                self.show_menu()
            return
        if self.ai_busy or self.game.current != 0:
            return
        self.handle_battle_click(kind, ref)
        self.render()

    def handle_battle_click(self, kind, ref) -> None:
        game = self.game
        me = game.players[0]
        if kind is None:
            self.clear_selection("已取消选择。")
            return
        if kind == "end_turn":
            self.on_end_turn()
            return
        if kind == "hand":
            index, card = ref
            if index == self.selected_index:
                self.clear_selection("已取消选择。")
                return
            if not game.can_play(me, card):
                self.status = f"{card.name} 现在无法打出（法力不足或没有合法目标）。"
                return
            self.selected_minion = None
            if card.targeting == "none":
                game.play_card(me, card)
                self.selected_card = None
                self.selected_index = None
                self.pending_target_mode = None
                self.status = f"打出了 {card.name}。"
                self.after_player_action()
            else:
                self.selected_card = card
                self.selected_index = index
                self.pending_kind = "card"
                self.pending_target_mode = card.targeting
                self.status = f"{card.name}：请选择目标。"
            return
        if kind == "power":
            if not game.can_use_power(me):
                self.status = "英雄技能本回合已用或法力不足。"
                return
            mode = me.hero_entity.hero.power_targeting
            if mode == "none":
                game.use_hero_power(me)
                self.status = "使用了英雄技能。"
                self.after_player_action()
            else:
                self.selected_card = None
                self.selected_minion = None
                self.pending_kind = "power"
                self.pending_target_mode = mode
                self.status = "英雄技能：请选择目标。"
            return
        if kind in {"minion", "hero"}:
            entity = ref
            if self.pending_target_mode:
                if not self.is_targetable(entity):
                    self.status = "该目标不合法，请重新选择。"
                    return
                if self.pending_kind == "card" and self.selected_card is not None:
                    game.play_card(me, self.selected_card, entity)
                    self.status = f"对 {entity.name} 生效。"
                else:
                    game.use_hero_power(me, entity)
                    self.status = f"英雄技能命中 {entity.name}。"
                self.clear_selection(self.status)
                self.after_player_action()
                return
            if kind == "minion" and entity.owner == 0:
                if game.minion_can_attack(entity):
                    self.selected_minion = entity
                    self.status = f"已选择 {entity.name}，请点击攻击目标。"
                else:
                    reason = "本回合无法攻击（刚入场/已攻击/被冻结）"
                    self.status = f"{entity.name} {reason}。"
                return
            if self.selected_minion is not None:
                if not game.can_be_attacked(entity):
                    self.status = "对方有嘲讽随从，必须先攻击它。"
                    return
                attacker = self.selected_minion
                if game.attack(attacker, entity):
                    self.status = f"{attacker.name} 攻击了 {entity.name}。"
                self.selected_minion = None
                self.after_player_action()
                return
            self.status = "先点击自己的随从，再点击攻击目标。"
            return

    def clear_selection(self, status: str = "") -> None:
        self.selected_card = None
        self.selected_minion = None
        self.hover_index = None
        self.selected_index = None
        self.pending_target_mode = None
        self.pending_kind = None
        if status:
            self.status = status

    def after_player_action(self) -> None:
        if self.game.finished:
            self.render()

    def on_end_turn(self) -> None:
        game = self.game
        if game is None or game.finished or game.current != 0 or self.ai_busy:
            return
        self.clear_selection("回合结束，等待对手行动…")
        game.end_turn()
        self.render()
        self.ai_busy = True
        self.root.after(650, self.run_ai_step)

    def run_ai_step(self) -> None:
        game = self.game
        if game is None:
            self.ai_busy = False
            return
        if game.finished or game.current != 1:
            self.ai_busy = False
            self.status = "你的回合。"
            self.render()
            return
        ai = SimpleAI(game, game.players[1])
        acted = self._ai_single_action(ai)
        self.render()
        if game.finished:
            self.ai_busy = False
            return
        if acted:
            self.root.after(600, self.run_ai_step)
        else:
            game.end_turn()
            self.ai_busy = False
            self.status = "你的回合，开始行动吧！"
            self.render()

    def _ai_single_action(self, ai: SimpleAI) -> bool:
        if ai._try_lethal():
            return True
        if ai._play_best_card():
            return True
        if ai._use_power():
            return True
        return ai._attack_once()

    def run(self) -> None:
        self.root.mainloop()


def main() -> None:
    CardGameApp().run()
