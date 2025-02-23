from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
from typing import Dict, List

app = FastAPI()

# CORS 설정 - 프론트엔드 도메인을 여기에 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포 시에는 실제 프론트엔드 도메인으로 변경하세요
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/menu")
async def get_menu():
    try:
        # Chrome 옵션 설정
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--log-level=3')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

        # 웹드라이버 설정
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        try:
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
                date = row.find_element(By.TAG_NAME, "th").text.strip().split('\n')[0]
                
                # 나머지 정보는 td 태그에 있음
                cols = row.find_elements(By.TAG_NAME, "td")
                
                if len(cols) >= 2:
                    meal_type = cols[0].text.strip()
                    menu_text = cols[1].text.strip()
                    menu_items = [item.strip() for item in menu_text.split('\n') if item.strip()]
                    
                    if date not in menu_data:
                        menu_data[date] = {}
                    
                    menu_data[date][meal_type] = menu_items

            return {
                "status": "success",
                "data": menu_data
            }

        finally:
            driver.quit()

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 서버 상태 확인용 엔드포인트
@app.get("/")
async def read_root():
    return {"status": "ok", "message": "Server is running"}