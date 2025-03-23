import os
import shutil

def replace_sprites():
    """
    Заменяет старые спрайты на масштабированные версии
    """
    old_dir = 'assets/sprites'
    new_dir = 'assets/sprites_resized'
    
    print("\nЗамена спрайтов:")
    print("-" * 50)
    
    # Создаем резервную копию старых спрайтов
    backup_dir = 'assets/sprites_backup'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        for filename in os.listdir(old_dir):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                shutil.copy2(os.path.join(old_dir, filename), backup_dir)
        print("Создана резервная копия старых спрайтов")
    
    # Заменяем старые спрайты на новые
    for filename in os.listdir(new_dir):
        if filename.endswith(('.png', '.jpg', '.jpeg')):
            shutil.copy2(os.path.join(new_dir, filename), old_dir)
            print(f"Заменен спрайт: {filename}")
    
    print("-" * 50)
    print("Замена завершена. Старые спрайты сохранены в assets/sprites_backup")

if __name__ == "__main__":
    replace_sprites() 