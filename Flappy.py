import os, random, datetime
import pygame

pygame.init()
LARGURA, ALTURA = 400, 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Flappy Bird")
relogio = pygame.time.Clock()
fonte = pygame.font.SysFont(None, 40)
fonte_pequena = pygame.font.SysFont(None, 26)

GRAVIDADE, PULO, VELOCIDADE = 0.5, -8, 3     # física do jogo
LARGURA_CANO, DISTANCIA = 70, 220            # largura do cano e espaço entre canos
PASSARO_X = 80

# Dificuldade: o vão começa com 160 e diminui 10 a cada 20 pontos, até no mínimo 100
VAO_INICIAL, VAO_MINIMO, DIMINUI, A_CADA = 160, 100, 10, 20

def tamanho_do_vao(pontos):
    return max(VAO_MINIMO, VAO_INICIAL - (pontos // A_CADA) * DIMINUI)

# Recorde do dia: fica num arquivo "recorde.txt" na mesma pasta do jogo,
# guardando só a data e a maior pontuação, por exemplo: 2026-11-10;37
ARQUIVO_RECORDE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recorde.txt")

def carregar_recorde():
    hoje = datetime.date.today().isoformat()
    try:
        with open(ARQUIVO_RECORDE) as arquivo:
            data, valor = arquivo.read().strip().split(";")
        return int(valor) if data == hoje else 0   # recorde de outro dia não vale
    except (OSError, ValueError):
        return 0                                    # arquivo ainda não existe

def salvar_recorde(valor):
    with open(ARQUIVO_RECORDE, "w") as arquivo:
        arquivo.write(f"{datetime.date.today().isoformat()};{valor}")

def novo_cano(x, vao):
    return {"x": x, "vao": vao, "topo": random.randint(60, ALTURA - vao - 60), "contou": False}

def reiniciar():  # y do pássaro, velocidade, canos, pontos, estado
    canos = [novo_cano(LARGURA + 100 + i * DISTANCIA, VAO_INICIAL) for i in range(3)]
    return ALTURA // 2, 0, canos, 0, "esperando"

def desenhar_passaro(x, y, vel, quadro, batendo):
    sup = pygame.Surface((50, 40), pygame.SRCALPHA)        # "folha" transparente
    pygame.draw.ellipse(sup, "gold", (5, 6, 36, 28))        # corpo
    pygame.draw.ellipse(sup, (255, 240, 170), (12, 20, 22, 12))  # barriga
    pygame.draw.ellipse(sup, "black", (5, 6, 36, 28), 2)    # contorno
    asa = (8, 22, 10)[(quadro // 4) % 3] if batendo else 15  # asa sobe e desce
    pygame.draw.ellipse(sup, "white", (3, asa, 18, 11))
    pygame.draw.ellipse(sup, "black", (3, asa, 18, 11), 2)
    pygame.draw.circle(sup, "white", (31, 14), 7)           # olho
    pygame.draw.circle(sup, "black", (31, 14), 7, 2)
    pygame.draw.circle(sup, "black", (34, 14), 3)           # pupila
    pygame.draw.polygon(sup, "orangered", [(35, 20), (48, 23), (35, 27)])  # bico
    pygame.draw.polygon(sup, "black", [(35, 20), (48, 23), (35, 27)], 2)
    angulo = max(-30, min(70, vel * 4))                     # sobe de bico para cima, cai de bico para baixo
    girado = pygame.transform.rotate(sup, -angulo)
    tela.blit(girado, girado.get_rect(center=(x, y)))

y, vel, canos, pontos, estado = reiniciar()
recorde = carregar_recorde()
novo_recorde = False
quadro = 0
rodando = True
while rodando:
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            rodando = False
        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_SPACE:
            if estado == "morto":
                y, vel, canos, pontos, estado = reiniciar()
                recorde = carregar_recorde()          # se virou o dia, o recorde zera
                novo_recorde = False
            else:
                estado, vel = "voando", PULO          # 1) PULO: velocidade para cima

    if estado == "voando":
        vel += GRAVIDADE                              # 1) GRAVIDADE: puxa para baixo
        y += vel
        passaro = pygame.Rect(PASSARO_X - 15, y - 15, 30, 30)
        for c in canos:
            c["x"] -= VELOCIDADE
            cima = pygame.Rect(c["x"], 0, LARGURA_CANO, c["topo"])
            baixo = pygame.Rect(c["x"], c["topo"] + c["vao"], LARGURA_CANO, ALTURA)
            if passaro.colliderect(cima) or passaro.colliderect(baixo):
                estado = "morto"                      # 3) COLISÃO com cano
            if not c["contou"] and c["x"] + LARGURA_CANO < PASSARO_X:
                c["contou"], pontos = True, pontos + 1  # 4) PONTO ao passar
        if canos[0]["x"] < -LARGURA_CANO:             # 2) CANO saiu da tela: cria outro
            canos.pop(0)
            canos.append(novo_cano(canos[-1]["x"] + DISTANCIA, tamanho_do_vao(pontos)))
        if y > ALTURA or y < 0:
            estado = "morto"                          # 3) COLISÃO com chão ou teto

        if estado == "morto" and pontos > recorde:    # 5) RECORDE: só grava se bateu
            recorde, novo_recorde = pontos, True
            salvar_recorde(recorde)

    tela.fill("skyblue")
    for c in canos:
        pygame.draw.rect(tela, "forestgreen", (c["x"], 0, LARGURA_CANO, c["topo"]))
        pygame.draw.rect(tela, "forestgreen", (c["x"], c["topo"] + c["vao"], LARGURA_CANO, ALTURA))
    quadro += 1
    desenhar_passaro(PASSARO_X, int(y), vel, quadro, batendo=(vel < 0 or estado == "esperando"))
    tela.blit(fonte.render(str(pontos), True, "white"), (LARGURA // 2 - 10, 30))
    tela.blit(fonte_pequena.render(f"Recorde de hoje: {recorde}", True, "white"), (10, 8))
    if estado != "voando":
        aviso = "Espaco para comecar" if estado == "esperando" else "Bateu! Espaco recomeca"
        tela.blit(fonte.render(aviso, True, "white"), (40, ALTURA // 2 + 60))
        if novo_recorde:
            tela.blit(fonte.render("NOVO RECORDE!", True, "gold"), (95, ALTURA // 2 + 100))
    pygame.display.flip()
    relogio.tick(60)
pygame.quit()
