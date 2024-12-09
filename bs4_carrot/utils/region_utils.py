import sys
import os
import csv

def get_resource_path(relative_path):
    """ PyInstaller로 패키징된 실행 파일에서 리소스 경로를 반환 """
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# CSV 파일에서 지역 데이터 로드
def load_region_data(csv_path):
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        return [row for row in reader]
    
def find_location_ids(province, data):
    location_data = []
    for row in data:
        if row["province"] == province:
            location_data.append({"city": row["region"], "id": row["id"]})
    return location_data