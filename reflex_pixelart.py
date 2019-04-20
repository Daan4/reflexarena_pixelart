# tested with python 3.6 and the opencv-python package installed via 'pip install opencv-python'
# Keep in mind that file size can become very large for high res images. Generates 17 lines of text per pixel.
# Released under MIT license.

# The settings (in all caps) should be self explanatory.
# You can copy the contents of the worldspawn output file into your .map file.
# Alternatively you can set APPEND to True and add the brushes directly into your .map file
# Make sure to back up your .map file before using this functionality.

# For questions or suggestions you can send a message to Daan#2052 on Discord.

import cv2
import numpy as np
import sys

# input file path
INPUT_FILE = 'D:\\Libraries\\Documents\\pycharmprojects\\reflexarena_pixelart\\test images\\rocket gang.png'

# worldspawn output file path
WORLDSPAWN_OUTPUT_FILE = 'D:\\Libraries\\Documents\\pycharmprojects\\reflexarena_pixelart\\brushes.txt'
# prefab output file path
PREFAB_OUTPUT_FILE = 'D:\\Libraries\\Documents\\pycharmprojects\\reflexarena_pixelart\\prefabs.txt'

# Use prefabs for pixels occurring more than once.
# Using this should reduce the file size.
# Generated prefabs will be written to PREFAB_OUTPUT_FILE and have to be copied to the top of your map file.
# (Between the version and the global worldspawn entity)
USE_PREFABS = True

# append to the worldspawn output file instead of overwriting it
# Make sure to back up your .map file before using this functionality.
# This only works for worldspawn, prefabs will have to be manually copied.
APPEND = False

# size per pixel in units
PIXEL_SIZE = 16

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

# Rotate the image clockwise by this angle in degrees using opencv before converting it.
IMAGE_ROTATE_ANGLE = 0

# Scale the image using opencv before converting it.
IMAGE_SCALE = 1

# Flip the x and z axes
FLIP_XZ = False

# Flip the y and z axes
FLIP_YZ = False

# Add an effect name here to use effects instead of brushes. Set to None to use brushes.
# The effects use the same materials and colors that a brush would have.
# Using an effect instead of brushes can reduce the file size and increase performance.
# EFFECT_NAME = 'common/meshes/concrete/concrete_tile_128x128'
EFFECT_NAME = None
# Effect scale to use
EFFECT_SCALE = 1/128
# Distance between neighbouring effects in units on the X axis
EFFECT_OFFSET_X = 1
# Distance between neighbouring effects in units on the Y axis
EFFECT_OFFSET_Y = 1
# Effect angles same order as in game
EFFECT_ANGLES = (0, 90, 0)
# Number of materials the effect has
EFFECT_NUM_MATERIALS = 1


def generate_brush_string(xmin, xmax, ymin, ymax, zmin, zmax, _color, _material):
    brush = '    brush\n'
    brush += '        vertices\n'
    brush += f'            {xmin:.6f} {ymax:.6f} {zmax:.6f}\n'
    brush += f'            {xmax:.6f} {ymax:.6f} {zmax:.6f}\n'
    brush += f'            {xmax:.6f} {ymax:.6f} {zmin:.6f}\n'
    brush += f'            {xmin:.6f} {ymax:.6f} {zmin:.6f}\n'
    brush += f'            {xmin:.6f} {ymin:.6f} {zmax:.6f}\n'
    brush += f'            {xmax:.6f} {ymin:.6f} {zmax:.6f}\n'
    brush += f'            {xmax:.6f} {ymin:.6f} {zmin:.6f}\n'
    brush += f'            {xmin:.6f} {ymin:.6f} {zmin:.6f}\n'
    brush += '        faces\n'
    brush += f'            0.000000 0.000000 1.000000 1.000000 0.000000 0 1 2 3 {_color} {_material}\n'
    brush += f'            0.000000 0.000000 1.000000 1.000000 0.000000 6 5 4 7 {_color} {_material}\n'
    brush += f'            0.000000 0.000000 1.000000 1.000000 0.000000 2 1 5 6 {_color} {_material}\n'
    brush += f'            0.000000 0.000000 1.000000 1.000000 0.000000 0 3 7 4 {_color} {_material}\n'
    brush += f'            0.000000 0.000000 1.000000 1.000000 0.000000 3 2 6 7 {_color} {_material}\n'
    brush += f'            0.000000 0.000000 1.000000 1.000000 0.000000 1 0 4 5 {_color} {_material}\n'
    return brush


def generate_effect_string(_x, y, z, ax, ay, az, name, _material, _color, scale, num_materials):
    effect = '    entity\n'
    effect += '        type Effect\n'
    effect += f'        Vector3 position {_x:.6f} {y:.6f} {z:.6f}\n'
    effect += f'        Vector3 angles {ax:.6f} {ay:.6f} {az:.6f}\n'
    effect += f'        String64 effectName {name}\n'
    for i in range(num_materials):
        effect += f'        String256 material{i}Name {_material}\n'
        effect += f'        ColourARGB32 material{i}Albedo {_color}\n'
    effect += f'        Float effectScale {scale}\n'
    return effect


