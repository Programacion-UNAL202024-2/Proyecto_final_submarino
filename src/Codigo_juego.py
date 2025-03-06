import pygame
import random
import sys
import os

pygame.init()
pygame.mixer.init()

ANCHO_PANTALLA = 1280
ALTO_PANTALLA = 720

VELOCIDAD_DISPARO = 6
VELOCIDAD_ENEMIGOS_BASE = 2
VELOCIDAD_DISPARO_ENEMIGO_BASE = 4
VELOCIDAD_FONDO = 2  


BLANCO = (255, 255, 255)
ROJO = (255, 0, 0)
VERDE = (0, 255, 0)
AZUL = (105, 175, 255)
NARANJA = (240, 120, 3)
AMARILLO = (255, 220, 61)
MORADO = (68, 43, 141)
NEGRO = (0, 0, 0)
AZUL_OSCURO = (43, 2, 140)
AZUL_CLARO = (230, 255, 255)


nivel = 1
puntuacion = 0
enemigos_restantes = 5


CARPETA_BASE = os.path.dirname(__file__)

def cargar_imagen(nombre_archivo, ancho, alto):
    ruta = os.path.join(CARPETA_BASE, nombre_archivo)
    try:
        imagen = pygame.image.load(ruta)
        return pygame.transform.scale(imagen, (ancho, alto))
    except pygame.error:
        return pygame.Surface((ancho, alto))



imagen_submarino = cargar_imagen('submarino.png', 100, 100)
imagen_daño = cargar_imagen('submarino_daño.png', 100, 100)
imagen_arma = cargar_imagen('arma.png', 50, 20)
imagen_fondo = cargar_imagen('fondo.jpg', ANCHO_PANTALLA, ALTO_PANTALLA)
imagenes_enemigos = [cargar_imagen(f'enemigo{i}.png', 100, 100) for i in range(4)]
imagen_inicio = cargar_imagen('fondo_inicio.jpg', ANCHO_PANTALLA, ALTO_PANTALLA)
imagen_vida = cargar_imagen('llave_vida.png', 80, 80)
imagen_final = cargar_imagen('fondo_final.jpg', ANCHO_PANTALLA, ALTO_PANTALLA)

try:
    pygame.mixer.music.load(os.path.join(CARPETA_BASE, 'music_fondo.mp3'))
    pygame.mixer.music.play(-1)
except pygame.error:
    pass

try:
    sonido_disparo = pygame.mixer.Sound(os.path.join(CARPETA_BASE, 'music_disparo.mp3'))
    sonido_explosion = pygame.mixer.Sound(os.path.join(CARPETA_BASE, 'music_fondo.mp3'))
except pygame.error:
    sonido_disparo = None
    sonido_explosion = None


