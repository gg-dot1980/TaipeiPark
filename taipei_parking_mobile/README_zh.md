# 附近好停｜臺北市手機停車查詢原型

## 操作方法

1. 開啟 `index.html`：預設顯示明星咖啡館（臺北市武昌街一段7號），地圖範圍為**直線半徑500公尺**，並非驗證後的500公尺步行路線。
2. 輸入其他臺北市地址或地標後按「查詢」，或使用 `?lat=25.04415&lng=121.51271&name=明星咖啡館` 直接開啟目的地。
3. 點候選停車位置再按「Google Maps 導航」。列表路邊優先，其後為官方停車場及OSM候選。**任何無可靠有效時間的空位值，皆不應視為即時空位。**
4. 如果查詢不到資料，請使用內建「北市好停車」官方連結。不應從無資料推論沒有合法車格。

## Cloudflare Pages 部署

將 `index.html`、`_worker.js` 放在同一個 Pages 輸出資料夾，透過 Git 整合部署。此 `_worker.js` 使用 Pages Advanced Mode；未配置 Worker 或僅由本機開啟 HTML 時，官方 XML 將無法由 `/api/...` 載入，請勿把此情況當作無空位。

- `/api/park-static` 臺北市停車場基本資料 XML。
- `/api/park-live` 臺北市停車場剩餘格數 XML。
- `/api/road-segments` 路邊路段資料 XML，預留接口（**尚未實作空間座標配對，不能直接畫為逐格即時車位**）。

官方資料來源：
- https://data.taipei/dataset/detail?id=d5c0656b-5250-4179-a491-c94daa56ef2c
- https://data.taipei/dataset/detail?id=434638ca-8770-42c1-940d-0386a74f6eb9
- https://data.taipei/dataset/detail?id=5a911ea5-1694-4301-808e-e1780d971611

本原型另採用公開 OSM 圖資與 Overpass/Nominatim 外部線上服務（需要網路且受到第三方服務政策與速率限制）；這些候選**不屬官方認證可停車位置**。不得把這類 POI 的存在視為可合法停放。若正式上線，應改用部署在自己的後端的圖資／地理編碼，並於伺服器端快取，遵守來源使用政策。瀏覽器若有網路、但外部服務故障，原型也可能只有目的地標記。

## iPhone「分享 → 附近好停」捷徑設計

建立「捷徑」，啟用「在分享表單中顯示」，接收 URL：
1. 從 Google Maps 目的地位置頁，按「分享」→ 選擇捷徑「附近好停」（不是導航路線本身）。
2. 展開 Google Maps 分享短連結，解析目的地經緯度，或讀取 Google Maps URL 內的 `q=` / `query=` 地點字串。**Google Maps 短網址可能無法在網頁瀏覽器直接解析。**
3. 使用「URL 編碼」組成 `https://你的-pages-網址/?lat=緯度&lng=經度&name=地點名稱`；只有地點文字時則 `?q=地址`；然後「開啟 URL」。
4. 也可把預設地址的網頁加入 iPhone 主畫面，一次點擊即可查看候選車位，最少操作。

**需要另行開發才能達到完整需求**：載入官方53.69MB SHP路邊逐格圖資並轉換WGS84 GeoJSON，驗證 `pktype=01` 等車種與指定時段禁停／費率；逐格即時狀態來源需核對 TDX/官方涵蓋率與時間戳；500公尺**步行**判定需人行路網路由引擎；抵達後概率需長期蒐集歷史資料。此版本不可當成已完成上述能力。

## 資料安全

本版無帳號、無個人追蹤、無 API key；會連線至 Leaflet CDN、OSM 圖磚、OSM Nominatim、Overpass，以及你部署網站所使用的 Cloudflare Pages。自行輸入的地址會發往 Nominatim。導航按鈕則會將選定位置傳給 Google Maps。
