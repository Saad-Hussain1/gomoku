'''Game of Gomoku (A.K.A. Five in a Row) for player vs. AI
see: https://en.wikipedia.org/wiki/Gomoku
'''

def make_empty_board(sz):
    board = []
    for i in range(sz):
        board.append([" "]*sz)
    return board


def print_board(board):
    s = "*"
    for i in range(len(board[0])-1):
        s += str(i%10) + "|"
    s += str((len(board[0])-1)%10)
    s += "*\n"
    for i in range(len(board)):
        s += str(i%10)
        for j in range(len(board[0])-1):
            s += str(board[i][j]) + "|"
        s += str(board[i][len(board[0])-1])
        s += "*\n"
    s += (len(board[0])*2 + 1)*"*"
    print(s)


def put_seq_on_board(board, y, x, d_y, d_x, length, col):
    for i in range(length):
        board[y][x] = col
        y += d_y
        x += d_x


def score(board):
    MAX_SCORE = 100000
    
    open_b = {}
    semi_open_b = {}
    open_w = {}
    semi_open_w = {}
    
    for i in range(2, 6):
        open_b[i], semi_open_b[i] = detect_rows(board, "b", i)
        open_w[i], semi_open_w[i] = detect_rows(board, "w", i)
    
    if open_b[5] >= 1 or semi_open_b[5] >= 1:
        return MAX_SCORE
    
    elif open_w[5] >= 1 or semi_open_w[5] >= 1:
        return -MAX_SCORE
        
    return (-10000 * (open_w[4] + semi_open_w[4])+ 
            500  * open_b[4]                     + 
            50   * semi_open_b[4]                + 
            -100  * open_w[3]                    + 
            -30   * semi_open_w[3]               + 
            50   * open_b[3]                     + 
            10   * semi_open_b[3]                +  
            open_b[2] + semi_open_b[2] - open_w[2] - semi_open_w[2])


def analysis(board):
    for c, full_name in [["b", "Black"], ["w", "White"]]:
        print("%s stones" % (full_name))
        for i in range(2, 6):
            open, semi_open = detect_rows(board, c, i);
            print("Open rows of length %d: %d" % (i, open))
            print("Semi-open rows of length %d: %d" % (i, semi_open))


def play_gomoku(board_size):
    board = make_empty_board(board_size)
    board_height = len(board)
    board_width = len(board[0])
    
    while True:
        print_board(board)
        if is_empty(board):
            move_y = board_height // 2
            move_x = board_width // 2
        else:
            move_y, move_x = search_max(board)
        
        print("Computer move: (%d, %d)" % (move_y, move_x))
        board[move_y][move_x] = "b"
        print_board(board)
        analysis(board)
        
        game_res = is_win(board)
        if game_res in ["White won", "Black won", "Draw"]:
            return game_res
        
        print("Your move:")
        move_y = int(input("y coord: "))
        move_x = int(input("x coord: "))
        board[move_y][move_x] = "w"
        print_board(board)
        analysis(board)
        
        game_res = is_win(board)
        if game_res in ["White won", "Black won", "Draw"]:
            return game_res


def is_empty(board):
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] != ' ':
                return False
    return True


def is_bounded(board, y_end, x_end, length, d_y, d_x):
    bounded_count = 0
    y_start = y_end - (d_y * (length - 1))
    x_start = x_end - (d_x * (length - 1))
    bounded_at_start_y = False
    bounded_at_start_x = False
    bounded_at_end_y = False
    bounded_at_end_x = False
    #Check edges of board:
    if d_y == 1:
        if y_start == 0:
            bounded_count += 1
            bounded_at_start_y = True
        if y_end == 7:
            bounded_count += 1
            bounded_at_end_y = True
    if d_x == 1:
        if x_start == 0:
            bounded_at_start_x = True
            if not bounded_at_start_y:
                bounded_count += 1
        if x_end == 7:
            bounded_at_end_x = True
            if not bounded_at_end_y:
                bounded_count += 1
    elif d_x == -1:
        if x_start == 7:
            bounded_at_start_x = True
            if not bounded_at_start_y:
                bounded_count += 1
        if x_end == 0:
            bounded_at_end_x = True
            if not bounded_at_end_y:
                bounded_count += 1
    #Check both ends of sequence:
    if not bounded_at_start_y and not bounded_at_start_x:
        if board[y_start - d_y][x_start - d_x] != ' ':
            bounded_count += 1
    if not bounded_at_end_y and not bounded_at_end_x:
        if board[y_end + d_y][x_end + d_x] != ' ':
            bounded_count += 1  
    #Result of function:
    if bounded_count == 0:
        return "OPEN"
    elif bounded_count == 1:
        return "SEMIOPEN"
    else:
        return "CLOSED"


