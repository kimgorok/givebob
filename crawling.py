from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time

# Chrome 옵션 설정
chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--log-level=3')
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

try:
    # 웹드라이버 설정
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # 웹 페이지 접속
    url = "https://www.gachon.ac.kr/kor/7349/subview.do"
    driver.get(url)
    time.sleep(5)
    
    # 결과를 저장할 딕셔너리
    menu_data = {}
    
    # 테이블 찾기
    table = driver.find_element(By.TAG_NAME, "table")
    rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # 헤더 제외
    
    for row in rows:
        # 날짜 정보는 th 태그에 있음
        date = row.find_element(By.TAG_NAME, "th").text.strip().split('\n')[0]  # 날짜만 추출
        
        # 나머지 정보는 td 태그에 있음
        cols = row.find_elements(By.TAG_NAME, "td")
        
        if len(cols) >= 2:
            meal_type = cols[0].text.strip()
            menu_text = cols[1].text.strip()
            menu_items = [item.strip() for item in menu_text.split('\n') if item.strip()]
            
            if date not in menu_data:
                menu_data[date] = {}
            
            menu_data[date][meal_type] = menu_items
    
    print("\n최종 결과:")
    print(menu_data)

except Exception as e:
    print(f"에러 발생: {str(e)}")

finally:
    driver.quit()