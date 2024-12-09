import tkinter as tk

# 숫자만 입력받기 위한 함수
def validate_price_input(char):
    if char.isdigit() or char == "":  # 숫자만 입력 가능
        return True
    else:
        return False

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