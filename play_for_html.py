import copy
import random
import numpy as np

# プレイヤーを示す値
YOU = 1
COM = 2

X = ('a','b','c','d','e','f','g','h')
Y = ('1','2','3','4','5','6','7','8')

class Othello():
    def __init__(self,sq,hiddenn,init_player,record=False):
        '''コンストラクタ'''
        self.HIDDENLAYER = [(sq//2)*hiddenn,(sq//2)*hiddenn,2*hiddenn]
        self.hiddenn = hiddenn
        
        self.space = 4
        
        self.record = record
        if self.record:
            self.game_log_txt = ''
        
        self.sq = sq
        if sq==4 or sq==6:
            POPULATION = 20
        else:
            POPULATION = 10
        self.GN = random.randint(0,POPULATION)
        self.genom1= self.read(POPULATION,self.GN)
        self.is_end = False

        self.win_YOU = 0
        self.win_COM = 0
        if init_player == YOU:
            self.player = YOU # 次に置く石の 
            self.color = {#石の色を保持する辞書
                YOU : "black",
                COM : "white"
                }  
        else:
            self.player = COM
            self.color = {#石の色を保持する辞書
                YOU : "white",
                COM : "black"
                }  
   


        # オセロゲームの初期化
        self.initOthello()
        # イベントの設定
        if self.player == COM:
            self.com_yomi()       

    def read(self,popu,gn):
            
        #入力層
        INPUTLAYER = [self.sq//2,self.sq//2,2]
        #隠れ層

        GENOMS = INPUTLAYER[0]*self.HIDDENLAYER[0]+self.HIDDENLAYER[0]+INPUTLAYER[1]*self.HIDDENLAYER[1]+self.HIDDENLAYER[1]+INPUTLAYER[2]*self.HIDDENLAYER[2]+self.HIDDENLAYER[2]
        
        f = open(f"othello{self.sq}{self.sq}h{self.hiddenn}.txt","r",encoding='utf_8')
        genom = f.read()
        GANE = int(genom[:genom.find('[')])
        genom = genom[int(np.log10(GANE))+1:]

        ge = genom.split("・")

        for k in range(popu):
            ge[k] = ge[k].replace("array",'')
            ge[k] = ge[k].replace("]",'')
            ge[k] = ge[k].replace("[",'')
            ge[k] = ge[k].replace("(",'')
            ge[k] = ge[k].replace(")",'')
            ge[k] = ge[k].replace("\n",'')
            
            pregenom = []        
            for i in range(GENOMS):
                if i  == GENOMS-1:
                    a = ge[k][:]
                else:
                    a = ge[k][:ge[k].find(',')]
                pregenom.append(float(a))
                ge[k] = ge[k][ge[k].find(',')+1:]
            ge[k] = pregenom
        
            genom1 = []
            goukei = 0
            for w in range(len(INPUTLAYER)):
                g = []
                for i in range(self.HIDDENLAYER[w]):
                    g.append(pregenom[i*INPUTLAYER[w]:INPUTLAYER[w]+i*INPUTLAYER[w]])
                g.append(pregenom[goukei+INPUTLAYER[w]*self.HIDDENLAYER[w]:goukei+INPUTLAYER[w]*self.HIDDENLAYER[w]+self.HIDDENLAYER[w]])
                genom1.append(g)
                goukei += INPUTLAYER[w]*self.HIDDENLAYER[w]+self.HIDDENLAYER[w]

            ge[k] = genom1
            

        geno1 = ge[gn]
        f.close()
        return geno1
        
    def initOthello(self):
        '''ゲームの初期化を行う'''

        # 盤面上の石を管理する２次元リストを作成（最初は全てNone）
        self.board = [[0] * self.sq for _ in range(self.sq)]
        self.save_board = [[0] * self.sq for _ in range(self.sq)]
        self.placable_board = [[False] * self.sq for _ in range(self.sq)]
        
        # 計算した描画位置に石（円）を描画
        self.board[self.sq//2][self.sq//2] = "white"
        self.board[self.sq//2-1][self.sq//2-1] = "white"
        self.board[self.sq//2][self.sq//2-1] = "black"
        self.board[self.sq//2-1][self.sq//2] = "black"
        
        placable = self.getPlacable(1)
        self.showPlacable(placable)      

    def getPlacable(self,board):
        '''次に置くことができる石の位置を取得'''

        placable = []

        for y in range(self.sq):
            for x in range(self.sq):
                # (x,y) の位置のマスに石が置けるかどうかをチェック
                if self.checkPlacable(x, y,board):
                    # 置けるならその座標をリストに追加
                    placable.append((x, y))

        return placable

    def checkPlacable(self, x, y,board):
        '''(x,y)に石が置けるかどうかをチェック'''

        if board == 1:
            place_board = self.board
        elif board == 2:
            place_board = self.save_board

        # その場所に石が置かれていれば置けない
        if place_board[y][x] != 0:
            return False

        if self.player == YOU:
            other = COM
        else:
            other = YOU

        # (x,y)座標から縦横斜め全方向に対して相手の意思が裏返せるかどうかを確認
        for j in range(-1, 2):
            for i in range(-1, 2):

                # 真ん中方向はチェックしてもしょうがないので次の方向の確認に移る
                if i == 0 and j == 0:
                    continue

                # その方向が盤面外になる場合も次の方向の確認に移る
                if x + i < 0 or x + i >= self.sq or y + j < 0 or y + j >= self.sq:
                    continue

                # 隣が相手の色でなければその方向に石を置いても裏返せない
                if place_board[y + j][x + i] != self.color[other]:
                    continue

                # 置こうとしているマスから遠い方向へ１マスずつ確認
                for s in range(2, self.sq):
                    # 盤面外のマスはチェックしない
                    if x + i * s >= 0 and x + i * s < self.sq and y + j * s >= 0 and y + j * s < self.sq:
                        
                        if place_board[y + j * s][x + i * s] == 0:
                            # 自分の石が見つかる前に空きがある場合
                            # この方向の石は裏返せないので次の方向をチェック
                            break

                        # その方向に自分の色の石があれば石が裏返せる
                        if place_board[y + j * s][x + i * s] == self.color[self.player]:
                            return True
        
        # 裏返せる石がなかったので(x,y)に石は置けない
        return False

            
    def place(self, x, y, color, board):
        '''board(x,y)に色がcolorの石を置く'''

        # (x,y)に石が置かれた時に裏返る石を裏返す
        self.reverse(x, y, board)
        
        # (x,y)に石を置く（円を描画する）

        if board == 1:
            self.board[y][x] = color
            if self.record:
                self.game_log_txt += f'{X[x]}{Y[y]}'
            self.save()
            self.space += 1     
        self.save_board[y][x] = color

        
        # 次に石を置くプレイヤーを決める
        if board == 1:
            before_player = self.player
            self.nextPlayer()
                # 前と同じプレイヤーであればスキップされたことになるのでそれを表示
            if before_player==self.player and self.player==COM:
                self.com_yomi()

            elif not self.player:
                 # 次に石が置けるプレイヤーがいない場合はゲーム終了
                self.showResult()
            if self.player != None:
                # 次に石がおける位置を取得して表示
                placable = self.getPlacable(board)
                self.showPlacable(placable)
               

 

    def reverse(self, x, y,board):
        '''(x,y)に石が置かれた時に裏返す必要のある石を裏返す'''
        if board == 1:
            place_board = self.board
        elif board == 2:
            place_board = self.save_board
         #1:self.board 2:self.save_board

        now = self.player
        if self.player ==YOU:
            other = COM
        else:
            other = YOU
    
        if place_board[y][x] != 0:
            # (x,y)にすでに石が置かれている場合は何もしない
            return

        for j in range(-1, 2):
            for i in range(-1, 2):
                # 真ん中方向はチェックしてもしょうがないので次の方向の確認に移る
                if i == 0 and j == 0:
                    continue

                if x + i < 0 or x + i >= self.sq or y + j < 0 or y + j >= self.sq:
                    continue

                # 隣が相手の色でなければその方向で裏返せる石はない
                if place_board[y + j][x + i] != self.color[other]:
                    continue

                # 置こうとしているマスから遠い方向へ１マスずつ確認
                for s in range(2, self.sq):
                    # 盤面外のマスはチェックしない
                    if x + i * s >= 0 and x + i * s < self.sq and y + j * s >= 0 and y + j * s < self.sq:
                        
                        if place_board[y + j * s][x + i * s] == 0:
                            # 自分の石が見つかる前に空きがある場合
                            # この方向の石は裏返せないので次の方向をチェック
                            break

                        # その方向に自分の色の石があれば石が裏返せる
                        if place_board[y + j * s][x + i * s] == self.color[now]:
                            for n in range(1, s):

                                # 盤面の石の管理リストを石を裏返した状態に更新
                                place_board[y + j * n][x + i * n] = self.color[now]
                            
                            break

    def showPlacable(self,placable):
        for y in range(self.sq):
            for x in range(self.sq):
                if (x,y) in placable:
                    self.placable_board[y][x] = True
                else:
                    self.placable_board[y][x] = False


    def nextPlayer(self):
        '''次に石を置くプレイヤーを決める'''

        before_player = self.player

        # 石を置くプレイヤーを切り替える
        if self.player == YOU:
            self.player = COM
        else:
            self.player = YOU

        # 切り替え後のプレイヤーが石を置けるかどうかを確認
        placable = self.getPlacable(1)

        if len(placable) == 0:
            # 石が置けないのであればスキップ
            self.player = before_player

            # スキップ後のプレイヤーが石を置けるかどうかを確認
            placable = self.getPlacable(1)

            if len(placable) == 0:
                # それでも置けないのであれば両者とも石を置けないということ
                self.player = None

    def showResult(self):
        '''ゲーム終了時の結果を表示する'''
        self.is_end = True
        if self.kazoeru(1)[0] == 0:
            self.win_YOU = 1
        elif self.kazoeru(1)[0] == 2:
            self.win_COM = 1
        if self.record:
            kazu = self.kazoeru(1, color=True)
            if kazu[0] ==0:
                self.game_log_txt = 'B' + self.game_log_txt
            else:
                self.game_log_txt = 'W' + self.game_log_txt
            self.game_log()
            
    def click(self,x,y):
        if self.checkPlacable(x, y, 1):
            self.place(x, y, self.color[YOU],1)

    def com_random(self):
        placable = self.getPlacable(1)

        # 最初のマスを次に石を置くマスとする
        x, y = placable[random.randint(0,len(placable)-1)]

        # 石を置く
        self.place(x, y, self.color[self.player],1)

    def com_yomi(self):
        now = self.player #打つ人=now
        
        placa = self.getPlacable(1)
        point_list = [0]*len(placa)

        for i in range(len(placa)):
             #nowが打てる手それぞれ計算
            self.save()#save_boardを初期化
            self.player  = now
            self.place(placa[i][0], placa[i][1], self.color[now], 2)

            self.nextPlayer()#相手に変わる
            count = 1
            
            while True:
                nowplayer = self.player
                if nowplayer == YOU:
                    otherplayer = COM
                else:
                    otherplayer = YOU
                    
                placa2 = self.getPlacable(2)
                oita2 = copy.deepcopy(self.save_board)
                
                if len(placa2)==0:
                    break

                k_list =[0]*len(placa2)
                for j in range(len(placa2)):
                    #価値の計算
                    self.place(placa2[j][0],placa2[j][1],self.color[nowplayer],2)
                    

                    kboard = [[0] * self.sq for _ in range(self.sq)]
                    for y in range(self.sq):
                        for x in range(self.sq):
                            if self.save_board[y][x] == self.color[nowplayer]:
                                kboard[y][x] = 1
                            elif self.save_board[y][x] == self.color[otherplayer]:
                                kboard[y][x] = -1
                        
                    
                    lineu1 = kboard[0][:self.sq//2]
                    lineu2 = [kboard[0][self.sq-1-i] for i in range(self.sq//2)]
                    lined1 = [kboard[self.sq-1][i] for i in range(self.sq//2)]
                    lined2 = [kboard[self.sq-1][self.sq-1-i] for i in range(self.sq//2)]
                    linel1 = [kboard[i][0] for i in range(self.sq//2)]
                    linel2 = [kboard[self.sq-1-i][0] for i in range(self.sq//2)]
                    liner1 = [kboard[i][self.sq-1] for i in range(self.sq//2)]
                    liner2 = [kboard[self.sq-1-i][self.sq-1] for i in range(self.sq//2)]
                    
                    ob1 = [kboard[i][i] for i in range(self.sq//2)]
                    ob2 = [kboard[self.sq-1-i][self.sq-1-i] for i in range(self.sq//2)]
                    ob3 = [kboard[i][self.sq-1-i] for i in range(self.sq//2)]
                    ob4 = [kboard[self.sq-1-i][i] for i in range(self.sq//2)]
                    
                    nowkazu = 0
                    for y in range(self.sq):
                        for x in range(self.sq):
                            if self.save_board[y][x] == self.color[nowplayer]:
                                nowkazu += 1
                            
                    wariai = nowkazu/(self.sq**2)
                    if self.space+count+1 < (self.sq**2)//3:
                        tesuu = 1
                    elif self.space+count+1 < ((self.sq**2)//3)*2:
                        tesuu = 1.5
                    else:
                        tesuu = 2
                    waritesu = [wariai,tesuu]
                    
                    
                    a = self.forward(lineu1,self.genom1,0)
                    b = self.forward(lineu2,self.genom1,0)
                    c = self.forward(lined1,self.genom1,0)
                    d = self.forward(lined2,self.genom1,0)                    
                    e = self.forward(liner1,self.genom1,0)
                    f = self.forward(liner2,self.genom1,0)                    
                    g = self.forward(linel1,self.genom1,0)
                    h = self.forward(linel2,self.genom1,0)                    
                    m = self.forward(ob1,self.genom1,1)
                    n = self.forward(ob2,self.genom1,1)
                    k = self.forward(ob3,self.genom1,1)
                    l = self.forward(ob4,self.genom1,1)
                    
                    p = self.forward(waritesu,self.genom1,2)
                    
                    k_list[j] = (a+b+c+d+e+f+g+h)/2+m+n+k+l+p
                    self.save_board = copy.deepcopy(oita2)

                if nowplayer == now:
                    point_list[i] += np.max(k_list)
                else:
                    point_list[i] -= np.max(k_list)
                
                pl = placa2[np.argmax(k_list)]

                self.place(pl[0],pl[1], self.color[nowplayer], 2)
                self.nextPlayer()
                count += 1
                if len(self.getPlacable(2)) == 0:
                    self.nextPlayer()
                    if len(self.getPlacable(2)) == 0:
                        break
            kazu = self.kazoeru(2,player=now)
            if kazu[0] == 0:
                point_list[i] += 100
            elif kazu[0] == 2:
                point_list[i] -= 100
                

        self.player = now
        pl = placa[np.argmax(point_list)]
        self.place(pl[0],pl[1], self.color[now], 1)
        

    def forward(self, vector, genom,w):
        """順伝達"""
        
        w1 = []
        for i in range(self.HIDDENLAYER[w]):
            w1.append(genom[w][i])
        w2 = genom[w][self.HIDDENLAYER[w]]
        # vector: 特徴量, w1: 入力層から中間層への重み, w2: 中間層から出力層への重み
        layer1 = np.dot(w1,vector )
        layer2 = self.sigmoid(layer1)
        layer3 = np.dot(layer2, w2)
        return layer3
    
    def sigmoid(self, x):
        """活性化関数"""
        return 1 / (1 + np.exp(-x))

    def save(self):
        """
        セーブする
        """
        self.save_board = copy.deepcopy(self.board)
        
        
    def kazoeru(self,board,color=False,player=None):
        num_your = 0
        num_com = 0
        
        if color:
            kazo1 = 1
            kazo2 = -1
        elif player != None:
            if player == YOU:
                kazo1 = self.color[YOU]
                kazo2 = self.color[COM]
            elif player == COM:
                kazo1 = self.color[COM]
                kazo2 = self.color[YOU]   
        else:
            kazo1 = self.color[YOU]
            kazo2 = self.color[COM]
        
        if board == 1:
            kazoeru_board = self.board
        elif board == 2:
            kazoeru_board = self.save_board

        for y in range(self.sq):
            for x in range(self.sq):
                if kazoeru_board[y][x] == kazo1:
                    num_your += 1
                elif kazoeru_board[y][x] == kazo2:
                    num_com += 1
        if num_your > num_com:
            return 0,num_your,num_com
        elif num_your == num_com:
            return 1,num_your,num_com
        else:
            return 2,num_your,num_com
            
            
    def game_log(self):
        f = open(f"record.txt","r",encoding='utf_8')
        pre = f.read()
        new = pre.split('・')
        new.append(self.game_log_txt)
        f.close()
        g = open(f'record.txt', 'w')
        g.write('・'.join(map(str,new)))
        g.close()
