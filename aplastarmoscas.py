# Importar los módulos
import os
import pygame as pg

dir_principal = os.path.split(os.path.abspath(__file__))[0]
dir_datos = os.path.join(dir_principal, "datos")

# funciones para crear nuestros recursos
def cargar_image(nombre, colorkey=None, escala=1):
    nombre_completo = os.path.join(dir_datos, nombre)
    image = pg.image.load(nombre_completo)
    image = image.convert()

    tamaño = image.get_size()
    tamaño = (tamaño[0] * escala, tamaño[1] * escala)
    image = pg.transform.scale(image, tamaño)

    if colorkey is not None:
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey, pg.RLEACCEL)
    return image, image.get_rect()

def cargar_sonido(nombre):
    class NingunSonido:
        def play(self):
            pass

    if not pg.mixer or not pg.mixer.get_init():
        return NingunSonido()

    nombre_completo = os.path.join(dir_datos, nombre)
    sonido = pg.mixer.Sound(nombre_completo)

    return sonido

# clases para nuestros objetos del juego
class Puño(pg.sprite.Sprite):
    """mueve un puño cerrado en la pantalla, siguiendo el ratón"""

    def __init__(self):
        pg.sprite.Sprite.__init__(self)  # llama al inicializador de Sprite
        self.image, self.rect = cargar_image("matamoscas.png", -1)
        self.desplazamiento_puño = (-235, -80)
        self.golpeando = False

    def update(self):
        """mover el puño basado en la posición del ratón"""
        pos = pg.mouse.get_pos()
        self.rect.topleft = pos
        self.rect.move_ip(self.desplazamiento_puño)
        if self.golpeando:
            self.rect.move_ip(15, 25)

    def golpear(self, objetivo):
        """retorna verdadero si el puño colisiona con el objetivo"""
        if not self.golpeando:
            self.golpeando = True
            caja_colision = self.rect.inflate(-5, -5)
            return caja_colision.colliderect(objetivo.rect)

    def desgolpear(self):
        """llamado para retirar el puño"""
        self.golpeando = False

class Mosca(pg.sprite.Sprite):
    """mueve un mono a través de la pantalla. puede girar
    al mono cuando es golpeado."""

    def __init__(self):
        pg.sprite.Sprite.__init__(self)  # llama al inicializador de Sprite
        self.image, self.rect = cargar_image("fly.png", -1, 2)
        pantalla = pg.display.get_surface()
        self.area = pantalla.get_rect()
        self.rect.topleft = 10, 90
        self.movimiento = 18
        self.mareado = False

    def update(self):
        """caminar o girar, dependiendo del estado de la mosca"""
        if self.mareado:
            self._girar()
        else:
            self._caminar()

    def _caminar(self):
        """mover a la mosca a través de la pantalla, y girar en los extremos"""
        nueva_pos = self.rect.move((self.movimiento, 0))
        if not self.area.contains(nueva_pos):
            if self.rect.left < self.area.left or self.rect.right > self.area.right:
                self.movimiento = -self.movimiento
                nueva_pos = self.rect.move((self.movimiento, 0))
                self.image = pg.transform.flip(self.image, True, False)
        self.rect = nueva_pos

    def _girar(self):
        """girar la image de la mosca"""
        centro = self.rect.center
        self.mareado += 12
        if self.mareado >= 360:
            self.mareado = False
            self.image = self.original
        else:
            rotar = pg.transform.rotate
            self.image = rotar(self.original, self.mareado)
        self.rect = self.image.get_rect(center=centro)

    def golpeado(self):
        """esto hará que el mosca comience a girar"""
        if not self.mareado:
            self.mareado = True
            self.original = self.image

def principal():
    """esta función se llama cuando el programa inicia.
    inicializa todo lo necesario, luego corre en
    un bucle hasta que la función retorna."""
    # Inicializar todo
    golpes = 0
    pg.init()
    pantalla = pg.display.set_mode((1280, 480), pg.SCALED)
    pg.mouse.set_visible(False)

    # Crear el fondo
    fondo = pg.Surface(pantalla.get_size())
    fondo = fondo.convert()
    fondo.fill((170, 238, 187))

    # Poner texto en el fondo, centrado
    if pg.font:
        
        fuente = pg.font.Font(None, 64)
        texto = fuente.render("Aplasta a la Mosca", True, (10, 10, 10))
        pos_texto = texto.get_rect(centerx=fondo.get_width() / 2, y=10)
        fondo.blit(texto, pos_texto)

    # Mostrar el fondo
    pantalla.blit(fondo, (0, 0))
    pg.display.flip()

    # Preparar objetos del juego
    sonido_fallido = cargar_sonido("whiff.wav")
    sonido_golpe = cargar_sonido("punch.wav")
    mosca = Mosca()
    puño = Puño()
    todos_los_sprites = pg.sprite.RenderPlain((mosca, puño))
    reloj = pg.time.Clock()

    # Bucle principal
    jugando = True
    while jugando:
        reloj.tick(60)

        # Manejar eventos de entrada
        for evento in pg.event.get():
            if evento.type == pg.QUIT:
                jugando = False
            elif evento.type == pg.KEYDOWN and evento.key == pg.K_ESCAPE:
                jugando = False
            elif evento.type == pg.MOUSEBUTTONDOWN:
                if puño.golpear(mosca):
                    sonido_golpe.play()  # golpe
                    golpes = golpes + 1
                    mosca.golpeado()
                else:
                    golpes = 0
                    sonido_fallido.play()  # fallo

                fondo.fill((170, 238, 187))
                texto2 = fuente.render("Cantidad de golpes seguidos: " + str(golpes), True, (10, 30, 10))
                pos_texto2 = texto2.get_rect(centerx=fondo.get_width() / 2, y=50)
                fondo.blit(texto2, pos_texto2)
            elif evento.type == pg.MOUSEBUTTONUP:
                puño.desgolpear()

        todos_los_sprites.update()

        # Dibujar todo
        pantalla.blit(fondo, (0, 0))
        todos_los_sprites.draw(pantalla)
        pg.display.flip()

    pg.quit()

# Fin del juego

# esto llama a la función 'principal' cuando este script es ejecutado
if __name__ == "__main__":
    principal()