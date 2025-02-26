// 메뉴 데이터를 가져오는 비동기 함수
async function fetchMenuData() {
  const loadingEl = document.getElementById("education-loading");
  const errorEl = document.getElementById("education-error");
  const contentEl = document.getElementById("education-content");

  // loading 표시 보이기
  loadingEl.classList.add("show");
  errorEl.classList.remove("show");
  contentEl.textContent = "";

  try {
    const response = await fetch(
      "https://givebob.onrender.com/api/menu/education"
    );
    const data = await response.json(); // fetch를 사용했으므로 JSON 형식으로 파싱 필요

    if (data.status === "success") {
      const menuElements = []; // 메뉴를 담을 배열

      // 각 날짜와 해당 날짜의 식사 메뉴 처리
      for (const [date, meals] of Object.entries(data.data.menus)) {
        const dateDiv = document.createElement("div");
        dateDiv.className = "menu-date";
        dateDiv.textContent = date;
        menuElements.push(dateDiv);

        // 각 날짜의 식사 유형(아침, 점심, 저녁 등)과 메뉴 항목을 처리
        for (const [type, items] of Object.entries(meals)) {
          const typeDiv = document.createElement("div");
          typeDiv.className = "menu-type";
          typeDiv.textContent = type;
          menuElements.push(typeDiv);

          const ul = document.createElement("ul");
          ul.className = "menu-items";

          items.forEach((item) => {
            const li = document.createElement("li");
            li.textContent = item;
            ul.appendChild(li);
          });
          // 완성된 ul 요소를 menuElements 배열에 추가
          menuElements.push(ul);
        }
      }
      // 모든 메뉴 요소들을 콘텐츠 영역에 추가
      contentEl.append(...menuElements);
    } else {
      throw new Error("메뉴를 불러오는데 실패했습니다.");
    }
  } catch (error) {
    errorEl.textContent = "메뉴를 불러오는데 실패했습니다.";
    errorEl.classList.add("show");
  } finally {
    // loading 표시 숨기기
    loadingEl.classList.remove("show");
  }
}

// DOM이 완전히 로드되었을 때 실행되는 이벤트 리스너를 등록
document.addEventListener("DOMContentLoaded", () => {
  fetchMenuData(); // 페이지 로드 시 메뉴 데이터 가져옴
});
