class Token:
    def __init__(self, turn, id, name):
        self.turn = turn
        self.id = id
        self.name = name

    def color(self, game, offset=0):
        return game.colors[self.turn+offset]

    def rules(self):
        pass

class CNToken(Token):
    def __init__(self, turn, id, name):
        super().__init__(turn, id, name)

    from games import CNChess
    def rules(self, game: CNChess, loc):
        move_pts = []
        def _cannon(lim, drn):
            r = loc[0]+drn[0]
            c = loc[1]+drn[1]
            sup = False
            while lim(r,c):
                if not sup:
                    if game.at([r,c]):
                        sup = True
                    else:
                        move_pts.append([r,c])
                elif game.at([r,c]):
                    if game.at([r,c]).turn != self.turn:
                    # Cannon fire attack
                        move_pts.append([r,c])
                    break
                r += drn[0]
                c += drn[1]
        def _rook(lim, drn):
            r = loc[0]+drn[0]
            c = loc[1]+drn[1]
            while lim(r,c):
                tok = game.at([r,c])
                if not tok:
                    move_pts.append([r,c])
                elif tok.turn != self.turn:
                    move_pts.append([r,c])
                    break
                else:
                    break
                r += drn[0]
                c += drn[1]

        match self.id:
            case 0: # bing/zu
                lf = [loc[0], loc[1]+game.drn[self.turn]]
                if lf[1] >= 0 and lf[1] < 10:
                    tok = game.at(lf)
                    if not tok or tok.turn != self.turn:
                        move_pts.append(lf)
                c0, c1 = game.regions[self.turn]
                for ls in [[loc[0]-1, loc[1]], [loc[0]+1, loc[1]]]:
                    if ls[0] >= 0 and ls[0] < 9 and (ls[1] < c0 or ls[1] >= c1):
                        tok = game.at(lf)
                        if not tok or tok.turn != self.turn:
                            move_pts.append(ls)
            case 1: # pao
                _cannon(lambda r,c:r>=0, (-1,0))
                _cannon(lambda r,c:r<9, (1,0))
                _cannon(lambda r,c:c>=0, (0,-1))
                _cannon(lambda r,c:c<10, (0,1))
            case 2: # ju
                _rook(lambda r,c:r>=0, (-1,0))
                _rook(lambda r,c:r<9, (1,0))
                _rook(lambda r,c:c>=0, (0,-1))
                _rook(lambda r,c:c<10, (0,1))
            case 3: # ma
                for d1,d2 in [((-1,0),(-2,-1)),((-1,0),(-2,1)),((1,0),(2,-1)),((1,0),(2,1)),
                            ((0,-1),(-1,-2)),((0,-1),(1,-2)),((0,1),(-1,2)),((0,1),(1,2))]:
                    l2 = [loc[0]+d2[0], loc[1]+d2[1]]
                    if l2[0] >= 0 and l2[0] < 9 and l2[1] >= 0 and l2[1] < 10:
                        t1 = game.at([loc[0]+d1[0], loc[1]+d1[1]])
                        t2 = game.at(l2)
                        if not t1 and (not t2 or t2.turn != self.turn):
                            move_pts.append(l2)
            case 4: # xiang
                for drn in [(-1,-1), (-1,1), (1,-1), (1,1)]:
                    l1 = [loc[0]+drn[0], loc[1]+drn[1]]
                    l2 = [loc[0]+drn[0]*2, loc[1]+drn[1]*2]
                    rf, rt = game.regions[self.turn]
                    if l2[0] >= 0 and l2[0] < 9 and l2[1] >= rf and l2[1] < rt:
                        t1 = game.at(l1)
                        t2 = game.at(l2)
                        if not t1 and (not t2 or t2.turn != self.turn):
                            move_pts.append(l2)
            case 5: # shi
                pts = []
                if loc == game.cross[self.turn][0]:
                    pts = game.cross[self.turn][1]
                else:
                    pts.append(game.cross[self.turn][0])
                for p in pts:
                    t = game.at(p)
                    if not t or t.turn != self.turn:
                        move_pts.append(p)
            case 6: # jiang/shuai
                for drn in [(0,1),(0,-1),(1,0),(-1,0)]:
                    l = [loc[0]+drn[0], loc[1]+drn[1]]
                    within = True
                    for i in [0,1]:
                        if l[i] < game.camps[self.turn][i][0] or l[i] >= game.camps[self.turn][i][1]:
                            within = False
                            break
                    if not within:
                        continue
                    t = game.at(l)
                    if not t or t.turn != self.turn:
                        move_pts.append(l)
        return move_pts






                


                


