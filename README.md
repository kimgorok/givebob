# GiveBob - 가천대학교 교육대학원 학식 식단 크롬 익스텐션

## 프로젝트 소개
- 가천대학교 교육대학원의 점심 학식 메뉴를 알려주는 확장 프로그램입니다.
- 가천대학교, 가천대학교 사이버 캠퍼스에 접속하면 활성화됩니다.

### 목적
평소에 사이버 캠퍼스에 들어갈 일은 많았지만, 
학식 메뉴를 보려면 `가천대학교 홈페이지 -> 대학 생활 -> 학생 식당 -> 교육대학원 페이지`로 이동해야하는 번거로움이 있었습니다. 
그래서 사이버 캠퍼스에 들어가기만 해도 이번 주의 점심 메뉴를 보여주는 익스텐션이 있다면 정말 편하겠다고 생각했습니다.

## 주요 기능
- 가천대학교 도메인 한정: 가천대학교 웹사이트(*.gachon.ac.kr)에서만 활성화
- 주간 식단 정보: 교육대학원 점심과 저녁 메뉴 정보 제공
- 간편한 접근성: 브라우저 상단의 아이콘 클릭으로 바로 확인

## 폴더 구조
### 1. 백엔드
```mipsasm
back/
├── __pycache__/                   # Python 컴파일된 캐시 파일 디렉토리
│   └── main.cpython-313.pyc       # 컴파일된 Python 파일
├── database.py                    # 데이터베이스 연결 및 관리 모듈
├── main.py                        # 메인 백엔드 애플리케이션 코드
├── menu.db                        # SQLite 데이터베이스 파일 (식단 데이터 저장)
├── render.yaml                    # Render 배포 설정 파일
└── requirements.txt               # 필요한 Python 패키지 목록
```

### 2. 프론트엔드
```mipsasm
front/
├── .vscode/                       # VS Code 설정 디렉토리
│   └── settings.json              # VS Code 프로젝트 설정 파일
├── icons/                         # 아이콘 이미지 디렉토리
│   └── icon.png                   # 확장 프로그램 아이콘
├── background.js                  # 확장 프로그램 백그라운드 스크립트
├── index.html                     # 확장 프로그램 팝업 HTML
├── manifest.json                  # 확장 프로그램 매니페스트 파일
├── manifest.txt                   # 매니페스트 텍스트 버전 또는 설명
├── rule.json                      # 확장 프로그램 규칙 설정
├── script.js                      # 팝업 동작 스크립트
└── styles.css                     # 팝업 CSS 스타일시트
```

## 설치 방법
### Chrome 웹 스토어에서 설치 (준비 중)
  1. Chrome 웹 스토어 에서 "GiveBob" 또는 "밥줘"를 검색하세요.
  2. "추가" 버튼을 클릭하여 확장 프로그램을 설치하세요.

### 개발자 모드로 설치
1. 이 저장소를 클론하거나 다운로드하세요.
```
git clone https://github.com/your-username/givebob.git
```
2. Chrome 브라우저에서 chrome://extensions/ 페이지를 열고 우측 상단의 "개발자 모드"를 활성화하세요.
3. "압축해제된 확장 프로그램을 로드합니다." 버튼을 클릭하고 다운로드한 폴더를 선택하세요.

## 🧑‍💻 개발자 소개
|<img src="https://github.com/user-attachments/assets/3ae3d63a-3706-4aa2-9ff0-8db94d661436" width="150px" height="200px" />|
|:---:|
|**김현중**|
|Developer|
|[GitHub](https://github.com/kimgorok)|


## 🛠️ 기술 스택
### Skills

- 프론트엔드

<img src="https://img.shields.io/badge/HTML-239120?style=for-the-badge&logo=html5&logoColor=white"> <img src="https://img.shields.io/badge/CSS-239120?&style=for-the-badge&logo=css3&logoColor=white">
<img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=JavaScript&logoColor=white"> 

<br />

- 백엔드

<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white">

### DB
<img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white">

## 💻 주요 기능
**1. 식단 조회**

![image](https://github.com/user-attachments/assets/364707af-1405-4980-9c69-1d0ed349d9af)

## 😎 개발 과정 정리 블로그
[가천대학교 학식 메뉴 조회 익스텐션](https://velog.io/@kimgorok/%ED%81%AC%EB%A1%AC-%EC%9D%B5%EC%8A%A4%ED%85%90%EC%85%98-%EC%97%B0%EA%B5%AC%EC%86%8C-%EA%B0%80%EC%B2%9C%EB%8C%80%ED%95%99%EA%B5%90-%ED%95%99%EC%8B%9D-%EB%A9%94%EB%89%B4-%EC%A1%B0%ED%9A%8C-%EC%9D%B5%EC%8A%A4%ED%85%90%EC%85%98)
