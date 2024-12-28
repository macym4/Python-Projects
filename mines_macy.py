"""
6.101 Lab 7:
Six Double-Oh Mines
"""

#!/usr/bin/env python3

import typing
import doctest

# NO ADDITIONAL IMPORTS ALLOWED!


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    keys = ("board", "dimensions", "state", "visible")
    # ^ Uses only default game keys. If you modify this you will need
    # to update the docstrings in other functions!
    for key in keys:
        val = game[key]
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f"{key}:")
            for inner in val:
                print(f"    {inner}")
        else:
            print(f"{key}:", val)


# 2-D IMPLEMENTATION


def new_game_2d(nrows, ncolumns, mines):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Parameters:
       nrows (int): Number of rows
       ncolumns (int): Number of columns
       mines (list): List of mines, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: ongoing
    visible:
        [False, False, False, False]
        [False, False, False, False]
    """
    return new_game_nd((nrows, ncolumns), mines)


def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['visible'] to reveal (row, col).  Then, if (row, col) has no
    adjacent mines (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one mine
    is visible on the board after digging (i.e. game['visible'][mine_location]
    == True), 'victory' when all safe squares (squares that do not contain a
    mine) and no mines are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: victory
    visible:
        [False, True, True, True]
        [False, False, True, True]

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    state: defeat
    visible:
        [True, True, False, False]
        [False, False, False, False]
    """

    return dig_nd(game, (row, col))


