# 1. Получаем данные из предыдущей ноды (Новый стандарт n8n v2)
rows = [item["json"] for item in _items]

# 2. Наша виртуальная база данных себестоимости (COGS)
cogs_dict = {
    'TS-BLK-M': 300,      # Футболка
    'CASE-IPH15': 80,     # Чехол
    'SOCK-BAMB': 50       # Носки
}

# 3. Группируем строки по артикулу (SKU) через встроенные словари Python
groups = {}
for row in rows:
    sku = row.get('Артикул продавца')
    if not sku:
        continue
    if sku not in groups:
        groups[sku] = []
    groups[sku].append(row)

results = []

# 4. Пробегаемся по группам и считаем экономику
for sku, group in groups.items():
    cogs = cogs_dict.get(sku, 0)
    
    sales_qty = 0
    returns_qty = 0
    net_qty = 0
    gross_revenue = 0.0
    net_payout = 0.0
    total_logistics = 0.0
    
    for row in group:
        operation = row.get('Обоснование для оплаты')
        qty = int(row.get('Кол-во', 0))
        revenue = float(row.get('Вайлдберриз реализовал Товар (Пр)', 0))
        payout = float(row.get('К перечислению Продавцу за реализованный Товар', 0))
        logistics = float(row.get('Услуги по доставке товара покупателю', 0))
        
        net_qty += qty
        net_payout += payout
        total_logistics += logistics
        
        if operation == 'Продажа':
            sales_qty += qty
            gross_revenue += revenue
        elif operation == 'Возврат':
            returns_qty += abs(qty)
            
    # Финальные расчеты
    total_cogs = net_qty * cogs
    net_profit = net_payout - total_logistics - total_cogs
    margin_pct = (net_profit / gross_revenue) * 100 if gross_revenue > 0 else 0
    
    results.append({
        'sku': sku,
        'cogs_per_unit': cogs,
        'sales_qty': sales_qty,
        'returns_qty': returns_qty,
        'net_qty': net_qty,
        'gross_revenue': round(gross_revenue, 2),
        'net_payout': round(net_payout, 2),
        'total_logistics': round(total_logistics, 2),
        'total_cogs': round(total_cogs, 2),
        'net_profit': round(net_profit, 2),
        'margin_pct': round(margin_pct, 2)
    })

# Возвращаем результат в формате n8n
return [{'json': {'aggregated_report': results}}]
