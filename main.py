import pygame
import random
import sys
import time
import csv
import operator
import helpers.pygame_textinput

pygame.init()

size = [1525, 800]
screen = pygame.display.set_mode(size)
estado = "menu" # menu - game

pygame.display.set_caption('Stick Man')

pygame.mixer.music.load('imagenes/otros/Mortal Kombat Theme Remix 2012.mp3')
pygame.mixer.music.set_volume(0.15)
pygame.mixer.music.play(-1)

clock = pygame.time.Clock()
background_index = 0
highest_wave = 1

default_index = 0


class Imagen:
    def __init__(self, nombre_imagen, coordenadas, dimensiones):
        self.coordenadas = coordenadas #Lista de dos coordenadas[x,y]
        self.dimensiones = dimensiones #Lista de dos dimensiones[w,h]
        self.imagen = pygame.image.load(nombre_imagen)
        self.imagen = pygame.transform.scale(self.imagen, self.dimensiones)
    
    def dibujar(self):
        screen.blit(self.imagen, self.coordenadas)

class Boton(Imagen):

    def __init__(self, nombre_imagen, coordenadas, dimensiones, segunda_imagen):

        super().__init__(nombre_imagen,coordenadas,dimensiones)

        self.imagen_2 = pygame.image.load(segunda_imagen) # Imagen cuando boton  activo
        self.imagen_2 = pygame.transform.scale(self.imagen_2, self.dimensiones)

    def is_over(self, mouse_coords): # Devolver True si el mouse esta encima

        if self.coordenadas[0] <= mouse_coords[0] and mouse_coords[0] <= self.dimensiones[0] + self.coordenadas[0]: # x
            if self.coordenadas[1] <= mouse_coords[1] and mouse_coords[1] <= self.dimensiones[1] + self.coordenadas[1]:
                return True
        return False

    def dibujar_boton(self, mouse_coords): # Comprueba si el mouse esta encima e imprime boton 1 o 2
        if self.is_over(mouse_coords):
            screen.blit(self.imagen_2, self.coordenadas)
        else:
            screen.blit(self.imagen, self.coordenadas)

class Texto:
    def __init__(self, texto, coords, size):
        self.texto = texto 
        self.coords = coords # Lista [x,y]
        self.size = size  # Entero

        # Crear Fuente
        self.fuente = pygame.font.Font("imagenes/fonts/Pokemon_GB.ttf", self.size) # Fuente, tamaño

        # Renderizando el texto con la fuente
        self.renderizado = self.fuente.render(self.texto, True, [255, 255, 255]) # 1 = suavizado de bordes 

    def dibujar(self):
        screen.blit(self.renderizado, self.coords)
    
    def update_txt(self, texto):
        self.texto = texto
        self.renderizado = self.fuente.render(self.texto, True, [255, 255, 255]) # RGB BLANCO [255, 255, 255]

class Caracter:

    def __init__(self, coords):
        self.vida = 100
        self.velocidad = 8
        self.coordenadas = coords # Lista de 2 [x, y]
        self.direccion = 1 # Derecha = 1 / Izquierda = 0
        self.dano = 5

        self.animation = "nada" # Que esta haciendo? - Nos indica si se esta animando o no.
        self.index = 0 # Indice del animacion
        self.reversa = False # Animacion en reversa
        self.text_vida = Texto(str(self.vida), [self.coordenadas[0] + 50, self.coordenadas[1]-10], 30)

    # Animaciones: PAsas una imagen, y la imprimen

    def correr(self, imagen): 
        if self.direccion == 1 and self.coordenadas[0] < size[0] - self.middle - 20: 
            self.coordenadas[0] += self.velocidad
        elif self.direccion == 0 and self.coordenadas[0] + self.middle - 20 > 0:
            self.coordenadas[0] -= self.velocidad 
        imagen.coordenadas = self.coordenadas 
        imagen.dibujar()

    def golpear(self, imagen):
        imagen.coordenadas = self.coordenadas 
        imagen.dibujar()

    def nada(self, imagen):
        imagen.coordenadas = self.coordenadas   
        imagen.dibujar()

    def damage(self, imagen):
        if self.direccion == 1 and self.coordenadas[0] > 0:
            self.coordenadas[0] -= 5
        elif self.direccion == 0 and self.coordenadas[0] < size[0] - self.middle - 20:
            self.coordenadas[0] += 5 
        imagen.coordenadas = self.coordenadas
        imagen.dibujar()

        if self.index == 5: # Bajar vida en fotograma 5
            self.vida -= self.dano

    def imprimir_vida(self):
        self.text_vida.update_txt(str(self.vida))  
        self.text_vida.coords = [self.coordenadas[0] + self.middle - 40, self.coordenadas[1]-10]
        self.text_vida.dibujar()


