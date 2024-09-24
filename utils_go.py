import copy
def _loc_adj(r, c, board, ignore_ocp=False):
    adjacent = []
    if r > 0 and (ignore_ocp or board[r-1][c] == 2):
        adjacent.append([r-1, c])
    if r < board.shape[0]-1 and (ignore_ocp or board[r+1][c] == 2):
        adjacent.append([r+1, c])
    if c > 0 and (ignore_ocp or board[r][c-1] == 2):
        adjacent.append([r, c-1])
    if c < board.shape[1]-1 and (ignore_ocp or board[r][c+1] == 2):
        adjacent.append([r, c+1])
    return adjacent

class Cluster:
    def __init__(self, r:int, c:int, board):
        self.adjacent = []
        self.body = [[r,c]]
        self.adjacent += _loc_adj(r, c, board)

class BWClusters:
    def __init__(self, board):
        self.bclusters = list[Cluster]()
        self.wclusters = list[Cluster]()
        self.board = board
    
    def join(self, turn:int, r:int, c:int):
        ally = self.bclusters
        enemy = self.wclusters
        if turn:
            ally = self.wclusters
            enemy = self.bclusters
        backup = copy.deepcopy(self.bclusters), copy.deepcopy(self.wclusters)
        
        i = 0
        attack = []
        while i < len(enemy):
            for j in range(len(enemy[i].adjacent)):
                if enemy[i].adjacent[j] == [r,c]:
                    enemy[i].adjacent.pop(j)
                    break
            if not enemy[i].adjacent:
                # clear board location for all cluster body
                locs = enemy.pop(i).body
                for b in locs:
                    self.board[b[0]][b[1]] = 2
                    attack.append(b)
            else:
                i += 1
        for a in attack:
            adj = _loc_adj(a[0], a[1], self.board, True)
            for cl in ally:
                for b in cl.body:
                    if b in adj:
                        cl.adjacent.append(a)
                        break

        belong, group = None, []
        i = 0
        while i < len(ally):
            if [r,c] in ally[i].adjacent:
                group.append(ally.pop(i))
            else:
                i += 1
        if not group:
            belong = Cluster(r, c, self.board)
        else:
            belong = self._merge(r, c, group)
        ally.append(belong)
        
        if not belong.adjacent:
            for loc in [[r,c]]+attack:
                self.board[loc[0]][loc[1]] = 2
            self.bclusters = backup[0]
            self.wclusters = backup[1]
            return False
        return True

    def _merge(self, r, c, group:list[Cluster]):
        group[0].body.append([r,c])
        for cl in group[1:]:
            group[0].body += cl.body
            for a in cl.adjacent:
                if a not in group[0].adjacent:
                    group[0].adjacent.append(a)
        for a in _loc_adj(r, c, self.board):
            if a not in group[0].adjacent:
                group[0].adjacent.append(a)
        group[0].adjacent.remove([r,c])
        return group[0]

