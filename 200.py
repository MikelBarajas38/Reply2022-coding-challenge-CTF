import argparse

def parse(path):

    with open(path, 'r') as f:
        lines = f.readlines()

    grid = []

    for line in lines:
        grid.append(list(line.strip()))

    return grid

def valid(i, j, grid):
    return i >= 0 and i < len(grid) and j >= 0 and j < len(grid[0])
    
def count_neighbors(i, j, grid, c):

    di = [-1, -1, -1, 0, 0, 1, 1, 1]
    dj = [-1, 0, 1, -1, 1, -1, 0, 1]

    count = 0
    for k in range(8):
        if valid(i + di[k], j + dj[k], grid) and grid[i + di[k]][j + dj[k]] == c:
            count += 1

    return count

def generate_portal_grid(grid):

    n = len(grid)
    m = len(grid[0])

    portal_grid = [[(-1, -1) for _ in range(m)] for _ in range(n)]

    portal_matcher = {}

    for i in range(n):
        for j in range(m):

            if not grid[i][j].islower():
                continue

            p = grid[i][j]

            if p not in portal_matcher:
                portal_matcher[p] = (i, j)
            else:
                pi, pj = portal_matcher[p]
                portal_grid[i][j] = (pi, pj)
                portal_grid[pi][pj] = (i, j)

    return portal_grid

def simulate(initial_grid):

    n = len(initial_grid)
    m = len(initial_grid[0])

    grid = [initial_grid]
    lim = n * m

    portal_grid = []
    portal_grid.append(generate_portal_grid(grid[0]))

    for i in range(n):
        for j in range(m):

            if grid[0][i][j] == 'A':
                si, sj = i, j

            if grid[0][i][j] == 'B':
                ei, ej = i, j

    for k in range(1, lim):

        grid.append([['.' for _ in range(m)] for _ in range(n)])

        for i in range(n):
            for j in range(m):
                
                black_holes = count_neighbors(i, j, grid[k-1], '&')

                if grid[k-1][i][j] == '&':
                    if black_holes == 2 or black_holes == 3:
                        grid[k][i][j] = '&'
                    continue

                if grid[k-1][i][j] != '&' and black_holes >= 3:
                        grid[k][i][j] = '&'
                else:
                    if i == si and j == sj:
                        grid[k][i][j] = 'A'
                    elif i == ei and j == ej:
                        grid[k][i][j] = 'B'
                    else:
                        grid[k][i][j] = grid[k-1][i][j]

        portal_grid.append(generate_portal_grid(grid[k]))

        for i in range(n):
            for j in range(m):
                if portal_grid[k-1][i][j] != portal_grid[k][i][j]:
                    grid[k][i][j] = '&'

    return grid, portal_grid

best_paths = []
best_len = 1000000000
best_pcount = 0

def dfs(grid, portal_grid, visited, i, j, k, current_path, current_portal_count): 

    global best_paths, best_len, best_pcount

    if visited[i][j]:
        return
    
    if grid[k][i][j] == '&':
        return
    
    if len(current_path) > best_len:
        return

    if grid[k][i][j] == 'B': 

        if len(current_path) < best_len or (len(current_path) == best_len and current_portal_count > best_pcount):
            best_paths.clear()
            best_len = len(current_path)
            best_pcount = current_portal_count
            best_paths.append(current_path)
        elif len(current_path) == best_len and current_portal_count == best_pcount:
            best_paths.append(current_path)

        return
    
    visited[i][j] = True

    di = [-1, 1, 0, 0]
    dj = [0, 0, -1, 1]
    move = ['N', 'S', 'W', 'E']

    for d in range(4):
        if valid(i + di[d], j + dj[d], grid[k]) and not visited[i + di[d]][j + dj[d]] and grid[k][i + di[d]][j + dj[d]] != '&':
            if portal_grid[k][i + di[d]][j + dj[d]] != (-1, -1):
                visited[i + di[d]][j + dj[d]] = True
                pi, pj = portal_grid[k][i + di[d]][j + dj[d]]
                dfs(grid, portal_grid, visited, pi, pj, k + 1, current_path + move[d], current_portal_count + 1)
                visited[i + di[d]][j + dj[d]] = False
            else: 
                dfs(grid, portal_grid, visited, i + di[d], j + dj[d], k + 1, current_path + move[d], current_portal_count)

    visited[i][j] = False

def generate_best_paths(grid, portal_grid):

    n = len(grid[0])
    m = len(grid[0][0])

    visited = [[False for _ in range(m)] for _ in range(n)]

    for i in range(n):
            for j in range(m):
                if grid[0][i][j] == 'A':
                    dfs(grid, portal_grid, visited, i, j, 0, "", 0)    

def solve(initial_state):

    global best_paths, best_len, best_pcount

    grid, portal_grid = simulate(initial_state)

    generate_best_paths(grid, portal_grid)

    best_paths.sort()
    
    flag = f'{len(best_paths)}-'
    for p in best_paths:
        flag += p
    flag += f'-{best_pcount}'
    
    return flag    

def main():

    parser = argparse.ArgumentParser(description='First challenge')
    parser.add_argument('path', help='Path to input file')
    args = parser.parse_args()
    path = args.path

    grid = parse(path)

    print('\nInitial state:')
    for row in grid:
        print(row)

    flag = solve(grid)
    print('\npassword:')
    print(flag)

    f = open('pass.txt', 'w')
    f.write(flag)
    f.close

if __name__ == '__main__':
    main()