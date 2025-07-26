# Telegram Support Bot

Telegram Support Bot для технической поддержки пользователей.
Имеется три вида панели:
1. Основная - она предназначена для пользователей, которые через панель будут создавать и просматривать свои запросы.
2. Панель для сотрудников технической поддержки. Доступ к этой панели можно получить, введя пароль выданный администратором. В этой панели агент поддержки может просматривать и отвечать на все запросы пользователей.
3. Админ-панель - нужна для добавления и удаления сотрудников поддержки, генерации/удаления паролей доступа, а также для отключения бота.

## Скриншот
![Screenshot](https://github.com/Blazzerrr/TelegramSupportBot/blob/master/image.png) 

## Настройка
Установите все зависимости из блока ниже с помощью PIP</br>
Скопируйте файл telegram-bot/config.py.example в telegram-bot/config.py и, следуя инструкциям внутри, заполните все обязательные для запуска переменные.
После выполнения инструкции, запустите файл sql.py
```bash
cd telegram-bot
python3 sql.py
```
Если все выполнилось без ошибок - настройка бота завершена и вы можете переходить к запуску бота.

## Запуск
```bash
cd telegram-bot
python3 bot.py
```

## Автозапуск через Docker и GitHub Actions

В репозитории присутствуют `Dockerfile` и `docker-compose.yml`, позволяющие
разворачивать бота в контейнере. Процесс автоматического деплоя на Ubuntu сервер
настраивается следующим образом:

1. Установите Docker и docker-compose на сервер.
2. Создайте каталог, например `/srv/telegram-bot`, в который будут копироваться
   файлы репозитория.
3. В настройках GitHub добавьте секреты:
   - `SERVER_HOST` – адрес сервера;
   - `SERVER_USER` – SSH пользователь;
   - `SERVER_SSH_KEY` – приватный ключ для подключения;
   - `SERVER_PATH` – путь из шага 2;
   - при необходимости `SERVER_PORT` – порт SSH (по умолчанию 22).
4. После изменения `telegram-bot/config.py` на сервере, GitHub Actions при каждом
   push в ветку `master` или `main` копирует файлы и выполняет
   `docker compose up -d --build`, перезапуская бота.

## Зависимости
- pyTelegramBotAPI
- cryptography
- pymysql

## Донат
— USDT TRC20 / TRX : **<code>TGGu7SE2AiTqKtyiqSn8abZeh62nLZPg7N</code>**</br>
— USDT ERC20 / ETH : **<code>0xD2F03940ec729BfDFA79a5b7a867e8F55E470b67</code>**</br>
— BTC: **<code>bc1qhajqf6k3lass7sq8y2p3jg6xav6hrnguacdgsz</code>**</br>
— XRP: **<code>r3do8Bp7qfobrv5QmyBqp3PzJ2k8VQtGY8</code>**</br>
— BNB: **<code>bnb1wv357zh590hmys3z07fv56mv8uqua4cvz2p3dw</code>**</br>
— DOGE: **<code>DL1vn98EWknvSsbkFeruZYk3DhSLft8QWQ</code>**
