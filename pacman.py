# ============================================================
#  Pac-Man em Python (pygame)
#  Para instalar:  pip install pygame
#  Para jogar:     python pacman.py
#  Controles: setas do teclado. Espaço recomeça no fim do jogo.
# ============================================================

import math
import random
import pygame


# O MAPA
#  #  parede        .  ponto        o  pastilha de poder
#  -  porta da casa dos fantasmas (só fantasma passa)
#  espaço = caminho vazio

T = 20   # tamanho de cada quadradinho, em pixels

MAPA = [
    "############################",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#o####.#####.##.#####.####o#",
    "#.####.#####.##.#####.####.#",
    "#..........................#",
    "#.####.##.########.##.####.#",
    "#.####.##.########.##.####.#",
    "#......##....##....##......#",
    "######.##### ## #####.######",
    "     #.##### ## #####.#     ",
    "     #.##          ##.#     ",
    "     #.## ###--### ##.#     ",
    "######.## #      # ##.######",
    "      .   #      #   .      ",
    "######.## #      # ##.######",
    "     #.## ######## ##.#     ",
    "     #.##          ##.#     ",
    "     #.## ######## ##.#     ",
    "######.## ######## ##.######",
    "#............##............#",
    "#.####.#####.##.#####.####.#",
    "#.####.#####.##.#####.####.#",
    "#o..##................##..o#",
    "###.##.##.########.##.##.###",
    "###.##.##.########.##.##.###",
    "#......##....##....##......#",
    "#.##########.##.##########.#",
    "#.##########.##.##########.#",
    "#..........................#",
    "############################",
]

COLUNAS = len(MAPA[0])
LINHAS = len(MAPA)
ALTURA_PLACAR = 40
LARGURA_TELA = COLUNAS * T
ALTURA_TELA = LINHAS * T + ALTURA_PLACAR

VELOCIDADE = 2          # pixels por quadro (precisa dividir T sem sobrar)
TEMPO_ASSUSTADO = 7 * 60  # 7 segundos (o jogo roda a 60 quadros por segundo)
DIRECOES = [(1, 0), (-1, 0), (0, 1), (0, -1)]   # direita, esquerda, baixo, cima



# PAREDES E MOVIMENTO
# Os personagens andam de quadradinho em quadradinho.
# Só podem mudar de direção quando estão exatamente no centro de um.

def eh_parede(coluna, linha, fantasma=False):
    if linha < 0 or linha >= LINHAS:
        return True
    letra = MAPA[linha][coluna % COLUNAS]
    if letra == "#":
        return True
    if letra == "-":
        return not fantasma                  # a porta só deixa fantasma passar
    return False


def alinhado(x, y):
    return x % T == 0 and y % T == 0


