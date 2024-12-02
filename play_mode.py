from pico2d import *
from select import select

import game_framework
import game_world
from Item import Item
from Map import Map, Tile
from Player import Player
from enemies import Snake, Boss

def init():
    global player, map_obj, camera_x, camera_y, select_tile, stage
    global bgm
    stage = 1
    select_tile = 'solid'

    bgm = load_music('03. Menu.mp3')

    player = Player(0,0)
    game_world.add_object(player, 2)
    game_world.add_collision_pair('Player:Map', player, None)

    map_obj = Map(46, 38)  # 맵 생성 (가로 46 타일, 세로 38 타일 예시)
    camera_x, camera_y = 0, 0
    map_obj.load_map(f"{stage}.csv")
    bgm.set_volume(64)
    bgm.play()
    """s = Snake(0)
    b = Boss()
    game_world.add_object(s, 1)
    game_world.add_collision_pair('Player:Monster', player, s)
    game_world.add_collision_pair('Whip:Monster', None, s)
    game_world.add_object(b,  1)
    game_world.add_collision_pair('Player:Monster', player, b)
    game_world.add_collision_pair('Whip:Monster', None, b)"""




def finish():
    game_world.clear()


def handle_events():
    global select_tile, stage
    events = pico2d.get_events()
    for event in events:
        if event.type == pico2d.SDL_QUIT:
            game_framework.quit()

        elif event.type == pico2d.SDL_KEYDOWN:

            if event.key == pico2d.SDLK_ESCAPE:
                game_framework.quit()

            elif event.key == pico2d.SDLK_o:
                map_obj.save_map("current_map.csv")
            elif event.key == pico2d.SDLK_p:
                map_obj.load_map("current_map.csv")


            elif event.key == pico2d.SDLK_1:
                select_tile = 'solid'
            elif event.key == pico2d.SDLK_2:
                select_tile = 'ladder'
            elif event.key == pico2d.SDLK_3:
                select_tile = 'spike'

            elif event.key == pico2d.SDLK_UP:
                if player.move_stage:
                    player.intodoor_sound.set_volume(32)
                    player.intodoor_sound.play()
                    stage += 1
                    load_next_stage(stage)
                    player.move_stage = False
                player.handle_event(event)
            else:
                player.handle_event(event)

        elif event.type == pico2d.SDL_MOUSEBUTTONDOWN:
             mouse_x, mouse_y = event.x, 960 - event.y

             world_x = camera_x + mouse_x
             world_y = camera_y + mouse_y

             tile_x = world_x // 80
             tile_y = world_y // 80

             if event.button == 1:
                 set_solid_tile(tile_x, tile_y, select_tile)
             elif event.button == 3:
                 Item(tile_x, tile_y, 2, 15)
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

    start_x = int(max(camera_x // 80, 0))
    start_y = int(max(camera_y // 80, 0))
    end_x = int(min((camera_x + 1920) // 80 + 1, 46))
    end_y = int(min((camera_y + 960) // 80 + 1, 38))

    for x in range(start_x, end_x):
        for y in range(start_y, end_y):
            screen_x = (x * 80) - camera_x
            screen_y = (y * 80) - camera_y
            Tile.sprite_sheet.clip_draw_to_origin(128 * 8, 128 * 6, 128, 128, screen_x, screen_y, 95, 95)


    if player.view_down == True:
        game_world.render(camera_x, camera_y - 240)
    elif player.view_up == True:
        game_world.render(camera_x, camera_y + 240)
    else:
        game_world.render(camera_x, camera_y)
    pico2d.update_canvas()


def pause():
    pass

def resume():
    pass

def explosive(x, y):
    global map_obj
    affected_tiles = []
    for dx in range(-1, 2):  # -1, 0, 1
        for dy in range(-1, 2):
            affected_tiles.append((x + dx, y + dy))

    more = [ (x, y + 2), (x, y - 2), (x - 2, y), (x + 2, y) ]
    affected_tiles.extend(more)
    affected_tiles = list(set(affected_tiles))
    for tile_pos in affected_tiles:
        tile = map_obj.tiles[tile_pos]
        if tile.tile_type in ('solid', 'spike'):
            map_obj.add_tile('empty', tile_pos[0], tile_pos[1])

def create_rope(self, tile_x, tile_y):
    global map_obj

    map_obj.add_tile('rope_head', tile_x, tile_y)
    for i in range(1, 8):
        next_y = tile_y - i
        if (tile_x, next_y) in map_obj.tiles:
            tile = map_obj.tiles[(tile_x, next_y)]
            if tile.tile_type == 'empty':
                map_obj.add_tile('rope', tile_x, next_y)
            elif tile.tile_type in ['rope', 'rope_head']:
                continue
            else:
                break

def set_solid_tile(x, y, tile_type):
    global map_obj
    tile = map_obj.tiles[(x, y)]
    map_obj.add_tile(tile_type, x, y)

def save_current_state():
    global player, player_state
    player_state = {
        'hp': player.hp,
        'bomb_count': player.bomb_count,
        'rope_count': player.rope_count,
        'gold': player.gold
    }

def restore_player_state():
    global player, player_state
    player.hp = player_state.get('hp', 4)
    player.bomb_count = player_state.get('bomb_count', 4)
    player.rope_count = player_state.get('rope_count', 4)
    player.gold = player_state.get('gold', 0)

def load_next_stage(stg):
    global player, map_obj, bgm
    save_current_state()
    game_world.clear()
    map_obj.load_map(f"{stg}.csv")
    game_world.add_object(player, 1)
    if stg == 2:
        bgm = load_music('06. Old timer.mp3')
        bgm.set_volume(64)
        bgm.play()
    else:
        bgm = load_music('08. Hidden dangers.mp3')
        bgm.set_volume(64)
        bgm.play()