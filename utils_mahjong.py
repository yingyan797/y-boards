import random, copy

class Tile:
    def __init__(self, name):
        self.name = name   
    def rank(self):
        return 0

class NumTile(Tile):
    def __init__(self, num:int, suit:int, name="") -> None:
        super().__init__(name)
        self.num = num
        self.suit = suit
    def rank(self):
        return 12*self.suit+self.num-1

class WindTile(Tile):
    def __init__(self, id:int, name=""):
        super().__init__(name)
        self.id = id
    def rank(self):
        return 35+self.id

class FlowerTile(Tile):
    def __init__(self, id:int, name=""):
        super().__init__(name)
        self.id = id

class Hand:
    def __init__(self, ts:list[Tile], wall:list[Tile]) -> None:
        self.wall = wall
        self.inner = ts
        self.expose = list[Tile]()
        self.flowers = list[Tile]()

    def grab(self):
        while len(self.wall) > 0:
            t = self.wall.pop()
            if not isinstance(t, FlowerTile):
                self.inner.append(t)
                return True
            self.flowers.append(t)
        return False

    def replace(self):
        i = 0
        while i < len(self.inner):
            if isinstance(self.inner[i], FlowerTile):
                self.flowers.append(self.inner.pop(i)) 
            else:
                i += 1
        self._rank()
        for _ in self.flowers:
            self.grab()
            self._insert(self.inner.pop())

    def _rank(self):
        self.inner.sort(key=lambda t:t.rank())
    def _insert(self, t:Tile):
        r = t.rank()
        for i in range(len(self.inner)):
            if r < self.inner[i].rank():
                self.inner = self.inner[:i]+[t]+self.inner[i:]
                return
        self.inner.append(t)

    def _find(self, t:Tile, posf=0):
        i = posf
        while i < len(self.inner):
            if self.inner[i].rank() == t.rank():
                return i
            if self.inner[i].rank() < t.rank():
                return -1
            i += 1
        return -1

    def chi_check(self, t):
        res = []
        if not isinstance(t, NumTile):
            return res
        nr = []
        for d in [-2,-1,1,2]:
            n = t.num+d
            if n >= 1 and n <= 9:
                nr.append(n)
        pf = 0
        nr_pos = []
        for n in nr:
            p = self._find(NumTile(n, t.suit), pf)
            nr_pos.append(p)
            if p < 0:
                continue
            pf = p+1
        for i in range(len(nr_pos)-1):
            if nr_pos[i] >= 0 and nr_pos[i+1] >= 0:
                res.append([nr_pos[i], nr_pos[i+1]])
        return res

    def multi_check(self, t):
        pf = 0
        res = []
        while True:
            p = self._find(t, pf)
            if p >= 0:
                pf = p+1
                res.append(p)
            else:
                return res
            
    def win_check(self, tadd=None):
        backup = copy.deepcopy(self.inner)
        if not tadd:
            tadd = self.inner.pop()
        self._insert(tadd)
        # Check seqs 3
        i, prog = 0, 0
        seq, repeat = [],False
        while True:
            if i == len(self.inner) or isinstance(self.inner[i], WindTile):
                if not repeat:
                    break
                else:
                    i = prog
                    repeat = False
                    continue

            t = self.inner[i]
            if not seq or t.rank() >= seq[-1].rank()+2:
                seq = [t]
            else:
                seq.append(t)
                if len(seq) == 3:
                    for s in seq:
                        self.inner.remove(s) 
                    self.inner = self.inner[:prog] + seq + self.inner[prog:]
                    prog += 3
                    repeat = True
                    seq = []
            i += 1
        
        # Check triple
        seq, pf = [], prog
        for t in self.inner[pf:]:
            if not seq:
                seq.append(t)
            elif t.rank() == seq[-1].rank():
                seq.append(t)
                if len(seq) == 3:
                    seq = []
                    prog += 3
            else:
                seq = [t]

        # Check pair
        if len(self.inner[prog:]) == 2 and self.inner[-1].rank() == self.inner[-2].rank():
            return True
        self.inner = backup
        return False
   
    def push(self, t, group:list):
        group.reverse()
        self.expose += [t]+[self.inner.pop(i) for i in group]

    def show(self):
        res = ([],[],[])
        for t in self.expose:
            res[0].append(t.name)
        for t in self.inner:
            res[1].append(t.name)
        for t in self.flowers:
            res[2].append(t.name)        
        print(res) 

names = ["一二三四伍六七八九", ["1>","2>","3>", "4>","5>","6>","7>","8>","9>"], 
         ["/1","/2","/3","/4","/5","/6","/7","/8","/9"], "東南西北中發口", "春夏秋冬梅蘭竹菊"]
def tiles(shuffle=True):
    all_tiles = list[Tile]()
    for i in range(9):
        for s in range(3):
            all_tiles += [NumTile(i+1, s,names[s][i]) for _ in range(4)]
    for i in range(7):
        all_tiles += [WindTile(i,names[3][i]) for _ in range(4)]

    for i in range(8):
        all_tiles.append(FlowerTile(i,names[4][i]))
    if shuffle:
        random.shuffle(all_tiles)
    return all_tiles

if __name__ == "__main__":
    ts = tiles(shuffle=False)
    h = Hand(ts[:26:2], ts[26:])
    h.replace()
    h.show()
    print(h.multi_check(NumTile(2,0)))
    h.push(NumTile(2,0,"二"), [2,3])
    h.show()