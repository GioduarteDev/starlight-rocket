import ast
import math
import os
from pathlib import Path
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import pygame

source = Path('main.py').read_text(encoding='utf-8')
tree = ast.parse(source)
block = next(n for n in tree.body if isinstance(n, ast.If))
loop = next(n for n in block.body if isinstance(n, ast.While))
setup = ast.Module(body=tree.body[:tree.body.index(block)] + block.body[:block.body.index(loop)], type_ignores=[])
ns = {}
exec(compile(setup, 'main.py', 'exec'), ns)
step = compile(ast.Module(body=loop.body, type_ignores=[]), 'main.py', 'exec')
class Clock:
    def tick(self, fps):
        return 0
ns['clock'] = Clock()
pressed = set()
class Keys:
    def __getitem__(self, key):
        return key in pressed
pygame.key.get_pressed = lambda: Keys()
def frame(*keys):
    pressed.clear()
    pressed.update(keys)
    exec(step, ns)
def fresh():
    ns['resetar_missao']()
    ns['estado_tela'] = 'PLAYING'
    return ns['estado']
def close(a, b):
    assert math.isclose(a, b, abs_tol=1e-9), (a, b)

assert ns['DT'] == 1/60 and ns['GRAVIDADE'] == 9.8
assert ns['MASSA_FOGUETE'] == ns['COMBUSTIVEL_INICIAL'] == 100000
s = fresh()
assert s['y'] > 0 and s['vx'] == s['vy'] == 0
frame()
close(s['ay'], -9.8)
assert s['y'] < 22 and s['combustivel'] == 100000
for key in (pygame.K_SPACE, pygame.K_w):
    s = fresh()
    frame(key)
    close(s['ay'], 0.2)
    assert s['combustivel'] == 99900
    old_ay = s['ay']
    frame(key)
    assert s['ay'] > old_ay and s['combustivel'] == 99800
for key, angle in ((pygame.K_a, -30), (pygame.K_LEFT, -30), (pygame.K_d, 30), (pygame.K_RIGHT, 30)):
    s = fresh()
    frame(pygame.K_w, key)
    assert s['angulo'] == angle
    close(s['ax'], 10 * math.sin(math.radians(angle)))
    close(s['ay'], 10 * math.cos(math.radians(angle)) - 9.8)
    assert s['x'] * angle > 0
s = fresh()
s['combustivel'] = 50
frame(pygame.K_SPACE)
assert s['combustivel'] == 0
frame(pygame.K_SPACE)
close(s['ay'], -9.8)
s = fresh()
s['y'] = 0.00001
frame()
assert ns['estado_tela'] == 'GAME_OVER' and s['y'] == s['vx'] == s['vy'] == 0
s = fresh()
for _ in range(299):
    frame(pygame.K_SPACE)
assert ns['fase'] == 1
frame(pygame.K_SPACE)
assert ns['fase'] == 2 and ns['estado_tela'] == 'LEVEL_INTRO'
close(ns['tempo_acumulado'], 5)
ns['estado_tela'] = 'PLAYING'
s = ns['estado']
for i in range(3):
    star = ns['estrelas_fase_2'][i]
    s.update(x=star['x'], y=star['y'], vx=0, vy=0)
    frame(pygame.K_SPACE)
    assert ns['estado_tela'] == ('WIN' if i == 2 else 'PLAYING')
assert sum(e['coletada'] for e in ns['estrelas_fase_2']) == 3
assert ns['particulas']
score = ns['score_total']
frame()
assert ns['score_total'] == score
pygame.event.post(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_r))
frame()
assert ns['fase'] == 1 and ns['estado_tela'] == 'LEVEL_INTRO'
assert ns['estado'] == ns['novo_voo']() and not ns['particulas']
assert ns['score_total'] == 0 and not any(e['coletada'] for e in ns['estrelas_fase_2'])
for screen in ('INTRO', 'MENU', 'GAME_OVER', 'WIN'):
    ns['estado_tela'] = screen
    frame()
for forbidden in ('fase == 3', 'fase == 4', 'meteoro', 'tiro', 'K_f', 'cooldown', 'fase_3', 'fase_4'):
    assert forbidden.casefold() not in source.casefold(), forbidden
pygame.quit()
print('OK: fisica, controles, combustivel, solo, transicao em 300 passos, vitoria com 3 estrelas, score, reinicio e renderizacao de todas as telas.')
