# Telegram Games Bot 🎮

Многопользовательский Telegram-бот с коллекцией мини-игр, развёрнутый на Render.com.

## Игры

- ❌ **Крестики-нолики** — против бота с простым ИИ
- 🔢 **Угадай число** — бот загадывает 1-100
- ✊ **Камень-Ножницы-Бумага** — классика
- 🔤 **Виселица** — угадывание русских слов по буквам
- ⚡ **Быстрый клик** — реакция в миллисекундах

## Технологии

- Python 3.11+
- [aiogram 3.x](https://docs.aiogram.dev/) — фреймворк Telegram-бота
- [FastAPI](https://fastapi.tiangolo.com/) — веб-фреймворк для webhook
- Render.com — хостинг (бесплатный тариф)

## Установка и запуск локально

```bash
git clone https://github.com/YOUR_USERNAME/telegram-games-bot.git
cd telegram-games-bot
pip install -r requirements.txt
cp .env.example .env
# Отредактируй .env и впиши свой BOT_TOKEN
python main.py
```

## Деплой на Render

1. Создай аккаунт на [render.com](https://render.com/)
2. New → Web Service → подключи GitHub-репозиторий
3. Настрой:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Добавь переменные окружения:
   - `BOT_TOKEN` — токен от @BotFather
   - `RENDER_EXTERNAL_URL` — URL сервиса (автоматически подставляется Render)
5. Нажми Deploy

## Настройка вебхука

Вебхук устанавливается автоматически при старте бота. Если нужно вручную:

```
GET https://api.telegram.org/bot<TOKEN>/setWebhook?url=<RENDER_URL>/webhook
```

## Лицензия

MIT
