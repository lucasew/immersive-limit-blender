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

parser = ArgumentParserForBlender()
parser.add_argument("-c", "--count", help="Quantas variações gerar de cada letra", default = 10, type = int)
parser.add_argument("-d", "--dir", help="Qual pasta salvar as imagens", default = "/tmp/abc_test", type = must_dir)
args = parser.parse_args()

COUNT = args.count
DIR = args.dir
LETTERS = ["A", "B", "C"]

def log(*args, **kwargs):
    return print(*args, **kwargs, file=stderr)

def random_degree():
	return random() * 2 * pi

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
    material.node_tree.nodes['Principled BSDF'].inputs[0].default_value = color
    return color

def abubleify_object(object, **kwargs):
    rotation = rotate_object_randomly(object, **kwargs)
    color = change_color_randomly(bpy.data.materials['Letter Material'], **kwargs)
    letter = random_letter()
    object.data.body = letter
    return rotation, color, letter

def rad2floordeg(rad):
    return int(rad*180/pi)

if __name__ == "__main__":
    obj = bpy.context.object
    log(f"Renderizando para '{DIR}'...")
    dir = Path(DIR)
    for i in range(COUNT):
        log(f"Renderizando combinação {i+1}/{COUNT}")
        rotation = rotate_object_randomly(obj, euler = random_euler())
        color = change_color_randomly(bpy.data.materials['Letter Material'], color = random_color())
        for letter in LETTERS:
            #log(rotation, color, letter)
            rx,ry,rz = map(rad2floordeg, rotation)
            r, g, b, a = map(lambda v: int(v*255), color)
            filename = dir / letter / f'{r}-{g}-{b}-{rx}-{ry}-{rz}.png'
            obj.data.body = letter
            log(f"Renderizando '{str(filename)}'...")
            #log(rx, ry, rz)
            #log(r, g, b, a)
            bpy.context.scene.render.filepath = str(filename)
            bpy.ops.render.render(write_still=True)
