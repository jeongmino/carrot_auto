import sys
sys.path.append('/Users/ojeongmin/Desktop/carrotMarket/venv/lib/python3.13/site-packages')
import os

def get_resource_path(relative_path):
    """ PyInstaller로 패키징된 실행 파일에서 리소스 경로를 반환 """
    try:
        # PyInstaller에서 실행 중인 경우
        base_path = sys._MEIPASS
    except AttributeError:
        # 일반 Python 환경에서 실행 중인 경우
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# CSV 파일 경로
csv_path = get_resource_path("region.csv")

import csv
import time
import urllib.parse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
import chardet
import tkinter as tk
from tkinter import messagebox

province_list = [
    "서울특별시", "부산광역시", "대구광역시", "인천광역시", "광주광역시", "대전광역시", "울산광역시", 
    "세종특별자치시", "경기도", "강원특별자치도", "충청북도", "충청남도", "전라북도", "전라남도", "경상북도", 
    "경상남도", "제주특별자치도"
]


def update_price_label(entry_value, label):
    try:
        # 숫자만 추출하고, 콤마를 없애고, 숫자로 변환
        raw_value = entry_value.replace(',', '')
        value = int(raw_value)

        under_bilion_won_div = value // 100000000
        under_bilion_won_mov = value % 100000000
        under_man_won_div = value // 10000
        under_man_won_mov = value % 10000
        # 10000 단위로 변환해서 출력
        if value >= 100000000:
            if under_bilion_won_mov == 0:
                formatted_value = f"{under_bilion_won_div}억원"
            elif under_bilion_won_mov < 10000:
                formatted_value = f"{under_bilion_won_div}억 {under_man_won_mov}원"
            else: 
                formatted_value = f"{under_bilion_won_div}억 {((under_bilion_won_mov) // 10000)}만 {under_man_won_mov}원"
        elif value >= 10000:
            if under_man_won_mov == 0:
                formatted_value = f"{under_man_won_div}만원"
            else:
                formatted_value = f"{under_man_won_div}만 {under_man_won_mov}원"
        else:
            formatted_value = f"{value}원"
        
        # 라벨에 표시
        label.config(text=f"({formatted_value})")
    
    except ValueError:
        # 숫자가 아닌 값을 입력한 경우 예외 처리
        label.config(text="(잘못된 입력)")

# 데이터 로드 함수 (키워드)
def load_keyword_data():
    with open('keyword.csv', 'rb') as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        print(f"자동 감지된 인코딩: {encoding}")
    
    try:
        with open('keyword.csv', 'r', encoding=encoding) as f:
            reader = csv.DictReader(f)
            keyword_data = next(reader)
            print("읽어온 키워드 데이터:", keyword_data)
            # 공백 제거
            keyword_data = {key.strip(): value.strip() for key, value in keyword_data.items()}
            return keyword_data
    except UnicodeDecodeError as e:
        print(f"인코딩 읽기 실패: {e}")
        return None

# 데이터 로드 함수 (지역)
def load_region_data():
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        return [row for row in reader]

# 선택된 Province에 맞는 모든 지역 찾기
def find_location_ids(province, data):
    location_data = []
    
    # Province에 맞는 지역 정보를 찾기
    for row in data:
        if row["province"] == province:
            location_data.append({"city": row["region"], "id": row["id"]})
    
    return location_data

# Chrome로 여러 탭을 열고 새로고침하는 함수
def open_chrome_tabs(location_data, product, min_price, max_price):
    options = Options()
    options.headless = False  # Chrome 드라이버가 보이도록 설정 (headless는 기본적으로 False)

    # Chrome 웹 드라이버 사용
    service = ChromeService(executable_path='/opt/homebrew/bin/chromedriver')  # chromedriver 경로 설정
    driver = webdriver.Chrome(service=service, options=options)  # Chrome WebDriver를 사용
    
    urls = []
    for region in location_data:
        encoded_product = urllib.parse.quote(product)  # product 인코딩
        encoded_city = urllib.parse.quote(region['city'])  # city 인코딩
        url = f"https://www.daangn.com/kr/buy-sell/?in={encoded_city}-{region['id']}&price={min_price}__{max_price}&search={encoded_product}"
        urls.append(url)

    for url in urls:
        driver.execute_script(f"window.open('{url}', '_blank');")  # 새 탭을 열기
        print(f"크롬 탭을 열었습니다: {url}")
    
    return driver

