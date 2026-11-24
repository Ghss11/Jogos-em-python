# ============================================================
#  Xadrez com janela (Tkinter)
#  - A inteligência vem do arquivo xadrez IA.py (avaliar, minimax...).
#  - Este arquivo só cuida da TELA: desenhar o tabuleiro e ler cliques.
#
#  Os dois arquivos precisam estar na MESMA pasta.
#  Para jogar:   python xadrez_janela.py
# ============================================================

import tkinter as tk
from tkinter import messagebox

import chess
from xadrez_ia import escolher_lance

##  ------------------------------------------------------------
# Configurações visuais
# ------------------------------------------------------------
TAMANHO = 72                 # tamanho de cada casa, em pixels
COR_CLARA = "#f0d9b5"
COR_ESCURA = "#b58863"
COR_SELECIONADA = "#f6f669"  # casa da peça que você clicou
COR_ULTIMO_LANCE = "#cdd26a" # casas do último lance jogado
FONTE_PECAS = ("Segoe UI Symbol", 42)
FONTE_COORD = ("Arial", 9, "bold")

# Desenho de cada peça (usamos o mesmo desenho para as duas cores
# e só mudamos a cor de preenchimento)
SIMBOLOS = {
    chess.PAWN: "♟",
    chess.KNIGHT: "♞",
    chess.BISHOP: "♝",
    chess.ROOK: "♜",
    chess.QUEEN: "♛",
    chess.KING: "♚",
}


