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
async def get_bob_menu():
    try:
        # 최신 데이터 확인
        latest_menu = get_latest_menu()
        
        # 데이터가 없거나 6시간 이상 지난 경우 새로 크롤링
        if not latest_menu or datetime.now() - latest_menu['created_at'] > timedelta(days=7):
            base_url = "https://www.gachon.ac.kr/kor/7349/subview.do"
            menu_data = crawl_education_menu(base_url)
            save_menu(menu_data)
            return {"status": "success", "data": menu_data}
            
        return {"status": "success", "data": latest_menu['menus']}
    
    except Exception as e:
        print(f"Error: {str(e)}")  # 로깅
        # 에러 발생 시 최신 데이터 반환 시도
        latest_menu = get_latest_menu()
        if latest_menu:
            return {"status": "success", "data": latest_menu['menus']}
        raise HTTPException(status_code=500, detail="메뉴를 불러오는데 실패했습니다.")

@app.get("/")
async def read_root():
    return {
        "status": "ok",
        "message": "Server is running",
        "endpoints": [
            "/api/menu/education - 교육대학원 식당"
        ]
    }