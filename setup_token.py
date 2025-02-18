# setup_token.py

def set_token():
    print("Введите токен из BotFather:")  # Сообщение для пользователя
    token = input("Токен: ")  # Запрашиваем токен
    
    # Проверка, что токен не пустой
    if not token:
        print("Ошибка: токен не может быть пустым.")
        return

    # Попытка открыть и отредактировать bot.py
    try:
        with open('bot.py', 'r') as file:
            file_data = file.readlines()

        # Ищем строку с TOKEN и заменяем её
        for i, line in enumerate(file_data):
            if line.startswith('TOKEN ='):
                file_data[i] = f'TOKEN = "{token}"\n'
                break

        # Перезаписываем bot.py с новым токеном
        with open('bot.py', 'w') as file:
            file.writelines(file_data)

        print("Токен успешно добавлен в bot.py.")  # Подтверждение успешного добавления

    except FileNotFoundError:
        print("Ошибка: файл bot.py не найден.")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    set_token()