class JogoXadrez:
    def __init__(self, janela):
        self.janela = janela
        self.janela.title("Minha IA de Xadrez")
        self.profundidade = 3   # quantos lances a IA olha à frente

        # Área onde o tabuleiro é desenhado
        self.canvas = tk.Canvas(janela, width=8 * TAMANHO, height=8 * TAMANHO,
                                highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.clique)   # chama self.clique a cada clique

        # Texto de status embaixo do tabuleiro
        self.status = tk.Label(janela, text="", font=("Arial", 13), pady=6)
        self.status.pack()

        tk.Button(janela, text="Nova partida", command=self.nova_partida).pack(pady=(0, 8))

        self.nova_partida()

    # --------------------------------------------------------
    # Começar uma partida
    # --------------------------------------------------------
    def nova_partida(self):
        self.tabuleiro = chess.Board()
        self.selecionada = None      # casa da peça que o jogador clicou
        self.ultimo_lance = None
        self.ia_pensando = False

        brancas = messagebox.askyesno(
            "Nova partida",
            "Você quer jogar de brancas?\n\n(Sim = brancas, Não = pretas)")
        self.cor_humano = chess.WHITE if brancas else chess.BLACK

        self.desenhar()
        if self.cor_humano == chess.WHITE:
            self.status.config(text="Sua vez. Clique numa peça e depois no destino.")
        else:
            self.vez_da_ia()

    # --------------------------------------------------------
    # Conversão entre casa do xadrez e posição na tela
    # (se você joga de pretas, o tabuleiro aparece de cabeça para baixo)
    # --------------------------------------------------------
    def casa_para_tela(self, casa):
        coluna = chess.square_file(casa)   # 0 = a ... 7 = h
        linha = chess.square_rank(casa)    # 0 = 1 ... 7 = 8
        if self.cor_humano == chess.WHITE:
            x, y = coluna, 7 - linha
        else:
            x, y = 7 - coluna, linha
        return x * TAMANHO, y * TAMANHO

    def tela_para_casa(self, px, py):
        x, y = px // TAMANHO, py // TAMANHO
        if not (0 <= x <= 7 and 0 <= y <= 7):
            return None
        if self.cor_humano == chess.WHITE:
            return chess.square(x, 7 - y)
        else:
            return chess.square(7 - x, y)

    # --------------------------------------------------------
    # Desenhar o tabuleiro inteiro
    # --------------------------------------------------------
    def desenhar(self):
        self.canvas.delete("all")

        for casa in chess.SQUARES:
            x, y = self.casa_para_tela(casa)
            coluna = chess.square_file(casa)
            linha = chess.square_rank(casa)

            # Cor da casa
            if casa == self.selecionada:
                cor = COR_SELECIONADA
            elif self.ultimo_lance and casa in (self.ultimo_lance.from_square,
                                                self.ultimo_lance.to_square):
                cor = COR_ULTIMO_LANCE
            elif (coluna + linha) % 2 == 0:
                cor = COR_ESCURA
            else:
                cor = COR_CLARA
            self.canvas.create_rectangle(x, y, x + TAMANHO, y + TAMANHO,
                                         fill=cor, outline="")

            # Letras (a-h) na fileira de baixo e números (1-8) na coluna da esquerda
            if y == 7 * TAMANHO:
                self.canvas.create_text(x + TAMANHO - 7, y + TAMANHO - 8,
                                        text="abcdefgh"[coluna], font=FONTE_COORD,
                                        fill="#5a3e2b")
            if x == 0:
                self.canvas.create_text(x + 7, y + 9, text=str(linha + 1),
                                        font=FONTE_COORD, fill="#5a3e2b")

            # Peça
            peca = self.tabuleiro.piece_at(casa)
            if peca:
                simbolo = SIMBOLOS[peca.piece_type]
                cx, cy = x + TAMANHO / 2, y + TAMANHO / 2 + 2
                if peca.color == chess.WHITE:
                    # contorno preto + peça branca por cima
                    for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
                        self.canvas.create_text(cx + dx, cy + dy, text=simbolo,
                                                font=FONTE_PECAS, fill="black")
                    self.canvas.create_text(cx, cy, text=simbolo,
                                            font=FONTE_PECAS, fill="white")
                else:
                    self.canvas.create_text(cx, cy, text=simbolo,
                                            font=FONTE_PECAS, fill="black")

        # Bolinhas mostrando para onde a peça selecionada pode ir
        if self.selecionada is not None:
            for lance in self.tabuleiro.legal_moves:
                if lance.from_square == self.selecionada:
                    x, y = self.casa_para_tela(lance.to_square)
                    cx, cy = x + TAMANHO / 2, y + TAMANHO / 2
                    r = 9
                    self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r,
                                            fill="#4a4a4a", outline="")

    # --------------------------------------------------------
    # O que acontece quando você clica no tabuleiro
    # --------------------------------------------------------
    def clique(self, evento):
        if self.ia_pensando or self.tabuleiro.is_game_over():
            return
        if self.tabuleiro.turn != self.cor_humano:
            return

        casa = self.tela_para_casa(evento.x, evento.y)
        if casa is None:
            return
        peca = self.tabuleiro.piece_at(casa)

        # 1º clique: escolher uma peça sua
        if self.selecionada is None:
            if peca and peca.color == self.cor_humano:
                self.selecionada = casa
                self.desenhar()
            return

        # 2º clique: tentar mover para a casa clicada
        lance = self.achar_lance(self.selecionada, casa)
        if lance:
            self.fazer_lance(lance)
            if not self.tabuleiro.is_game_over():
                self.vez_da_ia()
        elif peca and peca.color == self.cor_humano:
            self.selecionada = casa          # trocou de peça
            self.desenhar()
        else:
            self.selecionada = None          # clicou num lugar inválido: cancela
            self.desenhar()

    def achar_lance(self, origem, destino):
        for lance in self.tabuleiro.legal_moves:
            if lance.from_square == origem and lance.to_square == destino:
                # Na promoção, o peão vira dama automaticamente
                if lance.promotion is None or lance.promotion == chess.QUEEN:
                    return lance
        return None

    def fazer_lance(self, lance):
        self.tabuleiro.push(lance)
        self.ultimo_lance = lance
        self.selecionada = None
        self.desenhar()
        if self.tabuleiro.is_game_over():
            self.fim_de_jogo()

    # --------------------------------------------------------
    # Vez da IA
    # --------------------------------------------------------
    def vez_da_ia(self):
        self.ia_pensando = True
        self.status.config(text="IA pensando...")
        # espera um instante para a tela atualizar antes da IA começar a pensar
        self.janela.after(100, self.jogada_da_ia)

    def jogada_da_ia(self):
        lance = escolher_lance(self.tabuleiro, self.profundidade)
        nome = self.tabuleiro.san(lance)
        self.ia_pensando = False
        self.fazer_lance(lance)

        if not self.tabuleiro.is_game_over():
            texto = f"IA jogou {nome}. Sua vez."
            if self.tabuleiro.is_check():
                texto += "  Você está em xeque!"
            self.status.config(text=texto)

    # --------------------------------------------------------
    # Fim de jogo
    # --------------------------------------------------------
    def fim_de_jogo(self):
        if self.tabuleiro.is_checkmate():
            vencedor = not self.tabuleiro.turn   # quem NÃO está na vez deu o mate
            if vencedor == self.cor_humano:
                texto = "Xeque-mate! Você venceu!"
            else:
                texto = "Xeque-mate! A IA venceu."
        else:
            texto = "Empate!"
        self.status.config(text=texto)
        messagebox.showinfo("Fim de jogo", texto)


if __name__ == "__main__":
    janela = tk.Tk()
    janela.resizable(False, False)
    JogoXadrez(janela)
    janela.mainloop()
