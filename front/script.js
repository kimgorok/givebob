async function fetchMenuData(endpoint, containerId) {
  const loadingEl = document.getElementById(`${containerId}-loading`);
  const errorEl = document.getElementById(`${containerId}-error`);
  const contentEl = document.getElementById(`${containerId}-content`);

  // loading 표시 보이기
  loadingEl.classList.add("show");
  errorEl.classList.remove("show");
  contentEl.textContent = "";

  try {
    const response = await fetch(
      `https://givebob.onrender.com/api/menu/${endpoint}`
    );
    const data = await response.json();

    if (data.status === "success") {
      const menuElements = [];

      for (const [date, meals] of Object.entries(data.data.menus)) {
        const dateDiv = document.createElement("div");
        dateDiv.className = "menu-date";
        dateDiv.textContent = date;
        menuElements.push(dateDiv);

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

          menuElements.push(ul);
        }
      }

      contentEl.append(...menuElements);
    } else {
      throw new Error("Failed to fetch menu data");
    }
  } catch (error) {
    errorEl.textContent = "메뉴를 불러오는데 실패했습니다.";
    errorEl.classList.add("show");
  } finally {
    // loading 표시 숨기기
    loadingEl.classList.remove("show");
  }
}

// DOM이 로드되면 메뉴 데이터를 가져옵니다
document.addEventListener("DOMContentLoaded", () => {
  fetchMenuData("education", "education");
});
