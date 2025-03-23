import pygame
import sys
import random
import os
from levels import LEVELS  # Импортируем уровни

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Основные константы игры
WINDOW_WIDTH = 800   # Ширина окна игры
WINDOW_HEIGHT = 600  # Высота окна игры
FPS = 60            # Частота обновления экрана

# Определение цветов в формате RGB
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)

# Создание главного окна игры
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Mario Bros")
clock = pygame.time.Clock()

# Функция для загрузки изображений
def load_image(name):
    """
    Загружает изображение из папки assets/sprites
    convert_alpha() оптимизирует изображение для быстрого отображения
    """
    return pygame.image.load(os.path.join('assets', 'sprites', name)).convert_alpha()

# Словарь со всеми спрайтами игры
SPRITES = {
    'mario_right': load_image('mario_right.png'),    # Спрайт Марио, смотрящего вправо
    'mario_jump': load_image('mario_jump.png'),      # Спрайт Марио в прыжке
    'goomba': load_image('goomba.png'),              # Спрайт врага (гумба)
    'goomba_dead': load_image('goomba_dead.png'),    # Спрайт раздавленной гумбы
    'brick': load_image('brick.png'),                # Спрайт блока
    'ground': load_image('ground.png'),              # Спрайт земли
    'platform': load_image('platform.png'),          # Спрайт платформы
    'coin': load_image('coin.png'),                  # Спрайт монеты
    'mushroom': load_image('mushroom.png'),          # Спрайт гриба (бонус)
    'flower': load_image('flower.png'),              # Спрайт цветка (бонус)
    'coin_effect': load_image('coin_effect.png'),    # Эффект сбора монеты
    'jump_effect': load_image('jump_effect.png'),    # Эффект прыжка
    'heart': load_image('heart.png'),                # Иконка жизни
    'coin_icon': load_image('coin_icon.png')         # Иконка монеты
}

# Создание отраженного спрайта для движения влево
SPRITES['mario_left'] = pygame.transform.flip(SPRITES['mario_right'], True, False)

class Player(pygame.sprite.Sprite):
    """
    Класс игрока (Марио)
    Управляет всеми характеристиками и поведением главного героя
    """
    def __init__(self):
        super().__init__()
        # Инициализация спрайта и его размеров
        self.image = SPRITES['mario_right']
        self.rect = self.image.get_rect()
        # Начальная позиция
        self.rect.x = 100
        self.rect.y = WINDOW_HEIGHT - 100
        # Физические характеристики
        self.speed_x = 0
        self.speed_y = 0
        self.jumping = False
        self.double_jump_available = True  # Доступность двойного прыжка
        self.gravity = 0.8
        self.jump_speed = -15
        # Характеристики персонажа
        self.facing_right = True
        self.lives = 3
        self.score = 0
        self.power_up = False
        self.invincible = False
        self.invincible_timer = 0

    def jump(self):
        """
        Обработка прыжка игрока
        Включает логику одиночного и двойного прыжка
        """
        if not self.jumping:  # Первый прыжок
            self.speed_y = self.jump_speed
            self.jumping = True
            self.double_jump_available = True
            return True
        elif self.double_jump_available:  # Двойной прыжок
            self.speed_y = self.jump_speed
            self.double_jump_available = False
            return True
        return False

    def update(self):
        """
        Обновление состояния игрока каждый кадр
        Включает физику движения, гравитацию и обновление спрайтов
        """
        # Применение гравитации
        self.speed_y += self.gravity
        self.rect.y += self.speed_y

        # Движение по горизонтали
        self.rect.x += self.speed_x

        # Обновление спрайта в зависимости от направления движения
        if self.speed_x > 0:
            self.facing_right = True
            self.image = SPRITES['mario_right']
        elif self.speed_x < 0:
            self.facing_right = False
            self.image = SPRITES['mario_left']

        # Обновление спрайта при прыжке
        if self.jumping:
            self.image = SPRITES['mario_jump']

        # Ограничение движения только по нижней границе экрана
        if self.rect.bottom > WINDOW_HEIGHT - 50:
            self.rect.bottom = WINDOW_HEIGHT - 50
            self.speed_y = 0
            self.jumping = False
            self.double_jump_available = True

        # Обновление таймера неуязвимости
        if self.invincible:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.invincible = False

