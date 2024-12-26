# Авторизация

## Как авторизоваться и получить Bearer токен

1. Отправляем запрос `POST /auth/sign_in`

    - В заголовках указываем хедер `Content-Type: application/x-www-form-urlencoded`
    - В теле запроса передаём:
        - `username` (str) - логин аккаунта
        - `password` (str) - пароль аккаунта

2. В ответе получаем

   ```json
   {
     "access_token": "Ваш токен",
     "token_type": "bearer"
   }
   ```

> **Сохраняем токен для последующего использования**
