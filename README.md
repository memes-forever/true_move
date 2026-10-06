# Frappe CRM — локальная разработка в Docker

Стек: Frappe Framework **v16** (Python 3.14, Node 24) + Frappe CRM (`main`), MariaDB 11.8, Redis.

## Структура

```
frappe-crm/                 ← git-репозиторий инфраструктуры (compose, init.sh, README)
├── docker-compose.yml
├── init.sh
└── apps/
    └── true_move/           ← своё приложение, ОТДЕЛЬНЫЙ git-репозиторий (в корневом — в .gitignore)
```

- **frappe** и **crm** — чужой код, лежит в docker-томе `bench-data`, не редактируем.
- **true_move** — весь свой код. Лежит на Mac, в контейнере `apps/true_move` — симлинк на `/workspace/apps/true_move`.
  Всё, что Frappe генерирует в developer_mode (doctype JSON/py/js), сразу появляется здесь.
- Приложение — отдельный репозиторий, потому что на сервер его ставят `bench get-app <git-url>`.

## Что нужно

- Docker Desktop для Mac, в настройках ресурсов не меньше **4 ГБ RAM** (лучше 6).
- Порты 8000 и 9000 должны быть свободны.

## Запуск

```bash
cd /Users/vlad/america/frappe-crm
docker compose up -d
docker compose logs -f frappe      # первый запуск 10–20 минут: клонирование и сборка фронта
```

Когда в логах появится `Готово`, а затем строки `web.1 | * Running on ...`, открывайте:

- **CRM:** http://localhost:8000/crm
- **Desk (админка Frappe):** http://localhost:8000/app

Логин: `Administrator`, пароль: `admin`.

## Повседневные команды

```bash
docker compose stop                      # остановить (данные сохраняются)
docker compose start                     # запустить снова (быстро, без переустановки)
docker compose exec frappe bash          # консоль внутри контейнера
# внутри: cd frappe-bench && bench --site crm.localhost console   — Python-консоль сайта
docker compose down -v                   # ПОЛНЫЙ сброс: удалит БД и весь код bench
```

Если первый запуск упал (например, обрыв сети), просто `docker compose restart frappe`:
скрипт `init.sh` пропускает уже выполненные шаги.

## Первый свой DocType

Правильно держать доработки в **своём приложении**, а не править код CRM.

### 1. Приложение

Уже есть: `apps/true_move` (модуль `True Move`). `init.sh` само регистрирует и ставит его на сайт,
в том числе после полного сброса `down -v`.

### 2. Создать DocType через интерфейс

1. Откройте http://localhost:8000/app/doctype/new
2. Name: в единственном числе, например `Contract`, **Module:** `True Move`.
3. Добавьте поля, например:
   - `contract_number` — Data, обязательное;
   - `deal` — Link → `CRM Deal`;
   - `amount` — Currency;
   - `status` — Select (`Draft`, `Signed`, `Closed`);
   - `signed_on` — Date.
4. Сохраните.

Благодаря `developer_mode` Frappe сразу создаст:

- таблицу `tabContract` в БД;
- файлы в `apps/true_move/true_move/true_move/doctype/contract/` (`contract.json`, `contract.py`, `contract.js`);
- форму и список в Desk: http://localhost:8000/app/contract;
- REST API: `GET/POST http://localhost:8000/api/resource/Contract`.

### 3. Добавить логику

В `contract.py`:

```python
import frappe
from frappe.model.document import Document

class Contract(Document):
    def validate(self):
        if self.status == "Signed" and not self.signed_on:
            frappe.throw("Укажите дату подписания")
```

После правки Python-кода: `bench restart` не нужен в dev-режиме, достаточно обновить страницу.
Если меняли JSON/схему вручную: `bench --site crm.localhost migrate`.

### Где редактировать код

Свой код открывайте прямо на Mac: `apps/true_move`. Коммиты делайте в этом же каталоге (`cd apps/true_move && git ...`).
Чтобы почитать исходники frappe/crm или получить автодополнение по ним, используйте VS Code **Dev Containers** →
«Attach to Running Container» → `crm-frappe-1`.

## Правила

1. Не правьте код `frappe` и `crm`: все изменения делайте в `true_move` (хуки, override, свои doctype).
2. Изменения через **Customize Form** (поля в `CRM Deal`, `CRM Lead` и т.д.) хранятся в БД, не в коде.
   Выставляйте у них Module = `True Move` и выгружайте в репозиторий:
   `bench --site crm.localhost export-fixtures --app true_move` → `true_move/fixtures/*.json`.
3. Server Script / Client Script из интерфейса удобны для экспериментов, а окончательный код переносите в приложение.
4. Изменения в данных между версиями оформляйте патчами (`true_move/patches.txt`).

## Что дальше

- Кастомные поля к сделкам и лидам: в Desk через **Customize Form** (`CRM Deal`, `CRM Lead`), см. правило 2.
- Свои объекты пока видны в Desk (`/app/...`), а не в Vue-интерфейсе CRM; встраивать их туда — отдельная доработка фронтенда.
- Хуки на события CRM (`doc_events` для `CRM Deal` и др.) — в `true_move/hooks.py`.
