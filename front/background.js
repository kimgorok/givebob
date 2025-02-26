// 익스텐션이 설치되거나 업데이트 될 때
chrome.runtime.onInstalled.addListener(() => {
  // 기본적으로 익스텐션 활성화
  chrome.action.enable();
});

// 가천대학교 도메인인지 확인하는 함수
function isGachonDomain(url) {
  return url && url.match(/^https?:\/\/([^\/]+\.)?gachon\.ac\.kr/);
}

// URL이 변경될 때마다 확인
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  // 탭이 로딩되는 동안 여러 번 호출될 수 있으므로 URL 변경 시에만 확인
  if (changeInfo.url) {
    // 변경된 URL이 가천대학교 도메인인지 확인
    if (isGachonDomain(tab.url)) {
      // 가천대학교 도메인이면 익스텐션 활성화
      chrome.action.enable(tabId); // 팝업은 자동으로 열지 않음
    } else {
      // 다른 사이트에서는 (아이콘)비활성화
      chrome.action.disable(tabId);
    }
  }
});

// 새 탭이 활성화될 때마다 확인
chrome.tabs.onActivated.addListener(async (activeInfo) => {
  // 현재 활성화된 탭의 정보 가져옴
  const tab = await chrome.tabs.get(activeInfo.tabId);
  if (isGachonDomain(tab.url)) {
    // 가천대학교 사이트면 활성화
    chrome.action.enable(activeInfo.tabId);
  } else {
    chrome.action.disable(activeInfo.tabId);
  }
});
