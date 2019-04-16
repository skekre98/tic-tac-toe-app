from flask import Flask, session, render_template, request, redirect, url_for
from random import randint,shuffle
import copy

### Globals ###

app = Flask(__name__)
app.secret_key = '9*TGIKi7tggkuyUPJKdY%W^$WKLHOyjv,liIUFL>N>'

class Move(object):
    row = 0
    column = 0
    score = 0

    def __init__(self,row,column,score):
        self.row = row
        self.column = column
        self.score = score

def parsenum (s):
    try:
        return int(s)
    except ValueError:
        return float(s)

# Checks if there are still any legal moves remaining
def is_Full(board):
    for row in board:
        for col in row:
            if(col == 0):
                return False
    return True

def sort_Moves(list):
    for i in range(0, len(list) - 1):
        for j in range(i, len(list)):
            if list[i].score < list[j].score:
                temp = list[i]
                list[i] = list[j]
                list[j] = temp

# This method will return the state of the board
# -1 ~ X won
# 0 ~ Draw
# 1 ~ 0 won
# 100 ~ Incomplete
def get_Result(board):
    if (
    (board[0][0] == 1 and board[0][1] == 1 and board[0][2] == 1) or
    (board[1][0] == 1 and board[1][1] == 1 and board[1][2] == 1) or
    (board[2][0] == 1 and board[2][1] == 1 and board[2][2] == 1) or
    (board[0][0] == 1 and board[1][0] == 1 and board[2][0] == 1) or
    (board[0][1] == 1 and board[1][1] == 1 and board[2][1] == 1) or
    (board[0][2] == 1 and board[1][2] == 1 and board[2][2] == 1) or
    (board[0][0] == 1 and board[1][1] == 1 and board[2][2] == 1) or
    (board[0][2] == 1 and board[1][1] == 1 and board[2][0] == 1)  
    ): return -1
    elif (
    (board[0][0] == 2 and board[0][1] == 2 and board[0][2] == 2) or
    (board[1][0] == 2 and board[1][1] == 2 and board[1][2] == 2) or
    (board[2][0] == 2 and board[2][1] == 2 and board[2][2] == 2) or
    (board[0][0] == 2 and board[1][0] == 2 and board[2][0] == 2) or
    (board[0][1] == 2 and board[1][1] == 2 and board[2][1] == 2) or
    (board[0][2] == 2 and board[1][2] == 2 and board[2][2] == 2) or
    (board[0][0] == 2 and board[1][1] == 2 and board[2][2] == 2) or
    (board[0][2] == 2 and board[1][1] == 2 and board[2][0] == 2)
    ): return 1
    elif is_Full(board): return 0
    else: return 100 

# This method will return the best move for the computer
# X=1
# O=2
def get_Best_Move(brd, turn):
    available_Moves = [] # A list of available moves for the computer to make
    for i in range(3):
        for j in range(3):
            if (brd[i][j] == 0):
                available_Moves.append(Move(i,j,0))

    if len(available_Moves) == 0: #board is full
        return 0

    target_Moves = []
    for move in available_Moves:
        b = copy.deepcopy(brd) # Makes copy of current game state
        if (turn == 1):
            b[move.row][move.column] = 1
        else:
            b[move.row][move.column] = 2

        result = get_Result(b)
        score = 0
        if result == 0:
            score == 0
        elif (result == -1 and turn == 1) or (result == 1 and turn == 2):
            score = 1
        else:
            other = 1
            if turn == 1:
                other = 2

            nextMove = get_Best_Move(b, other)
            score = -1*(nextMove.score)

        move.score = score
        if move.score == 1:
            return move
        target_Moves.append(move)


    shuffle(target_Moves)
    sort_Moves(target_Moves)
    return target_Moves[0]


def compute_win(grid):
    color = session['color']
    op_color = abs(session['color']-3)
    rotate_grid = [[grid[0][x],grid[1][x],grid[2][x]] \
                       for x,l in enumerate(grid)]


    if [color,color,color] in grid or [color,color,color] in rotate_grid:
        return color
    if [op_color,op_color,op_color] in grid \
       or [op_color,op_color,op_color] in rotate_grid:
        return op_color


    return 0



@app.route("/setup", methods=['GET'])
def setup():
    return render_template('setup.html');

@app.route("/setup", methods=['POST'])
def update_setup():
    session['grid'] = [[0,0,0],[0,0,0],[0,0,0]]
    session['color'] = parsenum(request.form['color'])
    session['order'] = parsenum(request.form['order'])
    session['turn'] = 0
    session['win'] = 0
    return redirect(url_for('index'))

@app.route("/restart")
def restart():
    session['grid'] = [[0,0,0],[0,0,0],[0,0,0]]
    session['turn'] = 0
    session['win'] = 0
    return redirect(url_for('index'))

@app.route("/", methods=['GET'])
def index():

    if not 'grid' in session:
        return redirect(url_for('setup'))

    # configure first time
    if session['order'] == 2 and session['turn'] == 0:
        session['turn'] += 1 
        while True:

            bestMove = get_Best_Move(session['grid'],  
                                       abs(session['color']-3))

            if session['grid'][bestMove.row][bestMove.column] == 0:
                session['grid'][bestMove.row][bestMove.column] = abs(session['color']-3)
                break

    return render_template('index.html', 
                           grid=session['grid'],
                           turn = session['turn'],
                           win = session['win'])

@app.route("/", methods=['POST'])
def update():
    session['win'] = get_Result(session['grid']);
    print(session['win'])
    if session['win'] == 100:
        # perform player move
        session['turn'] += 1
        p_row = parsenum(request.form['play'].split(',')[0])
        p_column = parsenum(request.form['play'].split(',')[1])
        if session['grid'][p_row][p_column] == 0:
            session['grid'][p_row][p_column] = session['color']
            
    
            # perform computer move
            session['turn'] += 1
            while True and session['turn'] < 10:
                
                bestMove = get_Best_Move(session['grid'],  
                                       abs(session['color']-3))

                if session['grid'][bestMove.row][bestMove.column] == 0:
                    session['grid'][bestMove.row][bestMove.column] = abs(session['color']-3)
                    break

    session['win'] = get_Result(session['grid']);
    return render_template('index.html', 
                           grid=session['grid'],
                           turn = session['turn'],
                           win = session['win'])

if __name__ == "__main__":
    app.run(debug=True)
