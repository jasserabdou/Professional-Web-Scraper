from itemadapter import ItemAdapter
import sqlite3


class WsPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        field_names = adapter.field_names()
        for field_name in field_names:
            if field_name != 'description':
                value = adapter.get(field_name)
                if value:
                    adapter[field_name] = value.strip()

        lowercase_keys = ['category', 'product_type']
        for lowercase_key in lowercase_keys:
            value = adapter.get(lowercase_key)
            if value:
                adapter[lowercase_key] = value.lower()

        price_keys = ['price', 'price_excl_tax', 'price_incl_tax', 'tax']
        for price_key in price_keys:
            value = adapter.get(price_key)
            if value:
                value = value.replace('£', '')
                adapter[price_key] = float(value)

        availability_string = adapter.get('availability')
        if availability_string:
            split_string_array = availability_string.split('(')
            if len(split_string_array) >= 2:
                availability_array = split_string_array[1].split(' ')
                adapter['availability'] = int(availability_array[0])
            else:
                adapter['availability'] = 0

        num_reviews_string = adapter.get('num_reviews')
        if num_reviews_string:
            adapter['num_reviews'] = int(num_reviews_string)

        stars_string = adapter.get('stars')
        if stars_string:
            split_stars_array = stars_string.split(' ')
            if len(split_stars_array) >= 2:
                stars_text_value = split_stars_array[1].lower()
                if stars_text_value == "zero":
                    adapter['stars'] = 0
                elif stars_text_value == "one":
                    adapter['stars'] = 1
                elif stars_text_value == "two":
                    adapter['stars'] = 2
                elif stars_text_value == "three":
                    adapter['stars'] = 3
                elif stars_text_value == "four":
                    adapter['stars'] = 4
                elif stars_text_value == "five":
                    adapter['stars'] = 5

        return item


class ConnectiontoSQLitePipline:
    def __init__(self):
        self.conn = sqlite3.connect('books.db')
        self.cur = self.conn.cursor()
        self.cur.execute("""
        CREATE TABLE IF NOT EXISTS books(
            id INTEGER PRIMARY KEY,
            url TEXT,
            title TEXT,
            upc TEXT,
            product_type TEXT,
            price_excl_tax REAL,
            price_incl_tax REAL,
            tax REAL,
            price REAL,
            availability INTEGER,
            num_of_reviews INTEGER,
            num_of_stars INTEGER,
            category TEXT,
            description TEXT
        )
        """)

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        self.cur.execute("""
        INSERT INTO books (
            url,
            title,
            upc,
            product_type,
            price_excl_tax,
            price_incl_tax,
            tax,
            price,
            availability,
            num_of_reviews,
            num_of_stars,
            category,
            description
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                         (
                             adapter.get('url'),
                             adapter.get('title'),
                             adapter.get('upc'),
                             adapter.get('product_type'),
                             adapter.get('price_excl_tax'),
                             adapter.get('price_incl_tax'),
                             adapter.get('tax'),
                             adapter.get('price'),
                             adapter.get('availability'),
                             adapter.get('num_of_reviews'),
                             adapter.get('num_of_stars'),
                             adapter.get('category'),
                             adapter.get('description')
                         ))

        self.conn.commit()
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()
