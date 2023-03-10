Для настройки подключения к базе данных используется файл `secrets.yml`. По-умолчанию используется БД sqlite из файла `dbname.db`.

Объявление классов для взаимодействия с таблицами и создание тестовых строк в таблицах прописаны в файле `orm_db.py`. Чтобы создать таблицы в БД и заполнить тестовые строки необходимо исполнить файл `orm_db.py`. Запуск приложения `uvicorn fastapi_hw:app --host localhost --port 8000 --reload`.

Асинхронное веб приложение которое обрабатывает:
 - `<host>:<port>/items/` GET-запрос на получение всех товарных позиций;
 - `<host>:<port>/stores/` GET-запрос на получение всех магазинов;
 - `<host>:<port>/sales/` POST-запрос с json-телом для сохранения данных о произведенной продаже (item_id товара + store_id магазина);
 - `<host>:<port>/stores/top/` GET-запрос на получение данных по топ 10 самых доходных магазинов за месяц (id + адрес + суммарная выручка);
 - `<host>:<port>/items/top/` GET-запрос на получение данных по топ 10 самых продаваемых товаров (id + наименование + количество проданных товаров).