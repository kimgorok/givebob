from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
import time

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_monday_date():
    """현재 날짜가 속한 주의 월요일 날짜를 반환"""
    today = datetime.now()
    monday = today - timedelta(days=today.weekday())
    return monday.strftime("%Y.%m.%d")

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def construct_url(base_url, monday_date, week):
    """
    주차별 URL 생성 함수
    week: 'pre' (이전 주), '' (현재 주), 'next' (다음 주)
    """
    if week in ['pre', 'next']:
        params = f"monday={monday_date}&week={week}"
        # URL에 파라미터 추가
        return f"{base_url}?enc={params}"
    return base_url

def crawl_education_menu(base_url: str, monday_date: str, week: str = ''):
    url = construct_url(base_url, monday_date, week)
    driver = setup_driver()
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        
 
        
        menu_data = {
            "menus": {}
        }
        
        table = wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # 헤더 제외
        
        for row in rows:
            try:
                cells = row.find_elements(By.TAG_NAME, "td")
                if not cells:
                    continue
                
                date_cell = row.find_element(By.TAG_NAME, "th")
                date = date_cell.text.strip().split('\n')[0]
                
                if len(cells) >= 2:
                    meal_type = cells[0].text.strip()
                    menu_text = cells[1].text.strip()
                    
                    if menu_text and menu_text != "등록된 식단내용이(가) 없습니다.":
                        menu_items = [item.strip() for item in menu_text.split('\n') if item.strip()]
                        
                        if date not in menu_data["menus"]:
                            menu_data["menus"][date] = {}
                        
                        menu_data["menus"][date][meal_type] = menu_items
            except Exception as e:
                print(f"Row processing error: {str(e)}")
                continue

        return menu_data
    finally:
        driver.quit()

@app.get("/api/menu/education")
async def get_education_menu(week: str = ''):
    """
    week: 'pre' (이전 주), '' (현재 주), 'next' (다음 주)
    """
    try:
        base_url = "https://www.gachon.ac.kr/kor/7349/subview.do"
        monday_date = get_monday_date()
        
        menu_data = crawl_education_menu(base_url, monday_date, week)
        return {"status": "success", "data": menu_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    return {
        "status": "ok",
        "message": "Server is running",
        "endpoints": [
            "/api/menu/education - 교육대학원 식당"
        ]
    }