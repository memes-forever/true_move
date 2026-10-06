# PyCharm: venv и интерпретатор

Код всё равно запускается в Docker (`bench start` в контейнере). Локальный venv на Mac нужен для PyCharm:
автодополнения, перехода к исходникам `frappe`/`crm`, подсветки ошибок и ruff.

Все команды — из корня репозитория.

## 1. Системные зависимости

```bash
brew install python@3.14 mysql-client pkgconf git
```

- `python@3.14` — та же версия, что в контейнере (`docker compose exec frappe frappe-bench/env/bin/python --version`).
- `mysql-client` и `pkgconf` нужны, чтобы собрать пакет `mysqlclient` (зависимость frappe).

## 2. venv

```bash
python3.14 -m venv .venv
source .venv/bin/activate
pip install -U pip wheel
```

`.venv/` уже в `.gitignore`.

## 3. Исходники frappe и crm

Берём те же ветки, что ставит `dev/init.sh` (`FRAPPE_BRANCH`, `CRM_BRANCH`). Клонируем в `.venv/src` —
так их не видно в дереве проекта, но PyCharm их индексирует как библиотеки.

```bash
mkdir -p .venv/src
git clone --depth 1 --branch version-16 https://github.com/frappe/frappe .venv/src/frappe
git clone --depth 1 --branch main       https://github.com/frappe/crm    .venv/src/crm
```

## 4. Python-зависимости

```bash
export PKG_CONFIG_PATH="$(brew --prefix mysql-client)/lib/pkgconfig"

pip install -e .venv/src/frappe
pip install -e .venv/src/crm
pip install -e .
pip install ruff pre-commit
```

Проверка:

```bash
python -c "import frappe, crm, true_move; print(frappe.__version__, frappe.__file__)"
```

### Обновить после `bench update` в контейнере

```bash
git -C .venv/src/frappe pull && git -C .venv/src/crm pull
source .venv/bin/activate
PKG_CONFIG_PATH="$(brew --prefix mysql-client)/lib/pkgconfig" pip install -e .venv/src/frappe -e .venv/src/crm
```

Полный сброс — просто `rm -rf .venv` и пройти шаги 2–4 заново.

## 5. Интерпретатор в PyCharm

1. **Settings** (`⌘,`) → **Project: true_move** → **Python Interpreter**.
2. **Add Interpreter** → **Add Local Interpreter…** → **Virtualenv Environment**.
3. **Environment: Existing**, **Interpreter:** `<корень репозитория>/.venv/bin/python` → **OK**.
4. Дождаться окончания индексации (внизу справа) — после этого `import frappe` резолвится, а
   `⌘`+клик по `frappe.get_doc` открывает исходник из `.venv/src/frappe`.

Рекомендуемые настройки:

- Плагин **Ruff** (Settings → Plugins → Marketplace), затем **Settings → Tools → Ruff**: *Run ruff when the
  python file is saved* — форматирование с табами по `pyproject.toml`, как в pre-commit.
- **Settings → Editor → Code Style → Python → Tabs and Indents:** *Use tab character* — во Frappe отступы табами.
- **Settings → Version Control → Git**: pre-commit хуки срабатывают и при коммите из PyCharm после `pre-commit install`.

## Альтернатива: интерпретатор из контейнера

PyCharm Professional умеет брать Python прямо из Docker Compose — окружение будет 1-в-1 как у работающего bench,
зато индексация медленнее и требует запущенного Docker.

1. **Add Interpreter** → **On Docker Compose…**
2. **Configuration file:** `dev/docker-compose.yml`, **Service:** `frappe` → **Next**.
3. **System Interpreter**, путь: `/home/frappe/bench-data/frappe-bench/env/bin/python` → **Create**.
4. Маппинг путей: корень репозитория ↔ `/workspace` (PyCharm подставит сам из `volumes`).
