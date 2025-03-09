from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
import sqlite3
import json
import os
import traceback

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
    """Chrome 웹드라이버 설정"""
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    
    # render.com에서 Chrome 바이너리 위치 설정
    # GOOGLE_CHROME_BIN 환경 변수가 설정되어 있으면 사용, 없으면 기본 경로 사용
    chrome_options.binary_location = os.getenv('GOOGLE_CHROME_BIN', '/app/.apt/usr/bin/google-chrome')
    
    # ChromeDriverManager를 사용하여 드라이버 설치
    service = Service(ChromeDriverManager().install())
    
    return webdriver.Chrome(service=service, options=chrome_options)

def crawl_education_menu(base_url: str):
    """가천대학교 교육대학원 식단 메뉴 크롤링"""
    try:
        driver = setup_driver()
        driver.get(base_url)
        driver.implicitly_wait(10)

        # 데이터 구조 초기화
        menu_data = {
            "menus": {}
        }

        # 테이블에서 날짜와 메뉴 정보 추출
        rows = driver.find_elements("css selector", "table tr")
        
        # 첫 번째 행(헤더)은 건너뛰기
        for row in rows[1:]:
            try:
                cells = row.find_elements("css selector", "td")
                if not cells:
                    continue
                    
                date_cell = row.find_element("css selector", "th")
                date = date_cell.text.strip().split('\n')[0]  # 날짜에서 첫 줄만 가져오기
                
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
        
        driver.quit()
        return menu_data
    
    except Exception as e:
        error_traceback = traceback.format_exc()
        print(f"크롤링 중 오류 발생: {str(e)}\n{error_traceback}")
        if 'driver' in locals():
            driver.quit()
        raise Exception(f"크롤링 실패: {str(e)}")

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
        
        # 데이터가 없거나 7일 이상 지난 경우 새로 크롤링
        need_refresh = latest_menu is None or (
            datetime.now() - latest_menu['created_at'] > timedelta(days=7)
        )
        
        if need_refresh:
            try:
                print("크롤링 시작...")
                menu_data = crawl_education_menu("https://www.gachon.ac.kr/kor/7349/subview.do")
                save_menu(menu_data)
                return {"status": "success", "data": menu_data}
            except Exception as e:
                print(f"크롤링 오류: {str(e)}")
                # 크롤링 실패 시, 이전 데이터가 있으면 그것을 반환
                if latest_menu:
                    return {"status": "success", "data": latest_menu['menus']}
                # 이전 데이터도 없으면 오류 반환
                raise HTTPException(status_code=500, detail=f"에러 유형: HTTPException, 메시지: 500: {str(e)}")
        else:
            # 최신 데이터가 있고 7일 이내인 경우
            return {"status": "success", "data": latest_menu['menus']}
            
    except Exception as e:
        error_message = f"에러 유형: {type(e).__name__}, 메시지: {str(e)}"
        print(error_message)
        raise HTTPException(status_code=500, detail=error_message)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)