def generate_prefab_string(_x, y, z, name):
    prefab = '    entity\n'
    prefab += '        type Prefab\n'
    prefab += f'        Vector3 position {_x:.6f} {y:.6f} {z:.6f}\n'
    prefab += f'        String64 prefabName {name}\n'
    return prefab


def rgb2hex(r, g, b):
    return hex(255*256**3+r*256**2+g*256+b)


if __name__ == '__main__':
    ox, oy, oz = ORIGIN
    worldspawn_lines = []
    prefab_lines = []
    x_max = -sys.maxsize
    y_max = -sys.maxsize
    z_max = -sys.maxsize
    x_min = sys.maxsize
    y_min = sys.maxsize
    z_min = sys.maxsize

    image = cv2.imread(INPUT_FILE, cv2.IMREAD_UNCHANGED)
    # Check if image has alpha channel
    if image.shape[2] == 4:
        has_alpha = True
    else:
        has_alpha = False
    # Scale image
    if IMAGE_SCALE < 1:
        image = cv2.resize(image, None, fx=IMAGE_SCALE, fy=IMAGE_SCALE, interpolation=cv2.INTER_AREA)
    elif IMAGE_SCALE > 1:
        image = cv2.resize(image, None, fx=IMAGE_SCALE, fy=IMAGE_SCALE, interpolation=cv2.INTER_CUBIC)
    height = image.shape[0]
    width = image.shape[1]
    # Rotate image
    if IMAGE_ROTATE_ANGLE != 0:
        M = cv2.getRotationMatrix2D((width/2, height/2), -IMAGE_ROTATE_ANGLE, 1)
        image = cv2.warpAffine(image, M, (width, height))
    # Create a list of unique RGB tuples that occur more than once
    if USE_PREFABS:
        tmp = image[:,:,0:3]
        tmp = tmp.reshape(height*width, 3)
        unique, counts = np.unique(tmp, return_counts=True, axis=0)
        unique_indices = np.where(counts > 1)
        prefabs = {rgb2hex(x[0], x[1], x[2]): None for x in unique[unique_indices]}
    # Apply flips to effect angles
    angle_x, angle_y, angle_z = EFFECT_ANGLES
    if FLIP_XZ:
        angle_x, angle_z = angle_z, angle_x
    if FLIP_YZ:
        angle_y, angle_z = angle_z, angle_y

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
            color = rgb2hex(red, green, blue)
            
            # set material
            material = MATERIAL
            for mat, rangelist in MATERIAL_OVERRIDES.items():
                for _range in rangelist:
                    if red >= _range[0] and green >= _range[1] and blue >= _range[2] and\
                            red <= _range[3] and green <= _range[4] and blue <= _range[5]:
                        material = mat
                        break
                if material != MATERIAL:
                    break

            # Create the brush/effect/prefab
            add_pixel = True
            if USE_PREFABS:
                try:
                    if prefabs[color] is None:
                        prefab_lines.append(f'prefab {color}\n')
                        prefabs[color] = color
                        if EFFECT_NAME is None:
                            prefab_lines.append('    entity\n')
                            prefab_lines.append('        type WorldSpawn\n')
                            prefab_lines.append(
                                generate_brush_string(ox, ox+PIXEL_SIZE, oy-PIXEL_SIZE, oy, oz, oz+PIXEL_SIZE, color, material))
                        else:
                            prefab_lines.append(
                                generate_effect_string(ox, oy, oz, angle_x, angle_y, angle_z, EFFECT_NAME,
                                                       material, color, EFFECT_SCALE, EFFECT_NUM_MATERIALS))
                        worldspawn_lines.append(generate_prefab_string(bx_min, by_min, bz_min, prefabs[color]))
                    else:
                        worldspawn_lines.append(generate_prefab_string(bx_min, by_min, bz_min, prefabs[color]))
                    add_pixel = False
                except KeyError:
                    pass
            if add_pixel:
                if EFFECT_NAME is None:
                    worldspawn_lines.append(generate_brush_string(bx_min, bx_max, by_min, by_max, bz_min, bz_max, color, material))
                else:
                    worldspawn_lines.append(generate_effect_string(bx_min, by_min, bz_min, angle_x, angle_y, angle_z, EFFECT_NAME,
                                                        material, color, EFFECT_SCALE, EFFECT_NUM_MATERIALS))

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
        worldspawn_lines.append(generate_brush_string(x_min, x_max, y_min, y_max, z_min, z_max, '0x00000000', CLIP_MATERIAL))
    
    if APPEND:
        open_mode = 'a+'
    else:
        open_mode = 'w+'
    with open(WORLDSPAWN_OUTPUT_FILE, open_mode) as f:
        f.writelines(worldspawn_lines)
    if USE_PREFABS:
        with open(PREFAB_OUTPUT_FILE, 'w+') as f:
            f.writelines(prefab_lines)
