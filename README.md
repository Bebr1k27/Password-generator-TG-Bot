# Password Generator Telegram Bot

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue">
  <img src="https://img.shields.io/badge/aiogram-3.x-green">
  <img src="https://img.shields.io/badge/Telegram-Bot-blue">
</p>

---

## О проекте

**Password Generator Telegram Bot** — это удобный Telegram-бот для генерации надёжных паролей с гибкими настройками и возможностью хранения истории.

---

## Возможности

* Генерация паролей
* Гибкая настройка:
  * длина (1–200)
  * используемые символы:
    * A-Z
    * a-z
    * 0-9
    * спецсимволы
* Сохранение истории
* Очистка истории
* Быстрая повторная генерация
* Удобный UI через inline-кнопки

---

## Интерфейс

> Минималистичный Telegram UI без лишнего мусора — всё через кнопки

---

## Стек технологий

* Python 3.10+
* aiogram 3.x
* SQLite
* python-dotenv

---

## Установка

```bash
git clone https://github.com/your-username/Password-generator-TG-Bot.git
cd Password-generator-TG-Bot
pip install -r requirements.txt
```

---

## Настройка

Создай файл `.env`:

```env
BOT_TOKEN=your_telegram_bot_token
```

Получить токен можно через @BotFather

---

## Запуск

```bash
python main.py
```


---

## Логика работы

1. Пользователь запускает `/start`
2. Выбирает параметры пароля
3. Бот генерирует пароль
4. (Опционально) сохраняет в историю

---

## Автор

GitHub: https://github.com/Bebr1k27

Telegram: https://t.me/AvR37

---

## Поддержка

Если проект понравился, поставь звезду

---
