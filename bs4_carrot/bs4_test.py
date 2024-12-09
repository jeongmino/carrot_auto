import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox
import urllib.parse
import csv
import os
import sys
from utils.tk_utils import update_price_label, validate_price_input

# 지역 목록
province_list = [
    "서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "대전광역시", "울산광역시", 
    "세종특별자치시", "경기도", "강원특별자치도", "충청북도", "충청남도", "전라북도", "전라남도", "경상북도", 
    "경상남도", "제주특별자치도"
]

def get_resource_path(relative_path):
    """ PyInstaller로 패키징된 실행 파일에서 리소스 경로를 반환 """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

csv_path = get_resource_path("./resource/region.csv")

# CSV 파일에서 지역 데이터 로드
def load_region_data():
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        return [row for row in reader]

region_data = load_region_data()

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

# 선택한 Province에 해당하는 지역 목록 찾기
def find_location_ids(province, data):
    location_data = []
    for row in data:
        if row["province"] == province:
            location_data.append({"city": row["region"], "id": row["id"]})
    return location_data

# 검색 버튼 클릭 시 실행되는 함수
def on_search():
    province = province_var.get()
    keyword = keyword_entry.get()
    min_price = min_price_entry.get()
    max_price = max_price_entry.get()
    num_results = result_count_var.get()

    # 가격이 비어 있으면 기본값으로 설정
    if not min_price:
        min_price = "0"
    if not max_price:
        max_price = "100000000"

    # 지역 찾기
    location_data = find_location_ids(province, region_data)

    # URL 딕셔너리 만들기
    urls = {}
    for region in location_data:
        encoded_keyword = urllib.parse.quote(keyword)
        encoded_city = urllib.parse.quote(region['city'])
        url = f"https://www.daangn.com/kr/buy-sell/?in={encoded_city}-{region['id']}&price={min_price}__{max_price}&search={encoded_keyword}"
        urls[region['city']] = url  # 지역(city)을 키로 하고 URL을 값으로 저장

    # 크롤링 시작
    data_list = []
    for city, url in urls.items():  # urls 딕셔너리에서 city를 키로, url을 값으로 꺼냄
        print(f"크롤링 중: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            response.encoding = 'utf-8'
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            result_items = soup.find_all('a', class_='click_search_result_item')

            for item in result_items:
                data_price = item.get('data-price')
                data_title = item.get('data-title')
                data_href = item.get('href')
                img_tag = item.find('img')
                data_img = img_tag.get('src') if img_tag else None

                if data_price and data_title:
                    data_list.append({
                        'price': data_price,
                        'title': data_title,
                        'province': province,
                        'region': city  # 이제 region은 city를 그대로 사용
                    })

            # 가격 순으로 정렬
            sorted_data_list = sort_by_price(data_list)

            # 결과 출력할 갯수 결정
            if num_results != '전체':
                sorted_data_list = sorted_data_list[:int(num_results)]  # 결과 갯수에 맞게 슬라이싱

        else:
            print(f"페이지를 가져오는 데 실패했습니다. 상태 코드: {response.status_code}")
            messagebox.showerror("Error", f"페이지를 가져오는 데 실패했습니다. 상태 코드: {response.status_code}")

        for entry in sorted_data_list:  # 정렬된 데이터 출력
                print(f"가격: {entry['price']} - 제목: {entry['title']} - 지역: {entry['region']}")

# Tkinter GUI 설정
root = tk.Tk()
root.title("지역 검색 및 탭 열기")
root.geometry("500x350")

# 지역 선택 드롭다운 메뉴
province_var = tk.StringVar(value="서울특별시")
province_label = tk.Label(root, text="지역:")
province_label.grid(row=0, column=0, padx=10, pady=10)
province_menu = tk.OptionMenu(root, province_var, *province_list)
province_menu.grid(row=0, column=1, padx=10, pady=10)

# 검색 키워드 입력란
keyword_label = tk.Label(root, text="검색 키워드:")
keyword_label.grid(row=1, column=0, padx=10, pady=10)
keyword_entry = tk.Entry(root)
keyword_entry.grid(row=1, column=1, padx=10, pady=10)

# 최소 가격 입력란
min_price_label = tk.Label(root, text="최소 가격:")
min_price_label.grid(row=2, column=0, padx=10, pady=10)
min_price_entry = tk.Entry(root)
min_price_entry.grid(row=2, column=1, padx=10, pady=10)

# 최소 가격 옆에 가격 단위 표시 라벨
min_price_unit_label = tk.Label(root, text="(0원)")
min_price_unit_label.grid(row=2, column=2, padx=10, pady=10)

# 최대 가격 입력란
max_price_label = tk.Label(root, text="최대 가격:")
max_price_label.grid(row=3, column=0, padx=10, pady=10)
max_price_entry = tk.Entry(root)
max_price_entry.grid(row=3, column=1, padx=10, pady=10)

# 최대 가격 옆에 가격 단위 표시 라벨
max_price_unit_label = tk.Label(root, text="(0원)")
max_price_unit_label.grid(row=3, column=2, padx=10, pady=10)

# 가격 입력이 변경될 때마다 라벨 업데이트
min_price_entry.bind("<KeyRelease>", lambda event: update_price_label(min_price_entry.get(), min_price_unit_label))
max_price_entry.bind("<KeyRelease>", lambda event: update_price_label(max_price_entry.get(), max_price_unit_label))

# 출력 갯수 선택 드롭다운 메뉴
result_count_var = tk.StringVar(value="30")
result_count_label = tk.Label(root, text="출력 갯수:")
result_count_label.grid(row=4, column=0, padx=10, pady=10)
result_count_menu = tk.OptionMenu(root, result_count_var, "30", "50", "100", "200", "전체")
result_count_menu.grid(row=4, column=1, padx=10, pady=10)

# 검색 버튼
search_button = tk.Button(root, text="검색", command=on_search)
search_button.grid(row=5, column=0, columnspan=2, pady=20)

# 실행
root.mainloop()