class Heroe(Caracter):

    def __init__(self, coords):
        super().__init__(coords)
        self.middle = 113


class Enemigo(Caracter):

    def __init__(self, coords, direccion):
        super().__init__(coords)
        self.direccion = direccion
        self.tarea = "nada"
        self.dano += 2
        self.middle = 225

    def check_tarea(self):

        if self.tarea == "nada":
            return True

        if self.tarea == "go":
            if abs(Hero.coordenadas[0] + Hero.middle - self.coordenadas[0] - self.middle) < 150:
                return True
            else:
                return False

        if self.tarea == "golpe":
            if self.animation == "golpe":
                return False
            else:
                return True

        if self.tarea == "huir":

            # Terminar tarea de huir si ya estan en los bordes
            if self.coordenadas[0] <= 0 or self.coordenadas[0] >= size[0] - self.middle - 20:
                return True

            if abs(Hero.coordenadas[0] + Hero.middle - self.coordenadas[0] - self.middle) > 600:
                return True
            else:
                return False


    def selecionar_tarea(self):

        probabilidad=random.randint(0, 1000)

        if abs(Hero.coordenadas[0] + Hero.middle - self.coordenadas[0] - self.middle) < 150: 
            if probabilidad > 900:
                self.tarea = "golpe"
                self.index = 0 # Porque se necesita reiniciar el index (estaba corriendo)
            elif probabilidad < 150:
                self.tarea = "huir"
            else:
                self.tarea = "nada"
        else:
            if probabilidad > 900:
                self.tarea = "go"
            else:
                self.tarea = "nada"

    def definir_animacion(self):

        if self.animation == "damage": # Si recibe un golpe, la tarea no se redefine ._.
            return # Fuerza a la funcion a terminar y no devuelve nada

        if self.tarea == "golpe":
            self.animation = "golpe"
            if self.coordenadas[0] + self.middle < Hero.coordenadas[0] + Hero.middle:
                self.direccion = 1
            else:
                self.direccion = 0

        if self.tarea == "go":
            self.animation = "correr"
            if Hero.coordenadas[0] + Hero.middle < self.coordenadas[0] + self.middle:
                self.direccion = 0
            else:
                self.direccion = 1

        if self.tarea == "huir":
            self.animation = "correr"
            if self.coordenadas[0] + self.middle < Hero.coordenadas[0] + Hero.middle:
                self.direccion = 0
            else:
                self.direccion = 1


def print_background():
    global background_index
    lista_otros[3][int(background_index)].dibujar()
    background_index += 0.25
    if background_index == 7:
        background_index = 0
    return

def print_stats():
    global Bots
    Wave = Texto("Wave: " + str(n_wave), [50, 650], 28)
    Enemies = Texto("Remaining Enemies: " + str(len(Bots)), [50, 710], 28)
    Best = Texto("Your Best: "+ str(highest_wave), [1000, 650], 28)
    record_wave = read_database()
    Record = Texto("Global Record: "+ str(record_wave[0][1]), [1000, 710], 28)
    Wave.dibujar()
    Enemies.dibujar()
    Best.dibujar()
    Record.dibujar()
    return

def print_default(numb = 0):
    global default_index
    default[numb][int(default_index)].dibujar()
    default_index += 0.25
    if default_index == 7:
        default_index = 0
    return
    

def comprobar_movimiento():

    if Hero.animation == "damage": # Si golpean al heroe, no se comprueba movimientos
        return

    pressed_keys = pygame.key.get_pressed() # Diccionario con las teclas del teclado (bool)

    # Comprobar el movimiento 
    # La animacion se puede interrumpir por el usuario

    if pressed_keys[pygame.K_RIGHT] or pressed_keys[pygame.K_LEFT]:
        if Hero.animation != "correr":
            Hero.index = 0
        Hero.animation = "correr"

        if pressed_keys[pygame.K_RIGHT]:
            Hero.direccion = 1 # Va a la derecha
        else:
            Hero.direccion = 0 # va a la izquierda

    elif pressed_keys[pygame.K_SPACE]:
        if Hero.animation != "golpe":
            Hero.index=0
        Hero.animation = "golpe"

    else: 
        Hero.animation = "nada"
        Hero.index = 0