def detect_row(board, col, y_start, x_start, length, d_y, d_x):
    return (detect_row2(board, col, y_start, x_start, length, d_y, d_x)[0], detect_row2(board, col, y_start, x_start, length, d_y, d_x)[1])


def detect_row2(board, col, y_start, x_start, length, d_y, d_x):
    cur_y = y_start
    cur_x = x_start
    open_sequences = 0
    semiopen_sequences = 0
    closed_sequences = 0
    
    #If row is horizontal
    if d_y == 0:
        while cur_x < 8:
            if board[cur_y][cur_x] == col:
                col_in_row = 0
                x_in_seq = cur_x
                while x_in_seq < 8:
                    if board[cur_y][x_in_seq] == col:
                        col_in_row += 1
                    else:
                        break
                    x_in_seq += d_x
                if col_in_row == length:
                    if is_bounded(board, cur_y, x_in_seq - d_x, length, 0, d_x) == 'OPEN':
                        open_sequences += 1
                    elif is_bounded(board, cur_y, x_in_seq - d_x, length, 0, d_x) == 'SEMIOPEN':
                        semiopen_sequences += 1
                    elif is_bounded(board, cur_y, x_in_seq - d_x, length, 0, d_x) == 'CLOSED':
                        closed_sequences += 1
                cur_x = x_in_seq - d_x
            cur_x += d_x
    #If row is vertical
    elif d_x == 0:
        while cur_y < 8:
            if board[cur_y][cur_x] == col:
                col_in_row = 0
                y_in_seq = cur_y
                while y_in_seq < 8:
                    if board[y_in_seq][cur_x] == col:
                        col_in_row += 1
                    else:
                        break
                    y_in_seq += d_y
                if col_in_row == length:
                    if is_bounded(board, y_in_seq - d_y, cur_x, length, d_y, 0) == 'OPEN':
                        open_sequences += 1
                    elif is_bounded(board, y_in_seq - d_y, cur_x, length, d_y, 0) == 'SEMIOPEN':
                        semiopen_sequences += 1
                    elif is_bounded(board, y_in_seq - d_y, cur_x, length, d_y, 0) == 'CLOSED':
                        closed_sequences += 1
                cur_y = y_in_seq - d_y
            cur_y += d_y
    #If row is diagonal from top left to bottom right
    elif d_x == 1:
        while cur_y < 8 and cur_x < 8:
            if board[cur_y][cur_x] == col:
                col_in_row = 0
                y_in_seq = cur_y
                x_in_seq = cur_x
                while y_in_seq < 8 and x_in_seq < 8:
                    if board[y_in_seq][x_in_seq] == col:
                        col_in_row += 1
                    else:
                        break
                        
                    y_in_seq += d_y
                    x_in_seq += d_x
                if col_in_row == length:
                    if is_bounded(board, y_in_seq - d_y, x_in_seq - d_x, length, d_y, d_x) == 'OPEN':
                        open_sequences += 1
                    elif is_bounded(board, y_in_seq - d_y, x_in_seq - d_x, length, d_y, d_x) == 'SEMIOPEN':
                        semiopen_sequences += 1
                    elif is_bounded(board, y_in_seq - d_y, x_in_seq - d_x, length, d_y, d_x) == 'CLOSED':
                        closed_sequences += 1
                cur_y = y_in_seq - d_y
                cur_x = x_in_seq - d_x
            cur_y += d_y
            cur_x += d_x
    #If row is diagonal from top right to bottom left
    else:
        while cur_y < 8 and cur_x > -1:
            if board[cur_y][cur_x] == col:
                col_in_row = 0
                y_in_seq = cur_y
                x_in_seq = cur_x
                while y_in_seq < 8 and x_in_seq > -1:
                    if board[y_in_seq][x_in_seq] == col:
                        col_in_row += 1
                    else:
                        break
                    y_in_seq += d_y
                    x_in_seq += d_x
                if col_in_row == length:
                    if is_bounded(board, y_in_seq - d_y, x_in_seq - d_x, length, d_y, d_x) == 'OPEN':
                        open_sequences += 1
                    elif is_bounded(board, y_in_seq - d_y, x_in_seq - d_x, length, d_y, d_x) == 'SEMIOPEN':
                        semiopen_sequences += 1
                    elif is_bounded(board, y_in_seq - d_y, x_in_seq - d_x, length, d_y, d_x) == 'CLOSED':
                        closed_sequences += 1
                cur_y = y_in_seq - d_y
                cur_x = x_in_seq - d_x
            cur_y += d_y
            cur_x += d_x
    
    return (open_sequences, semiopen_sequences, closed_sequences)


