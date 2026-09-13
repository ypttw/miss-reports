// MISS & MISS ORDER 每日對帳門戶 - Google Apps Script (GAS) Web App 入口
// 部署方式：
// 1. 在 Google Drive 或 Google 試算表點「擴充功能」->「Apps Script」
// 2. 貼上此 Code.gs，並在左側「+」新增 HTML 檔案命名為 index，貼上 index.html
// 3. 右上角按「部署」->「新部署作業」->「網路應用程式」
//    - 執行身分：我
//    - 存取權：僅限我自己 (最安全，需登入 Google) 或 所有人
// 4. 取得專屬網址：https://script.google.com/macros/s/.../exec

function doGet(e) {
  return HtmlService.createHtmlOutputFromFile('index')
    .setTitle('MISS & MISS ORDER 對帳稽核儀表板')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1.0')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}
