import curses
import random


def desenha_passaro(stdscr, x, y, velocidade): # colocar velocidade como parametro. Se a velocidade for tal o desenho passa a ser outro
   if velocidade < 0:
       passaro = [' __',
                  '/v ">'
               ]
   else:
       passaro = [' __',
                  '/^ ">'
               ]
      
   for i, linha in enumerate(passaro):
       if 0 <= y + i < curses.LINES and 0 <= x < curses.COLS - len(linha):
           stdscr.addstr(y + i, x, linha, curses.color_pair(1))


def atualiza_passaro(estado):
   estado['velocidade'] += estado['gravidade']
   estado['velocidade'] = max(-4, min(estado['velocidade'], 2))
   estado['y'] += int(estado['velocidade'])
   estado['y'] = max(0, min(estado['y'], curses.LINES - 2))


def desenha_canos(stdscr, canos):
   for cano in canos:
       x = cano['x']
       buraco_y = cano['buraco_y']
       tam_buraco = cano['tam_buraco']


       if x < 0 or x >= curses.COLS - 1:
           continue  # aqui pra baixo o bagulho é doido


       for y in range(curses.LINES):
           if y < buraco_y or y > buraco_y + tam_buraco:
               if 0 <= y < curses.LINES:
                   try:
                       stdscr.addstr(y, x, '||', curses.color_pair(2))
                   except curses.error:
                       pass


def atualiza_canos(estado):
   novos_canos = []
   for cano in estado['canos']:
       cano['x'] -= 1
       if cano['x'] >= 0:
           novos_canos.append(cano)
       else:
           estado['pontuacao'] += 1
   estado['canos'] = novos_canos


   if estado['ultimo_cano'] <= 0:
       tam_buraco = 15
       min_y = 3
       max_y = curses.LINES - tam_buraco - 3
       buraco_y = random.randint(min_y, max_y)
       novo_cano = {
           'x': curses.COLS - 1,
           'buraco_y': buraco_y,
           'tam_buraco': tam_buraco
       }
       estado['canos'].append(novo_cano)
       estado['ultimo_cano'] = 50  # lógica da distância entre os canos
   else:
       estado['ultimo_cano'] -= 1


def colisao(estado):
   y = estado['y']
   x = estado['x']


   # Verifica colisão com o teto ou chão
   if y <= 0 or y >= curses.LINES - 2:
       estado['colisao'] = True
       return


   # Verifica colisão com o cano exatamente na posição do pássaro
   for cano in estado['canos']:
       if cano['x'] == x:
           buraco_y = cano['buraco_y']
           tam_buraco = cano['tam_buraco']
           if y < buraco_y or y > buraco_y + tam_buraco:
               estado['colisao'] = True
               return


   estado['colisao'] = False


