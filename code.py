import bpy
from math import pi
from random import random, choice
from mathutils import Euler, Color
from pathlib import Path
from sys import stderr, argv
import argparse

def must_dir(path):
    from os.path import isdir
    if isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"'{path}' não é uma pasta válida")

# from: https://blender.stackexchange.com/questions/6817/how-to-pass-command-line-arguments-to-a-blender-python-script
class ArgumentParserForBlender(argparse.ArgumentParser):
    def _get_argv_after_doubledash(self):
        try:
            idx = argv.index("--")
            return argv[idx+1:] # the list after '--'
        except ValueError as e: # '--' not in the list:
            return []
    def parse_args(self):
        return super().parse_args(args=self._get_argv_after_doubledash())

def parse_arguments():
    parser = ArgumentParserForBlender()
    parser.add_argument("-c", "--count", help="Quantas variações gerar de cada letra", default = 10, type = int)
    parser.add_argument("-d", "--dir", help="Qual pasta salvar as imagens", default = "/tmp/abc_test", type = must_dir)
    return parser.parse_args()

LETTERS = ["A", "B", "C"]
MATERIAL_LETTER = 'Letter Material'
SHADER_NODE_PRINCIPLED_BSDF = 'Principled BSDF'
HALF_CIRCLE_DEG = 180
MAX_COLOR_VALUE = 255
FULL_CIRCLE_RAD_MULTIPLIER = 2

def log(*args, **kwargs):
    return print(*args, **kwargs, file=stderr)

def random_degree():
	return random() * FULL_CIRCLE_RAD_MULTIPLIER * pi

def random_euler():
	return Euler((random_degree(), random_degree(), random_degree()), 'XYZ')

def random_color():
    color = Color()
    hue = random() # [0,1]
    color.hsv = (hue, 1, 1)
    return [color.r, color.g, color.b, 1]

def random_letter():
    return choice(LETTERS)

def rotate_object_randomly(obj, euler = random_euler()):
    obj.rotation_euler = euler
    return euler
    
def change_color_randomly(material, color = random_color()):
    material.node_tree.nodes[SHADER_NODE_PRINCIPLED_BSDF].inputs[0].default_value = color
    return color

def randomize_object_appearance(object, **kwargs):
    rotation = rotate_object_randomly(object, **kwargs)
    color = change_color_randomly(bpy.data.materials[MATERIAL_LETTER], **kwargs)
    letter = random_letter()
    object.data.body = letter
    return rotation, color, letter

def rad2floordeg(rad):
    return int(rad*HALF_CIRCLE_DEG/pi)

def main():
    args = parse_arguments()
    count = args.count
    output_dir = args.dir

    obj = bpy.context.object
    log(f"Renderizando para '{output_dir}'...")
    dir = Path(output_dir)
    for i in range(count):
        log(f"Renderizando combinação {i+1}/{count}")
        rotation = rotate_object_randomly(obj, euler = random_euler())
        color = change_color_randomly(bpy.data.materials[MATERIAL_LETTER], color = random_color())
        for letter in LETTERS:
            #log(rotation, color, letter)
            rx,ry,rz = map(rad2floordeg, rotation)
            r, g, b, a = map(lambda v: int(v*MAX_COLOR_VALUE), color)
            filename = dir / letter / f'{r}-{g}-{b}-{rx}-{ry}-{rz}.png'
            obj.data.body = letter
            log(f"Renderizando '{str(filename)}'...")
            #log(rx, ry, rz)
            #log(r, g, b, a)
            bpy.context.scene.render.filepath = str(filename)
            bpy.ops.render.render(write_still=True)

if __name__ == "__main__":
    main()