def pode_ir(x, y, direcao, fantasma=False):
    dx, dy = direcao
    return not eh_parede(x // T + dx, y // T + dy, fantasma)


def andar(personagem):
    dx, dy = personagem["direcao"]
    personagem["x"] += dx * VELOCIDADE
    personagem["y"] += dy * VELOCIDADE
    # Túnel: saiu por um lado, aparece do outro
    if personagem["x"] <= -T:
        personagem["x"] = (COLUNAS - 1) * T
    elif personagem["x"] >= COLUNAS * T:
        personagem["x"] = 0



# O ESTADO DO JOGO

INICIO_PACMAN = (13, 23)
INICIO_FANTASMAS = [(13, 14, "red"), (14, 14, "pink"),
                    (12, 14, "cyan"), (15, 14, "orange")]


def novo_jogo():
    jogo = {"pontos": [], "pastilhas": [], "placar": 0, "vidas": 3,
            "estado": "jogando", "quadro": 0}
    for y, linha in enumerate(MAPA):
        for x, c in enumerate(linha):
            if c == ".":
                jogo["pontos"].append(pygame.Rect(x*T + T//2 - 2, y*T + T//2 - 2, 4, 4))
            elif c == "o":
                jogo["pastilhas"].append(pygame.Rect(x*T + T//2 - 6, y*T + T//2 - 6, 12, 12))
    posicoes_iniciais(jogo)
    return jogo


def posicoes_iniciais(jogo):
    col, lin = INICIO_PACMAN
    jogo["pacman"] = {"x": col * T, "y": lin * T, "direcao": (0, 0),
                      "desejada": (0, 0), "olhando": (1, 0)}
    jogo["fantasmas"] = []
    for i, (col, lin, cor) in enumerate(INICIO_FANTASMAS):
        jogo["fantasmas"].append({
            "x": col * T, "y": lin * T, "direcao": (0, -1), "cor": cor,
            "espera": i * 3 * 60,   # cada fantasma sai 3 segundos depois do anterior
            "assustado": 0,         # quadros que ainda faltam de susto
        })



# ATUALIZAR TUDO A CADA QUADRO

def atualizar_pacman(jogo):
    p = jogo["pacman"]
    dx, dy = p["direcao"]

    # Voltar para trás pode ser a qualquer momento
    if p["desejada"] == (-dx, -dy) and p["direcao"] != (0, 0):
        p["direcao"] = p["desejada"]

    if alinhado(p["x"], p["y"]):
        if p["desejada"] != (0, 0) and pode_ir(p["x"], p["y"], p["desejada"]):
            p["direcao"] = p["desejada"]
        if not pode_ir(p["x"], p["y"], p["direcao"]):
            p["direcao"] = (0, 0)               # bateu na parede: para

    if p["direcao"] != (0, 0):
        p["olhando"] = p["direcao"]
    andar(p)

    # Comer pontos e pastilhas
    corpo = pygame.Rect(p["x"] + T//4, p["y"] + T//4, T//2, T//2)
    for ponto in jogo["pontos"][:]:
        if corpo.colliderect(ponto):
            jogo["pontos"].remove(ponto)
            jogo["placar"] += 10
    for pastilha in jogo["pastilhas"][:]:
        if corpo.colliderect(pastilha):
            jogo["pastilhas"].remove(pastilha)
            jogo["placar"] += 50
            for f in jogo["fantasmas"]:
                f["assustado"] = TEMPO_ASSUSTADO

    if not jogo["pontos"] and not jogo["pastilhas"]:
        jogo["estado"] = "venceu"


def atualizar_fantasma(f, jogo):
    if f["espera"] > 0:
        f["espera"] -= 1
        return
    if f["assustado"] > 0:
        f["assustado"] -= 1

    if alinhado(f["x"], f["y"]):
        dx, dy = f["direcao"]
        # Fantasma não dá meia-volta, a não ser que esteja num beco sem saída
        opcoes = [d for d in DIRECOES
                  if d != (-dx, -dy) and pode_ir(f["x"], f["y"], d, fantasma=True)]
        if not opcoes:
            opcoes = [(-dx, -dy)]

        if f["assustado"] > 0 or random.random() < 0.3:
            f["direcao"] = random.choice(opcoes)     # anda sem rumo
        else:
            # Persegue: escolhe o caminho que deixa mais perto do Pac-Man
            alvo_x, alvo_y = jogo["pacman"]["x"], jogo["pacman"]["y"]
            def distancia(d):
                nx, ny = f["x"] + d[0] * T, f["y"] + d[1] * T
                return (nx - alvo_x) ** 2 + (ny - alvo_y) ** 2
            f["direcao"] = min(opcoes, key=distancia)
    andar(f)


def checar_encontros(jogo):
    p = jogo["pacman"]
    for i, f in enumerate(jogo["fantasmas"]):
        if abs(p["x"] - f["x"]) < T * 0.7 and abs(p["y"] - f["y"]) < T * 0.7:
            if f["assustado"] > 0:
                # Pac-Man come o fantasma: ele volta para a casa
                jogo["placar"] += 200
                col, lin, _ = INICIO_FANTASMAS[i]
                f.update({"x": col * T, "y": lin * T, "direcao": (0, -1),
                          "assustado": 0, "espera": 2 * 60})
            else:
                # Fantasma pega o Pac-Man
                jogo["vidas"] -= 1
                if jogo["vidas"] == 0:
                    jogo["estado"] = "perdeu"
                else:
                    posicoes_iniciais(jogo)
                return


def atualizar(jogo):
    if jogo["estado"] != "jogando":
        return
    jogo["quadro"] += 1
    atualizar_pacman(jogo)
    checar_encontros(jogo)
    for f in jogo["fantasmas"]:
        atualizar_fantasma(f, jogo)
    checar_encontros(jogo)



# DESENHAR

def desenhar(tela, fonte, jogo):
    tela.fill("black")

    # Mapa
    for y, linha in enumerate(MAPA):
        for x, c in enumerate(linha):
            if c == "#":
                pygame.draw.rect(tela, "mediumblue", (x*T, y*T, T, T))
            elif c == "-":
                pygame.draw.rect(tela, "pink", (x*T, y*T + T//2 - 2, T, 4))

    for ponto in jogo["pontos"]:
        pygame.draw.circle(tela, "wheat", ponto.center, 2)
    if (jogo["quadro"] // 15) % 2 == 0:          # pastilhas piscando
        for pastilha in jogo["pastilhas"]:
            pygame.draw.circle(tela, "wheat", pastilha.center, 6)

    # Pac-Man: um círculo amarelo com uma "fatia" preta de boca
    p = jogo["pacman"]
    cx, cy = p["x"] + T // 2, p["y"] + T // 2
    raio = T // 2 - 1
    pygame.draw.circle(tela, "yellow", (cx, cy), raio)
    abertura = math.radians(abs(jogo["quadro"] % 20 - 10) * 4)   # boca abre e fecha
    angulo = math.atan2(p["olhando"][1], p["olhando"][0])
    boca = [(cx, cy),
            (cx + (raio + 1) * math.cos(angulo - abertura), cy + (raio + 1) * math.sin(angulo - abertura)),
            (cx + (raio + 1) * math.cos(angulo + abertura), cy + (raio + 1) * math.sin(angulo + abertura))]
    pygame.draw.polygon(tela, "black", boca)

    # Fantasmas
    for f in jogo["fantasmas"]:
        cx, cy = f["x"] + T // 2, f["y"] + T // 2
        cor = f["cor"]
        if f["assustado"] > 0:
            # azul; pisca em branco nos últimos 2 segundos
            cor = "white" if f["assustado"] < 120 and (f["assustado"] // 10) % 2 else "blue"
        pygame.draw.circle(tela, cor, (cx, cy - 2), raio)
        pygame.draw.rect(tela, cor, (cx - raio, cy - 2, raio * 2, raio + 1))
        pygame.draw.circle(tela, "white", (cx - 4, cy - 3), 3)
        pygame.draw.circle(tela, "white", (cx + 4, cy - 3), 3)

    # Placar e vidas
    base = LINHAS * T
    tela.blit(fonte.render(f"Placar: {jogo['placar']}", True, "white"), (10, base + 10))
    tela.blit(fonte.render(f"Vidas: {jogo['vidas']}", True, "white"), (LARGURA_TELA - 110, base + 10))

    if jogo["estado"] != "jogando":
        texto = "VOCE VENCEU!" if jogo["estado"] == "venceu" else "FIM DE JOGO"
        msg = fonte.render(f"{texto}  (Espaco para jogar de novo)", True, "yellow")
        tela.blit(msg, msg.get_rect(center=(LARGURA_TELA // 2, LINHAS * T // 2 - 3 * T)))

    pygame.display.flip()



# O LAÇO PRINCIPAL

def main():
    pygame.init()
    tela = pygame.display.set_mode((LARGURA_TELA, ALTURA_TELA))
    pygame.display.set_caption("Pac-Man")
    relogio = pygame.time.Clock()
    fonte = pygame.font.SysFont(None, 28)
    jogo = novo_jogo()

    teclas = {pygame.K_RIGHT: (1, 0), pygame.K_LEFT: (-1, 0),
              pygame.K_DOWN: (0, 1), pygame.K_UP: (0, -1)}

    rodando = True
    while rodando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                rodando = False
            elif evento.type == pygame.KEYDOWN:
                if evento.key in teclas:
                    # guarda a direção desejada; ela vale assim que for possível virar
                    jogo["pacman"]["desejada"] = teclas[evento.key]
                elif evento.key == pygame.K_SPACE and jogo["estado"] != "jogando":
                    jogo = novo_jogo()

        atualizar(jogo)
        desenhar(tela, fonte, jogo)
        relogio.tick(60)

    pygame.quit()


if __name__ == "__main__":
    main()