def imagen_hero(tarea): # Le pasamos una tarea y manda a que esa tarea se imprima

    Hero.imprimir_vida()

    if tarea == "nada": # indice 0
        imagen = animacion_heroe[0][Hero.direccion]
        Hero.nada(imagen)

    if tarea == "golpe": #indice 1 (golpe derecha) // indice 2 (golpe izquierda)
        if Hero.direccion==1:
            imagen = animacion_heroe[1][Hero.index]
        else:
            imagen = animacion_heroe[2][Hero.index]
        Hero.golpear(imagen)
            
        if Hero.reversa == False: # 0 - 5
            Hero.index+=1
        else:
            Hero.index-=1

        if Hero.index==6:
            Hero.reversa=True
            Hero.index=4
            
        if Hero.index==-1:
            Hero.index=0
            Hero.reversa=False
            Hero.animation="nada"
    
    if tarea == 'correr':
        if Hero.direccion == 1:
            imagen = animacion_heroe[3][Hero.index]
        else:
            imagen = animacion_heroe[4][Hero.index]

        Hero.correr(imagen)
        Hero.index += 1
        if Hero.index == 10:
            Hero.index = 4

    if tarea == "damage": # indice 5 (derecha) // Indice 6 (Izquierda)
        if Hero.direccion == 1:
            imagen = animacion_heroe[5][Hero.index]
        else:
            imagen = animacion_heroe[6][Hero.index]
        Hero.damage(imagen)

        Hero.index += 1
        if Hero.index == 10:
            Hero.index = 0
            Hero.animation = "nada"
        
