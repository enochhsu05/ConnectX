import numpy as np
import random

from kaggle_environments import evaluate, make

numRounds = 50


def basic_agent(obs, config):
    valid_moves = [col for col in range(config.columns) if obs.board[col] == 0]
    # Your code here: Amend the agent!
    player_piece = obs.mark
    opponent_piece = (player_piece % 2) + 1
    grid = np.asarray(obs.board).reshape(config.rows, config.columns)
    # Check if you can win in one move
    for i in valid_moves:
        if check_winning_move(grid, config, i, player_piece):
            return i
    # Check if you can stop your opponent from winning in onem
    for i in valid_moves:
        if check_winning_move(grid, config, i, opponent_piece):
            return i
    return valid_moves[0]


# Gets board at next step if agent drops piece in selected column
def drop_piece(grid, col, piece, config):
    next_grid = grid.copy()
    for row in range(config.rows - 1, -1, -1):
        if next_grid[row][col] == 0:
            break
    next_grid[row][col] = piece
    return next_grid


# Returns True if dropping piece in column results in game win
def check_winning_move(grid, config, col, piece):
    # Convert the board to a 2D grid
    next_grid = drop_piece(grid, col, piece, config)
    # horizontal
    for row in range(config.rows):
        for col in range(config.columns - (config.inarow - 1)):
            window = list(next_grid[row, col:col + config.inarow])
            if window.count(piece) == config.inarow:
                return True
    # vertical
    for row in range(config.rows - (config.inarow - 1)):
        for col in range(config.columns):
            window = list(next_grid[row:row + config.inarow, col])
            if window.count(piece) == config.inarow:
                return True
    # positive diagonal
    for row in range(config.rows - (config.inarow - 1)):
        for col in range(config.columns - (config.inarow - 1)):
            window = list(next_grid[range(row, row + config.inarow), range(col, col + config.inarow)])
            if window.count(piece) == config.inarow:
                return True
    # negative diagonal
    for row in range(config.inarow - 1, config.rows):
        for col in range(config.columns - (config.inarow - 1)):
            window = list(next_grid[range(row, row - config.inarow, -1), range(col, col + config.inarow)])
            if window.count(piece) == config.inarow:
                return True
    return False


def count_winning_moves(grid, config, piece):
    count = 0
    for i in range(config.columns):
        if grid[0][i] == 0 and check_winning_move(grid, config, i, piece):
            count += 1
    return count


def can_win_in_two(grid, config, piece):
    valid_moves = [0,1,2,3,4,5,6]
    # Check if a move can create two winning moves
    for i in valid_moves:
        if count_winning_moves(drop_piece(grid, i, piece, config), config, piece) >= 2:
            return True
    # Check if a move can create an unblockable winning move
    for i in valid_moves:
        if check_winning_move(drop_piece(grid, i, piece, config), config, i, piece) and \
                check_winning_move(drop_piece(drop_piece(grid, i, piece, config),
                                              i, piece, config), config, i, piece):
            return True
    return False


