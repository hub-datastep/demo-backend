import requests

# URL вашего сервера
url = "http://127.0.0.1:8080/upd/upload/"

# Путь к тестовому файлу
file_path = "d:\\utd-parsing1\\backups\\Трубы из сшитого полиэтилена\\Отгрузка труба Гребной 2.pdf"

# Открываем файл и отправляем его с помощью POST-запроса
with open(file_path, "rb") as f:
    files = {"file": (file_path, f)}
    response = requests.post(url, files=files)

# Выводим результат
print("Статус-код:", response.status_code)
print("Ответ сервера:", response.json())
