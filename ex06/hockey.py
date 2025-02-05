import pygame as pg
import random
import time
import sys


SCREENRECT = pg.Rect(0, 0, 1321, 701)


class Screen:  # スクリーン
    def __init__(self, title, size, bgf):
        self.title = title
        self.size = size
        pg.display.set_caption(title)

        #FULLCREEN 変数
        self.winstyle = 0  # |FULLSCREEN
        self.bestdepth = pg.display.mode_ok(SCREENRECT.size, self.winstyle, 32)

        self.sfc = pg.display.set_mode(
            SCREENRECT.size, self.winstyle, self.bestdepth)
        self.rct = self.sfc.get_rect()
        self.bgi_sfc = pg.image.load(bgf)
        self.bgi_rct = self.bgi_sfc.get_rect()

    def blit(self):
        self.sfc.blit(self.bgi_sfc, self.bgi_rct)

    def full_window(self):
        global fullscreen
        if not fullscreen:
            print("Changing to FULLSCREEN")
            screen_backup = self.sfc.copy()
            self.sfc = pg.display.set_mode(
                SCREENRECT.size, self.winstyle | pg.FULLSCREEN, self.bestdepth
            )
            self.sfc.blit(screen_backup, (0, 0))
        else:
            print("Changing to windowed mode")
            screen_backup = self.sfc.copy()
            self.sfc = pg.display.set_mode(
                SCREENRECT.size, self.winstyle, self.bestdepth
            )
            self.sfc.blit(screen_backup, (0, 0))
        pg.display.flip()
        fullscreen = not fullscreen


class Player:
    def __init__(self, color, xy, yoko, tate, key_delta, scr: Screen):
        self.sfc = pg.Surface((yoko, tate))  # 正方形の空のSurface
        self.sfc.set_colorkey((0, 0, 0))
        pg.draw.rect(self.sfc, color, (0, 0, yoko, tate), width=0)
        self.rct = self.sfc.get_rect()
        self.rct.center = xy
        self.key_delta = key_delta

    def blit(self, scr: Screen):
        scr.sfc.blit(self.sfc, self.rct)

    def update(self, scr: Screen):

        key_dct = pg.key.get_pressed()

        for key, delta in self.key_delta.items():
            if key_dct[key]:
                self.rct.centerx += delta[0]
                self.rct.centery += delta[1]
            if check_bound(self.rct, scr.rct) != (+1, +1):
                self.rct.centerx -= delta[0]
                self.rct.centery -= delta[1]
        self.blit(scr)


class Ball:  # ボールのクラス
    def __init__(self, color, xy, rad, vxy, scr: Screen):
        self.sfc = pg.Surface((2*rad, 2*rad))  # 正方形の空のSurface
        self.sfc.set_colorkey((0, 0, 0))
        pg.draw.circle(self.sfc, color, (rad, rad), rad)
        self.rct = self.sfc.get_rect()
        if random.randint(0, 1) == 0:  # ゲーム開始時に1P,2Pのどちらかが静止したボールを保持できるようにした
            self.rct.center = (300, 350)

        else:
            self.rct.center = (1000, 350)
        self.vx, self.vy = vxy
        self.vx = random.choice((self.vx, -1 * self.vx))
        self.vy = random.choice((self.vy, -1 * self.vy))

    def blit(self, scr: Screen):
        scr.sfc.blit(self.sfc, self.rct)

    def update(self, scr: Screen):
        self.rct.move_ip(self.vx, self.vy)
        yoko, tate = check_bound(self.rct, scr.rct)
        self.vx *= yoko
        self.vy *= tate
        self.blit(scr)



class Scoreboard:
    def __init__(self, color, xy, yoko, tate, px, scr: Screen):
        self.sfc = pg.Surface((yoko, tate))  # 正方形の空のSurface
        self.sfc.set_colorkey((0, 0, 0))
        pg.draw.rect(self.sfc, color, (0, 0, yoko, tate), width=0)
        self.rct = self.sfc.get_rect()
        self.rct.center = xy
        self.px = px

    def font_1(self, score: str):
        font = pg.font.Font(None, self.px)
        text = font.render(score, True, (255, 255, 255))
        self.blit(text, [20, 100])

    def font_2(self, score: str):
        font = pg.font.Font(None, self.px)
        text = font.render(score, True, (255, 255, 255))
        self.blit(text, [20, 100])

class Kabe:  # コートの角のクラス #高橋

    def __init__(self, color, xy, scr: Screen):  # pointsは鋭角, 直角, 鋭角の順
        self.sfc = pg.Surface((100, 100))  # 正方形の空のSurface
        self.sfc.set_colorkey((0, 0, 0))

        pg.draw.rect(self.sfc, color, (0, 0, 200, 200))  # 三角形を作成
        self.rct = self.sfc.get_rect()
        self.rct.center = xy


    def blit(self, scr: Screen):
        scr.sfc.blit(self.sfc, self.rct)


    def update(self, scr: Screen):
        self.blit(scr)


