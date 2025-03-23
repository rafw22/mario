import os
from PIL import Image

# Целевые размеры для разных типов спрайтов
TARGET_SIZES = {
    'mario_right': (32, 32),
    'mario_jump': (32, 32),
    'goomba': (32, 32),
    'goomba_dead': (32, 32),
    'brick': (32, 32),
    'ground': (32, 32),
    'platform': (32, 32),
    'coin': (16, 16),
    'mushroom': (32, 32),
    'flower': (32, 32),
    'coin_effect': (32, 32),
    'jump_effect': (32, 32),
    'heart': (16, 16),
    'coin_icon': (16, 16)
}

def resize_sprites():
    """
    Масштабирует все спрайты до нужных размеров
    """
    sprite_dir = 'assets/sprites'
    output_dir = 'assets/sprites_resized'
    
    # Создаем директорию для масштабированных спрайтов
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    print("\nМасштабирование спрайтов:")
    print("-" * 50)
    
    for filename in os.listdir(sprite_dir):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            filepath = os.path.join(sprite_dir, filename)
            output_path = os.path.join(output_dir, filename)
            
            # Получаем имя файла без расширения
            name = os.path.splitext(filename)[0]
            
            # Если для этого спрайта определен целевой размер
            if name in TARGET_SIZES:
                target_size = TARGET_SIZES[name]
                with Image.open(filepath) as img:
                    # Масштабируем изображение с сохранением пропорций
                    resized = img.resize(target_size, Image.Resampling.LANCZOS)
                    resized.save(output_path)
                    print(f"Спрайт: {filename}")
                    print(f"Исходный размер: {img.size}")
                    print(f"Новый размер: {target_size}")
                    print("-" * 50)
            else:
                print(f"Пропущен спрайт {filename} - не определен целевой размер")
                print("-" * 50)

if __name__ == "__main__":
    resize_sprites() 