class Platform(pygame.sprite.Sprite):
    """
    Класс платформ
    Создает различные типы платформ (земля, платформы, блоки)
    """
    def __init__(self, x, y, width, type='ground'):
        super().__init__()
        # Выбор типа платформы и соответствующего спрайта
        if type == 'ground':
            self.image = pygame.transform.scale(SPRITES['ground'], (width, 32))
        elif type == 'platform':
            self.image = pygame.transform.scale(SPRITES['platform'], (width, 32))
        elif type == 'brick':
            self.image = pygame.transform.scale(SPRITES['brick'], (32, 32))
        # Установка позиции
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

class Coin(pygame.sprite.Sprite):
    """
    Класс монет
    Создает собираемые монеты с определенной ценностью
    """
    def __init__(self, x, y):
        super().__init__()
        self.image = SPRITES['coin']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.value = 100  # Количество очков за сбор монеты

class PowerUp(pygame.sprite.Sprite):
    """
    Класс бонусов (грибы и цветки)
    Создает движущиеся бонусы с разными эффектами
    """
    def __init__(self, x, y, type='mushroom'):
        super().__init__()
        self.type = type
        # Выбор типа бонуса и его характеристик
        if type == 'mushroom':
            self.image = SPRITES['mushroom']
            self.value = 1000
            self.speed_x = 2
            self.speed_y = 0
            self.gravity = 0.8
            self.jumping = False
        else:
            self.image = SPRITES['flower']
            self.value = 2000
            self.speed_x = 0
            self.speed_y = 0
            self.gravity = 0
            self.jumping = False
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, platforms):
        """
        Обновление движения бонуса
        Включает движение по горизонтали и гравитацию
        """
        if self.type == 'mushroom':
            # Применяем гравитацию
            self.speed_y += self.gravity
            self.rect.y += self.speed_y

            # Движение по горизонтали
            self.rect.x += self.speed_x

            # Проверяем столкновения с платформами
            hits = pygame.sprite.spritecollide(self, platforms, False)
            if hits:
                # Если столкнулись с платформой снизу
                if self.speed_y > 0:
                    self.rect.bottom = hits[0].rect.top
                    self.speed_y = 0
                    self.jumping = False
                # Если столкнулись с платформой сверху
                elif self.speed_y < 0:
                    self.rect.top = hits[0].rect.bottom
                    self.speed_y = 0

                # Если столкнулись с платформой сбоку
                if self.speed_x > 0:
                    self.rect.right = hits[0].rect.left
                    self.speed_x *= -1
                elif self.speed_x < 0:
                    self.rect.left = hits[0].rect.right
                    self.speed_x *= -1

            # Ограничение движения по краям экрана
            if self.rect.left < 0:
                self.rect.left = 0
                self.speed_x *= -1
            if self.rect.right > WINDOW_WIDTH:
                self.rect.right = WINDOW_WIDTH
                self.speed_x *= -1

class Goomba(pygame.sprite.Sprite):
    """
    Класс врагов (гумба)
    Создает движущихся врагов, которые ходят по платформам
    """
    def __init__(self, x, y, current_level):
        super().__init__()
        self.image = SPRITES['goomba']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.speed_x = 2
        self.speed_y = 0
        self.gravity = 0.8
        self.dead = False
        self.death_timer = 30
        self.current_level = current_level

    def update(self, platforms):
        """
        Обновление состояния врага
        Включает движение по платформам и анимацию смерти
        """
        if not self.dead:
            # Применяем гравитацию
            self.speed_y += self.gravity
            self.rect.y += self.speed_y

            # Движение по горизонтали
            self.rect.x += self.speed_x

            # Проверяем столкновения с платформами
            hits = pygame.sprite.spritecollide(self, platforms, False)
            if hits:
                # Если столкнулись с платформой снизу
                if self.speed_y > 0:
                    self.rect.bottom = hits[0].rect.top
                    self.speed_y = 0
                # Если столкнулись с платформой сверху
                elif self.speed_y < 0:
                    self.rect.top = hits[0].rect.bottom
                    self.speed_y = 0

                # Если столкнулись с платформой сбоку или дошли до края
                if self.speed_x > 0:
                    if self.rect.right >= hits[0].rect.right:
                        self.speed_x *= -1
                elif self.speed_x < 0:
                    if self.rect.left <= hits[0].rect.left:
                        self.speed_x *= -1

            # Ограничение движения по краям уровня
            if self.rect.left < 0:
                self.rect.left = 0
                self.speed_x *= -1
            if self.rect.right > LEVELS[self.current_level]['width']:
                self.rect.right = LEVELS[self.current_level]['width']
                self.speed_x *= -1
        else:
            self.death_timer -= 1
            if self.death_timer <= 0:
                self.kill()

