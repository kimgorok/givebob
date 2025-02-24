// 익스텐션이 설치될 때
chrome.runtime.onInstalled.addListener(() => {
  // 기본적으로 익스텐션 활성화
  chrome.action.enable();
});

// URL이 변경될 때마다 확인
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.url) {
    // 가천대학교 도메인인지 확인
    if (tab.url.match(/^https?:\/\/([^\/]+\.)?gachon\.ac\.kr/)) {
      // 익스텐션 활성화하고 팝업 표시
      chrome.action.enable(tabId);
      chrome.action.openPopup();
    } else {
      // 다른 사이트에서는 비활성화
      chrome.action.disable(tabId);
    }
  }
});

// 새 탭이 활성화될 때마다 확인
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  const tab = await chrome.tabs.get(activeInfo.tabId);
  if (tab.url && tab.url.match(/^https?:\/\/([^\/]+\.)?gachon\.ac\.kr/)) {
    // 가천대학교 사이트면 팝업 표시
    chrome.action.enable(activeInfo.tabId);
    chrome.action.openPopup();
  } else {
    chrome.action.disable(activeInfo.tabId);
  }
});
