# tested with python 3.6 and the opencv-python package installed via 'pip install opencv-python'
# Keep in mind that file size can become very large for high res images. Generates 17 lines of text per pixel.
# Released under MIT license.

# The settings (in all caps) should be self explanatory.
# You can copy the contents of the output file into your .map file.
# Alternatively you can set APPEND to True and add the brushes directly into your .map file
# Make sure to back up your .map file before using this functionality.

# For questions or suggestions you can send a message to Daan#2052 on Discord.

import cv2
import sys

# input file path
INPUT_FILE = 'D:\\Libraries\\Documents\\pycharmprojects\\reflexarena_pixelart\\test images\\sarge28.png'

# output file path
OUTPUT_FILE = 'D:\\Libraries\\Documents\\pycharmprojects\\reflexarena_pixelart\\output.txt'

# append to the output file instead of overwriting it
# Make sure to back up your .map file before using this functionality.
APPEND = False

# size per pixel in units
PIXEL_SIZE = 1

# reflex material name
MATERIAL = 'common/materials/effects/glow2'

# The dictionary key is a material name and the value is a list of (inclusive) rgb range tuples.
# Any pixel within a given range will have its material changed to the one given here.
# If a pixel fits in multiple ranges then the first material encountered will be used.
# Example: {'common/liquids/lava/lava': [(0, 0, 0, 50, 50, 50), (100, 100, 100, 150, 150, 150)],
#           'common/liquids/water/water': [...]}
# Range tuple format: [(r_low, g_low, b_low, r_high, g_high, b_high)]
# The example will change all pixels with rgb values between 0-50 or 100-150 to lava.
MATERIAL_OVERRIDES = {}

# x, y, z coordinates of the top left pixel
ORIGIN = (0, 0, 0)

# Add clip extending this many units from the image. Set to a negative number to not add clip.
CLIP_PADDING = 1

# Material that´s used as a clip
CLIP_MATERIAL = 'internal/editor/textures/editor_fullclip'

# List of transparent colors given as (r,g,b) tuples. Pixels with these colors are not converted to brushes.
# for example [(56, 62, 23), (255, 0, 0)]
TRANSPARANT_COLORS = []

# If the image has an alpha channel, pixels with an alpha value below this value will be ignored.
ALPHA_THRESHOLD = 0

# Rotate the image clockwise by this angle in degrees before converting it.
ROTATE_ANGLE = 0

# Flip the x and z axes
FLIP_XZ = False

# Flip the y and z axes
FLIP_YZ = False

# Add an effect name here to use effects instead of brushes. Set to None to use brushes.
# The effects use the same materials and colors that a brush would have
EFFECT_NAME = None
# Effect scale to use
EFFECT_SCALE = 1/128
# Distance between neighbouring effects in units on the X axis
EFFECT_OFFSET_X = 1
# Distance between neighbouring effects in units on the Y axis
EFFECT_OFFSET_Y = 1
# Effect angles same order as in game
EFFECT_ANGLES = (0, 90, 0)
# Number materials of the effect
EFFECT_NUM_MATERIALS = 1

