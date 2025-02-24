async function fetchMenuData(endpoint, containerId) {
  const loadingEl = document.getElementById(`${containerId}-loading`);
  const errorEl = document.getElementById(`${containerId}-error`);
  const contentEl = document.getElementById(`${containerId}-content`);

  loadingEl.style.display = "block";
  errorEl.style.display = "none";
  contentEl.innerHTML = "";

  try {
    const response = await fetch(
      `https://givebob.onrender.com/api/menu/${endpoint}`
    );
    const data = await response.json();

    if (data.status === "success") {
      let html = "";

      for (const [date, meals] of Object.entries(data.data.menus)) {
        html += `<div class="menu-date">${date}</div>`;
        for (const [type, items] of Object.entries(meals)) {
          html += `
              <div class="menu-type">${type}</div>
              <ul class="menu-items">
                ${items.map((item) => `<li>${item}</li>`).join("")}
              </ul>
            `;
        }
      }

      contentEl.innerHTML = html;
    } else {
      throw new Error("Failed to fetch menu data");
    }
  } catch (error) {
    errorEl.textContent = "메뉴를 불러오는데 실패했습니다.";
    errorEl.style.display = "block";
  } finally {
    loadingEl.style.display = "none";
  }
}

// 페이지 로드 시 메뉴 가져오기
document.addEventListener("DOMContentLoaded", () => {
  fetchMenuData("education", "education");
});
