chrome.runtime.onInstalled.addListener(() => {
  // 기본적으로 익스텐션 아이콘을 비활성화
  chrome.action.disable();
});

// URL이 변경될 때마다 확인
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.url) {
    // 가천대학교 도메인인지 확인
    if (tab.url.match(/^https?:\/\/([^\/]+\.)?gachon\.ac\.kr/)) {
      // 익스텐션 활성화
      chrome.action.enable(tabId);
    } else {
      // 익스텐션 비활성화
      chrome.action.disable(tabId);
    }
  }
});
