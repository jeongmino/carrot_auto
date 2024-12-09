import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox
import urllib.parse
import csv
import os
import sys

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

csv_path = get_resource_path("region.csv")

# CSV 파일에서 지역 데이터 로드
def load_region_data():
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        return [row for row in reader]

region_data = load_region_data()

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

    # 가격이 비어 있으면 기본값으로 설정
    if not min_price:
        min_price = "0"
    if not max_price:
        max_price = "100000000"

    # 지역 찾기
    location_data = find_location_ids(province, region_data)

    urls = []
    for region in location_data:
        encoded_keyword = urllib.parse.quote(keyword)
        encoded_city = urllib.parse.quote(region['city'])
        url = f"https://www.daangn.com/kr/buy-sell/?in={encoded_city}-{region['id']}&price={min_price}__{max_price}&search={encoded_keyword}"
        urls.append(url)

    # URL 크롤링 및 데이터 출력
    for url in urls:
        print(f"크롤링 중: {url}")
        response = requests.get(url)
        if response.status_code == 200:
            response.encoding = 'utf-8'
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            result_items = soup.find_all('a', class_='click_search_result_item')

            data_list = []
            for item in result_items:
                data_price = item.get('data-price')
                data_title = item.get('data-title')
                # data_href = item.get('href')
                # img_tag = item.find('img')
                # data_img = img_tag.get('src') if img_tag else None

                if data_price and data_title and data_href:
                    data_list.append({
                        'price': data_price,
                        'title': data_title,
                        # 'href': data_href,
                        # 'img': data_img
                    })

            # 결과 출력
            for entry in data_list:
                print(entry)
        else:
            print(f"페이지를 가져오는 데 실패했습니다. 상태 코드: {response.status_code}")
            messagebox.showerror("Error", f"페이지를 가져오는 데 실패했습니다. 상태 코드: {response.status_code}")

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

# 최대 가격 입력란
max_price_label = tk.Label(root, text="최대 가격:")
max_price_label.grid(row=3, column=0, padx=10, pady=10)
max_price_entry = tk.Entry(root)
max_price_entry.grid(row=3, column=1, padx=10, pady=10)

# 검색 버튼
search_button = tk.Button(root, text="검색", command=on_search)
search_button.grid(row=4, column=0, columnspan=2, pady=20)

# 실행
root.mainloop()