def detect_rows(board, col, length):
    return (detect_rows2(board, col, length)[0], detect_rows2(board, col, length)[1])


def detect_rows2(board, col, length):
    open_seq = 0
    semiopen_seq = 0
    closed_seq = 0
    for i in range(8):
        #Verticals:
        res1 = detect_row2(board, col, 0, i, length, 1, 0)
        open_seq += res1[0]
        semiopen_seq += res1[1]
        closed_seq += res1[2]
        #Horizontals:
        res2 = detect_row2(board, col, i, 0, length, 0, 1)
        open_seq += res2[0]
        semiopen_seq += res2[1]
        closed_seq += res2[2]
        #Diagonal down-right, iterate along x-axis
        res3 = detect_row2(board, col, 0, i, length, 1, 1)
        open_seq += res3[0]
        semiopen_seq += res3[1]
        closed_seq += res3[2]
        #Diagonal down-left, iterate along x-axis
        res5 = detect_row2(board, col, 0, i, length, 1, -1)
        open_seq += res5[0]
        semiopen_seq += res5[1]
        closed_seq += res5[2]
    for i in range(1, 8):
        #Diagonal down-right, iterate along y-axis
        res4 = detect_row2(board, col, i, 0, length, 1, 1)
        open_seq += res4[0]
        semiopen_seq += res4[1]
        closed_seq += res4[2]
        #Diagonal down-left, iterate along y-axis
        res6 = detect_row2(board, col, i, 7, length, 1, -1)
        open_seq += res6[0]
        semiopen_seq += res6[1]
        closed_seq += res6[2]
    return (open_seq, semiopen_seq, closed_seq)


def search_max(board):
    free_squares = []
    cur_max = -100000
    index_cur_max = 0
    
    for y in range(8):
        for x in range(8):
            if board[y][x] == ' ':
                free_squares.append([y, x])
    for index in free_squares:
        board[index[0]][index[1]] = 'b'
        if score(board) >= cur_max:
            cur_max = score(board)
            index_cur_max = (index[0], index[1])
        board[index[0]][index[1]] = ' '
    
    return index_cur_max


def is_win(board):
    for i in range(3):
        if detect_rows2(board, 'b', 5)[i] > 0:
            return 'Black won'
        elif detect_rows2(board, 'w', 5)[i] > 0:
            return 'White won'
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == ' ':
                return 'Continue playing'
    return 'Draw'


board = make_empty_board(8)


