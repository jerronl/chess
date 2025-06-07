# xiangqi_v3_custom.py
# ✅ 使用 chess(1).rar 的 GIF 命名规则与选中态图

import pygame
import sys
import json
import copy
import os

pygame.init()
pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 540, 600
CELL_SIZE = 60
OFFSET_X, OFFSET_Y = 30, 30
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("中国象棋 V3")

WHITE, BLACK, RED, GRAY = (255, 255, 255), (0, 0, 0), (200, 0, 0), (200, 200, 200)

ASSETS = "assets"
PIECE_IMAGES = {}
SELECTED_IMAGES = {}

# 闪烁事件
BLINK_EVENT = pygame.USEREVENT + 1
blink = GRAY
# pygame.time.set_timer(BLINK_EVENT, 500)

# 加载 GIF 图像（根据 chess(1).rar 命名规则）
for prefix, color in [("b", BLACK), ("r", RED)]:
    names = (
        ["Ju", "Ma", "Xiang", "Shi", "Pao", "Zu", "Jiang"]
        if prefix == "b"
        else ["Ju", "Ma", "Xiang", "Shi", "Pao", "Bing", "Shuai"]
    )
    chinese = (
        ["車", "馬", "象", "士", "炮", "卒", "將"]
        if prefix == "b"
        else ["車", "馬", "相", "仕", "炮", "兵", "帥"]
    )
    for en, zh in zip(names, chinese):
        normal_file = f"{prefix}{en}.GIF"
        select_file = f"{prefix}{en}2.GIF"
        normal_path = os.path.join(ASSETS, normal_file)
        select_path = os.path.join(ASSETS, select_file)
        if os.path.exists(normal_path):
            PIECE_IMAGES[(zh, color)] = pygame.image.load(normal_path).convert_alpha()
        if os.path.exists(select_path):
            SELECTED_IMAGES[(zh, color)] = pygame.image.load(
                select_path
            ).convert_alpha()

# 背景图
board_path = os.path.join(ASSETS, "board.png")
BOARD_IMG = pygame.image.load(board_path) if os.path.exists(board_path) else None

# 音效（可选）
SOUND_MOVE = (
    pygame.mixer.Sound(os.path.join(ASSETS, "move.wav"))
    if os.path.exists(os.path.join(ASSETS, "move.wav"))
    else None
)
SOUND_EAT = (
    pygame.mixer.Sound(os.path.join(ASSETS, "eat.wav"))
    if os.path.exists(os.path.join(ASSETS, "eat.wav"))
    else None
)
SOUND_UNDO = (
    pygame.mixer.Sound(os.path.join(ASSETS, "undo.wav"))
    if os.path.exists(os.path.join(ASSETS, "undo.wav"))
    else None
)

# 初始棋子
initial_pieces = [
    ("車", 0, 0, BLACK),
    ("馬", 1, 0, BLACK),
    ("象", 2, 0, BLACK),
    ("士", 3, 0, BLACK),
    ("將", 4, 0, BLACK),
    ("士", 5, 0, BLACK),
    ("象", 6, 0, BLACK),
    ("馬", 7, 0, BLACK),
    ("車", 8, 0, BLACK),
    ("炮", 1, 2, BLACK),
    ("炮", 7, 2, BLACK),
    *[("卒", i, 3, BLACK) for i in range(0, 9, 2)],
    ("車", 0, 9, RED),
    ("馬", 1, 9, RED),
    ("相", 2, 9, RED),
    ("仕", 3, 9, RED),
    ("帥", 4, 9, RED),
    ("仕", 5, 9, RED),
    ("相", 6, 9, RED),
    ("馬", 7, 9, RED),
    ("車", 8, 9, RED),
    ("炮", 1, 7, RED),
    ("炮", 7, 7, RED),
    *[("兵", i, 6, RED) for i in range(0, 9, 2)],
]
pieces = [dict(name=n, x=x, y=y, color=c) for n, x, y, c in initial_pieces]
history = []
selected, current_turn = None, RED


def check_game_over():
    names = [p["name"] for p in pieces if p["name"] in ("帥", "將")]
    if "帥" not in names:
        return BLACK
    if "將" not in names:
        return RED
    return None


