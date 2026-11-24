# ============================================================
#  Minha primeira IA de xadrez
#  - A biblioteca "chess" cuida só das REGRAS do jogo.
#  - Toda a parte que "pensa" (avaliação + minimax) é minha.
#
#  Para instalar a biblioteca:   pip install chess
#  Para jogar:                   python xadrez_ia.py
# ============================================================

import random
import chess

# ------------------------------------------------------------
# PASSO 1 — AVALIAÇÃO
# Olha o tabuleiro e devolve uma nota.
# Nota positiva = bom para as brancas. Negativa = bom para as pretas.
# ------------------------------------------------------------

VALOR_DAS_PECAS = {
    chess.PAWN: 1,     # peão
    chess.KNIGHT: 3,   # cavalo
    chess.BISHOP: 3,   # bispo
    chess.ROOK: 5,     # torre
    chess.QUEEN: 9,    # dama
    chess.KING: 0,     # rei (não entra na conta, ele nunca é capturado)
}


def avaliar(tabuleiro):
    nota = 0
    for casa, peca in tabuleiro.piece_map().items():
        valor = VALOR_DAS_PECAS[peca.piece_type]
        if peca.color == chess.WHITE:
            nota += valor
        else:
            nota -= valor
    return nota


# ------------------------------------------------------------
# PASSO 2 — BUSCA (MINIMAX com poda alfa-beta)
# Simula lances à frente. As brancas querem a MAIOR nota,
# as pretas querem a MENOR nota.
# ------------------------------------------------------------

def minimax(tabuleiro, profundidade, alfa, beta):
    # Fim de jogo: xeque-mate vale "infinito" para quem deu o mate.
    # Somamos a profundidade para a IA preferir o mate mais rápido.
    if tabuleiro.is_checkmate():
        if tabuleiro.turn == chess.WHITE:   # brancas levaram mate
            return -(10000 + profundidade)
        else:                               # pretas levaram mate
            return 10000 + profundidade

    # Empate (afogamento, repetição, material insuficiente...)
    if tabuleiro.is_game_over():
        return 0

    # Chegamos no limite de lances que vamos olhar: avalia e para.
    if profundidade == 0:
        return avaliar(tabuleiro)

    lances = list(tabuleiro.legal_moves)

    if tabuleiro.turn == chess.WHITE:
        melhor = float("-inf")
        for lance in lances:
            tabuleiro.push(lance)                          # faz o lance
            nota = minimax(tabuleiro, profundidade - 1, alfa, beta)
            tabuleiro.pop()                                # desfaz o lance
            melhor = max(melhor, nota)
            alfa = max(alfa, nota)
            if beta <= alfa:     # poda: as pretas nunca deixariam chegar aqui
                break
        return melhor
    else:
        melhor = float("inf")
        for lance in lances:
            tabuleiro.push(lance)
            nota = minimax(tabuleiro, profundidade - 1, alfa, beta)
            tabuleiro.pop()
            melhor = min(melhor, nota)
            beta = min(beta, nota)
            if beta <= alfa:     # poda: as brancas nunca deixariam chegar aqui
                break
        return melhor


# ------------------------------------------------------------
# PASSO 3 — ESCOLHER O LANCE
# Testa cada lance possível e fica com o de melhor nota.
# ------------------------------------------------------------

def escolher_lance(tabuleiro, profundidade):
    lances = list(tabuleiro.legal_moves)
    random.shuffle(lances)   # para não jogar sempre igual quando há empate de notas

    brancas = tabuleiro.turn == chess.WHITE
    melhor_lance = None
    melhor_nota = float("-inf") if brancas else float("inf")

    for lance in lances:
        tabuleiro.push(lance)
        nota = minimax(tabuleiro, profundidade - 1, float("-inf"), float("inf"))
        tabuleiro.pop()

        if (brancas and nota > melhor_nota) or (not brancas and nota < melhor_nota):
            melhor_nota = nota
            melhor_lance = lance

    return melhor_lance


# ------------------------------------------------------------
# PASSO 4 — JOGAR CONTRA A IA NO TERMINAL
# ------------------------------------------------------------

def ler_lance_do_jogador(tabuleiro):
    while True:
        texto = input("Seu lance: ").strip()
        if texto.lower() == "sair":
            return None
        # Aceita notação padrão (e4, Nf3, O-O) ...
        try:
            return tabuleiro.parse_san(texto)
        except ValueError:
            pass
        # ... ou origem+destino (e2e4, g1f3)
        try:
            lance = chess.Move.from_uci(texto)
            if lance in tabuleiro.legal_moves:
                return lance
        except ValueError:
            pass
        print("Lance inválido. Exemplos: e4, Nf3, O-O ou e2e4. Digite 'sair' para encerrar.")


def jogar():
    profundidade = 3   # quantos lances a IA olha à frente (4 fica mais forte, porém mais lento)

    cor = input("Você quer jogar de brancas ou pretas? (b/p): ").strip().lower()
    humano_e_branco = cor != "p"

    tabuleiro = chess.Board()

    while not tabuleiro.is_game_over():
        print()
        print(tabuleiro)
        print()

        vez_do_humano = (tabuleiro.turn == chess.WHITE) == humano_e_branco
        if vez_do_humano:
            lance = ler_lance_do_jogador(tabuleiro)
            if lance is None:
                print("Partida encerrada.")
                return
        else:
            print("IA pensando...")
            lance = escolher_lance(tabuleiro, profundidade)
            print("IA jogou:", tabuleiro.san(lance))

        tabuleiro.push(lance)

    print()
    print(tabuleiro)
    print("\nFim de jogo! Resultado:", tabuleiro.result())


if __name__ == "__main__":
    jogar()
