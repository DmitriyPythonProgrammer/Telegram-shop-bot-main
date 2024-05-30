import psycopg2
import sys
from datetime import date

from bot_config import ADMIN_ID

sys.path.append("/telegram_bot")
sys.path.append("/telegram_bot/markups")


def create_table():
    print("Creating table if not exists...")
    cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS products (
    "id" SERIAL PRIMARY KEY,
	"product_name"	TEXT,
	"available"	BIGINT DEFAULT 0,
	"price_day"	BIGINT DEFAULT 0,
	"deposit"	BIGINT DEFAULT 0,
	"photo"	TEXT DEFAULT '',
	"name_button"	TEXT DEFAULT '',
	"rent" BIGINT DEFAULT 0,
	"price" BIGINT DEFAULT 0,
	"online_product" BIGINT DEFAULT 0
    );
    """)
    cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS "users" (
	"id"    SERIAL PRIMARY KEY,
	"username_tg"	TEXT,
	"user_id" BIGINT,
	"date" TEXT
    )
    """)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS "admins" (
    	"user_id"	BIGINT PRIMARY KEY,
    	"username_tg"	TEXT
        )
        """)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS "orders" (
        "id" SERIAL PRIMARY KEY,
        "user_name" TEXT DEFAULT '',
        "user_id" BIGINT,
        "products" TEXT[][] DEFAULT '{}',
        "rent_price" BIGINT DEFAULT 0,
        "deposit_price" BIGINT DEFAULT 0,
        "final_price" BIGINT DEFAULT 0,
        "price" BIGINT DEFAULT 0,
        "method" TEXT DEFAULT '',
        "address" TEXT DEFAULT '',
        "pay_method" TEXT DEFAULT '',
        "date" TEXT DEFAULT ''
        )
        """) #method 0 - вывоз, 1 - доставка pay_method 0- наличные, 1 - карта
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS "suggestions" (
    	"id"	SERIAL PRIMARY KEY,
    	"username_tg"	TEXT,
    	"user_id" BIGINT,
    	"actual" BIGINT,
    	"suggestion"   TEXT,
    	"date" TEXT DEFAULT ''
        )
        """)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS "questions" (
        "id"	SERIAL PRIMARY KEY,
        "username_tg"	TEXT,
        "user_id" BIGINT,
        "actual" BIGINT,
        "question"   TEXT,
        "date" TEXT DEFAULT ''
        )
        """)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS "user_data" (
        "user_id" BIGINT PRIMARY KEY,
        "showed" BIGINT DEFAULT 0,
        "choices" TEXT[][] DEFAULT '{}',
        "rent_price" BIGINT DEFAULT 0,
        "deposit_price" BIGINT DEFAULT 0,
        "final_price" BIGINT DEFAULT 0,
        "offset_" BIGINT DEFAULT 0,
        "price" BIGINT DEFAULT 0
        )
        """)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS "bans" (
    	"id"    SERIAL PRIMARY KEY,
    	"username_tg"	TEXT,
    	"id_tg" BIGINT
        )
        """)
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS "settings" (
        "id"    SERIAL PRIMARY KEY,
        "section" TEXT,
        "name"	TEXT,
        "text_for_user" TEXT,
        "changeable" BIGINT,
        "may_be_empty" BIGINT,
        "value" TEXT,
        "value_type" TEXT
        )
        """)
    base.commit()
    print("Successfully!")


def sql_start():
    print("Connecting to the database...")
    global base, cursor
    base = psycopg2.connect(dbname='postgres', user='postgres', password='119788', host='localhost')
    cursor = base.cursor()
    print("Successfully!")


async def truncate_settings():
    cursor.execute("TRUNCATE settings")
    base.commit()


async def get_setting(setting_name):
    cursor.execute("SELECT value FROM settings WHERE name = %s", (setting_name,))
    check = cursor.fetchone()
    if check is None:
        return None
    return check[0]


async def update_setting(setting_name, value):
    cursor.execute("UPDATE settings SET value = %s WHERE name = %s", (value, setting_name))
    base.commit()


async def add_setting(section, name, value, text_for_user, changeable, may_be_empty, value_type):
    cursor.execute(
        "INSERT INTO settings(section, name, value, text_for_user, changeable, may_be_empty, value_type) VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING",
        (section, name, value, text_for_user, changeable, may_be_empty, value_type))
    base.commit()


async def add_suggestion(username_tg, user_id, suggestion):
    date_create = str(date.today())
    cursor.execute("INSERT INTO suggestions(user_id, username_tg, suggestion, date) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", (user_id, username_tg, suggestion, date_create))
    base.commit()


async def add_question(username_tg, user_id, question):
    date_create = str(date.today())
    cursor.execute("INSERT INTO questions(user_id, username_tg, question, date) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", (user_id, username_tg, question, date_create))
    base.commit()


async def add_admin(user_id, username_tg):
    cursor.execute("INSERT INTO admins(user_id, username_tg) VALUES (%s, %s) ON CONFLICT DO NOTHING", (user_id, username_tg))
    base.commit()


async def delete_admin(username_tg):
    cursor.execute("DELETE FROM admins WHERE username_tg = %s", (username_tg, ))
    base.commit()


async def return_admins():
    cursor.execute("SELECT user_id FROM admins")
    result = []
    for i in cursor.fetchall():
        result.append(i[0])
    result.append(ADMIN_ID)
    return result


async def return_admins_usernames():
    cursor.execute("SELECT username_tg FROM admins")
    result = []
    for i in cursor.fetchall():
        result.append(i[0])
    return result


async def add_value(name, count=0):
    cursor.execute("SELECT (available) FROM products WHERE product_name = %s", ([name]))
    available = cursor.fetchone()[0] + count
    cursor.execute("UPDATE products SET available = %s WHERE product_name = %s ", (available, name))
    base.commit()


async def add_user(username, id, date):
    cursor.execute("INSERT INTO users(username_tg, user_id, date) VALUES(%s, %s, %s) ON CONFLICT DO NOTHING;", (username, id, date))
    base.commit()


async def get_user_id(username):
    cursor.execute("SELECT user_id FROM users WHERE username_tg = %s", (username,))
    res = cursor.fetchone()
    if res == None:
        return None
    else:
        return res[0]


async def get_order_by_id(id):
    cursor.execute("SELECT user_name, date FROM orders WHERE id = %s", (id,))
    res = cursor.fetchone()
    return res


async def add_ban(username, id):
    assert (id is None), "Id is null"
    cursor.execute("INSERT INTO bans(username_tg, id_tg) VALUES(%s, %s) ON CONFLICT DO NOTHING;", (username, id))
    base.commit()


async def un_ban(username):
    cursor.execute("DELETE FROM bans WHERE username_tg = %s", (username,))
    base.commit()


async def is_banned(id):
    cursor.execute("SELECT username_tg FROM bans WHERE id_tg = %s", (id,))
    res = cursor.fetchone()
    if res is None:
        return False
    else:
        return True


async def add_data(id):
    cursor.execute("INSERT INTO user_data(user_id) VALUES(%s) ON CONFLICT DO NOTHING;", (id,))
    base.commit()


async def clear_data(id):
    cursor.execute("UPDATE user_data SET showed = %s, choices = %s, "
                   "rent_price = %s, deposit_price = %s, final_price = %s, offset_ = %s "
                   " WHERE user_id = %s",
                   (0, [], 0, 0, 0, 0, id))
    base.commit()


async def update_data(data):
    data = tuple(data)
    cursor.execute("UPDATE user_data SET showed = %s, choices = %s, "
                   "rent_price = %s, deposit_price = %s, final_price = %s, offset_ = %s, price = %s "
                   " WHERE user_id = %s", (data[1], data[2], data[3], data[4], data[5], data[6], data[7], data[0]))
    base.commit()


async def get_data(id):
    cursor.execute("SELECT * FROM user_data WHERE user_id = %s", (id,))
    data = cursor.fetchone()
    if data != None:
        return list(data)
    else:
        return False


async def return_available(name: str):
    cursor.execute("SELECT available FROM products WHERE product_name = %s", (name,))
    available = cursor.fetchone()
    return available


async def set_available(name: str, count):
    cursor.execute("UPDATE products SET available = %s WHERE product_name = %s", (count, name))
    base.commit()


async def add_order(data, method, name, address=''):
    data = tuple(data)
    date_create = str(date.today())
    cursor.execute("INSERT INTO orders(user_id, user_name, products, rent_price, deposit_price, final_price, price, method, address, date) "
                   "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING", (data[0], name, data[2], data[3], data[4], data[5], data[7], method, address, date_create))
    base.commit()


async def return_all_bans():
    cursor.execute("SELECT * FROM bans")
    res = cursor.fetchall()
    return res


async def return_all_users():
    cursor.execute("SELECT * FROM users")
    res = cursor.fetchall()
    return res


async def return_all_orders():
    cursor.execute("SELECT * FROM orders")
    res = cursor.fetchall()
    return res


async def return_all_orders_date(id):
    cursor.execute("SELECT date FROM orders WHERE user_id = %s", (id,))
    check = cursor.fetchall()
    return check


async def return_all_questions_date(id):
    cursor.execute("SELECT date FROM questions WHERE user_id = %s", (id,))
    check = cursor.fetchall()
    return check


async def return_all_suggestions_date(id):
    cursor.execute("SELECT date FROM suggestions WHERE user_id = %s", (id,))
    check = cursor.fetchall()
    return check


async def checker():
    cursor.execute("SELECT * FROM products WHERE available != 0 LIMIT 1")
    check = cursor.fetchone()
    return check


async def return_products(offset, limit):
    cursor.execute(f"SELECT * FROM products WHERE available != 0 LIMIT {limit} OFFSET {offset}")
    return cursor.fetchall()


async def return_count_products():
    cursor.execute("SELECT COUNT(*) FROM products WHERE available != 0")
    return cursor.fetchone()


async def get_info(name):
    cursor.execute("SELECT product_name, price, price_day, deposit, online_product FROM products WHERE product_name = %s", (name,))
    product = cursor.fetchone()
    return product


async def add_pay_method(method, id):
    cursor.execute("UPDATE orders SET pay_method = %s WHERE user_id = %s", (method, id))
    base.commit()


async def get_order(id):
    cursor.execute("SELECT * FROM orders WHERE user_id = %s AND id = (SELECT max(id) FROM orders WHERE user_id = %s)", (id, id))
    order = cursor.fetchone()
    return order


async def add_product(name, day_price, deposit, photo, price, online=0):
    cursor.execute("INSERT INTO products(product_name, price_day, deposit, photo, price, online_product) VALUES(%s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING", (name, day_price, deposit, photo, price, online))
    base.commit()


async def get_product_name(id):
    cursor.execute("SELECT product_name FROM products WHERE id = %s", (id,))
    check = cursor.fetchone()
    return check[0]


async def get_product(id):
    cursor.execute("SELECT * FROM products WHERE id = %s", (id,))
    check = cursor.fetchone()
    return check


async def get_product_id(name):
    cursor.execute("SELECT id FROM products WHERE product_name = %s", (name,))
    check = cursor.fetchone()
    return check[0]


async def get_all_products():
    cursor.execute("SELECT * FROM products")
    check = cursor.fetchall()
    return check


async def get_products_id_name():
    cursor.execute("SELECT product_name, id FROM products")
    check = cursor.fetchall()
    if not bool(len(check)):
        return False
    else:
        return check


async def del_game(product_name):
    cursor.execute("DELETE FROM products WHERE product_name = %s", (product_name, ))
    base.commit()
