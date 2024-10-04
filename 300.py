import argparse
import stepic
from PIL import Image
import numpy as np
import cv2
import pytesseract
import os

def split_image(img, block_size):
    n, m = img.size
    blocks_n = n // block_size
    blocks = [[None for _ in range(blocks_n)] for _ in range(blocks_n)]
    for i in range(0, n, block_size):
        for j in range(0, m, block_size):
            if i+block_size > n or j+block_size > m:
                continue
            block = img.crop((j, i, j+block_size, i+block_size))
            blocks[i//block_size][j//block_size] = block
    return blocks

def preprocess(img):
    img = np.array(img)
    img = cv2.GaussianBlur(img, (5, 5), 0)
    _, img = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY)
    img = cv2.bitwise_not(img)
    img = cv2.dilate(img, np.ones((3, 3), np.uint8), iterations=1)
    img = Image.fromarray(img)
    return img

def get_sudoku_grid(img):

    n, m = img.size
    block_size = n // 16

    blocks = split_image(img, block_size)

    sudoku_grid = [[0 for _ in range(16)] for _ in range(16)]

    for i in range(16):
        for j in range(16):

            block = Image.fromarray(np.array(blocks[i][j])[10:-10, 10:-10])
            block = preprocess(block)
            block = block.resize((block.size[0]*3, block.size[1]*3), Image.BILINEAR)
            digit = pytesseract.image_to_string(block, config='--psm 13 --oem 3 -c tessedit_char_whitelist=0123456789')
            sudoku_grid[i][j] = digit.strip()

            if sudoku_grid[i][j]:
                sudoku_grid[i][j] = int(sudoku_grid[i][j])
                if sudoku_grid[i][j] > 16:
                    sudoku_grid[i][j] //= 10
            else:
                sudoku_grid[i][j] = 0
            
    return sudoku_grid

def solve_sudoku(sudoku_grid):

    def is_valid(sudoku_grid, i, j, num):
        for x in range(16):
            if sudoku_grid[i][x] == num or sudoku_grid[x][j] == num:
                return False
        for x in range(4):
            for y in range(4):
                if sudoku_grid[(i//4)*4+x][(j//4)*4+y] == num:
                    return False
        return True

    def solve(sudoku_grid):
        for i in range(16):
            for j in range(16):
                if sudoku_grid[i][j] == 0:
                    for num in range(1, 17):
                        if is_valid(sudoku_grid, i, j, num):
                            sudoku_grid[i][j] = num
                            if solve(sudoku_grid):
                                return True
                            sudoku_grid[i][j] = 0
                    return False
        return True

    solve(sudoku_grid)

    return sudoku_grid

def get_flag(img_path):

    scrambled_img = Image.open(img_path)

    decoded_img = stepic.decode(scrambled_img)
    # print(decoded_img)

    seed = int(decoded_img.replace('#', ''))

    np.random.seed(seed)

    scrambled_pix = scrambled_img.getdata()

    indices = np.random.permutation(len(scrambled_pix))

    unscrambled_pix = [0] * len(scrambled_pix)
    for i, pos in enumerate(indices):
        unscrambled_pix[pos] = scrambled_pix[i]

    img = Image.new(scrambled_img.mode, scrambled_img.size) 
    img.putdata(unscrambled_pix)
    #img.show()

    n, m = img.size
    # print(f'{n}x{m}')

    block_size = n // 4
    # print(f'block size: {block_size}')

    blocks = split_image(img, block_size)

    for i in range(4):
        for j in range(4):

            decoded_block = stepic.decode(blocks[i][j])
            message = int(decoded_block.replace('#', ''), 2)

            rotation = (message >> 4) * -90
            position = message & 0b001111

            fi = position // 4
            fj = position % 4

            # print(f'Block ({i}, {j}): rotation={rotation}, position={position} ({fi}, {fj})')

            blocks[i][j] = blocks[i][j].rotate(rotation)

            img.paste(blocks[i][j], (fj*block_size, fi*block_size))

    # img.show()

    get_sudoku_grid(img)

    sudoku_grid = get_sudoku_grid(img)

    flag = ''
    for row in solve_sudoku(sudoku_grid):
        for c in row:
            flag += str(c)
    
    return flag

def main():

    parser = argparse.ArgumentParser(description='First challenge')
    parser.add_argument('path', nargs='?', default=None, help='Path to input file')
    args = parser.parse_args()
    img_path = args.path

    if img_path:
        flag = get_flag(img_path)
        print(flag)
        return
    
    for i in range(1, 100):

        img_path = f'lvl{i}.png'
        zip_path = f'lvl{i+1}.zip'

        flag = get_flag(img_path)
        print(f'Level {i}: {flag}')

        os.system(f'7z x {zip_path} -p{flag}')

if __name__ == '__main__':
    main()