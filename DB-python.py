import psycopg2
import matplotlib.pyplot as plt

conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="dfyz2006",
    host="localhost",
    port="5432"
)

cur = conn.cursor()
cur.execute("SET search_path TO bd_shops;")
conn.commit()

print("ПОДКЛЮЧЕНИЕ К БАЗЕ ДАННЫХ УСПЕШНО")
print("="*50)

# ЗАПРОС 1: Доля поставок по поставщикам
cur.execute("""
    SELECT v.name, COUNT(d.product_id) as deliveries
    FROM vendors v
    LEFT JOIN product_deliv d ON v.id = d.vendor_id
    GROUP BY v.name
    ORDER BY deliveries DESC
    LIMIT 6;
""")
vendor_stats = cur.fetchall()

# ЗАПРОС 2: Продажи по месяцам
cur.execute("""
    SELECT DATE_TRUNC('month', visit_date) as month, COUNT(*) as sales_count
    FROM visits
    GROUP BY month
    ORDER BY month;
""")
monthly_sales = cur.fetchall()

# ЗАПРОС 3: Топ-5 продаваемых товаров
cur.execute("""
    SELECT p.product_name, SUM(v.line_size) as total_sold
    FROM product p
    JOIN visits v ON p.id = v.product_id
    GROUP BY p.product_name
    ORDER BY total_sold DESC
    LIMIT 5;
""")
top_selling = cur.fetchall()

# ЗАПРОС 4: Поставщики по странам
cur.execute("""
    SELECT country, COUNT(*) as vendor_count
    FROM vendors
    GROUP BY country
    ORDER BY vendor_count DESC;
""")
country_stats = cur.fetchall()

# ЗАПРОС 5: Выручка по магазинам
cur.execute("""
    SELECT s.market_name, SUM(v.line_size * p.price_sale_out) as revenue
    FROM shops s
    JOIN visits v ON s.id = v.shop_id
    JOIN product p ON v.product_id = p.id
    GROUP BY s.market_name
    ORDER BY revenue DESC;
""")
revenue_stats = cur.fetchall()

plt.figure(figsize=(8, 6))

vendor_stats_filtered = [v for v in vendor_stats if v[0] != 'Silver Tech']

names1 = [v[0] for v in vendor_stats_filtered]
values1 = [v[1] for v in vendor_stats_filtered]
plt.pie(values1, labels=names1, autopct='%1.1f%%', radius=1.5, textprops={'fontsize': 14})
plt.title('Доля поставок по поставщикам', fontsize=18, pad=30)
plt.tight_layout()
plt.show()

plt.figure(figsize=(10, 20))

# график 2: Продажи по месяцам
plt.subplot(4, 1, 1)
months = [m[0].strftime('%Y-%m') for m in monthly_sales if m[0]]
sales = [m[1] for m in monthly_sales if m[0]]
plt.plot(months, sales, 'o-', linewidth=2)
plt.title('Продажи по месяцам', fontsize=14)
plt.ylabel('Количество продаж')
plt.grid(True)
plt.xticks(rotation=45)

# график 3: Топ-5 товаров
plt.subplot(4, 1, 2)
names3 = [t[0] for t in top_selling]
values3 = [t[1] for t in top_selling]
plt.bar(names3, values3, color='blue')
plt.title('Топ-5 продаваемых товаров', fontsize=14)
plt.ylabel('Продано, шт')
plt.xticks(rotation=45)

# график 4: Поставщики по странам
plt.subplot(4, 1, 3)
names4 = [c[0] for c in country_stats]
values4 = [c[1] for c in country_stats]
plt.bar(names4, values4, color='green')
plt.title('Количество поставщиков по странам', fontsize=14)
plt.ylabel('Количество')
plt.xticks(rotation=45)

# график 5: Выручка по магазинам
plt.subplot(4, 1, 4)
names5 = [r[0] for r in revenue_stats]
values5 = [r[1] for r in revenue_stats]
plt.bar(names5, values5, color='red')
plt.title('Выручка по магазинам', fontsize=14)
plt.xlabel('Магазин')
plt.ylabel('Выручка, руб')
plt.xticks(rotation=45)

plt.tight_layout(pad=4.0)
plt.show()

cur.close()
conn.close()
print("Программа завершена")