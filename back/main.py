from contextlib import asynccontextmanager
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
import sqlite3
import json
import os
import time

# 데이터베이스 파일 경로 설정
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'menu.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS menu_data
        (id INTEGER PRIMARY KEY AUTOINCREMENT,
         created_at TIMESTAMP NOT NULL,
         menus TEXT NOT NULL)
    ''')
    conn.commit()
    conn.close()

def save_menu(menu_data):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        'INSERT INTO menu_data (created_at, menus) VALUES (?, ?)',
        (datetime.now(), json.dumps(menu_data))
    )
    conn.commit()
    conn.close()

def get_latest_menu():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        'SELECT created_at, menus FROM menu_data ORDER BY created_at DESC LIMIT 1'
    )
    result = c.fetchone()
    conn.close()
    
    if result:
        return {
            'created_at': datetime.strptime(result[0], '%Y-%m-%d %H:%M:%S.%f'),
            'menus': json.loads(result[1])
        }
    return None

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def crawl_education_menu(base_url: str):
    driver = setup_driver()
    try:
        driver.get(base_url)
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

def is_data_current(menu_data):
    """
    메뉴 데이터가 현재 날짜를 포함하고 있는지 확인합니다.
    """
    if not menu_data or not menu_data.get("menus"):
        return False
    
    today = datetime.now().strftime("%Y-%m-%d")  # 오늘 날짜
    this_week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime("%Y-%m-%d")  # 이번 주 시작일
    
    # 날짜 형식 통일을 위한 변환 함수
    def normalize_date(date_str):
        try:
            # 다양한 날짜 형식 처리 (예: "2025.03.09", "2025-03-09", "2025년 3월 9일")
            if '.' in date_str:
                parts = date_str.split('.')
                if len(parts) >= 3:
                    return f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)}"
            elif '-' in date_str:
                return date_str
            elif '년' in date_str and '월' in date_str and '일' in date_str:
                year = date_str.split('년')[0].strip()
                month = date_str.split('년')[1].split('월')[0].strip().zfill(2)
                day = date_str.split('월')[1].split('일')[0].strip().zfill(2)
                return f"{year}-{month}-{day}"
        except Exception:
            pass
        return date_str
    
    # 메뉴에 있는 날짜를 순회하며 현재 주에 해당하는 데이터가 있는지 확인
    for date_str in menu_data["menus"].keys():
        normalized_date = normalize_date(date_str)
        if normalized_date >= this_week_start:
            return True
    
    return False

def should_refresh_data(latest_menu):
    """
    데이터를 새로 가져와야 하는지 결정합니다.
    """
    if not latest_menu:
        return True
    
    # 데이터가 12시간 이내에 수집된 경우 재사용 (너무 자주 크롤링하지 않기 위함)
    if datetime.now() - latest_menu['created_at'] < timedelta(hours=12):
        # 하지만 데이터가 현재 주간에 맞는지 확인
        return not is_data_current(latest_menu['menus'])
    
    # 12시간 이상 지났거나 데이터가 현재 주간이 아니면 새로 크롤링
    return True

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 시작할 때 실행될 코드
    print("애플리케이션 시작")
    init_db()
    yield
    # 종료할 때 실행될 코드
    print("애플리케이션 종료")

app = FastAPI(lifespan=lifespan)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/menu/education")
async def get_bob_menu(force_refresh: bool = False):
    try:
        # 최신 데이터 확인
        latest_menu = get_latest_menu()
        
        # 강제 새로고침이 요청되었거나 데이터를 새로 가져와야 하는 경우
        if force_refresh or should_refresh_data(latest_menu):
            print("데이터 새로 크롤링 중...")
            base_url = "https://www.gachon.ac.kr/kor/7349/subview.do"
            menu_data = crawl_education_menu(base_url)
            
            # 새로 크롤링한 데이터가 있을 경우에만 저장
            if menu_data and menu_data.get("menus"):
                save_menu(menu_data)
                return {"status": "success", "data": menu_data, "source": "freshly_crawled"}
            
            # 크롤링 실패했지만 기존 데이터가 있는 경우
            if latest_menu:
                return {"status": "success", "data": latest_menu['menus'], "source": "cached"}
            
            # 크롤링 실패하고 기존 데이터도 없는 경우
            raise HTTPException(status_code=500, detail="메뉴를 불러오는데 실패했습니다.")
        
        # 기존 데이터 반환
        return {"status": "success", "data": latest_menu['menus'], "source": "cached"}
    
    except Exception as e:
        print(f"Error: {str(e)}")  # 로깅
        # 에러 발생 시 최신 데이터 반환 시도
        latest_menu = get_latest_menu()
        if latest_menu:
            return {"status": "success", "data": latest_menu['menus'], "source": "error_fallback"}
        raise HTTPException(status_code=500, detail="메뉴를 불러오는데 실패했습니다.")

@app.get("/api/refresh-menu")
async def force_refresh_menu():
    """데이터를 강제로 새로 크롤링하는 엔드포인트"""
    return await get_bob_menu(force_refresh=True)

@app.get("/")
async def read_root():
    return {
        "status": "ok",
        "message": "Server is running",
        "endpoints": [
            "/api/menu/education - 교육대학원 식당",
            "/api/refresh-menu - 메뉴 강제 새로고침"
        ]
    }