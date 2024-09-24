from flask import Flask, render_template, request
import game_types as gtypes
import games
import json, os

app = Flask(__name__)

class SiteTrack:
    def __init__(self) -> None:
        self.webs = {
            "--": (None, None),
            "Card remove": (games.CRemove, "cremove.html"),
            "Five linear": (games.FiveLinear, "bwboard.html", "static/fvlnboards/"),
            "Go": (games.Go, "bwboard.html", "static/goboards/"),
            "Chinese Chess": (games.CNChess, "chess.html"),
            "Standard Mahjong": (gtypes.Mahjong, "mahjong.html")
        }
        self.game:gtypes.Game = None

    def load_game(self, gname:str):
        info = self.webs[gname]
        self.game = info[0](gname)
        self.page = info[1]
        if len(info) > 2:
            self.storage = info[2]
        if isinstance(self.game, gtypes.MoveBoard):
            self.locf = None

site = SiteTrack()

@app.route('/home', methods=['GET', 'POST'])
def home():
    site.__init__()
    return render_template('index.html', games=site.webs.keys())

@app.route('/restart', methods=['GET', 'POST'])
def restart():
    site.game.restart()
    return render_template(site.page, game=site.game, end=False)

@app.route('/', methods=['GET', 'POST'])    # main page
def index():
    fm = request.form
    print(fm)
    gname = fm.get("gname")
    if fm.get("load_game"):
        if gname != "--":
            site.load_game(gname)
        if not site.game:
            return render_template('index.html', games=site.webs.keys())
        num = fm.get("n_players")
        n_players = 2
        if site.game.player_limit:
            n_players = site.game.player_limit
        elif num:
            n_players = int(num)

        site.game.seats(n_players)
        return render_template('index.html', n_players=n_players, games=site.webs.keys())
    elif fm.get("register"):
        for i in range(site.game.n_players):
            site.game.assign_player(fm.get("pname"+str(i)))
    else:
        return render_template('index.html', games=site.webs.keys())

    return render_template(site.page, game=site.game, end=False)

@app.route('/board', methods=['GET', 'POST'])
def board():
    assert(isinstance(site.game, gtypes.BoardGame))
    fm = request.form
    print(fm)
    end = False
    if fm.get("setting"):
        bfile = fm.get("lbf")
        if bfile:
            site.game.load(site.storage+bfile)
        else:
            site.game.create(int(fm.get("w")), int(fm.get("h")))
    else:
        if fm.get("save"):
            bfile = fm.get("sbf")
            site.game.save(site.storage+bfile+".csv")
        row, col = None,None
        for r in range(site.game.board.shape[0]):
            for c in range(site.game.board.shape[1]):
                if fm.get("put"+str(r)+"_"+str(c)):
                    row, col = r, c
                    break
        if row is not None and col is not None and site.game.put(row, col):
            if site.game.end():
                end = True
            else:
                site.game.next()
    return render_template(site.page, storage=site.storage, game=site.game, end=end)

@app.route('/chess', methods=['GET', 'POST'])
def chess():
    assert(isinstance(site.game, gtypes.MoveBoard))
    fm = request.form
    print(fm)
    if not site.game.ready:
        site.game.create(1,1)
    elif fm.get("start"):
        site.game.restart()
    row, col = None, None
    for r in range(site.game.shape[0]):
        for c in range(site.game.shape[1]):
            if fm.get("put"+str(r)+"_"+str(c)):
                row, col = r, c
                break
    winner = None
    if row is not None and col is not None:
        moved = False
        if site.locf is not None:
            if site.game.put(site.locf, [row,col]):
                site.game.update(row, col, site.locf)
                site.locf = None
                moved = True
                winner = site.game.end()
                site.game.next()
                
        if not moved:
            t = site.game.at([row, col])
            if t and t.turn == site.game.turn:
                site.locf = [row, col]
        
    return render_template(site.page, game=site.game, locf=site.locf, winner=winner)

@app.route('/mahjong', methods=['GET', 'POST'])
def mahjong():
    assert(isinstance(site.game, gtypes.Mahjong))
    fm = request.form
    print(fm)
    end = ""
    if fm.get("setting"):
        site.game.create(int(fm.get("mahjong_num")))
        site.turn_act = None

    if site.turn_act:
        if fm.get("cancel"+str(site.turn_act[0])):
            site.turn_act = None
        else:
            site.game.followers = []
            if site.turn_act[1] == "hu" and fm.get("hu"+str(site.turn_act[0])):
                end = "Win by acquire"
            elif site.turn_act[1] == "multi":
                if fm.get("peng"+str(site.turn_act[0])):
                    site.game.hands[site.turn_act[0]].push(site.game.cur_tile, site.turn_act[1][1:])
                elif fm.get("gane"+str(site.turn_act[0])):
                    site.game.hands[site.turn_act[0]].push(site.game.cur_tile, site.turn_act[1])
                      
    if site.game.followers:
        site.turn_act = site.game.followers.pop(0)
        site.game.turn = site.turn_act[1]

    hand = site.game.hands[site.game.turn]
    if hand.grab():
        if hand.win_check():
            end = "Win by self grabbing"
    else:
        end = "Draw, all tiles used"

    hands = []
    for p in range(site.game.n_players):
        hand = site.game.hands[p]
        h0 = [ex.name for ex in hand.expose]
        h2 = [fl.name for fl in hand.flowers]
        h1 = [(i, hand.inner[i].name) for i in range(len(hand.inner))]
        hands.append((h0,h1,h2))

            
    return render_template(site.page, game=site.game, hands=hands, acts_avail=acts_avail, history="12345", wall=site.game.wall, end=end)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)