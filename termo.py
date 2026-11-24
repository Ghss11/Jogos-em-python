# ============================================================
#  Meu Termo em Python
#  Para jogar:   python termo.py
#  Não precisa instalar nada: o Tkinter já vem com o Python.
# ============================================================

import random
import unicodedata
import tkinter as tk
from tkinter import messagebox


# A LISTA DE PALAVRAS
# Escritas sem acento, em maiúsculas. Você pode acrescentar as suas.

PALAVRAS = [
    "AMIGO", "AREIA", "BANCO", "BARCO", "BLOCO", "BOLSA", "CABRA", "CAMPO",
    "CANTO", "CARRO", "CARTA", "CERCA", "CERTO", "CHAVE", "CHUVA", "CINCO",
    "CLIMA", "CORPO", "CURSO", "DENTE", "DISCO", "FESTA", "FILHO", "FOLHA",
    "FORCA", "FORNO", "FRUTA", "GARFO", "GENTE", "GOLPE", "GRUPO", "HOTEL",
    "LAPIS", "LIMAO", "LINHA", "LIVRO", "MAIOR", "MANGA", "MARCO", "METRO",
    "MILHO", "MOTOR", "MUNDO", "NIVEL", "NOITE", "PADRE", "PALCO", "PAPEL",
    "PARTE", "PASTA", "PEDRA", "PEIXE", "PIANO", "PLANO", "POLVO", "PONTE",
    "PORTA", "PRAIA", "PRATO", "PRAZO", "PRETO", "PRIMO", "QUEDA", "RELVA",
    "RISCO", "ROUPA", "SABOR", "SALTO", "SELVA", "SINAL", "SONHO", "SORTE",
    "TARDE", "TECLA", "TEMPO", "TERRA", "TIGRE", "TINTA", "TORRE", "TREVO",
    "TRIGO", "VALOR", "VELHO", "VENTO", "VERDE", "VIDRO", "VIOLA", "VISTA",
    "ZEBRA",
]

TENTATIVAS = 6
LETRAS = 5


def comparar(chute, secreta):
    resultado = ["preto"] * LETRAS
    sobrando = list(secreta)

    # 1ª passada: letras no lugar certo = verde
    for i in range(LETRAS):
        if chute[i] == secreta[i]:
            resultado[i] = "verde"
            sobrando[i] = None

    # 2ª passada: letras que existem, mas em outro lugar = amarelo
    for i in range(LETRAS):
        if resultado[i] != "verde" and chute[i] in sobrando:
            resultado[i] = "amarelo"
            sobrando[sobrando.index(chute[i])] = None   # gasta essa letra

    return resultado


def sem_acento(texto):
    """Transforma 'ç' em 'C', 'ã' em 'A' etc."""
    decomposto = unicodedata.normalize("NFD", texto)
    return "".join(c for c in decomposto if unicodedata.category(c) != "Mn").upper()



# A JANELA

COR_FUNDO = "#6e5c62"
COR_VAZIO = "#615458"
COR_TECLA = "#4c4347"
CORES = {"verde": "#3aa394", "amarelo": "#d3ad69", "preto": "#312a2c"}
PRIORIDADE = {"preto": 1, "amarelo": 2, "verde": 3}   # para colorir o teclado


