

def sort_by_price(data_list):
    # 문자열에서 null 문자를 제거하고, 가격을 정수로 변환하여 정렬
    for item in data_list:
        price = item['price'].replace(',', '').replace('원', '').strip()
        price = price.replace('\x00', '')  # null 문자를 제거
        try:
            item['price_int'] = int(price)
        except ValueError:
            item['price_int'] = float('inf')  # 가격이 잘못된 항목은 맨 뒤로 보냄
    return sorted(data_list, key=lambda x: x.get('price_int', float('inf')))