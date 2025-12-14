import os

def register():
    print("Регистрация")
    name = input("Введите имя: ").strip()
    if not name:
        print("Имя не может быть пустым!")
        return
    
    email = input("Введите email: ").strip()
    if '@' not in email or '.' not in email:
        print("Email должен содержать '@' и '.'")
        return
    
    password = input("Введите пароль (минимум 6 символов): ")
    if len(password) < 6:
        print("Пароль слишком короткий!")
        return
    
    # Проверка существования файла и дубликата email
    if os.path.exists('users.txt'):
        try:
            with open('users.txt', 'r') as f:
                for line in f:
                    parts = line.strip().split(':')
                    if len(parts) == 3 and parts[0] == email:
                        print("Email уже зарегистрирован!")
                        return
        except FileNotFoundError:
            pass
    
    # Запись нового пользователя
    with open('users.txt', 'a') as f:
        f.write(f"{email}:{name}:{password}\n")
    print("Пользователь зарегистрирован!")

def login():
    print("Вход")
    email = input("Введите email: ").strip()
    password = input("Введите пароль: ").strip()
    
    if not os.path.exists('users.txt'):
        print("Файл с пользователями не найден!")
        return
    
    with open('users.txt', 'r') as f:
        for line in f:
            parts = line.strip().split(':')
            if len(parts) == 3 and parts[0] == email and parts[2] == password:
                print(f"Добро пожаловать, {parts[1]}!")
                return
    
    print("Неверный email или пароль!")

def main_menu():
    while True:
        print("\n=== Меню ===")
        print("1. Регистрация")
        print("2. Вход")
        print("3. Выход")
        
        choice = input("Выберите действие (1-3): ").strip()
        
        if choice == '1':
            register()
        elif choice == '2':
            login()
        elif choice == '3':
            print("До свидания!")
            break
        else:
            print("Неверный выбор! Попробуйте снова.")

# Запуск программы
if __name__ == "__main__":
    main_menu()
