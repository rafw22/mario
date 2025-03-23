import os
from PIL import Image

def analyze_sprites():
    """
    Анализирует размеры всех спрайтов в папке assets/sprites
    """
    sprite_dir = 'assets/sprites'
    print("\nАнализ размеров спрайтов:")
    print("-" * 50)
    
    for filename in os.listdir(sprite_dir):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            filepath = os.path.join(sprite_dir, filename)
            with Image.open(filepath) as img:
                width, height = img.size
                print(f"Спрайт: {filename}")
                print(f"Размер: {width}x{height} пикселей")
                print(f"Соотношение сторон: {width/height:.2f}")
                print("-" * 50)

if __name__ == "__main__":
    analyze_sprites() 