import numpy as np

class Game:
    def __init__(self, name):
        self.name = name
        self.round, self.turn = 0, 0
        self.n_players = 0
        self.ready = False
        self.player_limit = None
    def seats(self, num):
        self.n_players = num
        self.player_names = []

    def create(self):
        self.ready = True
    def restart(self):
        self.round, self.turn = 0,0
    def assign_player(self, name:str):
        if not name:
            name = "Player "+str(len(self.player_names)) 
        if len(self.player_names) < self.n_players:
            self.player_names.append(name)
            return True
        return False
    def cur_player(self):
        return self.player_names[self.turn]
    def next(self):
        if self.turn < self.n_players-1:
            self.turn += 1
        else:
            self.turn = 0
            self.round += 1

    def end(self):
        pass

class BoardGame(Game):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.board: np.ndarray = None

    def create(self):
        super().create()

    def load(self, fn):
        with open(fn, "r") as f:
            lines = f.readlines()
        info = lines[0].split(",")
        self.create(int(info[0]), int(info[1]))
        self.round = int(info[2])
        self.turn = int(info[3])
        for r in range(len(lines)):
            cs = lines[r].split(",")
            for c in range(len(cs)):
                n = int(cs[c])
                self.board[r][c] = n

    def save(self, fn="game"):
        with open(fn, "w") as f:
            f.write(str(self.board.shape[1])+","+str(self.board.shape[0])+","+str(self.round)+","+str(self.turn))
            for row in self.board:
                f.write("\n"+str(row[0]))
                for c in row[1:]:
                    f.write(","+str(c))

    def restart(self):
        super().restart()
        self.create(self.board.shape[1], self.board.shape[0])

    def put(self):
        return True

class BWBoard(BoardGame):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.player_limit = 2

    def create(self, w, h):
        super().create()
        self.board = np.array([[2 for _ in range(w)] for _ in range(h)], dtype=np.int8)
            
    def put(self, r, c):
        self.board[r][c] = self.turn
        return True
    
class MoveBoard(BoardGame):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.player_limit = 2
        self.colors = ["", "", "", ""]

    def create(self, w, h):
        super().create()
        self.shape = (h,w)
        self.board = [[None for _ in range(w)] for _ in range(h)]

    def restart(self):
        self.round, self.turn = 0,0
        self.create(self.shape[1], self.shape[0])

    def color(self):
        return self.colors[self.turn]
    
    def at(self, loc):
        return self.board[loc[0]][loc[1]]

    def put(self, locf, loct):
        if locf == loct:
            return False
        tok = self.at(locf)
        pts = tok.rules(self, locf)
        return loct in pts
    
    def update(self, row, col, locf):
        self.board[row][col] = self.at(locf)
        self.board[locf[0]][locf[1]] = None

from utils_mahjong import Tile, tiles, Hand
class Mahjong(Game):
    def __init__(self, name):
        super().__init__(name)
        self.player_limit = 4
        self.followers = []
        self.acts_avail = [{"chi":["吃",False],"peng":["碰",False],"gang":["槓",False],"hu":["胡",False]} for _ in range(4)]

    def create(self, num:int):
        self.num = num
        self.wall = tiles()
        self.hands = [Hand([self.wall.pop() for _ in range(num)], self.wall) for _ in range(4)]
        for i in range(self.n_players):
            self.hands[i].replace()
        self.cur_tile = None
        super().create()
    
    def _next_n(self, n)->list[int]:
        seq = []
        for i in range(1, n+1):
            hnum = (self.turn+i) % self.n_players
            seq.append(hnum)
        return seq
    
    def seq_check(self, tile:Tile):
        self.cur_tile = tile
        hnums = self._next_n(self.n_players-1)
        # check hu
        for hnum in hnums:
            hand = self.hands[hnum]
            if hand.win_check(tile):
                self.acts_avail[hnum]["hu"][1] = True
                self.followers.append((hnum, "hu", []))
        # check peng/gang
        for hnum in hnums:
            hand = self.hands[hnum]
            ts = hand.multi_check(tile)
            if len(ts) >= 2:
                self.acts_avail[hnum]["peng"][1] = True
                if len(ts) >= 3:
                    self.acts_avail[hnum]["gang"][1] = True
                self.followers.append((hnum, "multi", ts))
                break
        # check chi
        hand = self.hands[hnums[0]]
        ts = hand.chi_check(tile)
        if ts:
            self.acts_avail[hnum]["chi"][1] = True
            self.followers.append((hnum, "chi", ts))




        

        


        
