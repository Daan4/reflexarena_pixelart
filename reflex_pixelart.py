# tested with python 3.6 and the opencv-python package installed via 'pip install opencv-python'
# Keep in mind that file size can become very large for high res images. Generates 17 lines of text per pixel.
# Released under MIT license.

# The settings (in all caps) should be self explanatory.
# You can copy the contents of the output file into your .map file.

# For questions or suggestions you can send a message to Daan#2052 on Discord.

import cv2
import sys

# input file path
INPUT_FILE = 'C:\\example\\file.png'

# output file path
OUTPUT_FILE = 'C:\\example\\output.txt'

# size per pixel in units
PIXEL_SIZE = 16

# reflex material name
MATERIAL = 'common/materials/effects/glow2'

# x, y, z offset
ORIGIN = (0, 0, 0)

# Add clip extending this many units from the image. Set to a negative number to not add clip.
CLIP_PADDING = 1

# List of transparent colors given as (r,g,b) tuples. Pixels with these colors are not converted to brushes.
# for example [(56, 62, 23), (255, 0, 0)]
TRANSPARANT_COLORS = []

# Flip the x and y axes.
FLIP_XY = False

# Flip the x and z axes
FLIP_XZ = False

# Flip the y and z axes
FLIP_YZ = False

if __name__ == '__main__':
    image = cv2.imread(INPUT_FILE)
    height = image.shape[0]
    width = image.shape[1]
    ox, oy, oz = ORIGIN
    lines = []
    x_max = -sys.maxsize
    y_max = -sys.maxsize
    z_max = -sys.maxsize
    x_min = sys.maxsize
    y_min = sys.maxsize
    z_min = sys.maxsize
    with open(OUTPUT_FILE, 'w+') as f:
        for y in range(0, height):
            for x in range(0, width):
                blue = int(image[y, x, 0])
                green = int(image[y, x, 1])
                red = int(image[y, x, 2])
                if (red, green, blue) in TRANSPARANT_COLORS:
                    # Skip pixel colors marked as transparant
                    continue
                
                # calculate brush vertex coordinates
                bx_min = ox + x * PIXEL_SIZE
                bx_max = ox + (x + 1) * PIXEL_SIZE
                by_min = oy - (y + 1) * PIXEL_SIZE
                by_max = oy - y * PIXEL_SIZE
                bz_min = oz
                bz_max = oz+PIXEL_SIZE

                # perform any flips
                if FLIP_XY:
                    bx_min, by_min, bx_max, by_max = by_min, bx_min, by_max, bx_max
                if FLIP_XZ:
                    bx_min, bz_min, bx_max, bz_max = bz_min, bx_min, bz_max, bx_max
                if FLIP_YZ:
                    by_min, bz_min, by_max, bz_max = bz_min, by_min, bz_max, by_max
                
                # track bounding coordinates for drawn brushes to draw a clip later
                if bx_max > x_max:
                    x_max = bx_max
                if bx_min < x_min:
                    x_min = bx_min
                if by_max > y_max:
                    y_max = by_max
                if by_min < y_min:
                    y_min = by_min
                if bz_max > z_max:
                    z_max = bz_max
                if bz_min < z_min:
                    z_min = bz_min

                lines.append('    brush\n')
                lines.append('        vertices\n')
                lines.append(f'            {bx_min:.6f} {by_max:.6f} {bz_max:.6f}\n')
                lines.append(f'            {bx_max:.6f} {by_max:.6f} {bz_max:.6f}\n')
                lines.append(f'            {bx_max:.6f} {by_max:.6f} {bz_min:.6f}\n')
                lines.append(f'            {bx_min:.6f} {by_max:.6f} {bz_min:.6f}\n')
                lines.append(f'            {bx_min:.6f} {by_min:.6f} {bz_max:.6f}\n')
                lines.append(f'            {bx_max:.6f} {by_min:.6f} {bz_max:.6f}\n')
                lines.append(f'            {bx_max:.6f} {by_min:.6f} {bz_min:.6f}\n')
                lines.append(f'            {bx_min:.6f} {by_min:.6f} {bz_min:.6f}\n')
                lines.append('        faces\n')
                lines.append(f'            0.000000 0.000000 1.000000 1.000000 0.000000 0 1 2 3 {hex(255*256**3+red*256**2+green*256+blue)} {MATERIAL}\n')
                lines.append(f'            0.000000 0.000000 1.000000 1.000000 0.000000 6 5 4 7 {hex(255*256**3+red*256**2+green*256+blue)} {MATERIAL}\n')
                lines.append(f'            0.000000 0.000000 1.000000 1.000000 0.000000 2 1 5 6 {hex(255*256**3+red*256**2+green*256+blue)} {MATERIAL}\n')
                lines.append(f'            0.000000 0.000000 1.000000 1.000000 0.000000 0 3 7 4 {hex(255*256**3+red*256**2+green*256+blue)} {MATERIAL}\n')
                lines.append(f'            0.000000 0.000000 1.000000 1.000000 0.000000 3 2 6 7 {hex(255*256**3+red*256**2+green*256+blue)} {MATERIAL}\n')
                lines.append(f'            0.000000 0.000000 1.000000 1.000000 0.000000 1 0 4 5 {hex(255*256**3+red*256**2+green*256+blue)} {MATERIAL}\n')

        # Add clip brush around all pixel brushes.
        if CLIP_PADDING >= 0:
            x_min -= CLIP_PADDING
            x_max += CLIP_PADDING
            y_min -= CLIP_PADDING
            y_max += CLIP_PADDING
            z_min -= CLIP_PADDING
            z_max += CLIP_PADDING

            lines.append('    brush\n')
            lines.append('        vertices\n')
            lines.append(f'            {x_min:.6f} {y_max:.6f} {z_max:.6f}\n')
            lines.append(f'            {x_max:.6f} {y_max:.6f} {z_max:.6f}\n')
            lines.append(f'            {x_max:.6f} {y_max:.6f} {z_min:.6f}\n')
            lines.append(f'            {x_min:.6f} {y_max:.6f} {z_min:.6f}\n')
            lines.append(f'            {x_min:.6f} {y_min:.6f} {z_max:.6f}\n')
            lines.append(f'            {x_max:.6f} {y_min:.6f} {z_max:.6f}\n')
            lines.append(f'            {x_max:.6f} {y_min:.6f} {z_min:.6f}\n')
            lines.append(f'            {x_min:.6f} {y_min:.6f} {z_min:.6f}\n')
            lines.append('        faces\n')
            lines.append('            0.000000 0.000000 1.000000 1.000000 0.000000 0 1 2 3 0x00000000 internal/editor/textures/editor_fullclip\n')
            lines.append('            0.000000 0.000000 1.000000 1.000000 0.000000 6 5 4 7 0x00000000 internal/editor/textures/editor_fullclip\n')
            lines.append('            0.000000 0.000000 1.000000 1.000000 0.000000 2 1 5 6 0x00000000 internal/editor/textures/editor_fullclip\n')
            lines.append('            0.000000 0.000000 1.000000 1.000000 0.000000 0 3 7 4 0x00000000 internal/editor/textures/editor_fullclip\n')
            lines.append('            0.000000 0.000000 1.000000 1.000000 0.000000 3 2 6 7 0x00000000 internal/editor/textures/editor_fullclip\n')
            lines.append('            0.000000 0.000000 1.000000 1.000000 0.000000 1 0 4 5 0x00000000 internal/editor/textures/editor_fullclip\n')

        f.writelines(lines)
