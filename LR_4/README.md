# size2json

Небольшое Flask-приложение для задания с маршрутами `/login` и `/size2json`.

## Что делает

- `GET /login` возвращает JSON:
  `{"author":"1154880"}`
- `POST /size2json` принимает PNG-файл в поле `image` формата `multipart/form-data`
- В ответ возвращает JSON с размерами изображения:
  `{"width":123,"height":456}`
- Если передан не PNG, возвращает:
  `{"result":"invalid filetype"}`

## Дополнительно

- Главная страница `/` содержит простую форму загрузки
- Отправка файла выполняется асинхронно, без перезагрузки страницы
- Показывается thumbnail последнего успешно загруженного изображения
- Состояние последней загрузки доступно по маршруту `/last-upload`

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install flask pillow
python webapp_size2json.py
```

После запуска приложение будет доступно на `http://127.0.0.1:5000`.