class Effect(pygame.sprite.Sprite):
    """
    Класс визуальных эффектов
    Создает временные эффекты (сбор монеты, прыжок)
    """
    def __init__(self, x, y, type='coin'):
        super().__init__()
        if type == 'coin':
            self.image = SPRITES['coin_effect']
        else:
            self.image = SPRITES['jump_effect']
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.lifetime = 20  # Длительность эффекта в кадрах

    def update(self):
        """
        Обновление эффекта
        Удаляет эффект после истечения времени жизни
        """
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

class Game:
    """
    Основной класс игры
    Управляет игровым процессом, уровнями и состоянием игры
    """
    def __init__(self):
        # Создание групп спрайтов для разных типов объектов
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.power_ups = pygame.sprite.Group()
        self.goombas = pygame.sprite.Group()
        self.dead_goombas = pygame.sprite.Group()
        self.effects = pygame.sprite.Group()
        # Создание игрока
        self.player = Player()
        # Инициализация состояния игры
        self.running = True
        self.game_state = "menu"
        self.font = pygame.font.Font(None, 36)
        self.current_level = 'LEVEL_1'
        # Настройка камеры
        self.camera_x = 0
        # Настройка первого уровня
        self.setup_level()

    def setup_level(self):
        """
        Настройка уровня
        Создает все объекты уровня (платформы, монеты, враги и т.д.)
        """
        # Очистка всех групп спрайтов
        self.all_sprites.empty()
        self.platforms.empty()
        self.coins.empty()
        self.power_ups.empty()
        self.goombas.empty()
        self.dead_goombas.empty()
        self.effects.empty()

        # Получаем данные текущего уровня
        level_data = LEVELS[self.current_level]

        # Добавление игрока
        self.player.rect.x = 100
        self.player.rect.y = WINDOW_HEIGHT - 100
        self.all_sprites.add(self.player)

        # Создание платформ
        for ground in level_data['ground']:
            platform = Platform(ground['x'], ground['y'], ground['width'], ground['type'])
            self.platforms.add(platform)
            self.all_sprites.add(platform)

        for platform_data in level_data['platforms']:
            platform = Platform(platform_data['x'], platform_data['y'], 
                              platform_data['width'], platform_data['type'])
            self.platforms.add(platform)
            self.all_sprites.add(platform)

        # Создание монет
        for coin_data in level_data['coins']:
            coin = Coin(coin_data['x'], coin_data['y'])
            self.coins.add(coin)
            self.all_sprites.add(coin)

        # Создание бонусов
        for power_up_data in level_data['power_ups']:
            power_up = PowerUp(power_up_data['x'], power_up_data['y'], power_up_data['type'])
            self.power_ups.add(power_up)
            self.all_sprites.add(power_up)

        # Создание врагов
        for goomba_data in level_data['goombas']:
            goomba = Goomba(goomba_data['x'], goomba_data['y'], self.current_level)
            self.goombas.add(goomba)
            self.all_sprites.add(goomba)

        # Создание чекпоинта
        self.checkpoint = pygame.Rect(
            level_data['checkpoint']['x'],
            level_data['checkpoint']['y'],
            level_data['checkpoint']['width'],
            level_data['checkpoint']['height']
        )
        self.next_level = level_data['checkpoint']['next_level']

        # Сброс позиции камеры
        self.camera_x = 0

    def update_camera(self):
        """
        Обновление позиции камеры
        Камера следует за игроком, когда он приближается к краям экрана
        """
        # Если игрок приближается к правому краю экрана
        if self.player.rect.right > WINDOW_WIDTH - 200:
            self.camera_x = self.player.rect.right - (WINDOW_WIDTH - 200)
        # Если игрок приближается к левому краю экрана
        elif self.player.rect.left < 200:
            self.camera_x = self.player.rect.left - 200
        # Ограничиваем камеру границами уровня
        self.camera_x = max(0, min(self.camera_x, LEVELS[self.current_level]['width'] - WINDOW_WIDTH))

    def handle_menu(self):
        """
        Обработка главного меню
        Управляет отображением и взаимодействием с меню
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.game_state = "playing"

        # Отрисовка меню
        screen.fill(BLACK)
        title = self.font.render("Mario Bros", True, WHITE)
        start_text = self.font.render("Нажмите ПРОБЕЛ для начала", True, WHITE)
        
        screen.blit(title, (WINDOW_WIDTH//2 - title.get_width()//2, WINDOW_HEIGHT//3))
        screen.blit(start_text, (WINDOW_WIDTH//2 - start_text.get_width()//2, WINDOW_HEIGHT//2))

    def handle_game(self):
        """
        Обработка игрового процесса
        Управляет всеми игровыми механиками и взаимодействиями
        """
        # Обработка событий
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.game_state = "menu"
                if event.key == pygame.K_SPACE:
                    if self.player.jump():
                        effect = Effect(self.player.rect.centerx, self.player.rect.bottom, 'jump')
                        self.effects.add(effect)
                        self.all_sprites.add(effect)

        # Управление персонажем
        keys = pygame.key.get_pressed()
        self.player.speed_x = 0
        if keys[pygame.K_LEFT]:
            self.player.speed_x = -5
        if keys[pygame.K_RIGHT]:
            self.player.speed_x = 5

        # Обновление всех объектов
        for sprite in self.all_sprites:
            if isinstance(sprite, (PowerUp, Goomba)):
                sprite.update(self.platforms)
            else:
                sprite.update()

        # Проверка столкновений с платформами
        hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
        if hits:
            self.player.rect.bottom = hits[0].rect.top
            self.player.speed_y = 0
            self.player.jumping = False

        # Сбор монет
        coin_hits = pygame.sprite.spritecollide(self.player, self.coins, True)
        for coin in coin_hits:
            self.player.score += coin.value
            effect = Effect(coin.rect.centerx, coin.rect.centery, 'coin')
            self.effects.add(effect)
            self.all_sprites.add(effect)

        # Сбор бонусов
        power_up_hits = pygame.sprite.spritecollide(self.player, self.power_ups, True)
        for power_up in power_up_hits:
            self.player.score += power_up.value
            if power_up.type == 'mushroom':
                self.player.power_up = True
            else:
                self.player.invincible = True
                self.player.invincible_timer = 300

        # Столкновение с врагами
        if not self.player.invincible:
            goomba_hits = pygame.sprite.spritecollide(self.player, self.goombas, False)
            for goomba in goomba_hits:
                if self.player.speed_y > 0:
                    if (self.player.rect.bottom <= goomba.rect.centery and 
                        self.player.rect.right > goomba.rect.left and 
                        self.player.rect.left < goomba.rect.right):
                        goomba.dead = True
                        goomba.image = SPRITES['goomba_dead']
                        self.player.speed_y = self.player.jump_speed / 2
                        self.player.score += 500
                        self.goombas.remove(goomba)
                        self.dead_goombas.add(goomba)
                        break
                
                self.player.lives -= 1
                if self.player.lives <= 0:
                    self.game_state = "menu"
                    self.player.lives = 3
                    self.player.score = 0
                    self.setup_level()
                else:
                    self.player.rect.x = 100
                    self.player.rect.y = WINDOW_HEIGHT - 100
                    self.player.speed_y = 0
                    self.player.jumping = False
                    self.player.double_jump_available = True

        # Обновление мертвых врагов
        for dead_goomba in self.dead_goombas:
            dead_goomba.death_timer -= 1
            if dead_goomba.death_timer <= 0:
                dead_goomba.kill()

        # Проверка достижения чекпоинта
        checkpoint_rect = pygame.Rect(
            self.checkpoint.x - self.camera_x,
            self.checkpoint.y,
            self.checkpoint.width,
            self.checkpoint.height
        )
        if self.player.rect.colliderect(checkpoint_rect):
            self.current_level = self.next_level
            self.setup_level()

        # Обновление камеры
        self.update_camera()

        # Отрисовка игры
        screen.fill(BLUE)
        
        # Отрисовка всех спрайтов с учетом камеры
        for sprite in self.all_sprites:
            screen.blit(sprite.image, (sprite.rect.x - self.camera_x, sprite.rect.y))
        
        # Отображение счета и жизней
        score_text = self.font.render(f"Счет: {self.player.score}", True, WHITE)
        lives_text = self.font.render(f"Жизни: {self.player.lives}", True, WHITE)
        level_text = self.font.render(f"Уровень: {self.current_level}", True, WHITE)
        screen.blit(score_text, (10, 10))
        screen.blit(lives_text, (10, 40))
        screen.blit(level_text, (10, 70))

    def run(self):
        """
        Основной игровой цикл
        Управляет состоянием игры и обновлением экрана
        """
        while self.running:
            if self.game_state == "menu":
                self.handle_menu()
            elif self.game_state == "playing":
                self.handle_game()

            pygame.display.flip()
            clock.tick(FPS)

        pygame.quit()
        sys.exit()

# Запуск игры
if __name__ == "__main__":
    game = Game()
    game.run() 