def imagen_enemigo(): # Elige la imagen de los enemigos para que se manden a imprimir

    for i in range(len(Bots)):

        Bots[i].imprimir_vida()

        if Bots[i].animation == "nada":
            imagen = animacion_bots[0][Bots[i].direccion]
            Bots[i].nada(imagen)

        if Bots[i].animation == "golpe": 

            if Bots[i].direccion==1:
                imagen = animacion_bots[1][Bots[i].index]
            else:
                imagen = animacion_bots[2][Bots[i].index]
            Bots[i].golpear(imagen)
                
            if Bots[i].reversa == False: 
                Bots[i].index+=1
            else:
                Bots[i].index-=1

            if Bots[i].index==6:
                Bots[i].reversa=True
                Bots[i].index=4
                
            if Bots[i].index==-1:
                Bots[i].index=0
                Bots[i].reversa=False
                Bots[i].animation="nada"

        if Bots[i].animation == 'correr':
            if Bots[i].direccion == 1:
                imagen = animacion_bots[3][Bots[i].index//2]
            else:
                imagen = animacion_bots[4][Bots[i].index//2]

            Bots[i].correr(imagen)
            Bots[i].index += 1

            if Bots[i].index == 8 * 2:
                Bots[i].index = 4
        
        if Bots[i].animation == "damage":

            if Bots[i].direccion == 1:
                imagen = animacion_bots[5][Bots[i].index // 2]
            else:
                imagen = animacion_bots[6][Bots[i].index // 2]
            Bots[i].damage(imagen)

            Bots[i].index += 1
            if Bots[i].index == 10:
                Bots[i].index = 0
                Bots[i].animation = "nada"


def check_golpe(): # Revisa si el usuario o un bot dio un golpe valido

    if Hero.animation == "golpe" and Hero.index == 0 and not Hero.reversa: # Iniciando golpe
        for i in range(len(Bots)): # Recorre los enemigos
            if abs(Hero.coordenadas[0] + Hero.middle - Bots[i].coordenadas[0] - Bots[i].middle) < 150: # Comprueba quines estan cerca

                # Comprueba que la direccion sea correcta
                if Bots[i].coordenadas[0] + Bots[i].middle < Hero.coordenadas[0] + Hero.middle and Hero.direccion == 0:
                    Bots[i].animation = "damage"
                    Bots[i].index = 0
                    Bots[i].direccion = 1

                elif Bots[i].coordenadas[0] + Bots[i].middle > Hero.coordenadas[0] + Hero.middle and Hero.direccion == 1:
                    Bots[i].animation = "damage"
                    Bots[i].index = 0
                    Bots[i].direccion = 0
                

    for i in range(len(Bots)):
        if Bots[i].animation == "golpe" and Bots[i].index == 0 and not Bots[i].reversa:
            if abs(Hero.coordenadas[0] + Hero.middle - Bots[i].coordenadas[0] - Bots[i].middle) < 150:

                if Bots[i].coordenadas[0] + Bots[i].middle < Hero.coordenadas[0] + Hero.middle and Bots[i].direccion == 1:
                    Hero.animation = "damage"
                    Hero.index = 0
                    Hero.direccion = 0

                elif Bots[i].coordenadas[0] + Bots[i].middle > Hero.coordenadas[0] + Hero.middle and Bots[i].direccion == 0:
                    Hero.animation = "damage"
                    Hero.index = 0
                    Hero.direccion = 1

def next_wave():

    global Hero
    global Bots
    global highest_wave

    Hero = Heroe([750, 300])
    Hero.vida += (n_wave -1 ) * 40

    if n_wave > 7:
        Hero.dano += (n_wave - 7) * 5

    Bots = []
    for i in range(n_wave):
        if i % 2: # == 1
            x = i * 40
        else: # == 0
            x = size[0] - 225 - (i * 40)
        Bots.append(Enemigo([x, 300], i % 2))

    if n_wave > highest_wave: highest_wave = n_wave

    return
        
    

def menu(): # Menu principal

    global estado # Como modificamos su valor, utilizamos global
    global n_wave
    global contar # Creamos contar, para saber si hacemos cuenta regresiva en game()
    
    for event in pygame.event.get():
        presionar = pygame.mouse.get_pressed() # Si mouse se presiono (0,0,0)
        if event.type == pygame.QUIT: 
            sys.exit()
        if presionar[0] == 1 and lista_otros[2].is_over(pygame.mouse.get_pos()): #saber si el boton se presiona
            estado = "game"
            n_wave = 1
            next_wave() 
            contar = time.time()
            
    # Draw Zone
    lista_otros[0].dibujar() # Imagen de fondo
    print_default(0)
    lista_otros[2].dibujar_boton(pygame.mouse.get_pos()) # dibuja el boton
    lista_otros[4].dibujar()


    pygame.display.update()

def cuenta_regresiva():
    n = 6 - (time.time() - contar)
    print_background()
    txt1 = Texto("Battle begins in " + str(int(n))+ " seconds", [200, 40], 45)
    txt2 = Texto("Wave " + str(n_wave), [615, 110], 40)
    txt1.dibujar()
    txt2.dibujar()
    pygame.display.update()


def game_over():
    global estado

    if evaluate_database(n_wave):
        textinput = helpers.pygame_textinput.TextInput(text_color=(255,255,255), font_family="imagenes/fonts/Pokemon_GB.ttf", font_size=100, cursor_color=(255,255,255),max_string_length=3)
        
        contar2 = time.time()
        while(time.time() - contar2 < 60):
            if textinput.update(pygame.event.get()):
                name = textinput.get_text()
                write_database(name, n_wave)
                break
            screen.fill((30,30,30))
            txt1 = Texto("NEW HIGH SCORE", [480, 40], 45)
            txt2 = Texto(f"You reached wave {n_wave}", [410, 110], 40)
            txt3 = Texto("Enter Your Initials", [410, 600], 40)
            txt1.dibujar()
            txt2.dibujar()
            txt3.dibujar()

            events = pygame.event.get()
            textinput.update(events)
            screen.blit(textinput.get_surface(), (650,670))

            print_default(1) 
            pygame.display.update()

            for event in events:
                if event.type == pygame.QUIT:
                    sys.exit()


        contar2 = time.time()
        scores = read_database()
        while(time.time() - contar2 < 6):
            screen.fill((0,0,0))
            txt1 = Texto("LEADERBOARD", [580, 40], 45)
            txt2 = Texto(scores[0][0], [550, 200], 30)
            txt3 = Texto(scores[0][1], [900, 200], 30)
            txt4 = Texto(scores[1][0], [550, 300], 30)
            txt5 = Texto(scores[1][1], [900, 300], 30)
            txt6 = Texto(scores[2][0], [550, 400], 30)
            txt7 = Texto(scores[2][1], [900, 400], 30)
            txt8 = Texto(scores[3][0], [550, 500], 30)
            txt9 = Texto(scores[3][1], [900, 500], 30)
            txt10 = Texto(scores[4][0], [550, 600], 30)
            txt11 = Texto(scores[4][1], [900, 600], 30)
            txt1.dibujar()
            txt2.dibujar()
            txt3.dibujar()
            txt4.dibujar()
            txt5.dibujar()
            txt6.dibujar()
            txt7.dibujar()
            txt8.dibujar()
            txt9.dibujar()
            txt10.dibujar()
            txt11.dibujar()
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
        estado = "menu"
    else:
        contar2 = time.time()
        while(time.time() - contar2 < 6):
            print_background()
            txt1 = Texto("GAME OVER", [580, 40], 45)
            txt2 = Texto(f"You reached wave {n_wave}", [410, 110], 40)
            txt1.dibujar()
            txt2.dibujar()
            print_default(2)
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
        estado = "menu"
    

def game():

    global estado
    global contar
    global n_wave

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()


    # Draw Zone
    
    #lista_otros[1].dibujar() # Imprimir imagen de background (cueva)
    print_background()
    print_stats()

    if time.time() - contar < 5:
        cuenta_regresiva()
        return

    # Impresion del personaje
    
    comprobar_movimiento() # Comprueba y cambia el movimiento del Heroe
    

    # Impresion Bots

    for i in range(len(Bots)):
        if Bots[i].check_tarea(): # Verifica si la tarea del bot esta completa
            Bots[i].selecionar_tarea() # Selecciona una tarea para el bot si no tienen ninguna
        Bots[i].definir_animacion() # Define lo que debe hacer en determinada tarea


    check_golpe()

    imagen_enemigo() # Seleccionar e imprimir la imagen del enemigo segun la tarea
    imagen_hero(Hero.animation) # Selecciona e imprimir la imagen del heroe segun la tarea

    i = 0
    while (i < len(Bots)):
        if Bots[i].vida <= 0:
            del Bots[i]
            i -= 1
        i += 1

    if Hero.vida <= 0:
        game_over()
    
    if len(Bots) == 0:
        contar = time.time()
        n_wave += 1
        next_wave()

    pygame.display.update()
    clock.tick(25) # Fps (40)


def main(): # La funcion principal del juego
    while (True):
        if (estado == "menu"): menu()
        elif (estado == "game"): game()

def import_images(): # Funcion que importa las imagenes

    global animacion_heroe
    global animacion_bots
    global lista_otros
    global default

    lista_otros = [] # Lista que guarda todas las imagenes que no son animaciones
    lista_otros.append(Imagen("imagenes/otros/background.png", [0,0], size))
    lista_otros.append(Imagen("imagenes/otros/fondo.jpg", [0,0], size))
    lista_otros.append(Boton("imagenes/otros/boton1.png", [537,322], [430, 155], "imagenes/otros/boton2.png"))
    lista_otros.append([])
    lista_otros.append(Imagen("imagenes/otros/title.png", [60,100], [1500, 150]))

    for i in range(7):
        lista_otros[3].append(Imagen("imagenes/background_images/"+str(i+1)+".jpg", [0,0], size))

    # IMPORTACION DE FOTOGRAMAS DEL HEROE ************************************************************************

    animacion_heroe = [] # Matriz que guarda los fotogramas de las animaciones del heroe

    # Stop: 0

    direction = "imagenes/hero/Stop Char Images/Stop "
    animacion_heroe.append([])
    for i in range(1,3): # stop_imagenes indice = 0
        animacion_heroe[0].append(Imagen(direction + str(i) + ".png", [0,0], [225,279]))

    # Golpear: 1 - 2

    direction="imagenes/hero/Hit Right/Hit "
    animacion_heroe.append([])
    for i in range (1,7):
        animacion_heroe[1].append(Imagen(direction+ str(i)+".png",[0,0],[225,279]))

    direction="imagenes/hero/Hit Left/Hit "
    animacion_heroe.append([])
    for i in range (1,7):
        animacion_heroe[2].append(Imagen(direction+ str(i)+".png",[0,0],[225,279]))

    # Correr: 3 - 4

    direction = "imagenes/hero/Run Right/Run "
    animacion_heroe.append([])
    for i in range(1,12):
        animacion_heroe[3].append(Imagen(direction + str(i) +".png", [0,0], [225, 279]))

    direction = "imagenes/hero/Run Left/Run "
    animacion_heroe.append([])
    for i in range(1,12):
        animacion_heroe[4].append(Imagen(direction + str(i) +".png", [0,0], [225, 279]))
    
    # DAMAGE: Right: 5 -  Left: 6

    direction = "imagenes/hero/Damage Right/Recibir "
    animacion_heroe.append([])
    for i in range(1,11):
        animacion_heroe[5].append(Imagen(direction + str(i) + ".png", [0,0], [225,279]))

    direction = "imagenes/hero/Damage Left/Recibir "
    animacion_heroe.append([])
    for i in range(1,11):
        animacion_heroe[6].append(Imagen(direction + str(i) + ".png", [0,0], [225,279]))

    # IMPORTACION DE FOTOGRAMAS DE LOS BOTS ************************************************************************

    animacion_bots = [] # Matriz que guarda los fotogramas de las animaciones de los bots

    direction = "imagenes/enemigos/Stop Char Images/Stop "
    animacion_bots.append([])
    for i in range(1,3): # stop_imagenes indice = 0
        animacion_bots[0].append(Imagen(direction + str(i) + ".png", [0,0], [390,280]))


    # Golpear: 1 - 2

    direction="imagenes/enemigos/Hit Right/Hit "
    animacion_bots.append([])
    for i in range (1,7):
        animacion_bots[1].append(Imagen(direction+ str(i)+".png",[0,0],[450,280]))

    direction="imagenes/enemigos/Hit Left/Hit "
    animacion_bots.append([])
    for i in range (1,7):
        animacion_bots[2].append(Imagen(direction+ str(i)+".png",[0,0],[450,280]))

    # Correr: 3 - 4

    direction = "imagenes/enemigos/Run Right/Run "
    animacion_bots.append([])
    for i in range(1,9):
        animacion_bots[3].append(Imagen(direction + str(i) +".png", [0,0], [450,280]))

    direction = "imagenes/enemigos/Run Left/Run "
    animacion_bots.append([])
    for i in range(1,9):
        animacion_bots[4].append(Imagen(direction + str(i) +".png", [0,0], [450,280]))
    
    # DAMAGE: Right: 5 -  Left: 6

    direction = "imagenes/enemigos/Damage Right/Recibir "
    animacion_bots.append([])
    for i in range(1,11):
        animacion_bots[5].append(Imagen(direction + str(i) + ".png", [0,0], [450,280]))

    direction = "imagenes/enemigos/Damage Left/Recibir "
    animacion_bots.append([])
    for i in range(1,11):
        animacion_bots[6].append(Imagen(direction + str(i) + ".png", [0,0], [450,280]))

    default = [[], [], []]
    for i in range(8):
        default[0].append(Imagen("imagenes/hero/Default/" +str(i)+".png", [130, 400], [380, 380]))
    for i in range(8):
        default[1].append(Imagen("imagenes/hero/Default2/" +str(i)+".png", [600, 225], [380, 380]))
    for i in range(8):
        default[2].append(Imagen("imagenes/hero/Default3/" +str(i)+".png", [600, 225], [380, 380]))

def read_database():
    unsorted = open('database/database.csv', "r")
    csv1 = list(csv.reader(unsorted))
    csv1.sort(key=lambda l:int(l[1]),reverse=True)
    scores = []
    for i in range(5):
        scores.append(csv1[i])
    return scores

def evaluate_database(wave):
    unsorted = open('database/database.csv', "r")
    csv1 = list(csv.reader(unsorted))
    csv1.sort(key=lambda l:int(l[1]),reverse=True)
    if wave >= int(csv1[4][1]):
        return True
    else:
        return False

def write_database(name, wave):
    with open('database/database.csv', 'a+', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([name, wave])
        

import_images()
main()