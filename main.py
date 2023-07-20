import pandas as pd


url = "https://file.notion.so/f/s/0f8850ad-e46f-4f37-99ea-0e4e2a6af5b6/trial_task.json?id=2583a04b-4256-4c1f-939e-6eac0f749ceb&table=block&spaceId=41165294-a784-489a-a401-1a916d020564&expirationTimestamp=1689868800000&signature=-1D4yL8SjErQtHRmRLR8SDvsSk6n_DPQ5uefnI1oeLs&downloadName=trial_task.json"
data = pd.read_json(url)


#1. Cтоимость доставки для каждого склада
tariffs = {}

for _, row in data.iterrows():
    warehouse = row['warehouse_name']
    products = row['products'] 
    total_quantity = sum(product['quantity'] for product in products)

    if warehouse in tariffs:
        continue

    tariff = row['highway_cost'] / total_quantity
    tariffs[warehouse] = tariff

print('1. Cтоимость доставки для каждого склада:')
for warehouse, tariff in tariffs.items():
    print(f'Склад: {warehouse}, Тариф: {tariff}')


# 2. Найти суммарное количество , суммарный доход , суммарный расход и суммарную прибыль для каждого товара
# (представить как таблицу со столбцами 'product', 'quantity', 'income', 'expenses', 'profit')
summary = {
    'product': [],
    'quantity': [],
    'income': [],
    'expenses': [],
    'profit': []
}

for _, row in data.iterrows():
    products = row['products']

    for product in products:
        product_name = product['product']
        price = product['price']
        quantity = product['quantity']
        expenses = row['highway_cost'] * quantity

        if product_name in summary['product']:
            index = summary['product'].index(product_name)
            summary['quantity'][index] += quantity
            summary['income'][index] += price * quantity
            summary['expenses'][index] += expenses
            summary['profit'][index] += price * quantity + expenses
        else:
            summary['product'].append(product_name)
            summary['quantity'].append(quantity)
            summary['income'].append(price * quantity)
            summary['expenses'].append(expenses)
            summary['profit'].append(price * quantity + expenses)

summary_table = pd.DataFrame(summary)
print(f'\n2. Расчет прибыли:\n {summary_table}')


# 3. Составить табличку со столбцами 'order_id' (id заказа) и 'order_profit' (прибыль полученная с заказа). А также вывести среднюю прибыль заказов.
order_profit = {
    'order_id': [],
    'order_profit': []
}

for _, row in data.iterrows():
    order_id = row['order_id']
    products = row['products']
    highway_cost = row['highway_cost']
    total_profit = 0

    for product in products:
        price = product['price']
        quantity = product['quantity']
        profit = price * quantity + highway_cost
        total_profit += profit

    order_profit['order_id'].append(order_id)
    order_profit['order_profit'].append(total_profit)

order_profit_table = pd.DataFrame(order_profit)

average_profit = order_profit_table['order_profit'].mean()

print("\n3. Таблица с прибылью по заказам:")
print(order_profit_table)
print("\nСредняя прибыль по заказам:", average_profit)


#4. Составить табличку типа 'warehouse_name' , 'product','quantity', 'profit', 'percent_profit_product_of_warehouse'
# (процент прибыли продукта заказанного из определенного склада к прибыли этого склада)
summary = {
    'product': [],
    'warehouse_name': [],
    'quantity': [],
    'income': [],
    'expenses': [],
    'profit': []
}

tariffs = {}
for _, row in data.iterrows():
    warehouse = row['warehouse_name']
    products = row['products'] 
    total_quantity = sum(product['quantity'] for product in products)

    if warehouse in tariffs:
        continue

    tariff = row['highway_cost'] / total_quantity
    tariffs[warehouse] = tariff

for _, row in data.iterrows():
    products = row['products']

    for product in products:
        product_name = product['product']
        warehouse = row['warehouse_name']
        price = product['price']
        quantity = product['quantity']
        expenses = tariffs[warehouse] * quantity
        profit = price * quantity + expenses

        key = f"{product_name}_{warehouse}"
        if key in summary['product']:
            index = summary['product'].index(key)
            summary['quantity'][index] += quantity
            summary['income'][index] += price * quantity
            summary['expenses'][index] += expenses
            summary['profit'][index] += profit
        else:
            summary['product'].append(key)
            summary['warehouse_name'].append(warehouse)
            summary['quantity'].append(quantity)
            summary['income'].append(price * quantity)
            summary['expenses'].append(expenses)
            summary['profit'].append(profit)

summary_table = pd.DataFrame(summary)
profit_by_warehouse = summary_table.groupby('warehouse_name')['profit'].sum().reset_index()

# Объединение таблиц, чтобы добавить столбец 'percent_profit_product_of_warehouse'
summary_table = pd.merge(summary_table, profit_by_warehouse, on='warehouse_name', suffixes=('', '_warehouse'))

summary_table['percent_profit_product_of_warehouse'] = (summary_table['profit'] / summary_table['profit_warehouse']) * 100

# Убрать название склада из столбца 'product'
summary_table['product'] = summary_table['product'].apply(lambda x: x.split('_')[0])

print(f'\n4. Процент прибыли продукта заказанного из определенного склада к прибыли этого склада:\n{summary_table[["warehouse_name", "product", "quantity", "profit", "percent_profit_product_of_warehouse"]]}')


# 5. Взять предыдущую табличку и отсортировать 'percent_profit_product_of_warehouse' по убыванию, после посчитать накопленный процент. Накопленный процент - это новый столбец в этой табличке, который должен называться
# 'accumulated_percent_profit_product_of_warehouse'. По своей сути это постоянно растущая сумма отсортированного по убыванию столбца 'percent_profit_product_of_warehouse'.
summary_table = summary_table.sort_values(by='percent_profit_product_of_warehouse', ascending=False)
summary_table['accumulated_percent_profit_product_of_warehouse'] = summary_table.groupby('warehouse_name')['percent_profit_product_of_warehouse'].cumsum()
print(f'\n2. Рассчет накопленного процента::\n{summary_table[["warehouse_name", "product", "quantity", "profit", "percent_profit_product_of_warehouse", "accumulated_percent_profit_product_of_warehouse"]]}')


# 6. Присвоить A,B,C - категории на основании значения накопленного процента ('accumulated_percent_profit_product_of_warehouse'). Если значение накопленного процента меньше или равно 70, то категория A.
# Если от 70 до 90 (включая 90), то категория Б. Остальное - категория C. Новый столбец обозначить в таблице как 'category'.
def categorize_profits(percent):
    if percent <= 70:
        return 'A'
    elif 70 < percent <= 90:
        return 'B'
    else:
        return 'C'

summary_table['category'] = summary_table['accumulated_percent_profit_product_of_warehouse'].apply(categorize_profits)
print(f'\n6. Присвоение категорий:\n{summary_table[["warehouse_name", "product", "quantity", "profit", "percent_profit_product_of_warehouse", "accumulated_percent_profit_product_of_warehouse", "category"]]}')
