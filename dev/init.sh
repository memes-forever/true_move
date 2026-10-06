#!/bin/bash
# Идемпотентная установка: каждый шаг пропускается, если уже выполнен,
# поэтому после сбоя достаточно просто перезапустить контейнер.
set -euo pipefail

BENCH_ROOT=/home/frappe/bench-data
BENCH=$BENCH_ROOT/frappe-bench
SITE=crm.localhost
FRAPPE_BRANCH=version-16
CRM_BRANCH=main
MY_APP=true_move

cd "$BENCH_ROOT"

# 1. Bench + Frappe
if [ ! -d "$BENCH/apps/frappe" ]; then
    echo ">>> Создаю bench (Frappe $FRAPPE_BRANCH)..."
    rm -rf "$BENCH"
    bench init --skip-redis-config-generation \
        --frappe-branch "$FRAPPE_BRANCH" \
        --python python3.14 \
        frappe-bench
fi

cd "$BENCH"

# 2. Подключение к контейнерам БД и Redis
bench set-mariadb-host mariadb
bench set-redis-cache-host redis://redis:6379
bench set-redis-queue-host redis://redis:6379
bench set-redis-socketio-host redis://redis:6379

# Redis — отдельный контейнер; watch (пересборка фронта) включайте вручную при необходимости
sed -i '/redis/d' ./Procfile
sed -i '/watch/d' ./Procfile

# 3. Приложение CRM
if [ ! -d "$BENCH/apps/crm" ]; then
    echo ">>> Скачиваю Frappe CRM ($CRM_BRANCH)..."
    bench get-app crm --branch "$CRM_BRANCH"
fi

# 3a. Своё приложение: корень репозитория на Mac (/workspace), в bench — симлинк на него.
#     Не bind mount: шаг 1 делает rm -rf "$BENCH".
if [ -d "apps/$MY_APP" ] && [ ! -L "apps/$MY_APP" ]; then
    echo ">>> Убираю старую копию $MY_APP из тома в $BENCH_ROOT/$MY_APP.bak"
    rm -rf "$BENCH_ROOT/$MY_APP.bak"
    mv "apps/$MY_APP" "$BENCH_ROOT/$MY_APP.bak"
fi
ln -sfn /workspace "apps/$MY_APP"
# Переустановить пакет, если editable-установка смотрит в старый путь (или её нет)
if ! ./env/bin/python -c "import $MY_APP" 2>/dev/null; then
    echo ">>> Устанавливаю пакет $MY_APP..."
    ./env/bin/pip install -q -e "apps/$MY_APP"
fi
if ! grep -qx "$MY_APP" sites/apps.txt; then
    echo ">>> Регистрирую $MY_APP..."
    sed -i -e '$a\' sites/apps.txt   # гарантировать перевод строки в конце
    echo "$MY_APP" >> sites/apps.txt
fi

# 4. Сайт
if [ ! -f "$BENCH/sites/$SITE/site_config.json" ]; then
    echo ">>> Создаю сайт $SITE..."
    bench new-site "$SITE" \
        --force \
        --mariadb-root-password 123 \
        --admin-password admin \
        --mariadb-user-host-login-scope='%'
    bench --site "$SITE" install-app crm
    bench --site "$SITE" install-app "$MY_APP"
    bench --site "$SITE" set-config developer_mode 1
    bench --site "$SITE" set-config mute_emails 1
    bench --site "$SITE" set-config server_script_enabled 1
    bench --site "$SITE" clear-cache
    bench use "$SITE"
fi

echo ">>> Готово: http://localhost:8000/crm  (Administrator / admin)"
exec bench start
