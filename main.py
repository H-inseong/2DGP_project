from pico2d import open_canvas, close_canvas, hide_lattice

import game_framework
import play_mode

WIDTH = 1920
HEIGHT = 960

open_canvas(WIDTH, HEIGHT)
hide_lattice()
game_framework.run(play_mode)
close_canvas()