class Termo:
    def __init__(self, janela):
        self.janela = janela
        janela.title("Termo")
        janela.configure(bg=COR_FUNDO, padx=20, pady=15)

        # Grade de 6 linhas x 5 quadrados
        grade = tk.Frame(janela, bg=COR_FUNDO)
        grade.pack()
        self.quadrados = []
        for l in range(TENTATIVAS):
            linha = []
            for c in range(LETRAS):
                q = tk.Label(grade, text="", width=2, font=("Arial", 28, "bold"),
                             fg="white", bg=COR_VAZIO, relief="flat")
                q.grid(row=l, column=c, padx=3, pady=3, ipadx=6, ipady=4)
                linha.append(q)
            self.quadrados.append(linha)

        # Mensagens
        self.status = tk.Label(janela, text="", font=("Arial", 13),
                               fg="white", bg=COR_FUNDO, pady=8)
        self.status.pack()

        # Teclado na tela (dá para clicar ou usar o teclado do computador)
        self.teclas = {}
        teclado = tk.Frame(janela, bg=COR_FUNDO)
        teclado.pack()
        fileiras = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        for n, fileira in enumerate(fileiras):
            f = tk.Frame(teclado, bg=COR_FUNDO)
            f.pack(pady=2)
            if n == 2:
                self.criar_tecla(f, "ENTER", self.enviar, largura=6)
            for letra in fileira:
                self.teclas[letra] = self.criar_tecla(
                    f, letra, lambda l=letra: self.digitar(l))
            if n == 2:
                self.criar_tecla(f, "⌫", self.apagar, largura=4)

        tk.Button(janela, text="Nova partida", command=self.nova_partida).pack(pady=(12, 0))

        janela.bind("<Key>", self.tecla_pressionada)
        self.nova_partida()

    def criar_tecla(self, pai, texto, acao, largura=3):
        t = tk.Label(pai, text=texto, width=largura, font=("Arial", 13, "bold"),
                     fg="white", bg=COR_TECLA, pady=6, cursor="hand2")
        t.pack(side="left", padx=2)
        t.bind("<Button-1>", lambda e: acao())
        return t

    def nova_partida(self):
        self.secreta = random.choice(PALAVRAS)
        self.linha = 0          # em qual tentativa estamos
        self.chute = ""         # o que você já digitou na linha atual
        self.acabou = False
        self.cor_das_teclas = {}

        for linha in self.quadrados:
            for q in linha:
                q.config(text="", bg=COR_VAZIO)
        for t in self.teclas.values():
            t.config(bg=COR_TECLA)
        self.status.config(text="Digite uma palavra de 5 letras e aperte Enter.")

    # Digitação

    def tecla_pressionada(self, evento):
        if evento.keysym == "Return":
            self.enviar()
        elif evento.keysym == "BackSpace":
            self.apagar()
        else:
            letra = sem_acento(evento.char)
            if len(letra) == 1 and "A" <= letra <= "Z":
                self.digitar(letra)

    def digitar(self, letra):
        if self.acabou or len(self.chute) == LETRAS:
            return
        self.chute += letra
        self.mostrar_chute()

    def apagar(self):
        if self.acabou or not self.chute:
            return
        self.chute = self.chute[:-1]
        self.mostrar_chute()

    def mostrar_chute(self):
        for c in range(LETRAS):
            letra = self.chute[c] if c < len(self.chute) else ""
            self.quadrados[self.linha][c].config(text=letra)


    # Conferir o chute

    def enviar(self):
        if self.acabou:
            return
        if len(self.chute) < LETRAS:
            self.status.config(text="A palavra precisa ter 5 letras.")
            return

        cores = comparar(self.chute, self.secreta)

        # Pinta os quadrados da linha
        for c in range(LETRAS):
            self.quadrados[self.linha][c].config(bg=CORES[cores[c]])

        # Pinta o teclado (verde vence amarelo, que vence preto)
        for letra, cor in zip(self.chute, cores):
            atual = self.cor_das_teclas.get(letra)
            if atual is None or PRIORIDADE[cor] > PRIORIDADE[atual]:
                self.cor_das_teclas[letra] = cor
                self.teclas[letra].config(bg=CORES[cor])

        acertou = self.chute == self.secreta
        self.linha += 1
        self.chute = ""

        if acertou:
            self.acabou = True
            texto = f"Parabéns! Você acertou em {self.linha} tentativa(s)!"
            self.status.config(text=texto)
            messagebox.showinfo("Você venceu!", texto)
        elif self.linha == TENTATIVAS:
            self.acabou = True
            texto = f"Não foi dessa vez. A palavra era {self.secreta}."
            self.status.config(text=texto)
            messagebox.showinfo("Fim de jogo", texto)
        else:
            self.status.config(text=f"Tentativa {self.linha + 1} de {TENTATIVAS}.")


if __name__ == "__main__":
    janela = tk.Tk()
    janela.resizable(False, False)
    Termo(janela)
    janela.mainloop()
