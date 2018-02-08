from utils import *
import itertools

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist = row_units + column_units + square_units

# TODO: Update the unit list to add the new diagonal units
diagonal1 = []
diagonal2 = []

rowIndex = colIndex = 0

for i in range(len(rows)):
    diagonal1.append(rows[rowIndex] + cols[colIndex])
    diagonal2.append(rows[rowIndex] + cols[len(cols) - colIndex - 1])

    rowIndex += 1
    colIndex += 1

unitlist.append(diagonal1)
unitlist.append(diagonal2)

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers

    Notes
    -----
    Your solution can either process all pairs of naked twins from the input once,
    or it can continue processing pairs of naked twins until there are no such
    pairs remaining -- the project assistant test suite will accept either
    convention. However, it will not accept code that does not process all pairs
    of naked twins from the original input. (For example, if you start processing
    pairs of twins and eliminate another pair of twins before the second pair
    is processed then your code will fail the PA test suite.)

    The first convention is preferred for consistency with the other strategies,
    and because it is simpler (since the reduce_puzzle function already calls this
    strategy repeatedly).
    """
    # TODO: Implement this function!
    for unit in unitlist:
        twoChoiceToBox = {}
        nakedTwinChoiceBoxes = []

        for box in unit:
            if len(values[box]) != 2:
                continue

            if values[box] not in twoChoiceToBox:
                twoChoiceToBox[values[box]] = box
            else:
                nakedTwinChoiceBoxes.append(twoChoiceToBox[values[box]])
                nakedTwinChoiceBoxes.append(box)

        for box in unit:
            if len(values[box]) == 1 or box in nakedTwinChoiceBoxes:
                continue

            for nakedTwinChoiceBox in nakedTwinChoiceBoxes:
                for choice in values[nakedTwinChoiceBox]:
                    values[box] = values[box].replace(choice, '')

    return values

def containsAny(str, set):
    """Check whether 'str' contains ANY of the chars in 'set'"""
    return 1 in [c in str for c in set]

def eliminate(values):
    """Apply the eliminate strategy to a Sudoku puzzle

    The eliminate strategy says that if a box has a value assigned, then none
    of the peers of that box can have the same value.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the assigned values eliminated from peers
    """
    # TODO: Copy your code from the classroom to complete this function
    for box in [box for box in boxes if len(values[box]) == 1]:
        for peer in peers[box]:
            values[peer] = values[peer].replace(values[box], '')

    return values

def only_choice(values):
    """Apply the only choice strategy to a Sudoku puzzle

    The only choice strategy says that if only one box in a unit allows a certain
    digit, then that box must be assigned that digit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with all single-valued boxes assigned

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    """
    # TODO: Copy your code from the classroom to complete this function
    for unit in unitlist:
        for digit in cols:
            boxesWithDigit = [box for box in unit if digit in values[box]]

            if len(boxesWithDigit) == 1:
                values[boxesWithDigit[0]] = digit

    return values

def reduce_puzzle(values):
    """Reduce a Sudoku puzzle by repeatedly applying all constraint strategies

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary after continued application of the constraint strategies
        no longer produces any changes, or False if the puzzle is unsolvable 
    """
    # TODO: Copy your code from the classroom and modify it to complete this function
    stalled = False

    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])

        # Your code here: Use the Eliminate Strategy
        values = eliminate(values)

        # Your code here: Use the Only Choice Strategy
        values = only_choice(values)

        values = naked_twins(values)

        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])

        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after

        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False

    return values

def search(values):
    """Apply depth first search to solve Sudoku puzzles in order to solve puzzles
    that cannot be solved by repeated reduction alone.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary with all boxes assigned or False

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    and extending it to call the naked twins strategy.
    """
    # TODO: Copy your code from the classroom to complete this function
    values = reduce_puzzle(values)

    #values = naked_twins(values)

    # Failed to solve
    if not values:
        return False

    # Solved
    if all(len(values[box]) == 1 for box in boxes):
        return values

    # Choose one of the unfilled squares with the fewest possibilities
    boxToTry = None

    for box in boxes:
        if len(values[box]) == 1:
            continue

        if boxToTry is None or len(values[box]) < len(boxToTry):
            boxToTry = box

            if len(values[box]) == 2:
                break

    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    for tryChoice in values[boxToTry]:
        trySudoku = values.copy()

        trySudoku[boxToTry] = tryChoice

        tryResult = search(trySudoku)

        if tryResult:
            return tryResult

def solve(grid):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.
        
        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    values = grid2values(grid)
    values = search(values)
    return values


if __name__ == "__main__":
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(grid2values(diag_sudoku_grid))
    result = solve(diag_sudoku_grid)
    display(result)

    try:
        import PySudoku
        PySudoku.play(grid2values(diag_sudoku_grid), result, history)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
