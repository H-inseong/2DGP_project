from pico2d import *
import game_framework
import game_world
from Map import Map
from Player import Player
from enemies import Snake
from whip import Whip

def init():
    global player, map_obj, camera_x, camera_y
    player = Player(240, 240)
    game_world.add_object(player, 1)

    map_obj = Map(46, 38)  # 맵 생성 (가로 46 타일, 세로 38 타일 예시)
    map_obj.add_tile('ladder', 10, 10)
    map_obj.add_tile('solid', 10, 9)
    map_obj.add_tile('solid', 9, 9)
    map_obj.add_tile('solid', 10, 5)
    map_obj.add_tile('solid', 9, 5)
    map_obj.add_tile('solid', 10, 4)
    map_obj.add_tile('solid', 9, 4)

    map_obj.add_tile('rope_head', 10, 8)
    map_obj.add_tile('rope', 10, 7)
    map_obj.add_tile('rope', 10, 6)
    map_obj.add_tile('spike', 4, 4)
    map_obj.add_tile('spike', 5, 4)
    map_obj.add_tile('solid', 5, 3)
    camera_x, camera_y = 0, 0

    s = Snake(0)
    game_world.add_object(s, 1)
    game_world.add_collision_pair('Player:Monster', player, s)
    game_world.add_collision_pair('Whip:Monster', None, s)

    game_world.add_collision_pair('Player:Map', player, None)  # 그룹 A에 플레이어 추가
    for tile in map_obj.tiles.values():  # Tile 객체를 순회
        if tile.tile_type != 'empty':
            game_world.add_collision_pair('Player:Map', None, tile)
            game_world.add_collision_pair('items:Map', None, tile)
def finish():
    game_world.clear()


def handle_events():
    events = pico2d.get_events()
    for event in events:
        if event.type == pico2d.SDL_QUIT:
            game_framework.quit()
        elif event.type == pico2d.SDL_KEYDOWN and event.key == pico2d.SDLK_ESCAPE:
            game_framework.quit()
        else:
            player.handle_event(event)

def update():
    global camera_x, camera_y
    player.update()
    camera_x, camera_y = player.view_x, player.view_y
    game_world.update()
    game_world.handle_collisions()

def draw():
    pico2d.clear_canvas()
    if player.view_down == True:
        game_world.render(camera_x, camera_y - 240)
    if player.view_down == True:
        game_world.render(camera_x, camera_y + 240)
    game_world.render(camera_x, camera_y)
    pico2d.update_canvas()


def pause():
    pass

def resume():
    pass

def explosive(x, y):
    global map_obj  # map_obj를 전역 변수로 사용

    affected_tiles = []

    for dx in range(-1, 2):  # -1, 0, 1
        for dy in range(-1, 2):
            affected_tiles.append((x + dx, y + dy))

    # 각 면의 가운데 칸에서 한 칸 더 확장된 타일 추가
    more = [ (x, y + 2), (x, y - 2), (x - 2, y), (x + 2, y) ]
    affected_tiles.extend(more)
    affected_tiles = list(set(affected_tiles))

    for tile_pos in affected_tiles:
        try:
            tile = map_obj.tiles[tile_pos]
            if tile.tile_type in ('solid', 'spike'):
                map_obj.add_tile('empty', tile_pos[0], tile_pos[1])
                print(f"Tile at {tile_pos} changed to 'empty'.")
        except KeyError:
            # 지정된 좌표에 타일이 존재하지 않는 경우 무시
            print(f"Tile at {tile_pos} does not exist. Skipping.")