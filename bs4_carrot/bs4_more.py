import requests
from bs4 import BeautifulSoup
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import urllib.parse
from utils.tk_utils import update_price_label, validate_price_input
from utils.region_utils import get_resource_path, load_region_data, find_location_ids
from utils.function_utils import sort_by_price
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import time


# 지역 목록
province_list = [
    "서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "대전광역시", "울산광역시", 
    "세종특별자치시", "경기도", "강원특별자치도", "충청북도", "충청남도", "전라북도", "전라남도", "경상북도", 
    "경상남도", "제주특별자치도"
]

csv_path = get_resource_path("./resource/region.csv")

region_data = load_region_data(csv_path)

# 전역 변수로 크롤링된 데이터를 저장
global_data_list = []
global_origin_list = []


# 셀레니움으로 크롬 드라이버 실행
def get_driver():
    options = Options()
    options.headless = False  # headless 모드를 False로 설정하여 브라우저가 보이게 함
    service = ChromeService(executable_path='/opt/homebrew/bin/chromedriver')
    driver = webdriver.Chrome(service=service, options=options)
    return driver

# 더보기 버튼 클릭하고 데이터 크롤링 함수
def crawl_with_load_more(url, keyword, min_price, max_price, province, location_data):
    driver = get_driver()
    
    # URL에 대한 크롤링 시작
    urls = []
    for region in location_data:
        encoded_keyword = urllib.parse.quote(keyword)
        encoded_city = urllib.parse.quote(region['city'])
        url = f"https://www.daangn.com/kr/buy-sell/?in={encoded_city}-{region['id']}&price={min_price}__{max_price}&search={encoded_keyword}"
        urls.append(url)
    
    data_list = []
    total_articles = 0 
    
    # 각 URL에 대해서 "더 보기" 버튼을 클릭하여 데이터 불러오기
    for page_url in urls:
        driver.get(page_url)
        time.sleep(2)  # 페이지 로딩을 기다림
        
        # "더 보기" 버튼을 반복해서 클릭
        while True:
            try:
                load_more_button = driver.find_element(By.XPATH, '//div[@data-gtm="search_show_more_articles"]//button[contains(text(), "더보기")]')
                load_more_button.click()
                time.sleep(2)  # 버튼 클릭 후 페이지 로딩 대기
            except Exception as e:
                print("더 보기 버튼을 찾을 수 없거나 더 이상 페이지가 없습니다.")
                break  # 더 이상 "더 보기" 버튼이 없으면 반복 종료
        
        # 페이지에서 데이터를 추출
        html_content = driver.page_source
        soup = BeautifulSoup(html_content, 'html.parser')
        result_items = soup.find_all('a', class_='click_search_result_item')

        total_articles += len(result_items)  # 해당 페이지의 결과 항목 수를 더함

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
                    'region': region['city']
                })
    
    driver.quit()
    print(f"전체 아티클 갯수: {total_articles}")

    return data_list

# 검색 버튼 클릭 시 실행되는 함수
def on_search():
    global global_data_list, global_origin_list

    # 로딩 중 표시
    loading_label.config(text="로딩 중...")
    root.update()

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
    location_data = find_location_ids(province, region_data)
    data_list = crawl_with_load_more('url', keyword, min_price, max_price, province, location_data)

    

    # 가격 순으로 정렬
    sorted_data_list = sort_by_price(data_list)
    global_origin_list = sorted_data_list


    # 결과 출력할 갯수 결정
    if num_results != '전체':
        sorted_data_list = sorted_data_list[:int(num_results)]  # 결과 갯수에 맞게 슬라이싱

    # 전역 변수에 데이터를 저장
    global_data_list = sorted_data_list

    # 테이블에 데이터를 추가
    update_treeview(global_data_list)



    # 로딩 중 메시지 종료
    loading_label.config(text="")

# '갯수 바꾸기' 버튼을 눌렀을 때 Treeview를 갯수에 맞게 갱신하는 함수
def change_result_count():
    num_results = result_count_var.get()
    if global_origin_list:  # 이미 크롤링된 데이터가 있으면
        if num_results != '전체':
            data_to_display = global_origin_list[:int(num_results)]  # '전체'가 아닐 경우, 크롤링된 데이터에서 갯수만큼 출력
        else:
            data_to_display = global_origin_list
        print("origin: ", len(global_origin_list))
        print("data: ", len(global_data_list))
        update_treeview(data_to_display)