def render_2d_locations(game, all_visible=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (mines), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    mines).  game['visible'] indicates which squares should be visible.  If
    all_visible is True (the default is False), game['visible'] is ignored
    and all cells are shown.

    Parameters:
       game (dict): Game state
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                    by game['visible']

    Returns:
       A 2D array (list of lists)

    >>> game = {'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, True, False],
    ...                   [False, False, True, False]]}
    >>> render_2d_locations(game, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations(game, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    return render_nd(game, all_visible)


def render_2d_board(game, all_visible=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                           by game['visible']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'visible':  [[True, True, True, False],
    ...                            [False, False, True, False]]})
    '.31_\\n__1_'
    """
    locations = render_2d_locations(game, all_visible)
    final_string = ""
    for ix, row in enumerate(locations):
        temp_string = ""
        for iy, col in enumerate(row):
            # if you're at the first row index and the first col index
            # add a new line. Meaning it's a new row
            if ix and not iy:
                temp_string += "\n"
            temp_string += col
        final_string += temp_string
    return final_string


# N-D IMPLEMENTATION


def new_game_nd(dimensions, mines):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Args:
       dimensions (tuple): Dimensions of the board
       mines (list): mine locations as a list of tuples, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """

    board = create_board(dimensions, 0)
    mines_set = set(mines)
    for coordinates in mines:
        # create the mine
        set_this_value(board, coordinates, ".")

        # add one value to the values surrounding that mine
        for option in find_surrounding_coords(dimensions, coordinates):
            if option not in mines_set:
                set_this_value(board, option, None, 1)

    visible = create_board(dimensions, False)

    return {
        "board": board,
        "dimensions": dimensions,
        "state": "ongoing",
        "visible": visible,
    }


def create_board(dimensions, value):
    """
    Creates a board of a list of given dimensions filled with a certain
    value, given as the value input.
    """
    if len(dimensions) == 1:
        # create one line of value of dimensions[0] length
        return [value for _ in range(dimensions[0])]

    elif len(dimensions) != 1:
        # create another list where each value in the old list is replaced with
        # a new list of dimensions[1:] length
        return [create_board(dimensions[1:], value) for _ in range(dimensions[0])]

    return None


def index_this(orig_list, list_index_vals):
    """
    Indexes the given board for the list of indexes given.

    Returns that value, whether it be an integer or a list.
    """

    index_list = orig_list

    for val in list_index_vals:
        if val >= 0:
            # if the value is valid index the current index list
            index_list = index_list[val]

    return index_list


def set_this_value(orig_list, list_index_vals, new_val, add_val=0):
    """
    Sets a value in a board of index depth n to whatever new_val is.

    The values to index with are given in list_index_vals and the board
    is given in orig_list.
    """
    # index_this(orig_list, list_index_vals) = new_val

    index_list = orig_list
    for ix, val in enumerate(list_index_vals):
        # if it's the last value that we're indexing and it's a valid index
        if ix == len(list_index_vals) - 1 and val >= 0:
            # index the value. if it wants you to replace it replace it
            # otherwise add to the current value
            if new_val:
                index_list[val] = new_val
            if add_val:
                index_list[val] += add_val
        index_list = index_list[val]


def find_surrounding_coords(dimensions, coord):
    """
    Find the surrounding coords of a coordinate in a board of
    dimensions dimension. Dimensions given as a tuple.
    """
    final = []
    # find 1d surrouding values
    working_list = [(coord[0] + val,) for val in range(-1, 2)]

    for item in working_list:
        if item[0] >= dimensions[0] or item[0] < 0:
            working_list.remove(item)

    if len(coord) == 1:
        return working_list

    else:
        for item in working_list:
            # combine 1d surrounding values with the next dimension's value and so on
            final.extend(
                [
                    item + item2
                    for item2 in find_surrounding_coords(dimensions[1:], coord[1:])
                ]
            )

    return final


def dig_nd(game, coordinates):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the visible to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    mine.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one mine is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a mine) and no mines are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: defeat
    visible:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """

    # reveal all the avaliable squares
    revealed = reveal_recursion(game, coordinates)

    # check what the next state of victory/defeat/ongoing should be
    if game["state"] != "defeat":
        status = check_board_values(
            game, game["board"], game["visible"], game["dimensions"]
        )
        if status == "victory":
            game["state"] = "victory"

    return revealed


def check_surrounding_mines(game, coord):
    """
    Check the surrounding coordinates for mines. Returns an integer of how
    many mines are around it.
    """

    num_mines = 0
    for option in find_surrounding_coords(game["dimensions"], coord):
        if option == coord:
            continue
        if index_this(game["board"], option) == ".":
            num_mines += 1
    return num_mines


def reveal_recursion(game, coord):
    """
    Reveals the mines around a mine that have a value of 0 (no surrounding mines)
    """
    if (
        game["state"] == "defeat"
        or game["state"] == "victory"
        or index_this(game["visible"], coord)
    ):
        return 0

    current_val = index_this(game["board"], coord)
    if current_val == ".":
        set_this_value(game["visible"], coord, True)
        game["state"] = "defeat"
        return 1

    set_this_value(game["visible"], coord, True)
    revealed = 1

    if current_val == 0:
        # check all the surrounding coords
        for option in find_surrounding_coords(game["dimensions"], coord):
            revealed += reveal_recursion(game, option)

    return revealed


def check_board_values(game, board, visible, dimensions):
    """
    Returns a list of all of the values in a board of dimensions dimension.
    """
    game["state"] = "victory"

    if len(dimensions) == 1:
        for ix, val in enumerate(board):
            if val != "." and not visible[ix]:
                game["state"] = "ongoing"
                return "ongoing"

    elif len(dimensions) > 1:
        for ix, row in enumerate(board):
            # reduces the row being checked to a smaller dimension
            if check_board_values(game, row, visible[ix], dimensions[1:]) == "ongoing":
                # if it has any unrevealed non-bombs, set state to ongoing and stop
                # running
                game["state"] = "ongoing"
                return "ongoing"

    return "victory"


def all_board_values(dimensions):
    """
    Docstring
    """
    final = []
    # check all of the coordinates for that dimension
    working_list = [(n,) for n in range(dimensions[0])]
    if len(dimensions) == 1:
        return working_list

    else:
        for item in working_list:
            for item2 in all_board_values(dimensions[1:]):
                # add it to each value in a total list of
                # all the coordinates for the board
                final.append(item + item2)
    return final


def render_nd(game, all_visible=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (mines), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    mines).  The game['visible'] array indicates which squares should be
    visible.  If all_visible is True (the default is False), the game['visible']
    array is ignored and all cells are shown.

    Args:
       all_visible (bool): Whether to reveal all tiles or just the ones allowed
                           by game['visible']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [True, True],
    ...                [True, True]],
    ...               [[False, False], [False, False], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    final_board = create_board(game["dimensions"], "_")
    # for each coordinate in the whole board
    for coordinate in all_board_values(game["dimensions"]):
        current_val = index_this(game["board"], coordinate)
        if current_val == 0:
            current_val = " "
        if all_visible:
            # reveal all
            set_this_value(final_board, coordinate, str(current_val))
        elif not all_visible:
            # only reveal the ones that are visible
            if index_this(game["visible"], coordinate) is True:
                set_this_value(final_board, coordinate, str(current_val))
    return final_board


if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    #
    # doctest.run_docstring_examples(
    #    render_2d_locations,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )

    # ex_game = {'dimensions': (2, 4),
    # 'state': 'ongoing',
    # 'board': [['.', 3, 1, 0],
    #         ['.', '.', 1, 0]],
    # 'visible':  [[False, True, True, False],
    #         [False, False, True, False]]}
    # print(render_2d_board(ex_game))
    # print(render_2d_locations(ex_game))
    # print(new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)]))
    # print(g)
    # print(dig_nd(g, (0, 3, 0)))

    # print(find_surrounding_coords((10,20,3), (5,13,0)))
    pass
