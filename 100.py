import argparse

def parse(path):

    with open(path, 'r') as f:
        lines = f.readlines()

    grid = []
    wordlist = []
    is_grid = True

    for line in lines:

        line = line.strip()

        if not line:
            continue

        if line == 'Grid:':
            continue

        if line == 'Words:':
            is_grid = False
            continue

        if is_grid:
            grid.append(line.split())
        else:
            wordlist.append(line)

    return grid, wordlist

def horizontal_dfs(grid, word, i, j, c, can_bend):

    if c == len(word) - 1 and grid[i][j] == word[c]:
        grid[i][j] = '*'
        return True
    
    if grid[i][j] != word[c]:
        return False
    
    original = grid[i][j]
    grid[i][j] = '*'
    
    found = False

    if j+1 < len(grid[0]) and grid[i][j+1] != '*':
        found = horizontal_dfs(grid, word, i, j+1, c+1, can_bend)

    if not found and j-1 >= 0 and grid[i][j-1] != '*':
        found = horizontal_dfs(grid, word, i, j-1, c+1, can_bend)
    
    if not found and can_bend and i-1 >= 0 and grid[i-1][j] != '*':
        found = vertical_dfs(grid, word, i-1, j, c+1, False)
    
    if not found and can_bend and i+1 < len(grid) and grid[i+1][j] != '*':
        found = vertical_dfs(grid, word, i+1, j, c+1, False)

    if not found:
        grid[i][j] = original

    return found

def vertical_dfs(grid, word, i, j, c, can_bend):

    if c == len(word) - 1 and grid[i][j] == word[c]:
        grid[i][j] = '*'
        return True
    
    if grid[i][j] != word[c]:
        return False
    
    original = grid[i][j]
    grid[i][j] = '*'
    
    found = False

    if i+1 < len(grid) and grid[i+1][j] != '*':
        found = vertical_dfs(grid, word, i+1, j, c+1, can_bend)

    if not found and i-1 >= 0 and grid[i-1][j] != '*':
        found = vertical_dfs(grid, word, i-1, j, c+1, can_bend)
    
    if not found and can_bend and j-1 >= 0 and grid[i][j-1] != '*':
        found = horizontal_dfs(grid, word, i, j-1, c+1, False)
    
    if not found and can_bend and j+1 < len(grid[0]) and grid[i][j+1] != '*':
        found = horizontal_dfs(grid, word, i, j+1, c+1, False)

    if not found:
        grid[i][j] = original

    return found

def diagonal_dfs(grid, word, i, j, di, dj, c):

    if c == len(word) - 1 and grid[i][j] == word[c]:
        grid[i][j] = '*'
        return True
    
    if grid[i][j] != word[c]:
        return False
    
    original = grid[i][j]
    grid[i][j] = '*'
    
    found = False

    if i + di > 0 and i + di < len(grid) and j + dj >= 0 and j + dj < len(grid[0]) and grid[i+di][j+dj] != '*':
        found = diagonal_dfs(grid, word, i+di, j+dj, di, dj, c+1)

    if not found:
        grid[i][j] = original

    return found

def diagonal_search(grid, word, i, j):

    diagonal_dfs(grid, word, i, j, -1, -1, 0)
    diagonal_dfs(grid, word, i, j, -1, 1, 0)
    diagonal_dfs(grid, word, i, j, 1, -1, 0)
    diagonal_dfs(grid, word, i, j, 1, 1, 0)
    
    
def solve(grid, wordlist):

    for word in wordlist:
        for i in range(len(grid)):
            for j in range(len(grid[0])):
                if grid[i][j] == word[0]:
                    horizontal_dfs(grid, word, i, j, 0, True)
                    vertical_dfs(grid, word, i, j, 0, True)
                    diagonal_search(grid, word, i, j)

    flag = ''
    for row in grid:
        for c in row:
            if c != '*':
                flag += c

    return flag     

def main():

    parser = argparse.ArgumentParser(description='First challenge')
    parser.add_argument('path', help='Path to input file')
    args = parser.parse_args()
    path = args.path

    grid, wordlist = parse(path)

    print('\nGrid:')
    for row in grid:
        print(row)

    print('\nWords:')
    for word in wordlist:
        print(word)

    flag = solve(grid, wordlist)
    print('\npassword:')
    print(flag)
    
if __name__ == '__main__':
    main()