if __name__ == '__main__':
    image = cv2.imread(INPUT_FILE, cv2.IMREAD_UNCHANGED)
    height = image.shape[0]
    width = image.shape[1]
    if image.shape[2] == 4:
        has_alpha = True
    else:
        has_alpha = False
    if ROTATE_ANGLE != 0:
        M = cv2.getRotationMatrix2D((width/2, height/2), -ROTATE_ANGLE, 1)
        image = cv2.warpAffine(image, M, (width, height))
    ox, oy, oz = ORIGIN
    angle_x, angle_y, angle_z = EFFECT_ANGLES
    if FLIP_XZ:
        angle_x, angle_z = angle_z, angle_x
    if FLIP_YZ:
        angle_y, angle_z = angle_z, angle_y
    lines = []
    x_max = -sys.maxsize
    y_max = -sys.maxsize
    z_max = -sys.maxsize
    x_min = sys.maxsize
    y_min = sys.maxsize
    z_min = sys.maxsize
    if APPEND:
        open_mode = 'a+'
    else:
        open_mode = 'w+'
    with open(OUTPUT_FILE, open_mode) as f:
        for y in range(0, height):
            for x in range(0, width):
                blue = int(image[y, x, 0])
                green = int(image[y, x, 1])
                red = int(image[y, x, 2])
                if has_alpha:
                    alpha = int(image[y, x, 3])
                else:
                    alpha = 255
                if (red, green, blue) in TRANSPARANT_COLORS or alpha < ALPHA_THRESHOLD:
                    # Skip pixels marked as transparant
                    continue
                
                # calculate coordinates
                if EFFECT_NAME is None:
                    bx_min = ox + x * PIXEL_SIZE
                    bx_max = ox + (x + 1) * PIXEL_SIZE
                    by_min = oy - (y + 1) * PIXEL_SIZE
                    by_max = oy - y * PIXEL_SIZE
                    bz_min = oz
                    bz_max = oz + PIXEL_SIZE
                else:
                    bx_min = ox + x * EFFECT_OFFSET_X
                    bx_max = ox + x * EFFECT_OFFSET_X
                    by_min = oy - y * EFFECT_OFFSET_Y
                    by_max = oy - y * EFFECT_OFFSET_Y
                    bz_min = oz
                    bz_max = oz

                # perform any flips
                if FLIP_XZ:
                    bx_min, bz_min, bx_max, bz_max, ox, oz = bz_min, bx_min, bz_max, bx_max, oz, ox
                if FLIP_YZ:
                    by_min, bz_min, by_max, bz_max, oy, oz = bz_min, by_min, bz_max, by_max, oz, oy
                
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
                
                # set color
                brush_color = hex(255*256**3+red*256**2+green*256+blue)
                
                # set material
                brush_material = MATERIAL
                for mat, rangelist in MATERIAL_OVERRIDES.items():
                    for _range in rangelist:
                        if red >= _range[0] and green >= _range[1] and blue >= _range[2] and\
                                red <= _range[3] and green <= _range[4] and blue <= _range[5]:
                            brush_material = mat
                            break
                    if brush_material != MATERIAL:
                        break

                if EFFECT_NAME is None:
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
                    lines.append(f'            0.000000 0.000000 1.000000 1.000000 0.000000 0 1 2 3 {brush_color} {brush_material}\n')
                    lines.append(f'            0.000000 0.000000 1.000000 1.000000 0.000000 6 5 4 7 {brush_color} {brush_material}\n')
                    lines.append(f'            0.000000 0.000000 1.000000 1.000000 0.000000 2 1 5 6 {brush_color} {brush_material}\n')
                    lines.append(f'            0.000000 0.000000 1.000000 1.000000 0.000000 0 3 7 4 {brush_color} {brush_material}\n')
                    lines.append(f'            0.000000 0.000000 1.000000 1.000000 0.000000 3 2 6 7 {brush_color} {brush_material}\n')
                    lines.append(f'            0.000000 0.000000 1.000000 1.000000 0.000000 1 0 4 5 {brush_color} {brush_material}\n')
                else:
                    lines.append('    entity\n')
                    lines.append('        type Effect\n')
                    lines.append(f'        Vector3 position {bx_min:.6f} {by_min:.6f} {bz_min:.6f}\n')
                    lines.append(f'        Vector3 angles {angle_x:.6f} {angle_y:.6f} {angle_z:.6f}\n')
                    lines.append(f'        String64 effectName {EFFECT_NAME}\n')
                    for i in range(EFFECT_NUM_MATERIALS):
                        lines.append(f'        String256 material{i}Name {brush_material}\n')
                        lines.append(f'        ColourARGB32 material{i}Albedo {brush_color}\n')
                    lines.append(f'        Float effectScale {EFFECT_SCALE}\n')

        # Add clip brush around all pixel brushes/effects.
        if CLIP_PADDING >= 0:
            x_min -= CLIP_PADDING
            x_max += CLIP_PADDING
            y_min -= CLIP_PADDING
            y_max += CLIP_PADDING
            z_min -= CLIP_PADDING
            z_max += CLIP_PADDING
            if EFFECT_NAME is not None:
                x_min += EFFECT_OFFSET_X
                y_min -= EFFECT_OFFSET_Y

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
            lines.append(f'            0.000000 0.000000 1.000000 1.000000 0.000000 0 1 2 3 0x00000000 {CLIP_MATERIAL}\n')
            lines.append(f'            0.000000 0.000000 1.000000 1.000000 0.000000 6 5 4 7 0x00000000 {CLIP_MATERIAL}\n')
            lines.append(f'            0.000000 0.000000 1.000000 1.000000 0.000000 2 1 5 6 0x00000000 {CLIP_MATERIAL}\n')
            lines.append(f'            0.000000 0.000000 1.000000 1.000000 0.000000 0 3 7 4 0x00000000 {CLIP_MATERIAL}\n')
            lines.append(f'            0.000000 0.000000 1.000000 1.000000 0.000000 3 2 6 7 0x00000000 {CLIP_MATERIAL}\n')
            lines.append(f'            0.000000 0.000000 1.000000 1.000000 0.000000 1 0 4 5 0x00000000 {CLIP_MATERIAL}\n')

        f.writelines(lines)
