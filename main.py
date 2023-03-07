import asyncio #ランダム動作とアイテム追加
import pygame
import sys
import random
import math

img_item = pygame.image.load("kaihukuitem.png")#回復アイテム
img_bg = pygame.image.load("syutinghaikei1.png")#背景画像
img_player = pygame.image.load("syuting.png")#宇宙船画像
img_weapon = pygame.image.load("mikatatama.png")#宇宙船の銃弾画像
img_enemy = [
    pygame.image.load("tekikyara.png"),#敵キャラ画像
    pygame.image.load("tekikyaratama.png")#敵キャラの銃弾画像
]
img_explode = [#宇宙船の動き方コード
    None,
    pygame.image.load("syuting.png"),
    pygame.image.load("syuting.png"),
    pygame.image.load("syuting.png"),
    pygame.image.load("syuting.png"),
    pygame.image.load("syuting.png"),
    pygame.image.load("syuting.png"),
    pygame.image.load("syuting.png")
]
img_gauge = pygame.image.load("HP.png") #体力ゲージの画像
img_title = pygame.image.load("syutingtitle2.png") #タイトル画面「Gun Try Game」

#p_shoot=何か #自分の打つ音
#p_dame=何か #自分がダメージ受けた音
#e_down=何か #スコア獲得音
#m_bgm=何か #ゲームBGM音
#m_over=何か #ゲームオーバー音
#m_clear=何か #ゲームクリア音

WHITE = (255,255,255) #白
BLACK = (0,0,0) #黒
CLEAR=(255,255,51) #クリアカラー

BAD=(204,0,0) #ゲームオーバーカラー
idx = 0
bg_y = 0
px = 300 #プレイヤーのX座標
py = 300 #プレイヤーのY座標
bx = 0 #弾のX座標
by = 0 #弾のY座標
t = 0 
space = 0
score = 0
BULLET_MAX = 100 
ENEMY_MAX = 100 
ENEMY_BULLET = 1
bull_n = 0
bull_x =[0]*BULLET_MAX
bull_y =[0]*BULLET_MAX
bull_f =[False]*BULLET_MAX

ebull_n = 0
ebull_x = [0]*ENEMY_MAX
ebull_y = [0]*ENEMY_MAX
ebull_a = [0]*ENEMY_MAX
ebull_f =[False]*ENEMY_MAX
ebull_f2 = [False]*ENEMY_MAX
e_list = [0]*ENEMY_MAX
e_speed = [0]*ENEMY_MAX

EFFECT_MAX = 100 
e_n = 0
e_l = [0]*EFFECT_MAX
e_x = [0]*EFFECT_MAX 
e_y = [0]*EFFECT_MAX 

p_gauge = 100 #HPの数　敵の攻撃は一撃　20ダメージ与える
p_invincible = 0

def set_bullet():
    global bull_n
    bull_f[bull_n] = True
    bull_x[bull_n] = px-16
    bull_y[bull_n] = py-32
    bull_n = (bull_n+1)%BULLET_MAX

def move_bullet(screen):#弾を飛ばす　自分の
    for i in range(BULLET_MAX):
        if bull_f[i] == True:
            bull_y[i] = bull_y[i] - 32
            screen.blit(img_weapon,[bull_x[i],bull_y[i]])
            if bull_y[i] < 0:
                bull_f[i] = False

def move_player(screen,key): #プレイヤー動かす
    global px,py,space,p_gauge,p_invincible,idx,t
    if key[pygame.K_UP] == 1:
        py = py - 10
        if py < 300:
            py = 300
    if key[pygame.K_DOWN] == 1:
        py = py + 10
        if py > 660:
            py = 660
    if key[pygame.K_LEFT] == 1:
        px = px - 10
        if px < 20:
            px = 20
    if key[pygame.K_RIGHT] == 1:
        px = px + 10
        if px > 970:
            px = 970
    space = (space+1)*key[pygame.K_SPACE]
    if space%5 == 1: 
        set_bullet()
       #p_shoot.play()#自分が打つ音再生
    if p_invincible%2 == 0: #無敵状態なら点滅させる
        screen.blit(img_player,[px-16,py-16])

    if p_invincible > 0:
        p_invincible = p_invincible - 1 #無敵時は当たり判定を無効にする
        return
    elif idx == 1:
      for i in range(ENEMY_MAX): #敵との当たり判定をチェックする
        if ebull_f[i] == True:
            w = img_enemy[e_list[i]].get_width()
            h = img_enemy[e_list[i]].get_height()
            r = int((w+h)/4+(32+32)/4)
            if distance(ebull_x[i],ebull_y[i],px,py) < r*r: #敵及び敵の攻撃に接触判定
                effect(px,py)
               #p_damage.play()#自分がダメージ受けたときに鳴る 
                p_gauge = p_gauge - 20 #ダメージを受ける
                if p_gauge <= 0:
                    idx = 2
                    t = 0
                if p_invincible == 0:
                    p_invincible = 30 #無敵時間
                ebull_f[i] = False
                ebull_f2[i] = False

def set_enemy(x,y,a,enemy,speed): #敵のセット
    global ebull_n
    while True:
        if ebull_f[ebull_n] == False:
            ebull_f[ebull_n] = True
            ebull_x[ebull_n] = x
            ebull_y[ebull_n] = y
            ebull_a[ebull_n] = a
            e_list[ebull_n] = enemy
            e_speed[ebull_n] = speed
            break
        ebull_n = (ebull_n+1)%ENEMY_MAX
        
