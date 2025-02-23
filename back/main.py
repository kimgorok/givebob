from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=chrome_options)

def crawl_education_menu(url: str):
    driver = setup_driver()
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        
        info = {
            "location": "교육대학원",
            "operation_time": "월-금 8:30-19:00",
            "contact": "031-750-5491"
        }
        
        menu_data = {
            "info": info,
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

def crawl_vision_menu(url: str):
    driver = setup_driver()
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        
        info = {
            "location": "비전타워 식당",
            "operation_time": "월-금 11:00-19:00",
            "contact": "031-750-5289"
        }
        
        menu_data = {
            "info": info,
            "menus": {}
        }

        table = wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        rows = table.find_elements(By.TAG_NAME, "tr")
        
        current_date = None
        
        # 헤더 행 제외하고 시작
        for row in rows[1:]:
            try:
                # th 태그가 있는지 확인 (새로운 날짜 시작)
                th_elements = row.find_elements(By.TAG_NAME, "th")
                if th_elements:
                    current_date = th_elements[0].text.strip().split('\n')[0]  # 날짜만 추출
                
                # 현재 행의 메뉴 정보 가져오기
                cells = row.find_elements(By.TAG_NAME, "td")
                if len(cells) >= 2:
                    meal_type = cells[0].text.strip()
                    menu_text = cells[1].text.strip()
                    
                    if menu_text and menu_text != "등록된 식단내용이(가) 없습니다.":
                        if current_date not in menu_data["menus"]:
                            menu_data["menus"][current_date] = {}
                        
                        menu_items = [item.strip() for item in menu_text.split('\n') if item.strip()]
                        menu_data["menus"][current_date][meal_type] = menu_items
            
            except Exception as e:
                print(f"Row processing error: {str(e)}")
                continue

        return menu_data
    finally:
        driver.quit()

@app.get("/api/menu/education")
async def get_education_menu():
    try:
        menu_data = crawl_education_menu("https://www.gachon.ac.kr/kor/7349/subview.do")
        return {"status": "success", "data": menu_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/menu/vision")
async def get_vision_menu():
    try:
        menu_data = crawl_vision_menu("https://www.gachon.ac.kr/kor/7347/subview.do")
        return {"status": "success", "data": menu_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def read_root():
    return {
        "status": "ok",
        "message": "Server is running",
        "endpoints": [
            "/api/menu/education - 교육대학원 식당",
            "/api/menu/vision - 비전타워 식당"
        ]
    }