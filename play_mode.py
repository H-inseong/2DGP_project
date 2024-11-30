from pico2d import *
import game_framework
import game_world
from Map import Map
from Player import Player
from enemies import Snake, Boss


def init():
    global player, map_obj, camera_x, camera_y
    player = Player(80 * 5, 80 * 4)
    game_world.add_object(player, 2)


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
    b = Boss()
    game_world.add_object(s, 1)
    game_world.add_collision_pair('Player:Monster', player, s)
    game_world.add_collision_pair('Whip:Monster', None, s)
    game_world.add_object(b,  1)
    game_world.add_collision_pair('Player:Monster', player, b)
    game_world.add_collision_pair('Whip:Monster', None, b)

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
        elif event.type == pico2d.SDL_KEYDOWN:

            if event.key == pico2d.SDLK_ESCAPE:
                game_framework.quit()

            elif event.key == pico2d.SDLK_o:  # 'o' 키로 저장
                map_obj.save_map("current_map.csv")
            elif event.key == pico2d.SDLK_p:  # 'p' 키로 로드
                map_obj.load_map("current_map.csv")

            elif event.key == pico2d.SDLK_UP:
                if player.move_stage:  # door 위에서 위쪽 화살표 입력
                    load_next_stage()
                player.handle_event(event)
            else:
                player.handle_event(event)
        elif event.type == pico2d.SDL_MOUSEBUTTONDOWN:
             mouse_x, mouse_y = event.x, 960 - event.y  # 화면 좌표를 맵 좌표로 변환

             world_x = camera_x + mouse_x
             world_y = camera_y + mouse_y

             tile_x = world_x // 80
             tile_y = world_y // 80

             if event.button == 1:  # 왼쪽 마우스 버튼 클릭
                 set_solid_tile(tile_x, tile_y, 'solid')
             elif event.button == 3:  # 오른쪽 마우스 버튼 클릭 (선택 사항)
                 set_solid_tile(tile_x, tile_y, 'empty')
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
            else:
                break

def set_solid_tile(x, y, tile_type):
    global map_obj
    tile = map_obj.tiles[(x, y)]
        # 변경 가능한 타일 타입을 명확히 지정 (예: 'empty', 'spike', 'rope', 'rope_head' 등)
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
    player.hp = player_state.get('hp', 40)
    player.bomb_count = player_state.get('bomb_count', 4)
    player.rope_count = player_state.get('rope_count', 4)
    player.gold = player_state.get('gold', 0)

def load_next_stage():
    global player, map_obj
    save_current_state()
    game_world.clear()
    map_obj = Map(46, 38)
    player.x, player.y = 240, 240
    game_world.add_object(player, 1)