# Treeview에 데이터를 업데이트하는 함수
def update_treeview(data_list):
    # 기존 데이터 삭제
    for item in tree.get_children():
        tree.delete(item)

    # 새로운 데이터 추가 (번호를 추가해서 삽입)
    for index, entry in enumerate(data_list, 1):  # enumerate로 인덱스 번호 추가
        tree.insert("", "end", values=(index, entry['price'], entry['title'], entry['region']))  # 번호, 가격, 제목, 지역을 추가

# Tkinter GUI 설정
root = tk.Tk()
root.title("지역 검색 및 탭 열기")
root.geometry("1000x1000")  # 전체 창 크기를 키웁니다.

# 전체 프레임 설정
main_frame = tk.Frame(root)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# 검색 기능을 위한 프레임
search_frame = tk.Frame(main_frame)
search_frame.pack(fill="x", padx=5, pady=5)

# 지역 선택 드롭다운 메뉴
province_var = tk.StringVar(value="서울특별시")
province_label = tk.Label(search_frame, text="지역:")
province_label.grid(row=0, column=0, padx=10, pady=10)
province_menu = tk.OptionMenu(search_frame, province_var, *province_list)
province_menu.grid(row=0, column=1, padx=10, pady=10)

# 검색 키워드 입력란
keyword_label = tk.Label(search_frame, text="검색 키워드:")
keyword_label.grid(row=1, column=0, padx=10, pady=10)
keyword_entry = tk.Entry(search_frame)
keyword_entry.grid(row=1, column=1, padx=10, pady=10)

# 최소 가격 입력란
min_price_label = tk.Label(search_frame, text="최소 가격:")
min_price_label.grid(row=2, column=0, padx=10, pady=10)
min_price_entry = tk.Entry(search_frame)
min_price_entry.grid(row=2, column=1, padx=10, pady=10)

# 최소 가격 옆에 가격 단위 표시 라벨
min_price_unit_label = tk.Label(search_frame, text="(0원)")
min_price_unit_label.grid(row=2, column=2, padx=10, pady=10)

# 최대 가격 입력란
max_price_label = tk.Label(search_frame, text="최대 가격:")
max_price_label.grid(row=3, column=0, padx=10, pady=10)
max_price_entry = tk.Entry(search_frame)
max_price_entry.grid(row=3, column=1, padx=10, pady=10)

# 최대 가격 옆에 가격 단위 표시 라벨
max_price_unit_label = tk.Label(search_frame, text="(0원)")
max_price_unit_label.grid(row=3, column=2, padx=10, pady=10)

# 가격 입력이 변경될 때마다 라벨 업데이트
min_price_entry.bind("<KeyRelease>", lambda event: update_price_label(min_price_entry.get(), min_price_unit_label))
max_price_entry.bind("<KeyRelease>", lambda event: update_price_label(max_price_entry.get(), max_price_unit_label))

# 출력 갯수 선택 드롭다운 메뉴
result_count_var = tk.StringVar(value="30")
result_count_label = tk.Label(search_frame, text="출력 갯수:")
result_count_label.grid(row=4, column=0, padx=10, pady=10)
result_count_menu = tk.OptionMenu(search_frame, result_count_var, "30", "50", "100", "200", "전체")
result_count_menu.grid(row=4, column=1, padx=10, pady=10)

# '갯수 바꾸기' 버튼
change_count_button = tk.Button(search_frame, text="갯수 바꾸기", command=change_result_count)
change_count_button.grid(row=5, column=0, columnspan=3, pady=10)

# 로딩 중 라벨
loading_label = tk.Label(search_frame, text="", fg="red")
loading_label.grid(row=6, column=0, columnspan=3, pady=10)

# 검색 버튼
search_button = tk.Button(search_frame, text="검색", command=on_search)
search_button.grid(row=7, column=0, columnspan=3, pady=20)

# Treeview를 위한 프레임 (결과 출력 부분)
tree_frame = tk.Frame(main_frame)
tree_frame.pack(fill="both", expand=True)

# Treeview 위젯 설정
columns = ("번호", "가격", "제목", "지역")
tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
tree.heading("번호", text="번호")
tree.heading("가격", text="가격")
tree.heading("제목", text="제목")
tree.heading("지역", text="지역")
tree.pack(fill="both", expand=True)

# 실행
root.mainloop()