#===============================================================
if __name__ == '__main__':
    
    def test(current_output, expected_output):
        if current_output == expected_output:
            print('Passed!')
        else:
            print('Failed <-------------------------')
    
    print('==================================')
    print('TESTS FOR is_empty FUNCTION')
    board = make_empty_board(8)
    print_board(board)
    test(is_empty(board), True)
    put_seq_on_board(board, 0, 0, 1, 1, 1, 'b')
    test(is_empty(board), False)
    
    print('==================================')
    print('TESTS FOR is_bounded FUNCTION')
    test(is_bounded(board, 7, 3, 4, 1, 1), 'CLOSED')
    test(is_bounded(board, 7, 0, 5, 1, 0), 'SEMIOPEN')
    test(is_bounded(board, 7, 7, 8, 1, 1), 'CLOSED')
    test(is_bounded(board, 6, 4, 3, 1, 1), 'OPEN')
    test(is_bounded(board, 2, 5, 3, 1, -1), 'SEMIOPEN')
    test(is_bounded(board, 0, 0, 1, 1, 1), 'SEMIOPEN')
    test(is_bounded(board, 7, 0, 1, 1, 0), 'SEMIOPEN')
    test(is_bounded(board, 7, 0, 3, 1, -1), 'SEMIOPEN')
    test(is_bounded(board, 3, 4, 4, 1, 1), 'SEMIOPEN')
    test(is_bounded(board, 4, 3, 5, 1, -1), 'SEMIOPEN')
    test(is_bounded(board, 0, 7, 5, 0, 1), 'SEMIOPEN')
    
    print('==================================')
    print('TESTS FOR detect_row FUNCTION')
    #Test 1
    board = make_empty_board(8)
    put_seq_on_board(board, 1, 5, 1, 0, 3, "w")
    print_board(board)
    test(detect_row(board, "w", 0, 5, 3, 1, 0), (1,0))
    print()
    #Test 2
    board = make_empty_board(8)
    put_seq_on_board(board, 0, 0, 1, 1, 8, 'w')
    print_board(board)
    test(detect_row(board, 'w', 0, 0, 3, 1, 1), (0,0))
    print()
    #Test 3
    board = make_empty_board(8)
    put_seq_on_board(board, 5, 2, 1, -1, 2, 'b')
    put_seq_on_board(board, 1, 6, 1, -1, 3, 'b')
    print_board(board)
    test(detect_row(board, 'b', 0, 7, 2, 1, -1), (1, 0))
    print()
    #Test 4
    board = make_empty_board(8)
    put_seq_on_board(board, 0, 5, 1, 1, 2, 'b')
    print_board(board)
    test(detect_row(board, 'b', 0, 5, 2, 1, 1), (0,1))
    print()
    #Test 5
    board = make_empty_board(8)
    put_seq_on_board(board, 1, 6, 1, 1, 2, 'b')
    print_board(board)
    test(detect_row(board, 'b', 0, 5, 2, 1, 1), (0,1))
    print()
    #Test 6
    board = make_empty_board(8)
    put_seq_on_board(board, 0, 0, 1, 1, 2, 'b')
    put_seq_on_board(board, 2, 2, 1, 1, 2, 'w')
    put_seq_on_board(board, 5, 5, 1, 1, 2, 'b')
    print_board(board)
    test(detect_row(board, 'b', 0, 0, 2, 1, 1), (1, 0))
    
    print('==================================')
    print('TESTS FOR detect_rows FUNCTION')
    #Test 1
    board = make_empty_board(8)
    put_seq_on_board(board, 0, 2, 1, 0, 3, 'b')
    put_seq_on_board(board, 4, 0, 1, 1, 3, 'b')
    put_seq_on_board(board, 0, 7, 1, -1, 3, 'b')
    put_seq_on_board(board, 0, 5, 1, -1, 3, 'w')
    put_seq_on_board(board, 3, 6, 1, 0, 3, 'b')
    put_seq_on_board(board, 4, 1, 0, 1, 3, 'b')
    put_seq_on_board(board, 7, 0, 0, 1, 3, 'b')
    print_board(board)
    test(detect_rows(board, 'b', 3), (1, 4))
    print()
    #Test 2
    board = make_empty_board(8)
    put_seq_on_board(board, 1, 6, 1, -1, 3, 'b')
    put_seq_on_board(board, 0, 5, 1, -1, 3, 'b')
    put_seq_on_board(board, 3, 7, 1, -1, 3, 'b')
    print_board(board)
    test(detect_rows(board, 'b', 3), (1, 2))
    print()
    #Test 3
    board = make_empty_board(8)
    put_seq_on_board(board, 1, 0, 1, 1, 4,'w')
    put_seq_on_board(board, 1, 1, 1, 1, 4, 'w')
    put_seq_on_board(board, 1, 2, 1, 1, 4, 'w')
    put_seq_on_board(board, 1, 3, 1, 1, 4, 'w')
    print_board(board)
    test(detect_rows(board, 'w', 4), (7, 2))
    print()
    #Test 4
    board = make_empty_board(8)
    put_seq_on_board(board, 1, 0, 1, 1, 4,'w')
    put_seq_on_board(board, 1, 1, 1, 1, 4, 'w')
    put_seq_on_board(board, 1, 2, 1, 1, 4, 'w')
    put_seq_on_board(board, 1, 3, 1, 1, 4, 'w')
    put_seq_on_board(board, 2, 0, 1, 1, 4, 'b')
    print_board(board)
    test(detect_rows(board, 'w', 4), (3, 6))
    print()
    #Test 5
    board = make_empty_board(8)
    put_seq_on_board(board, 1, 0, 0, 1, 4,'w')
    put_seq_on_board(board, 2, 1, 0, 1, 4, 'w')
    put_seq_on_board(board, 3, 2, 0, 1, 4, 'w')
    put_seq_on_board(board, 4, 3, 0, 1, 3, 'w')
    put_seq_on_board(board, 2, 0, 1, 1, 4, 'b')
    put_seq_on_board(board, 4, 6, 1, -1, 4, 'w')
    put_seq_on_board(board, 0, 5, 0, 1, 3, 'w')
    put_seq_on_board(board, 0, 1, 0, 1, 4, 'b')
    print_board(board)
    test(detect_rows(board, 'w', 4), (0, 8))
    print()
    
    print('==================================')
    print('TESTS FOR is_win FUNCTION')
    #Test 1
    board = make_empty_board(8)
    put_seq_on_board(board, 3, 7, 1, -1, 5, 'w')
    print_board(board)
    test(is_win(board), 'White won')
    print()
    #Test 2
    board = make_empty_board(8)
    put_seq_on_board(board, 0, 7, 1, -1, 4, 'b')
    put_seq_on_board(board, 3, 2, 1, 1, 4, 'b')
    print_board(board)
    test(is_win(board), 'Black won')
    print()
    #Test 3
    board = make_empty_board(8)
    put_seq_on_board(board, 0, 7, 1, -1, 4, 'b')
    put_seq_on_board(board, 3, 2, 1, 1, 3, 'b')
    print_board(board)
    test(is_win(board), 'Black won')
    print()
    #Test 4
    board = make_empty_board(8)
    put_seq_on_board(board, 2, 7, 1, -1, 5, 'w')
    print_board(board)
    test(is_win(board), 'White won')
    print()
    #Test 5
    board = make_empty_board(8)
    put_seq_on_board(board, 0, 4, 0, 1, 4, 'w')
    put_seq_on_board(board, 0, 3, 1, -1, 3, 'w')
    print_board(board)
    test(is_win(board), 'White won')
    print()
    #Test 6
    board = make_empty_board(8)
    put_seq_on_board(board, 0, 0, 0, 1, 4, 'w')
    put_seq_on_board(board, 0, 5, 0, 1, 3, 'b')
    put_seq_on_board(board, 0, 4, 1, -1, 3, 'w')
    print_board(board)
    test(is_win(board), 'White won')
    print()
    #Test 7
    board = make_empty_board(8)
    put_seq_on_board(board, 0, 0, 0, 1, 4, 'b')
    put_seq_on_board(board, 0, 5, 0, 1, 3, 'w')
    put_seq_on_board(board, 0, 4, 1, -1, 3, 'b')
    print_board(board)
    test(is_win(board), 'Black won')
    print()
    #Test 8
    board = make_empty_board(8)
    put_seq_on_board(board, 0, 2, 1, 0, 3, 'b')
    put_seq_on_board(board, 4, 0, 1, 1, 3, 'b')
    put_seq_on_board(board, 0, 7, 1, -1, 3, 'b')
    put_seq_on_board(board, 0, 5, 1, -1, 3, 'w')
    put_seq_on_board(board, 3, 6, 1, 0, 3, 'b')
    put_seq_on_board(board, 4, 1, 0, 1, 3, 'b')
    put_seq_on_board(board, 7, 0, 0, 1, 3, 'b')
    put_seq_on_board(board, 3, 0, 0, 1, 4, 'w')
    put_seq_on_board(board, 0, 0, 1, 0, 3, 'b')
    put_seq_on_board(board, 0, 1, 1, 0, 3, 'w')
    put_seq_on_board(board, 2, 4, 1, 0, 3, 'b')
    print_board(board)
    test(is_win(board), 'Black won')
    print()
    #Test 9
    board = make_empty_board(8)
    put_seq_on_board(board, 0, 0, 0, 1, 4, 'b')
    put_seq_on_board(board, 1, 0, 0, 1, 4, 'w')
    put_seq_on_board(board, 2, 0, 0, 1, 4, 'b')
    put_seq_on_board(board, 3, 0, 0, 1, 4, 'w')
    put_seq_on_board(board, 4, 0, 0, 1, 4, 'b')
    put_seq_on_board(board, 5, 0, 0, 1, 4, 'w')
    put_seq_on_board(board, 6, 0, 0, 1, 4, 'b')
    put_seq_on_board(board, 7, 0, 0, 1, 4, 'w')
    put_seq_on_board(board, 0, 4, 0, 1, 4, 'w')
    put_seq_on_board(board, 1, 4, 0, 1, 4, 'b')
    put_seq_on_board(board, 2, 4, 0, 1, 4, 'w')
    put_seq_on_board(board, 3, 4, 0, 1, 4, 'b')
    put_seq_on_board(board, 4, 4, 0, 1, 4, 'w')
    put_seq_on_board(board, 5, 4, 0, 1, 4, 'b')
    put_seq_on_board(board, 6, 4, 0, 1, 4, 'w')
    put_seq_on_board(board, 7, 4, 0, 1, 4, 'b')
    print_board(board)
    test(is_win(board), 'Draw')
    print()
    
    board = make_empty_board(8)
    print_board(board)
    
    '''
    put_seq_on_board(board, y, x, d_y, d_x, length, col)
    is_bounded(board, y_end, x_end, length, d_y, d_x)
    detect_row(board, col, y_start, x_start, length, d_y, d_x)
    detect_rows(board, col, length)
    search_max(board)
    '''
    
    play_gomoku(8)
    