def check_bound(obj_rct, scr_rct):
    """
    第1引数：こうかとんrectまたは爆弾rect
    第2引数：スクリーンrect
    範囲内：+1／範囲外：-1
    """
    yoko, tate = +1, +1
    if obj_rct.left < scr_rct.left or scr_rct.right < obj_rct.right:
        yoko = -1
    if obj_rct.top < scr_rct.top or scr_rct.bottom < obj_rct.bottom:
        tate = -1
    return yoko, tate


# スコアを表示するクラス
class Texts:
    def __init__(self):
        self.font = pg.font.SysFont("msgotic", 70)

    def update(self, scr: Screen, score_1, score_2):
        self.txt = self.font.render(
            f"{score_1}----{score_2}", True, (65, 125, 105)
        )
        scr.sfc.blit(self.txt, (scr.rct.width/2-60, scr.rct.height-100))


def start():#追加機能start画面の作成（宮川）
    scr1 = Screen("2Dテニス", SCREENRECT.size, "fig/tennis_court.jpg")
    clock = pg.time.Clock()
    while True:
        scr1.blit()
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
        key_dct = pg.key.get_pressed() #辞書型
        if key_dct[pg.K_SPACE]:
            return
        pg.display.update()
        clock.tick(1000)


def main():
    global fullscreen
    clock = pg.time.Clock()
    scr = Screen("2Dテニス", SCREENRECT.size, "fig/tennis_court.jpg")
    fullscreen = False  # フルスクリーン無効
    # テキストのインスタンス生成
    text = Texts()

    xys = [(50, SCREENRECT.bottom-50), (50, 50), (SCREENRECT.width-50, 50),
           (SCREENRECT.width-50, SCREENRECT.height-50)]

    kabes = []  # 4つの壁のインスタンスを格納するリスト

    for xy in xys:
        kabe = Kabe((0, 0, 255), xy, scr)
        kabes.append(kabe)
        kabe.blit(scr)

    key_delta_p1 = {
        pg.K_w:    [0, -1],
        pg.K_s:  [0, +1],
        pg.K_a:  [-1, 0],
        pg.K_d: [+1, 0],
    }
    p1 = Player((255, 0, 0), (100, 350), 10, 100, key_delta_p1, scr)
    p1.blit(scr)

    key_delta_p2 = {
        pg.K_UP:    [0, -1],
        pg.K_DOWN:  [0, +1],
        pg.K_LEFT:  [-1, 0],
        pg.K_RIGHT: [+1, 0],
    }
    p2 = Player((0, 255, 0), (1100, 350), 10, 100, key_delta_p2, scr)
    p2.blit(scr)

    ball = Ball((0, 122, 122), (660, 350), 10, (0, 0), scr)
    ball.update(scr)

    ti = 4000  # 追加機能：タイマー(篠宮)
    cl = 0

    while True:
        scr.blit()
        for kabe in kabes: #壁を表示 #高橋
            kabe.blit(scr)
        p1.update(scr)
        p2.update(scr)

        p1_score, p2_score = 0, 0

        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_f:
                    scr.full_window()

        ball.update(scr)
        #ボールとの衝突
        if ti - cl > 400:  # 追加機能：初速を与えた際すぐに下記のif文が反応してしまうことを防ぐため
            if p1.rct.colliderect(ball.rct):  # 追加機能ボールが速度が0の時にプレイヤーが触ると動き出すようにした
                if ball.vx == 0:
                    ball.vx = +1
                    ball.vy = random.choice([-1, 1])
                    cl = ti
                else:
                    ball.vx *= -1
            elif p2.rct.colliderect(ball.rct):
                if ball.vx == 0:
                    ball.vx = -1
                    ball.vy = random.choice([-1, 1])
                    cl = ti
                else:
                    ball.vx *= -1
                    
        for kabe in kabes:  # 壁との衝突 #高橋
            if kabe.rct.colliderect(ball.rct):
                ball.vx = -1 * ball.vx
                ball.vy = -1 * ball.vy

        if ball.rct.left < scr.rct.left:  # 追加機能：ゴールに入った時に得点された側がボールを保持した状態で始められるようにした
            ball.rct.center = (300, 350)
            ball.vx = 0
            ball.vy = 0
            p2_score += 1
        if scr.rct.right < ball.rct.right:  # 出たとき
            ball.rct.center = (1000, 350)
            ball.vx = 0
            ball.vy = 0
            p1_score += 1

        #board.update(scr)
        ti += 1  # 篠宮制作タイマー
        text.update(scr, p1_score, p2_score)
        pg.display.update()
        clock.tick(1000)


if __name__ == "__main__":
    pg.init()
    start()
    main()
    pg.quit()
    sys.exit()