class SubmarinoJugador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = imagen_submarino
        self.image_normal = imagen_submarino
        self.image_daño = imagen_daño
        self.rect = self.image.get_rect(midleft=(50, ALTO_PANTALLA // 2))
        self.velocidad = 5
        self.vida = 1000  
        self.tiempo_daño = 0
        self.recibio_daño = False
    
    def recibir_daño(self):
        self.image = self.image_daño  
        self.tiempo_dañado = pygame.time.get_ticks()
        self.recibio_daño = True
    
    def update(self):
        teclas = pygame.key.get_pressed()
        if teclas[pygame.K_UP]:
            self.rect.y -= self.velocidad
        if teclas[pygame.K_DOWN]:
            self.rect.y += self.velocidad
        if teclas[pygame.K_LEFT]:
            self.rect.x -= self.velocidad
        if teclas[pygame.K_RIGHT]:
            self.rect.x += self.velocidad
        self.rect.clamp_ip(pantalla.get_rect())
        if self.recibio_daño and pygame.time.get_ticks() - self.tiempo_dañado > 600:  
            self.image = self.image_normal
            self.recibio_daño = False
    
    def disparar(self):
        disparo = Disparo(self.rect.right, self.rect.centery, 'derecha')
        todos_los_sprites.add(disparo)
        disparos.add(disparo)
        if sonido_disparo:
            sonido_disparo.play()

class Disparo(pygame.sprite.Sprite):
    def __init__(self, x, y, direccion):
        super().__init__()
        self.image = imagen_arma
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidad = VELOCIDAD_DISPARO
        self.direccion = direccion
    
    def update(self):
        if self.direccion == 'derecha':
            self.rect.x += self.velocidad
        elif self.direccion == 'izquierda':
            self.rect.x -= self.velocidad
        
        if self.rect.left > ANCHO_PANTALLA or self.rect.right < 0:
            self.kill()

class SubmarinoEnemigo(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = random.choice(imagenes_enemigos)
        self.rect = self.image.get_rect(midright=(ANCHO_PANTALLA, random.randint(50, ALTO_PANTALLA - 50)))
        self.velocidad = VELOCIDAD_ENEMIGOS_BASE + nivel
        self.vida = 100 + (nivel * 50)
        self.direccion = 1
    
    def update(self):
        self.rect.x -= self.velocidad
        self.rect.y += self.direccion * 2
        if self.rect.top <= 0 or self.rect.bottom >= ALTO_PANTALLA:
            self.direccion *= -1

        if self.rect.right < 0:
            self.rect.midright = (ANCHO_PANTALLA, random.randint(50, ALTO_PANTALLA - 50))
            self.vida = 100 + (nivel * 50)  
        
        if random.randint(0, 100) < 2:
            disparo = Disparo(self.rect.left, self.rect.centery, 'izquierda')
            disparo.velocidad = VELOCIDAD_DISPARO_ENEMIGO_BASE + nivel
            todos_los_sprites.add(disparo)
            disparos_enemigos.add(disparo)

        if self.vida <= 0:
            self.kill()
            global puntuacion, enemigos_restantes
            puntuacion += 1
            enemigos_restantes -= 1
            if sonido_explosion:
                sonido_explosion.play()


pantalla = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Submarino de Batalla")


todos_los_sprites = pygame.sprite.Group()
disparos = pygame.sprite.Group()
disparos_enemigos = pygame.sprite.Group()
enemigos = pygame.sprite.Group()

jugador = SubmarinoJugador()
todos_los_sprites.add(jugador)

objeto_vida = None
caida_vida = 3

def generar_objeto_vida():
    global objeto_vida
    objeto_vida = pygame.sprite.Sprite()
    objeto_vida.image = imagen_vida
    objeto_vida.rect = imagen_vida.get_rect(midtop=(random.randint(100, ANCHO_PANTALLA - 100), 0))
       
    if objeto_vida.rect.y > ALTO_PANTALLA:
        objeto_vida = None 
    
    if objeto_vida and objeto_vida.rect.y > ALTO_PANTALLA:
        objeto_vida = None    
        


def mover_fondo():
    global imagen_fondo
    
    imagen_fondo_x = 0
    imagen_fondo_x2 = ANCHO_PANTALLA
    velocidad_fondo = VELOCIDAD_FONDO
    
    imagen_fondo_x -= velocidad_fondo
    imagen_fondo_x2 -= velocidad_fondo

    if imagen_fondo_x < -ANCHO_PANTALLA:
        imagen_fondo_x = ANCHO_PANTALLA
    if imagen_fondo_x2 < -ANCHO_PANTALLA:
        imagen_fondo_x2 = ANCHO_PANTALLA
    
    pantalla.blit(imagen_fondo, (imagen_fondo_x, 0))
    pantalla.blit(imagen_fondo, (imagen_fondo_x2, 0))

def dibujar_barra_vida():
    ancho_barra = 300
    pygame.draw.rect(pantalla, ROJO, (20, 20, ancho_barra, 20))
    vida_actual = max(0, jugador.vida)
    pygame.draw.rect(pantalla, VERDE, (20, 20, (ancho_barra * vida_actual) / 1000, 20))

def dibujar_texto():
    fuente = pygame.font.Font(None, 36)
    nivel_texto = fuente.render(f'Nivel: {nivel}', True, BLANCO)
    pantalla.blit(nivel_texto, (ANCHO_PANTALLA - 150, 20))

def avanzar_nivel():
    global nivel, enemigos_restantes
    if enemigos_restantes <= 0:
        if nivel == 5:
            pantalla_final2()
            return
        nivel += 1
        enemigos_restantes = 5 + nivel

        objeto_vida = None
        generar_objeto_vida()  

        for _ in range(enemigos_restantes):
            enemigo = SubmarinoEnemigo()
            todos_los_sprites.add(enemigo)
            enemigos.add(enemigo)

def detectar_colisiones():
    global puntuacion, enemigos_restantes
    
    for disparo in disparos:
        enemigos_golpeados = pygame.sprite.spritecollide(disparo, enemigos, False)
        for enemigo in enemigos_golpeados:
            enemigo.vida -= 50
            disparo.kill()
            if enemigo.vida <= 0:
                enemigo.kill()
                puntuacion += 1
                enemigos_restantes -= 1
    
    for disparo in disparos_enemigos:
        if jugador.rect.colliderect(disparo.rect):
            jugador.vida -= 20
            disparo.kill()
            jugador.recibir_daño()
            if jugador.vida <= 0:
                pantalla_final1()
                return False
    global objeto_vida

    if objeto_vida and jugador.rect.colliderect(objeto_vida.rect):
        jugador.vida += 100 
        objeto_vida = None
         
        

    return True
  
def pantalla_final1():
    pantalla.blit(imagen_final, (0,0))
    
    ruta_fuente = os.path.join(os.path.dirname(__file__), "fuente", "gunplay.otf")
    fuente = pygame.font.Font(ruta_fuente, 60)

    texto = fuente.render("GAME OVER", True, ROJO)
        
    pantalla.blit(texto, (ANCHO_PANTALLA // 2 - texto.get_width() // 2, ALTO_PANTALLA // 2 - texto.get_height() // 2))
    
    pygame.display.flip()
    pygame.time.wait(3000)  
    pygame.quit()
    sys.exit()

def pantalla_final2():
    pantalla.blit(imagen_final, (0,0))
    
    ruta_fuente = os.path.join(os.path.dirname(__file__), "fuente", "gunplay.otf")
    fuente = pygame.font.Font(ruta_fuente, 60)

    texto = fuente.render("¡Felicidades! Acabaste con todos", True, AMARILLO)
        
    pantalla.blit(texto, (ANCHO_PANTALLA // 2 - texto.get_width() // 2, ALTO_PANTALLA // 2 - texto.get_height() // 2))
    
    pygame.display.flip()
    pygame.time.wait(3000)  
    pygame.quit()
    sys.exit()

def juego():
    reloj = pygame.time.Clock()

    for _ in range(enemigos_restantes):
        enemigo = SubmarinoEnemigo()
        todos_los_sprites.add(enemigo)
        enemigos.add(enemigo)

    while True:
        mover_fondo() 
        dibujar_barra_vida()
        dibujar_texto()
        
        
        if objeto_vida:
            pantalla.blit(objeto_vida.image, objeto_vida.rect)
            objeto_vida.rect.y += caida_vida

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    jugador.disparar()
        
        if not detectar_colisiones():
            break       
     

        avanzar_nivel()
        todos_los_sprites.update()
        todos_los_sprites.draw(pantalla)
        
        
        pygame.display.flip()
        reloj.tick(60)

def pantalla_inicio():
    pantalla.blit(imagen_inicio, (0,0))

    ruta_fuente = os.path.join(os.path.dirname(__file__), "fuente", "gunplay.otf")
    
    fuente = pygame.font.Font(ruta_fuente, 80)
    fuente1 = pygame.font.Font(ruta_fuente, 20)
    fuente2 = pygame.font.Font(ruta_fuente, 50)

 
    
    texto = fuente.render("SUBMARINO DE BATALLA", True, NARANJA)
    texto1 = "Presiona ENTER para comenzar"
    texto3 = fuente2.render("¡Aguanta lo que puedas!", True, AZUL_CLARO)

    
    x_pos = ANCHO_PANTALLA // 2 - texto.get_width() // 2
    y_pos = ALTO_PANTALLA // 2 - texto.get_height() // 2
    desplazamiento = -500  
    velocidad_texto = 10
    
   
    particle_list = []

    renderizado = fuente1.render(texto1, True, BLANCO)

    rect_x, rect_y = ANCHO_PANTALLA / 2 - 175, ALTO_PANTALLA - 170
    rect_ancho, rect_alto = 350, 50
    radio_borde = 20  
    grosor_borde = 5
    
    while True:
        pantalla.blit(imagen_inicio, (0,0))

            
        pygame.draw.rect(pantalla, AZUL, 
                     (rect_x - grosor_borde, rect_y - grosor_borde, 
                      rect_ancho + grosor_borde * 2, rect_alto + grosor_borde * 2), 
                     border_radius=radio_borde + grosor_borde)


        pygame.draw.rect(pantalla, AZUL_OSCURO, 
                     (rect_x, rect_y, rect_ancho, rect_alto), 
                     border_radius=radio_borde)
   
        texto_rect = renderizado.get_rect(center=(rect_x + rect_ancho // 2, rect_y + rect_alto // 2))
        pantalla.blit(renderizado, texto_rect)

        
        x_pos += velocidad_texto
        if x_pos > ANCHO_PANTALLA // 2 - texto.get_width() // 2:
            x_pos = ANCHO_PANTALLA // 2 - texto.get_width() // 2

        pantalla.blit(texto, (ANCHO_PANTALLA // 2 - texto.get_width() // 2, y_pos - 250))
        pantalla.blit(texto3, (ANCHO_PANTALLA // 2 - texto3.get_width() // 2, y_pos - 150))

        
        if random.randint(0, 10) < 3:
            particle_list.append([random.randint(0, ANCHO_PANTALLA), 0, random.randint(2, 4)])

        for particle in particle_list:
            pygame.draw.circle(pantalla, AZUL, (particle[0], particle[1]), 3)
            particle[1] += particle[2]
            if particle[1] > ALTO_PANTALLA:
                particle_list.remove(particle)
        


        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_RETURN:
                return

pantalla_inicio()
juego()