def confirm_restart():
    font = pygame.font.SysFont("SimHei", 28)
    text1 = font.render("是否重新开始？(Y/N)", True, (0, 0, 255))
    SCREEN.blit(text1, (WIDTH // 2 - text1.get_width() // 2, HEIGHT // 2 + 20))
    pygame.display.flip()
    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_y:
                return True
            elif event.key == pygame.K_n:
                return False


def restart_game():
    global pieces, history, selected, current_turn
    pieces = [dict(name=n, x=x, y=y, color=c) for n, x, y, c in initial_pieces]
    history.clear()
    selected = None
    current_turn = RED


def draw_board():
    if BOARD_IMG:
        SCREEN.blit(pygame.transform.scale(BOARD_IMG, (WIDTH, HEIGHT)), (0, 0))
    else:
        SCREEN.fill(WHITE)
        for i in range(10):
            pygame.draw.line(
                SCREEN,
                BLACK,
                (OFFSET_X, OFFSET_Y + i * CELL_SIZE),
                (OFFSET_X + 8 * CELL_SIZE, OFFSET_Y + i * CELL_SIZE),
                1,
            )
        for i in range(9):
            if i in (0, 8):
                pygame.draw.line(
                    SCREEN,
                    BLACK,
                    (OFFSET_X + i * CELL_SIZE, OFFSET_Y),
                    (OFFSET_X + i * CELL_SIZE, OFFSET_Y + 9 * CELL_SIZE),
                    1,
                )
            else:
                pygame.draw.line(
                    SCREEN,
                    BLACK,
                    (OFFSET_X + i * CELL_SIZE, OFFSET_Y),
                    (OFFSET_X + i * CELL_SIZE, OFFSET_Y + 4 * CELL_SIZE),
                    1,
                )
                pygame.draw.line(
                    SCREEN,
                    BLACK,
                    (OFFSET_X + i * CELL_SIZE, OFFSET_Y + 5 * CELL_SIZE),
                    (OFFSET_X + i * CELL_SIZE, OFFSET_Y + 9 * CELL_SIZE),
                    1,
                )

        # 九宫格斜线
        pygame.draw.line(
            SCREEN,
            BLACK,
            (OFFSET_X + 3 * CELL_SIZE, OFFSET_Y),
            (OFFSET_X + 5 * CELL_SIZE, OFFSET_Y + 2 * CELL_SIZE),
            1,
        )
        pygame.draw.line(
            SCREEN,
            BLACK,
            (OFFSET_X + 5 * CELL_SIZE, OFFSET_Y),
            (OFFSET_X + 3 * CELL_SIZE, OFFSET_Y + 2 * CELL_SIZE),
            1,
        )
        pygame.draw.line(
            SCREEN,
            BLACK,
            (OFFSET_X + 3 * CELL_SIZE, OFFSET_Y + 7 * CELL_SIZE),
            (OFFSET_X + 5 * CELL_SIZE, OFFSET_Y + 9 * CELL_SIZE),
            1,
        )
        pygame.draw.line(
            SCREEN,
            BLACK,
            (OFFSET_X + 5 * CELL_SIZE, OFFSET_Y + 7 * CELL_SIZE),
            (OFFSET_X + 3 * CELL_SIZE, OFFSET_Y + 9 * CELL_SIZE),
            1,
        )

        # 楚河汉界文字
        font = pygame.font.SysFont("SimHei", 28)
        text = font.render("楚 河     汉 界", True, BLACK)
        SCREEN.blit(
            text, (WIDTH // 2 - text.get_width() // 2, OFFSET_Y + 4.2 * CELL_SIZE)
        )


def draw_pieces():
    for p in pieces:
        cx = OFFSET_X + p["x"] * CELL_SIZE
        cy = OFFSET_Y + (9 - p["y"]) * CELL_SIZE
        key = (p["name"], p["color"])
        img = (
            SELECTED_IMAGES.get(key)
            if p is selected and key in SELECTED_IMAGES
            else PIECE_IMAGES.get(key)
        )
        if img:
            SCREEN.blit(pygame.transform.scale(img, (48, 48)), (cx - 24, cy - 24))
        else:
            font = pygame.font.SysFont("SimHei", 28)
            pygame.draw.circle(SCREEN, p["color"], (cx, cy), 24, 3)
            label = font.render(p["name"], True, p["color"])
            SCREEN.blit(
                label, (cx - label.get_width() // 2, cy - label.get_height() // 2)
            )


def draw_legal_moves():
    if not selected:
        return
    for tx in range(9):
        for ty in range(10):
            if (
                not get_piece_at(tx, ty)
                or get_piece_at(tx, ty)["color"] != selected["color"]
            ) and is_valid_move(selected, tx, ty):
                cx = OFFSET_X + tx * CELL_SIZE
                cy = OFFSET_Y + (9 - ty) * CELL_SIZE
                if get_piece_at(tx, ty):
                    pygame.draw.circle(
                        SCREEN, blink, (cx, cy), 24, 4
                    )  # 敌方棋子处画灰色圆环
                else:
                    pygame.draw.circle(SCREEN, blink, (cx, cy), 6)


def get_piece_at(x, y):
    return next((p for p in pieces if p["x"] == x and p["y"] == y), None)


def is_valid_move(piece, tx, ty):
    dx, dy = tx - piece["x"], ty - piece["y"]
    abs_dx, abs_dy = abs(dx), abs(dy)
    name, x, y = piece["name"], piece["x"], piece["y"]

    if name in ["兵", "卒"]:
        forward = -1 if piece["color"] == RED else 1
        if (piece["color"] == RED and y < 5) or (piece["color"] == BLACK and y > 4):
            return (abs_dx == 1 and dy == 0) or (dx == 0 and dy == forward)
        return dx == 0 and dy == forward

    if name in ["帥", "將"]:
        if not (
            3 <= tx <= 5 and (7 <= ty <= 9 if piece["color"] == RED else 0 <= ty <= 2)
        ):
            return False
        return abs_dx + abs_dy == 1

    if name in ["仕", "士"]:
        return (
            abs_dx == abs_dy == 1
            and (3 <= tx <= 5)
            and (7 <= ty <= 9 if piece["color"] == RED else ty <= 2)
        )

    if name in ["相", "象"]:
        if abs_dx == abs_dy == 2:
            mx, my = (x + tx) // 2, (y + ty) // 2
            if get_piece_at(mx, my):
                return False
            return ty >= 5 if piece["color"] == RED else ty <= 4

    if name == "馬":
        if abs_dx == 2 and abs_dy == 1:
            return not get_piece_at(x + dx // 2, y)
        if abs_dx == 1 and abs_dy == 2:
            return not get_piece_at(x, y + dy // 2)
        return False

    if name == "車":
        if dx == 0:
            step = 1 if dy > 0 else -1
            return all(not get_piece_at(x, y + i) for i in range(step, dy, step))
        if dy == 0:
            step = 1 if dx > 0 else -1
            return all(not get_piece_at(x + i, y) for i in range(step, dx, step))
        return False

    if name == "炮":
        count = 0
        if dx == 0:
            step = 1 if dy > 0 else -1
            for i in range(step, dy, step):
                if get_piece_at(x, y + i):
                    count += 1
        elif dy == 0:
            step = 1 if dx > 0 else -1
            for i in range(step, dx, step):
                if get_piece_at(x + i, y):
                    count += 1
        else:
            return False
        target = get_piece_at(tx, ty)
        return (count == 0 and not target) or (count == 1 and target)

    return False


def undo():
    global pieces, current_turn
    if history:
        pieces.clear()
        pieces.extend(history.pop())
        current_turn = RED if current_turn == BLACK else BLACK
        SOUND_UNDO.play()


def load_replay(filename="replay.txt"):
    global pieces, current_turn, selected
    try:
        with open(filename, encoding="utf-8") as f:
            for line in f:
                parts = line.strip().replace("->", "").split()
                if len(parts) == 5:
                    name, x1, y1, x2, y2 = parts
                    p = get_piece_at(int(x1), int(y1))
                    if p and p["name"] == name:
                        target = get_piece_at(int(x2), int(y2))
                        if target:
                            pieces.remove(target)
                        p["x"], p["y"] = int(x2), int(y2)
                        current_turn = RED if current_turn == BLACK else BLACK
    except Exception as e:
        print("棋谱导入失败：", e)


def main_loop():
    global selected, current_turn, blink
    while True:
        draw_board()
        draw_legal_moves()
        draw_pieces()
        pygame.display.flip()
        if check_game_over() and confirm_restart():
            restart_game()
        event = pygame.event.wait()

        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                undo()
            elif event.key == pygame.K_l:
                load_replay()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            gx = round((mx - OFFSET_X) / CELL_SIZE)
            gy = 9 - round((my - OFFSET_Y) / CELL_SIZE)
            if 0 <= gx <= 8 and 0 <= gy <= 9:
                clicked = get_piece_at(gx, gy)
                if selected:
                    if (
                        not clicked or clicked["color"] != selected["color"]
                    ) and is_valid_move(selected, gx, gy):
                        history.append(copy.deepcopy(pieces))
                        if clicked:
                            pieces.remove(clicked)
                            SOUND_EAT.play()
                        else:
                            SOUND_MOVE.play()
                        selected["x"], selected["y"] = gx, gy
                        current_turn = RED if current_turn == BLACK else BLACK
                    selected = None
                    pygame.time.set_timer(BLINK_EVENT, 0)
                elif clicked and clicked["color"] == current_turn:
                    selected = clicked
                    pygame.time.set_timer(BLINK_EVENT, 500)
        elif event.type == BLINK_EVENT:
            blink = GRAY if blink==RED else RED


if __name__ == "__main__":
    main_loop()
