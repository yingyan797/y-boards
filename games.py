from game_types import BoardGame, BWBoard, MoveBoard, np
from utils_go import BWClusters

class CRemove(BoardGame):
    def __init__(self, name) -> None:
        super().__init__(name)

    def create(self, w, h):
        super().create()
        self.board = np.ones((h, w), dtype=bool)
        self.board[0][0] = False

    def put(self, r, c):
        self.board[r:,c:] = False
        return True

    def end(self):
        return not self.board.any()
    
class FiveLinear(BWBoard):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.win_len = 5
    def end(self):
        for row in self.board:
            for c in range(self.board.shape[1]-self.win_len+1):
                if (row[c:c+self.win_len] == self.turn).all():
                    return True
        for c in range(self.board.shape[1]):
            for r in range(self.board.shape[0]-self.win_len+1):
                if (self.board[r:r+self.win_len, c] == self.turn).all():
                    return True
        for r in range(self.board.shape[0]-self.win_len+1):
            for c in range(self.board.shape[1]-self.win_len+1):
                win = True
                for i in range(self.win_len):
                    if self.board[r+i][c+i] != self.turn:
                        win = False
                        break
                if win:
                    return True
                
        for r in range(self.board.shape[0]-self.win_len+1):
            for c in range(self.win_len-1, self.board.shape[1]):
                win = True
                for i in range(self.win_len):
                    if self.board[r+i][c-i] != self.turn:
                        win = False
                        break
                if win:
                    return True
            
        return False
    
class Go(BWBoard):
    def __init__(self, name) -> None:
        super().__init__(name)

    def create(self, w, h):
        super().create(w, h)
        self.track = BWClusters(self.board)

    def put(self, r, c):
        super().put(r, c)
        return self.track.join(self.turn, r, c)

    def end(self):
        return False
    
class CNChess(MoveBoard):
    def __init__(self, name) -> None:
        super().__init__(name)
        self.colors = ["lightcoral", "darkgray", "red", "#626262"]
        self.drn = (1, -1)
        self.regions = ((0,5),(5,10))
        self.camps = (((3,6),(0,3)), ((3,6),(7,10)))
        self.cross = (([4,1], [[3,0],[5,0],[3,2],[5,2]]), ([4,8], [[3,7],[3,9],[5,7],[5,9]]))
        
    def create(self, w, h):
        super().create(10, 9)
        from utils_chess import CNToken
        for r in range(0,9,2):
            self.board[r][3] = CNToken(0,0,"兵")
            self.board[r][6] = CNToken(1,0,"卒")
        for r in [1,7]:
            self.board[r][2] = CNToken(0,1,"炮")
            self.board[r][7] = CNToken(1,1,"砲")
        for r in [0,8]:
            self.board[r][0] = CNToken(0,2,"車")
            self.board[r][9] = CNToken(1,2,"車")
        for r in [1,7]:
            self.board[r][0] = CNToken(0,3,"馬")
            self.board[r][9] = CNToken(1,3,"馬")
        for r in [2,6]:
            self.board[r][0] = CNToken(0,4,"相")
            self.board[r][9] = CNToken(1,4,"象")
        for r in [3,5]:
            self.board[r][0] = CNToken(0,5,"仕")
            self.board[r][9] = CNToken(1,5,"士")
        self.board[4][0] = CNToken(0,6,"帥")
        self.board[4][9] = CNToken(1,6,"將")
        self.king_locs = [[4,0], [4,9]]

    def update(self, row, col, locf):
        if self.at(locf).id == 6:
            self.king_locs[self.turn] = [row,col]
        
        face = False
        if self.king_locs[0][0] == self.king_locs[1][0]:
            face = True
            for c in range(self.king_locs[0][1]+1, self.king_locs[1][1]):
                if self.board[self.king_locs[0][0]][c] is not None:
                    face = False
                    break
        if face:
            self.king_locs[abs(1-self.turn)] = None
        elif self.board[row][col] and self.board[row][col].id == 6:
            self.king_locs[self.turn] = None

        super().update(row, col, locf)

    def end(self):
        for i in range(2):
            if self.king_locs[i] is None:
                return self.player_names[i]
        return None
        
if __name__ == "__main__":
    cnc = CNChess("")
    cnc.create(9,10)
    for row in cnc.board:
        names = []
        for c in row:
            if c:
                names.append(c.name)
            else:
                names.append("--")
        print(names)
