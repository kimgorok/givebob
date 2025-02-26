// 가천대학교 도메인인지 확인하는 함수
function isGachonDomain(url) {
  return url && url.match(/^https?:\/\/([^\/]+\.)?gachon\.ac\.kr/);
}

// URL이 변경될 때마다 확인
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  // 페이지 로딩이 완료된 경우에만 확인
  if (changeInfo.status === "complete" && tab.url) {
    // 가천대학교 도메인인지 확인
    if (tab.url.includes("gachon.ac.kr")) {
      // 가천대학교 도메인이면 익스텐션 활성화
      chrome.action.enable(tabId);
    } else {
      // 다른 사이트에서는 비활성화
      chrome.action.disable(tabId);
    }
  }
});

// 새 탭이 활성화될 때마다 확인
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  const tab = await chrome.tabs.get(activeInfo.tabId);
  if (tab.url && tab.url.includes("gachon.ac.kr")) {
    // 가천대학교 사이트면 활성화
    chrome.action.enable(activeInfo.tabId);
  } else {
    chrome.action.disable(activeInfo.tabId);
  }
});
