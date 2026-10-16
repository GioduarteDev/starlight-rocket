try:
    import pygame  # type: ignore[import-not-found]
except ModuleNotFoundError:
    pygame = None

import math
import random

random.seed(7)

if pygame is not None:
    pygame.init()

    # ============================================================
    # TELA
    # ============================================================
    tela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Starlight Rocket")
    LARGURA, ALTURA = tela.get_size()
    clock = pygame.time.Clock()

    # ============================================================
    # FÍSICA
    # ============================================================
    FPS = 60
    DT = 1 / 60
    GRAVIDADE = 9.8
    MASSA_FOGUETE = 100_000.0
    COMBUSTIVEL_INICIAL = 100_000.0
    CONSUMO_POR_FRAME = COMBUSTIVEL_INICIAL * 0.001  # 100 kg/frame
    EMPUXO = 2_000_000.0  # 2 x 10^6 N: hipótese temporária; expoente ilegível no enunciado.

    # ============================================================
    # MUNDO / JOGO
    # ============================================================
    PIXELS_POR_METRO = 12
    SOLO_BASE_Y = ALTURA - 98
    RAIO_FOGUETE = 1.8
    RAIO_ESTRELA = 1.2
    GOAL_ESTRELAS_FASE_2 = 3

    # ============================================================
    # CORES
    # ============================================================
    NAVY_1 = (6, 10, 28)
    NAVY_3 = (36, 48, 94)
    HORIZON = (76, 94, 156)
    WHITE = (240, 244, 255)
    SOFT_WHITE = (215, 225, 245)
    YELLOW = (255, 220, 90)
    GOLD = (255, 195, 70)
    CYAN = (115, 210, 255)
    RED = (228, 92, 118)
    PINK = (246, 130, 170)
    GREEN = (70, 200, 110)
    LIME = (125, 230, 120)
    PANEL = (8, 12, 24, 188)

    # ============================================================
    # FONTES
    # ============================================================
    fonte_titulo = pygame.font.SysFont("georgia", 58, bold=True)
    fonte_subtitulo = pygame.font.SysFont("georgia", 28, bold=True)
    fonte_grande = pygame.font.SysFont("consolas", 34, bold=True)
    fonte = pygame.font.SysFont("consolas", 20)
    fonte_pequena = pygame.font.SysFont("consolas", 17)
    fonte_crawl = pygame.font.SysFont("georgia", 25, bold=True)

    # ============================================================
    # FUNÇÕES AUXILIARES
    # ============================================================
    def distancia(x1, y1, x2, y2):
        return math.hypot(x2 - x1, y2 - y1)

    def mundo_para_tela(x_m, y_m, camera_x, camera_y):
        sx = LARGURA // 2 + (x_m - camera_x) * PIXELS_POR_METRO
        sy = SOLO_BASE_Y - (y_m - camera_y) * PIXELS_POR_METRO
        return int(sx), int(sy)

    def calcular_camera(estado):
        camera_y = max(0.0, estado["y"] - 30.0)
        if estado["x"] > 28.0:
            camera_x = estado["x"] - 28.0
        elif estado["x"] < -28.0:
            camera_x = estado["x"] + 28.0
        else:
            camera_x = 0.0
        return camera_x, camera_y

    def novo_voo():
        return {
            "x": 0.0,
            "y": 22.0,
            "vx": 0.0,
            "vy": 0.0,
            "ax": 0.0,
            "ay": 0.0,
            "combustivel": COMBUSTIVEL_INICIAL,
            "angulo": 0,
            "tempo_fase": 0.0,
        }

    def criar_estrelas_fase_2():
        posicoes = [
            (-11.0, 25.0), (0.0, 27.0), (11.0, 30.0),
            (-16.0, 36.0), (7.0, 39.0), (-4.0, 45.0),
            (14.0, 50.0), (-13.0, 56.0), (2.0, 61.0),
            (16.0, 68.0), (-8.0, 74.0), (9.0, 80.0),
        ]
        return [{"x": x, "y": y, "coletada": False} for x, y in posicoes]

    def criar_explosao(x, y, cor1=(255, 235, 120), cor2=(255, 255, 210), quantidade=18):
        particulas = []
        for i in range(quantidade):
            ang = (math.pi * 2 / quantidade) * i
            vel = random.uniform(0.8, 2.3)
            particulas.append(
                {
                    "x": x,
                    "y": y,
                    "vx": math.cos(ang) * vel,
                    "vy": math.sin(ang) * vel,
                    "vida": random.randint(18, 30),
                    "vida_max": 30,
                    "tamanho": random.randint(2, 4),
                    "cor1": cor1,
                    "cor2": cor2,
                }
            )
        return particulas

    def atualizar_particulas(particulas):
        for p in particulas[:]:
            p["x"] += p["vx"] * DT * 18
            p["y"] += p["vy"] * DT * 18
            p["vida"] -= 1
            if p["vida"] <= 0:
                particulas.remove(p)

    # ============================================================
    # CENÁRIO / FUNDO
    # ============================================================
    estrelas_fundo = []
    for _ in range(110):
        estrelas_fundo.append(
            {
                "x": random.randint(0, LARGURA),
                "y": random.randint(0, ALTURA),
                "r": random.randint(1, 2),
                "twinkle": random.randint(0, 120),
            }
        )

    aliens_decorativos = [
        {"x": 170, "y": 180},
        {"x": 420, "y": 120},
        {"x": 970, "y": 135},
        {"x": 1280, "y": 220},
        {"x": 1540, "y": 175},
        {"x": 1740, "y": 100},
    ]

    planetas = [
        {"x": LARGURA - 190, "y": 145, "r": 78, "cor": (220, 225, 250), "anel": False},
        {"x": 220, "y": 260, "r": 42, "cor": (255, 145, 180), "anel": False},
        {"x": 1230, "y": 300, "r": 54, "cor": (90, 180, 255), "anel": True},
        {"x": 1560, "y": 360, "r": 30, "cor": (245, 205, 120), "anel": False},
    ]

    def desenhar_aliens(frame_count):
        for alien in aliens_decorativos:
            flutuar = int(6 * math.sin((frame_count + alien["x"]) * 0.04))
            x = alien["x"]
            y = alien["y"] + flutuar
            pygame.draw.ellipse(tela, (160, 180, 215), (x - 22, y + 8, 44, 12))
            pygame.draw.ellipse(tela, (110, 235, 195), (x - 14, y, 28, 16))
            pygame.draw.ellipse(tela, (70, 160, 205), (x - 18, y + 6, 36, 10), 1)
            pygame.draw.circle(tela, (135, 255, 140), (x, y + 5), 5)
            pygame.draw.circle(tela, NAVY_1, (x - 2, y + 4), 1)
            pygame.draw.circle(tela, NAVY_1, (x + 2, y + 4), 1)
            pygame.draw.line(tela, (135, 255, 140), (x - 2, y - 1), (x - 5, y - 6), 1)
            pygame.draw.line(tela, (135, 255, 140), (x + 2, y - 1), (x + 5, y - 6), 1)

    def desenhar_background(frame_count):
        for y in range(ALTURA):
            t = y / ALTURA
            r = int(NAVY_1[0] * (1 - t) + HORIZON[0] * (t * 0.50) + NAVY_3[0] * (t * 0.50))
            g = int(NAVY_1[1] * (1 - t) + HORIZON[1] * (t * 0.50) + NAVY_3[1] * (t * 0.50))
            b = int(NAVY_1[2] * (1 - t) + HORIZON[2] * (t * 0.50) + NAVY_3[2] * (t * 0.50))
            pygame.draw.line(tela, (r, g, b), (0, y), (LARGURA, y))

        for planeta in planetas:
            brilho = int(3 * math.sin((frame_count + planeta["x"]) * 0.02))
            pygame.draw.circle(tela, planeta["cor"], (planeta["x"], planeta["y"]), planeta["r"])
            pygame.draw.circle(tela, (255, 255, 255), (planeta["x"] - planeta["r"] // 4, planeta["y"] - planeta["r"] // 4), max(2, planeta["r"] // 10))
            if planeta["anel"]:
                pygame.draw.ellipse(tela, (215, 235, 255), (planeta["x"] - planeta["r"] - 8, planeta["y"] - 10 + brilho, planeta["r"] * 2 + 16, 18), 2)

        for estrela in estrelas_fundo:
            intensidade = 210 + int(40 * math.sin((frame_count + estrela["twinkle"]) * 0.06))
            cor = (intensidade, intensidade, min(255, intensidade + 10))
            pygame.draw.circle(tela, cor, (estrela["x"], estrela["y"]), estrela["r"])

        desenhar_aliens(frame_count)

        sparkles = [(160, 130), (350, 200), (720, 110), (1050, 160), (1420, 120), (1650, 240)]
        for sx, sy in sparkles:
            tam = 8 + int(2 * math.sin((frame_count + sx) * 0.05))
            pygame.draw.line(tela, (255, 245, 180), (sx - tam, sy), (sx + tam, sy), 1)
            pygame.draw.line(tela, (255, 245, 180), (sx, sy - tam), (sx, sy + tam), 1)

    def desenhar_chao(camera_y):
        solo_tela_y = int(SOLO_BASE_Y + camera_y * PIXELS_POR_METRO)
        if solo_tela_y < ALTURA:
            pygame.draw.rect(tela, (20, 30, 32), (0, solo_tela_y, LARGURA, ALTURA - solo_tela_y))
            pygame.draw.rect(tela, (40, 120, 52), (0, solo_tela_y - 8, LARGURA, 10))
            pygame.draw.line(tela, (130, 235, 115), (0, solo_tela_y - 3), (LARGURA, solo_tela_y - 3), 2)

            for i in range(0, LARGURA, 34):
                h = 8 + (i // 34) % 4
                pygame.draw.line(tela, GREEN, (i, solo_tela_y - 2), (i + 2, solo_tela_y - h), 2)
                pygame.draw.line(tela, LIME, (i + 5, solo_tela_y - 2), (i + 7, solo_tela_y - h - 3), 2)

    # ============================================================
    # DESENHO DE OBJETOS
    # ============================================================
    def desenhar_estrela(x, y, camera_x, camera_y):
        sx, sy = mundo_para_tela(x, y, camera_x, camera_y)
        pontos = []
        for i in range(10):
            ang = math.radians(-90 + i * 36)
            raio = 13 if i % 2 == 0 else 6
            pontos.append((int(sx + math.cos(ang) * raio), int(sy + math.sin(ang) * raio)))
        pygame.draw.polygon(tela, GOLD, pontos)
        pygame.draw.circle(tela, (255, 245, 180), (sx, sy), 3)

    def desenhar_particulas(particulas, camera_x, camera_y):
        for p in particulas:
            px, py = mundo_para_tela(p["x"], p["y"], camera_x, camera_y)
            alpha = int(255 * (p["vida"] / p["vida_max"]))
            surf = pygame.Surface((22, 22), pygame.SRCALPHA)
            pygame.draw.circle(surf, (*p["cor1"], alpha), (11, 11), p["tamanho"])
            pygame.draw.circle(surf, (*p["cor2"], max(0, alpha - 40)), (11, 11), max(1, p["tamanho"] - 1))
            tela.blit(surf, surf.get_rect(center=(px, py)))

    def criar_sprite_foguete(motor_ligado):
        superficie = pygame.Surface((120, 190), pygame.SRCALPHA)

        if motor_ligado:
            pygame.draw.circle(superficie, (255, 140, 20, 60), (60, 150), 24)
            pygame.draw.circle(superficie, (255, 210, 70, 90), (60, 148), 18)
            pygame.draw.polygon(superficie, (255, 140, 30), [(46, 138), (74, 138), (60, 182)])
            pygame.draw.polygon(superficie, (255, 200, 55), [(49, 138), (71, 138), (60, 168)])
            pygame.draw.polygon(superficie, (255, 250, 185), [(53, 138), (67, 138), (60, 156)])

        pygame.draw.polygon(superficie, RED, [(45, 103), (16, 143), (49, 127)])
        pygame.draw.polygon(superficie, RED, [(75, 103), (104, 143), (71, 127)])
        pygame.draw.rect(superficie, (232, 236, 248), (41, 42, 38, 96), border_radius=17)
        pygame.draw.rect(superficie, (189, 200, 223), (41, 42, 10, 96), border_radius=8)
        pygame.draw.rect(superficie, (248, 251, 255), (61, 52, 6, 64), border_radius=2)
        pygame.draw.polygon(superficie, PINK, [(60, 9), (41, 52), (79, 52)])
        pygame.draw.circle(superficie, (78, 192, 255), (60, 73), 12)
        pygame.draw.circle(superficie, (200, 240, 255), (55, 68), 4)
        pygame.draw.rect(superficie, (95, 105, 125), (49, 130, 22, 10), border_radius=2)
        return superficie

    # ============================================================
    # UI
    # ============================================================
    def desenhar_banner_fase(fase):
        nomes = {
            1: "NÍVEL 1  •  VOO DE TESTE",
            2: "NÍVEL 2  •  BUSQUE 3 ESTRELINHAS",
        }
        caixa = pygame.Surface((640, 74), pygame.SRCALPHA)
        pygame.draw.rect(caixa, (8, 12, 24, 220), (0, 0, 640, 74), border_radius=18)
        pygame.draw.rect(caixa, (115, 155, 255, 255), (0, 0, 640, 74), 2, border_radius=18)
        texto = fonte_subtitulo.render(nomes[fase], True, WHITE)
        caixa.blit(texto, texto.get_rect(center=(320, 37)))
        tela.blit(caixa, caixa.get_rect(center=(LARGURA // 2, 82)))

    def desenhar_hud(estado, score_total, fase):
        painel = pygame.Surface((420, 352), pygame.SRCALPHA)
        pygame.draw.rect(painel, PANEL, (0, 0, 420, 352), border_radius=18)
        pygame.draw.rect(painel, (105, 135, 210, 140), (0, 0, 420, 352), 1, border_radius=18)
        tela.blit(painel, (22, 22))

        titulo = fonte_grande.render(f"NÍVEL {fase}", True, WHITE)
        tela.blit(titulo, (40, 38))

        massa_atual = MASSA_FOGUETE + estado["combustivel"]
        linhas = [
            f"Tempo no ar:   {score_total:.2f} s",
            f"Altitude:      {estado['y']:.2f} m",
            f"Posição X:     {estado['x']:.2f} m",
            f"Velocidade X:  {estado['vx']:.2f} m/s",
            f"Velocidade Y:  {estado['vy']:.2f} m/s",
            f"Aceleração X:  {estado['ax']:.2f} m/s²",
            f"Aceleração Y:  {estado['ay']:.2f} m/s²",
            f"Combustível:   {estado['combustivel'] / 1000:.1f} t",
            f"Massa total:   {massa_atual / 1000:.1f} t",
            f"Ângulo:        {estado['angulo']}°",
        ]
        for i, texto in enumerate(linhas):
            tela.blit(fonte.render(texto, True, SOFT_WHITE), (42, 82 + i * 22))

        bx, by, bw, bh = 42, 315, 300, 12
        pygame.draw.rect(tela, (45, 55, 82), (bx, by, bw, bh), border_radius=8)
        proporcao = estado["combustivel"] / COMBUSTIVEL_INICIAL
        pygame.draw.rect(tela, (110, 210, 255), (bx, by, int(bw * proporcao), bh), border_radius=8)
        tela.blit(fonte_pequena.render("Fuel", True, SOFT_WHITE), (bx, by - 18))

    def desenhar_controles():
        texto = fonte_pequena.render(
            "W/SPACE = PROPULSÃO   •   A/D ou ←/→ = 30°   •   R = REINICIAR   •   ESC = SAIR",
            True,
            (210, 215, 230),
        )
        tela.blit(texto, texto.get_rect(center=(LARGURA // 2, ALTURA - 28)))

    linhas_crawl = [
        "STARLIGHT ROCKET",
        "",
        "Resumo da missão:",
        "Foguete no ar e gravidade constante.",
        "W/SPACE ativa a propulsão.",
        "A/D ou setas inclinam 30°.",
        "Nível 1: sobreviva por 5 segundos.",
        "Nível 2: pegue 3 estrelas.",
        "Pressione ENTER para continuar.",
    ]

    def desenhar_intro(frame_count, offset_y):
        desenhar_background(frame_count)
        titulo = fonte_subtitulo.render("ST★RLIGHT ROCKET", True, CYAN)
        tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 110)))
        centro_x = LARGURA // 2
        base_y = ALTURA + offset_y - 130
        for i, linha in enumerate(linhas_crawl):
            y = base_y + i * 40
            if -80 < y < ALTURA + 120:
                progresso = 1 - max(0, min(1, y / ALTURA))
                escala = 0.55 + progresso * 0.32
                texto = fonte_crawl.render(linha, True, YELLOW)
                texto = pygame.transform.rotozoom(texto, 0, escala)
                tela.blit(texto, texto.get_rect(center=(centro_x, int(y))))

    def desenhar_menu(frame_count):
        desenhar_background(frame_count)
        pygame.draw.circle(tela, (28, 48, 95), (LARGURA // 2, 200), 170)
        titulo = fonte_titulo.render("STARLIGHT ROCKET", True, WHITE)
        subtitulo = fonte_subtitulo.render("anime night mission", True, (175, 205, 255))
        tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, 180)))
        tela.blit(subtitulo, subtitulo.get_rect(center=(LARGURA // 2, 228)))

        sprite = criar_sprite_foguete(True)
        sprite = pygame.transform.rotozoom(sprite, -18, 1.52)
        tela.blit(sprite, sprite.get_rect(center=(LARGURA // 2, 345)))

        caixa = pygame.Surface((780, 250), pygame.SRCALPHA)
        pygame.draw.rect(caixa, (8, 12, 24, 190), (0, 0, 780, 250), border_radius=22)
        pygame.draw.rect(caixa, (105, 145, 230, 120), (0, 0, 780, 250), 2, border_radius=22)
        tela.blit(caixa, caixa.get_rect(center=(LARGURA // 2, 585)))

        textos = [
            "NÍVEL 1  •  permaneça no ar por 5 segundos",
            "NÍVEL 2  •  colete 3 estrelas espalhadas",
            "",
            "A física permanece igual em todas as fases.",
            "ENTER = começar missão",
        ]
        for i, linha in enumerate(textos):
            cor = WHITE if i < 2 else SOFT_WHITE
            render = fonte.render(linha, True, cor)
            tela.blit(render, render.get_rect(center=(LARGURA // 2, 505 + i * 25)))

    def desenhar_game_over(score_total, frame_count):
        desenhar_background(frame_count)
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        tela.blit(overlay, (0, 0))
        titulo = fonte_titulo.render("FIM DE JOGO!", True, (255, 130, 150))
        score = fonte_subtitulo.render(f"Tempo total no ar: {score_total:.2f} s", True, WHITE)
        dica = fonte.render("Pressione R para reiniciar ou ESC para sair", True, SOFT_WHITE)
        tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, ALTURA // 2 - 70)))
        tela.blit(score, score.get_rect(center=(LARGURA // 2, ALTURA // 2)))
        tela.blit(dica, dica.get_rect(center=(LARGURA // 2, ALTURA // 2 + 58)))

    def desenhar_vitoria(score_total, frame_count):
        desenhar_background(frame_count)
        overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        tela.blit(overlay, (0, 0))
        titulo = fonte_titulo.render("MISSÃO CONCLUÍDA!", True, YELLOW)
        score = fonte_subtitulo.render(f"Tempo total no ar: {score_total:.2f} s", True, WHITE)
        dica = fonte.render("Pressione R para jogar novamente", True, SOFT_WHITE)
        tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, ALTURA // 2 - 70)))
        tela.blit(score, score.get_rect(center=(LARGURA // 2, ALTURA // 2)))
        tela.blit(dica, dica.get_rect(center=(LARGURA // 2, ALTURA // 2 + 58)))

    # ============================================================
    # ESTADO INICIAL
    # ============================================================
    estado_tela = "INTRO"  # INTRO, MENU, LEVEL_INTRO, PLAYING, GAME_OVER, WIN
    intro_offset_y = 0
    fase = 1
    estado = novo_voo()
    estrelas_fase_2 = criar_estrelas_fase_2()
    particulas = []
    tempo_acumulado = 0.0
    level_intro_timer = 0
    frame_count = 0

    def resetar_missao():
        global fase, estado, estrelas_fase_2, tempo_acumulado
        global level_intro_timer, estado_tela
        fase = 1
        estado = novo_voo()
        estrelas_fase_2 = criar_estrelas_fase_2()
        particulas.clear()
        tempo_acumulado = 0.0
        level_intro_timer = 140
        estado_tela = "LEVEL_INTRO"

    # ============================================================
    # LOOP PRINCIPAL
    # ============================================================
    rodando = True
    while rodando:
        clock.tick(FPS)
        frame_count += 1
        motor_ligado = False

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    rodando = False

                if estado_tela == "INTRO" and evento.key == pygame.K_RETURN:
                    estado_tela = "MENU"

                elif estado_tela == "MENU" and evento.key == pygame.K_RETURN:
                    resetar_missao()

                elif evento.key == pygame.K_r and estado_tela in (
                    "GAME_OVER", "WIN", "PLAYING", "LEVEL_INTRO"
                ):
                    resetar_missao()

        atualizar_particulas(particulas)

        if estado_tela == "INTRO":
            intro_offset_y -= 1.2
            if intro_offset_y < -ALTURA - 100:
                estado_tela = "MENU"

        if estado_tela == "LEVEL_INTRO":
            level_intro_timer -= 1
            if level_intro_timer <= 0:
                estado_tela = "PLAYING"

        elif estado_tela == "PLAYING":
            teclas = pygame.key.get_pressed()
            if teclas[pygame.K_a] or teclas[pygame.K_LEFT]:
                estado["angulo"] = -30
            elif teclas[pygame.K_d] or teclas[pygame.K_RIGHT]:
                estado["angulo"] = 30
            else:
                estado["angulo"] = 0

            motor_ligado = (teclas[pygame.K_w] or teclas[pygame.K_SPACE]) and estado["combustivel"] > 0
            massa_total = MASSA_FOGUETE + estado["combustivel"]

            forca_x = 0.0
            forca_y = -massa_total * GRAVIDADE
            if motor_ligado:
                angulo_rad = math.radians(estado["angulo"])
                forca_x += EMPUXO * math.sin(angulo_rad)
                forca_y += EMPUXO * math.cos(angulo_rad)
                estado["combustivel"] -= CONSUMO_POR_FRAME
                if estado["combustivel"] < 0:
                    estado["combustivel"] = 0.0

            estado["ax"] = forca_x / massa_total
            estado["ay"] = forca_y / massa_total
            estado["vx"] += estado["ax"] * DT
            estado["vy"] += estado["ay"] * DT
            estado["x"] += estado["vx"] * DT
            estado["y"] += estado["vy"] * DT
            estado["tempo_fase"] += DT

            if estado["y"] <= 0:
                estado["y"] = 0.0
                estado["vx"] = estado["vy"] = 0.0
                estado["ax"] = estado["ay"] = 0.0
                estado_tela = "GAME_OVER"

            if estado_tela == "PLAYING":
                if fase == 1:
                    if estado["tempo_fase"] >= 5.0 - 1e-12:
                        tempo_acumulado += estado["tempo_fase"]
                        fase = 2
                        estado = novo_voo()
                        particulas.clear()
                        estrelas_fase_2 = criar_estrelas_fase_2()
                        level_intro_timer = 140
                        estado_tela = "LEVEL_INTRO"

                elif fase == 2:
                    for estrela in estrelas_fase_2:
                        if estrela["coletada"]:
                            continue
                        d = distancia(estado["x"], estado["y"], estrela["x"], estrela["y"])
                        if d <= RAIO_FOGUETE + RAIO_ESTRELA:
                            estrela["coletada"] = True
                            particulas.extend(criar_explosao(estrela["x"], estrela["y"]))

                    coletadas = sum(1 for e in estrelas_fase_2 if e["coletada"])
                    if coletadas >= GOAL_ESTRELAS_FASE_2:
                        estado_tela = "WIN"

        camera_x, camera_y = calcular_camera(estado)
        score_total = tempo_acumulado + estado["tempo_fase"]

        if estado_tela == "INTRO":
            desenhar_intro(frame_count, intro_offset_y)

        elif estado_tela == "MENU":
            desenhar_menu(frame_count)

        elif estado_tela in ("LEVEL_INTRO", "PLAYING"):
            desenhar_background(frame_count)
            desenhar_chao(camera_y)

            if fase == 2:
                for estrela in estrelas_fase_2:
                    if not estrela["coletada"]:
                        desenhar_estrela(estrela["x"], estrela["y"], camera_x, camera_y)

            desenhar_particulas(particulas, camera_x, camera_y)

            foguete_x, foguete_y = mundo_para_tela(estado["x"], estado["y"], camera_x, camera_y)
            sprite = criar_sprite_foguete(motor_ligado)
            sprite_rot = pygame.transform.rotozoom(sprite, -estado["angulo"], 1.18)
            tela.blit(sprite_rot, sprite_rot.get_rect(center=(foguete_x, foguete_y)))

            desenhar_hud(estado, score_total, fase)
            desenhar_controles()

            if fase == 1:
                objetivo = "Objetivo: permanecer no ar por 5 segundos"
            elif fase == 2:
                coletadas = sum(1 for e in estrelas_fase_2 if e["coletada"])
                objetivo = f"Objetivo: buscar estrelinhas ({coletadas}/{GOAL_ESTRELAS_FASE_2})"
            img_obj = fonte.render(objetivo, True, YELLOW)
            tela.blit(img_obj, img_obj.get_rect(center=(LARGURA // 2, 135)))

            if estado_tela == "LEVEL_INTRO":
                desenhar_banner_fase(fase)

        elif estado_tela == "GAME_OVER":
            desenhar_game_over(score_total, frame_count)

        elif estado_tela == "WIN":
            desenhar_vitoria(score_total, frame_count)
            desenhar_particulas(particulas, camera_x, camera_y)

        pygame.display.flip()

    pygame.quit()

else:
    print("Pygame não está instalado. Instale pygame-ce para executar a simulação.")