def set_enemy1(x,y,a,enemy1,speed): #敵のセット
    global ebull_n
    while True:
        if ebull_f[ebull_n] == False:
            ebull_f[ebull_n] = True
            ebull_x[ebull_n] = x
            ebull_y[ebull_n] = y
            ebull_a[ebull_n] = a
            e_list[ebull_n] = enemy1
            e_speed[ebull_n] = speed
            break
        ebull_n = (ebull_n+1)%ENEMY_MAX

def move_enemy(screen): #敵の動かし方
    global score,idx,t
    for i in range(ENEMY_MAX):#ENEMY_MAX=100
        if ebull_f[i] == True:
            png = e_list[i]
            ebull_x[i] = ebull_x[i] + e_speed[i]*math.cos(math.radians(ebull_a[i]))
            ebull_y[i] = ebull_y[i] + e_speed[i]*math.sin(math.radians(ebull_a[i]))
            if e_list[i] == 0 and ebull_y[i] > 100 and ebull_f2[i] == False:#弾を発射
                set_enemy(ebull_x[i],ebull_y[i],90,1,15)
                ebull_f2[i] = True
            if ebull_x[i] < -40 or ebull_x[i] > 990 or ebull_y[i] < -40 or ebull_y[i] > 920: #画面外に敵が消える
                ebull_f[i] = False
                ebull_f2[i] = False

            if e_list[i] != ENEMY_BULLET:
                w = img_enemy[e_list[i]].get_width()
                h = img_enemy[e_list[i]].get_height()
                r = int((w+h)/4)+8
                for n in range(BULLET_MAX):
                    if bull_f[n] == True and distance(ebull_x[i]-16,ebull_y[i]-16,bull_x[n],bull_y[n]) < r*r:
                        bull_f[n] = False
                        effect(ebull_x[i],ebull_y[i])
                        score = score + 10 # スコア加算
                       #e_down.play() 
                        if score >= 100: #スコア最大数
                            idx = 3
                            t = 0
                        ebull_f[i] = False
                        ebull_f2[i] = False
            rz = pygame.transform.rotozoom(img_enemy[png],-180,1.0)
            screen.blit(rz,[ebull_x[i]-rz.get_width()/2,ebull_y[i]-rz.get_height()/2])

def effect(x,y):
    global e_n
    e_l[e_n] = 1
    e_x[e_n] = x
    e_y[e_n] = y
    e_n = (e_n+1)%EFFECT_MAX

def draw_effect(screen):
    for i in range(EFFECT_MAX):
        if e_l[i] > 0:
            rz = pygame.transform.rotozoom(img_explode[e_l[i]],0,0.5)
            screen.blit(rz,[e_x[i]-30,e_y[i]-30])
            e_l[i] = e_l[i] + 1
            if e_l[i] == 8:
                e_l[i] = 0

def distance(x1,y1,x2,y2):
    return ((x1-x2)*(x1-x2)+(y1-y2)*(y1-y2))

def draw_text(screen,x,y,text,size,col): #文字表示の関数
    font = pygame.font.Font(None,size)
    s = font.render(text,True,col)
    x = x - s.get_width()/2
    y = y - s.get_height()/2
    screen.blit(s,[x,y])

async def main():
    global t,bg_y,idx,score,p_gauge,p_invincible,px,py
    pygame.init()
    pygame.display.set_caption("シューティングゲーム")
    screen = pygame.display.set_mode((1350,800))
    clock = pygame.time.Clock()

    while True:
        await asyncio.sleep(0)
        t=t+1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        bg_y = (bg_y+16)%480
        screen.blit(img_bg,[0,bg_y-480])
        screen.blit(img_bg,[0,bg_y])
        key = pygame.key.get_pressed()

        if idx == 0: #タイトル画面　準備
            img_t = pygame.transform.rotozoom(img_title,0,0.8)
            screen.blit(img_t,[40,200])
            draw_text(screen,620,640,"PRESS SPACE!",80,WHITE)
            if key[pygame.K_SPACE] == 1:
                idx = 1
                t = 0
                score = 0
                px = 320
                py = 300
                p_gauge = 100
                p_invincible = 0
                for i in range(BULLET_MAX):
                    bull_f[i] = False
                for i in range(ENEMY_MAX):
                    ebull_f[i] = False

        if idx == 1:
            move_player(screen,key)
            move_bullet(screen)
           #m_bgm.play(-1) 

            if t%30 == 0:
               set_enemy(random.randint(20,620),-10,90,0,6)

            move_enemy(screen)
        if idx == 2: #ゲームオーバー
            draw_text(screen,675,380,"GAME OVER",200,BAD)
           #m_bgm.stop()
           #m_over.play() 
            if t == 100:
                idx = 0
                t = 0

       # if idx==3:
            
        if idx == 3: #ゲームクリア
            draw_text(screen,675,380,"GAME CLEAR",200,CLEAR)
           #m_bgm.stop()
           #m_clear.play() 
            if t == 100:
                idx = 0
                t = 0
        draw_effect(screen)
        if idx == 1:
            screen.blit(img_gauge,(10,700)) #体力ゲージ表示
            pygame.draw.rect(screen,(32,32,32),[10+p_gauge*2,700,(100-p_gauge)*2,70])
            draw_text(screen, 580, 20, "SCORE" + str(score), 30, WHITE) #スコアの表示
        pygame.display.update()
        clock.tick(30)

    

asyncio.run(main())

if __name__ == "__main__":
    main()