def get_win_percentages(agent1, agent2, n_rounds=numRounds):
    # Use default Connect Four setup
    config = {'rows': 6, 'columns': 7, 'inarow': 4}
    # Agent 1 goes first (roughly) half the time
    outcomes = evaluate("connectx", [agent1, agent2], config, [], n_rounds // 2)
    # Agent 2 goes first (roughly) half the time
    outcomes += [[b, a] for [a, b] in evaluate("connectx", [agent2, agent1], config, [], n_rounds - n_rounds // 2)]
    print("Agent 1 Win Percentage:", np.round(outcomes.count([1, -1]) / len(outcomes), 2))
    print("Agent 2 Win Percentage:", np.round(outcomes.count([-1, 1]) / len(outcomes), 2))
    print("Percentage of Draws:", np.round(outcomes.count([0, 0]) / len(outcomes), 2))
    print("Number of Invalid Plays by Agent 1:", outcomes.count([None, 0]))
    print("Number of Invalid Plays by Agent 2:", outcomes.count([0, None]))


# An agent that returns an integer in the range of [0,6] that represents the selected column
# obs.board - the game board (a Python list with one item for each grid location from top to bottom)
#             0 represents an empty space and 1 and 2 represents the two players' pieces
# obs.mark - the piece assigned to the agent (either 1 or 2)
# config.columns - number of columns in the game board (7 for Connect Four)
# config.rows - number of rows in the game board (6 for Connect Four)
# config.inarow - number of pieces a player needs to get in a row in order to win
def rules_agent(obs, config):
    valid_moves = [col for col in range(config.columns) if obs.board[col] == 0]
    good_moves = valid_moves.copy()
    player_piece = obs.mark
    opponent_piece = (player_piece % 2) + 1
    grid = np.asarray(obs.board).reshape(config.rows, config.columns)
    # Check if you can win in one move
    for i in valid_moves:
        if check_winning_move(grid, config, i, player_piece):
            return i
    # Check if you can stop your opponent from winning in one move
    for i in valid_moves:
        if check_winning_move(grid, config, i, opponent_piece):
            return i
    # Check if your move will let your opponent win immediately
    for i in valid_moves:
        if check_winning_move(drop_piece(grid, i, player_piece, config), config, i, opponent_piece):
            good_moves.remove(i)
    # Check if a move can create two winning moves
    for i in good_moves:
        if count_winning_moves(drop_piece(grid, i, player_piece, config), config, player_piece) >= 2:
            return i
    # Check if a move can create an unblockable winning move
    for i in good_moves:
        if check_winning_move(drop_piece(grid, i, player_piece, config), config, i, player_piece) and \
                check_winning_move(drop_piece(drop_piece(grid, i, player_piece, config),
                                              i, player_piece, config), config, i, player_piece):
            return i

    for i in good_moves:
        if count_winning_moves(drop_piece(grid, i, opponent_piece, config), config, opponent_piece) >= 2:
            return i

    for i in good_moves:
        if check_winning_move(drop_piece(grid, i, opponent_piece, config), config, i, opponent_piece) and \
                check_winning_move(drop_piece(drop_piece(grid, i, opponent_piece, config),
                                              i, opponent_piece, config), config, i, opponent_piece):
            return i

    if len(good_moves) == 0:
        return random.choice(valid_moves)

    return random.choice(good_moves)


def mid_agent(obs, config):
    valid_moves = [col for col in range(config.columns) if obs.board[col] == 0]
    good_moves = valid_moves.copy()
    player_piece = obs.mark
    opponent_piece = (player_piece % 2) + 1
    grid = np.asarray(obs.board).reshape(config.rows, config.columns)
    # Check if you can win in one move
    for i in valid_moves:
        if check_winning_move(grid, config, i, player_piece):
            return i
    # Check if you can stop your opponent from winning in one move
    for i in valid_moves:
        if check_winning_move(grid, config, i, opponent_piece):
            return i
    # Check if your move will let your opponent win immediately
    for i in valid_moves:
        if check_winning_move(drop_piece(grid, i, player_piece, config), config, i, opponent_piece):
            good_moves.remove(i)
    # Check if a move can create two winning moves
    for i in good_moves:
        if count_winning_moves(drop_piece(grid, i, player_piece, config), config, player_piece) >= 2:
            return i
    # Check if a move can create an unblockable winning move
    for i in good_moves:
        if check_winning_move(drop_piece(grid, i, player_piece, config), config, i, player_piece) and \
                check_winning_move(drop_piece(drop_piece(grid, i, player_piece, config),
                                              i, player_piece, config), config, i, player_piece):
            return i

    for i in good_moves:
        if count_winning_moves(drop_piece(grid, i, opponent_piece, config), config, opponent_piece) >= 2:
            return i

    for i in good_moves:
        if check_winning_move(drop_piece(grid, i, opponent_piece, config), config, i, opponent_piece) and \
                check_winning_move(drop_piece(drop_piece(grid, i, opponent_piece, config),
                                              i, opponent_piece, config), config, i, opponent_piece):
            return i

    if len(good_moves) == 0:
        return valid_moves[len(valid_moves) // 2]

    return good_moves[len(good_moves) // 2]


def mid_and_edge_agent(obs, config):
    valid_moves = [col for col in range(config.columns) if obs.board[col] == 0]
    good_moves = valid_moves.copy()
    player_piece = obs.mark
    opponent_piece = (player_piece % 2) + 1
    grid = np.asarray(obs.board).reshape(config.rows, config.columns)
    # Check if you can win in one move
    for i in valid_moves:
        if check_winning_move(grid, config, i, player_piece):
            return i
    # Check if you can stop your opponent from winning in one move
    for i in valid_moves:
        if check_winning_move(grid, config, i, opponent_piece):
            return i
    # Check if your move will let your opponent win immediately
    for i in valid_moves:
        if check_winning_move(drop_piece(grid, i, player_piece, config), config, i, opponent_piece):
            good_moves.remove(i)
    # Check if a move can create two winning moves
    for i in good_moves:
        if count_winning_moves(drop_piece(grid, i, player_piece, config), config, player_piece) >= 2:
            return i
    # Check if a move can create an unblockable winning move
    for i in good_moves:
        if check_winning_move(drop_piece(grid, i, player_piece, config), config, i, player_piece) and \
                check_winning_move(drop_piece(drop_piece(grid, i, player_piece, config),
                                              i, player_piece, config), config, i, player_piece):
            return i

    for i in good_moves:
        if count_winning_moves(drop_piece(grid, i, opponent_piece, config), config, opponent_piece) >= 2:
            return i

    for i in good_moves:
        if check_winning_move(drop_piece(grid, i, opponent_piece, config), config, i, opponent_piece) and \
                check_winning_move(drop_piece(drop_piece(grid, i, opponent_piece, config),
                                              i, opponent_piece, config), config, i, opponent_piece):
            return i

    if len(good_moves) == 0:
        return valid_moves[len(valid_moves) // 2]

    if len(good_moves) <= 5:
        return good_moves[0]
    return good_moves[len(good_moves) // 2]


def better_mid_agent(obs, config):
    valid_moves = [col for col in range(config.columns) if obs.board[col] == 0]
    good_moves = valid_moves.copy()
    player_piece = obs.mark
    opponent_piece = (player_piece % 2) + 1
    grid = np.asarray(obs.board).reshape(config.rows, config.columns)
    # Check if you can win in one move
    for i in valid_moves:
        if check_winning_move(grid, config, i, player_piece):
            return i
    # Check if you can stop your opponent from winning in one move
    for i in valid_moves:
        if check_winning_move(grid, config, i, opponent_piece):
            return i
    # Check if your move will let your opponent win immediately
    for i in valid_moves:
        if check_winning_move(drop_piece(grid, i, player_piece, config), config, i, opponent_piece):
            good_moves.remove(i)
    # Check if a move can create two winning moves
    for i in good_moves:
        if count_winning_moves(drop_piece(grid, i, player_piece, config), config, player_piece) >= 2:
            return i
    # Check if a move can create an unblockable winning move
    for i in good_moves:
        if check_winning_move(drop_piece(grid, i, player_piece, config), config, i, player_piece) and \
                check_winning_move(drop_piece(drop_piece(grid, i, player_piece, config),
                                              i, player_piece, config), config, i, player_piece):
            return i

    for i in good_moves:
        if count_winning_moves(drop_piece(grid, i, opponent_piece, config), config, opponent_piece) >= 2:
            return i

    for i in good_moves:
        if check_winning_move(drop_piece(grid, i, opponent_piece, config), config, i, opponent_piece) and \
                check_winning_move(drop_piece(drop_piece(grid, i, opponent_piece, config),
                                              i, opponent_piece, config), config, i, opponent_piece):
            return i

    better_moves = good_moves.copy()
    if len(good_moves) != 0:
        for i in good_moves:
            if can_win_in_two(drop_piece(grid, i, player_piece, config), config, opponent_piece):
                better_moves.remove(i)

    if len(good_moves) == 0:
        return valid_moves[len(valid_moves) // 2]
    elif len(better_moves) == 0:
        return good_moves[len(good_moves) // 2]

    return better_moves[len(better_moves) // 2]


#get_win_percentages(mid_agent, rules_agent)

# env = make("connectx", debug=True)
# env.run([rules_agent, "random"])
# env.render(mode="ipython")