# 모든 탭을 새로고침하는 함수
def refresh_all_tabs(driver):
    print("모든 탭 새로고침 시작...")
    for window_handle in driver.window_handles:
        driver.switch_to.window(window_handle)  # 각 탭으로 전환
        driver.refresh()  # 탭 새로고침
        print(f"탭을 새로고침 했습니다: {driver.current_url}")

# 새로고침 주기를 설정하고 주기적으로 새로고침하는 함수 (tkinter의 after 사용)
def refresh_periodically(root, driver, duration):
    # 새로고침 후 매 주기마다 새로고침 실행
    refresh_all_tabs(driver)  # 모든 탭 새로고침
    print(f"{duration}초 후 새로고침 실행")
    
    # after()로 새로고침을 재귀적으로 호출하여 주기적인 새로고침을 실행
    root.after(int(duration * 1000), refresh_periodically, root, driver, duration)  # 1000ms로 변환하여 재호출

# 숫자만 입력받기 위한 함수
def validate_price_input(char):
    if char.isdigit() or char == "":  # 숫자만 입력 가능
        return True
    else:
        return False

# 버튼 클릭 시 이벤트 함수
def on_search():
    province = province_var.get()
    keyword = keyword_entry.get()
    min_price = min_price_entry.get()
    max_price = max_price_entry.get()
    refresh_interval = refresh_interval_entry.get()

    if not keyword:
        messagebox.showerror("입력 오류", "검색 키워드를 입력해주세요.")
        return
    
    if not min_price or not max_price:
        messagebox.showerror("입력 오류", "가격 범위를 입력해주세요.")
        return
    
    if not refresh_interval:
        messagebox.showerror("입력 오류", "새로고침 간격을 입력해주세요.")
        return

    # 새로고침 간격을 분에서 초로 변환
    try:
        refresh_interval = float(refresh_interval) * 60  # 분을 초로 변환
    except ValueError:
        messagebox.showerror("입력 오류", "새로고침 간격에 유효한 숫자를 입력해주세요.")
        return

    # 지역 데이터를 로드하고 선택된 province에 맞는 location 찾기
    region_data = load_region_data()
    location_data = find_location_ids(province, region_data)

    if location_data:
        driver = open_chrome_tabs(location_data, keyword, min_price, max_price)  # 크롬 탭 열기
        
        # 새로고침 주기 설정: 사용자 입력에 따른 간격
        refresh_periodically(root, driver, refresh_interval)  # 사용자 입력 간격으로 새로고침
    else:
        messagebox.showerror("지역 정보 없음", "해당 지역에 대한 정보가 없습니다.")

# tkinter 윈도우 생성
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
min_price_entry = tk.Entry(root, validate="key", validatecommand=(root.register(validate_price_input), "%P"))
min_price_entry.grid(row=2, column=1, padx=10, pady=10)

# 최소 가격 옆에 가격 단위 표시 라벨
min_price_unit_label = tk.Label(root, text="(0원)")
min_price_unit_label.grid(row=2, column=2, padx=10, pady=10)

# 최대 가격 입력란
max_price_label = tk.Label(root, text="최대 가격:")
max_price_label.grid(row=3, column=0, padx=10, pady=10)
max_price_entry = tk.Entry(root, validate="key", validatecommand=(root.register(validate_price_input), "%P"))
max_price_entry.grid(row=3, column=1, padx=10, pady=10)

# 최대 가격 옆에 가격 단위 표시 라벨
max_price_unit_label = tk.Label(root, text="(0원)")
max_price_unit_label.grid(row=3, column=2, padx=10, pady=10)

# 가격 입력이 변경될 때마다 라벨 업데이트
min_price_entry.bind("<KeyRelease>", lambda event: update_price_label(min_price_entry.get(), min_price_unit_label))
max_price_entry.bind("<KeyRelease>", lambda event: update_price_label(max_price_entry.get(), max_price_unit_label))

# 새로고침 간격 입력란
refresh_interval_label = tk.Label(root, text="새로고침 간격 (분):")
refresh_interval_label.grid(row=4, column=0, padx=10, pady=10)
refresh_interval_entry = tk.Entry(root)
refresh_interval_entry.grid(row=4, column=1, padx=10, pady=10)

# 검색 버튼
search_button = tk.Button(root, text="검색", command=on_search)
search_button.grid(row=5, column=0, columnspan=2, pady=20)

# 실행
root.mainloop()