def sair(stdscr):
    stdscr.clear()
    msg = "Saindo do jogo..."
    height, width = stdscr.getmaxyx()
    stdscr.addstr(height // 2, (width - len(msg)) // 2, msg)
    stdscr.refresh()
    curses.napms(1000)

def desenha_titulo(stdscr):
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    titulo_ascii = [
        '____  _   ____ ___ ____  ____',  
        '|  _ \/ | | __ )_ _|  _ \ |  _ \ ',
        '| |_) | | |  _ \| || |_) || | | |',
        '|  __/| | | |_) | ||  _ < | |_| |',
        '|_|   |_| |____/___|_| \_\|____/', 
                                 
    ]
    for idx, linha in enumerate(titulo_ascii):
        y = idx
        x = (width - len(linha)) // 2
        if 0 <= y < height:
            stdscr.addstr(y, x, linha)
    stdscr.refresh()

def menu(stdscr):
    curses.curs_set(0)
    height, width = stdscr.getmaxyx()

    linhas_menu = [
        "Pressione ESPAÇO para jogar",
        "Pressione 't' para ver o tutorial",
        "Pressione 'q' para sair"
    ]

    largura = max(len(linha) for linha in linhas_menu) + 4
    altura = len(linhas_menu) + 4

    start_y = len(linhas_menu) + 10
    start_x = (width - largura) // 2

    while True:
        desenha_titulo(stdscr)

        janela = curses.newwin(altura, largura, start_y, start_x)
        janela.keypad(True)
        janela.clear()
        janela.box()

        titulo = "MENU INICIAL"
        janela.addstr(1, (largura - len(titulo)) // 2, titulo, curses.A_BOLD)

        for idx, linha in enumerate(linhas_menu):
            janela.addstr(2 + idx + 1, (largura - len(linha)) // 2, linha)

        janela.refresh()

        key = janela.getch()
        if key == ord(' '):
            return "jogar"
        elif key in (ord('q'), ord('Q')):
            return "sair"
        elif key in (ord('t'), ord('T')):
            mostrar_tutorial(stdscr)
            

def mostrar_tutorial(stdscr):
    stdscr.clear()
    stdscr.refresh()
    curses.curs_set(0)
   
    height, width = stdscr.getmaxyx()

    instrucoes = [
         "TUTORIAL DO JOGO",
        "",
        "O intuito do jogo é pontuar o máximo possível.",
        "A gravidade é constante, aperte espaço de forma consecutiva para dar altura ao pássaro.",
        "Evite os canos, se tocar na extensão deles ou nas bordas do mapa, perde.",
        "",
        "Aperte 'q' para voltar ao menu."
    ]

    for idx, linha in enumerate(instrucoes):
        y = height // 2 - len(instrucoes) // 2 + idx
        x = (width - len(linha)) // 2
        stdscr.addstr(y, x, linha, curses.A_BOLD if idx == 0 else 0)

    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key in (ord('q'), ord('Q')):
            stdscr.clear()
            stdscr.refresh()
            break 
    
       
def fim_de_jogo(stdscr, pontuacao):
    stdscr.nodelay(False)
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    
    msg1 = "FIM DE JOGO"
    msg2 = f"Sua pontuação: {pontuacao}"
    msg3 = "Pressione ESPAÇO para voltar ao menu"

    stdscr.addstr(height // 2 - 1, (width - len(msg1)) // 2, msg1, curses.A_BOLD)
    stdscr.addstr(height // 2, (width - len(msg2)) // 2, msg2)
    stdscr.addstr(height // 2 + 2, (width - len(msg3)) // 2, msg3)

    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key == ord(' '):
            return



def main(stdscr):
   curses.curs_set(0)
   stdscr.nodelay(True)


   curses.start_color()
   curses.init_pair(1, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # cor do passaro
   curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)   # cor do cano


   estado = {
       'x': 10,
       'y': 15,
       'velocidade': 0,
       'gravidade': 0.5,
       'pulo': -3,
       'canos': [],
       'ultimo_cano': 0,
       'pontuacao': 0,
       'colisao': False
        }


   while True:
       stdscr.clear()
       stdscr.addstr(0, 0, f"Pontuação: {estado['pontuacao']}")


       key = stdscr.getch()
       if key == ord(' '):
           estado['velocidade'] = estado['pulo']
           # aqui coloca a animação, bem facinho
       elif key == ord('q'):
           break


       # Atualiza o pássaro e os canos
       atualiza_passaro(estado)
       atualiza_canos(estado)


       # Checa colisão e atualiza o estado
       colisao(estado)
       if estado['colisao']:
           fim_de_jogo(stdscr, estado['pontuacao'])
           break  # Se houver colisão, encerra o jogo


       desenha_passaro(stdscr, estado['x'], estado['y'], estado['velocidade'])
       desenha_canos(stdscr, estado['canos'])


       stdscr.refresh()
       curses.napms(50)

def main_loop(stdscr):
    while True:
        escolha = menu(stdscr)
        if escolha == "jogar":
            main(stdscr)   
        elif escolha == "sair":
            sair(stdscr)
            break


if __name__ == "__main__":
   curses.wrapper(main_loop)