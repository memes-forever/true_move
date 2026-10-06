### True Move

Доработки Frappe CRM для True Move: справочник грузчиков (Mover), состав переезда (Move Item),
мобильная страница грузчика `/moves`, кастомные поля и раскладки форм CRM (fixtures).

Требует: Frappe Framework **v16** + [Frappe CRM](https://github.com/frappe/crm).

Локальная разработка в Docker — см. [dev/README.md](dev/README.md).

### Установка на сервер

Предполагается, что bench уже установлен ([инструкция](https://docs.frappe.io/framework/user/en/installation)).

```bash
bench init --frappe-branch version-16 --python python3.14 frappe-bench
cd frappe-bench

bench get-app crm --branch main
bench get-app https://github.com/memes-forever/true_move --branch main

bench new-site crm.example.com
bench --site crm.example.com install-app crm
bench --site crm.example.com install-app true_move

sudo bench setup production $USER      # nginx + supervisor
```

Если репозиторий приватный, серверу нужен доступ к GitHub: deploy key
(`git@github.com:memes-forever/true_move.git`) или токен в URL.

### Обновление

```bash
cd frappe-bench
bench update --apps true_move    # бэкап, git pull, migrate (patches + fixtures), build, restart
```

Или вручную:

```bash
cd apps/true_move && git pull && cd ../..
bench --site crm.example.com migrate
bench build --app true_move
bench restart
```

`migrate` применяет патчи из `true_move/patches.txt` и fixtures из `true_move/fixtures/`
(кастомные поля, Property Setter, раскладки CRM, роль «Грузчик»).

### Contributing

This app uses `pre-commit` for code formatting and linting:

```bash
pre-commit install
```

### License

mit
