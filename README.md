# Ethereum RiskFlow Lab

Nguyên mẫu nghiên cứu cho đề tài **Mô phỏng và cảnh báo luồng tiền rủi ro trên Ethereum Mainnet bằng Agent-Based Model, temporal transaction graph và kiểm chứng trên Sepolia Testnet**.

Hệ thống không kết luận một địa chỉ là phạm pháp. Điểm rủi ro chỉ dùng để ưu tiên trường hợp cần xem xét và luôn đi kèm lý do.

## Thành viên Nhóm 2

| Mã sinh viên | Họ và tên | Vai trò chính |
|---|---|---|
| B23DCTC081 | Vũ Thị Hà Nhi | Điều phối nghiên cứu, nội dung và đánh giá |
| B23DCTC095 | Châu Tuấn Thành | Dữ liệu Mainnet và temporal graph |
| B23DCTC005 | Nguyễn Duy Anh | ABM, risk scoring, Sepolia và dashboard |

## Các mô-đun

- `riskflow.rpc`: đọc log `Transfer` USDC đã xác nhận từ Ethereum Mainnet.
- `riskflow.graph`: dựng temporal directed weighted graph và trích xuất đặc trưng.
- `riskflow.abm`: sinh kịch bản bình thường, fan-out, fan-in, relay và thích nghi.
- `riskflow.risk`: chấm điểm 0-100 kèm reason codes.
- `riskflow.pipeline`: tạo artifact dữ liệu, graph, cảnh báo và metrics.
- `riskflow.server`: dashboard local không cần thư viện web ngoài.
- `contracts`: MockUSDC, AgentRegistry, ScenarioRecorder và RiskAlertRegistry cho Sepolia.

## Chạy nhanh không cần cài thư viện ngoài

Yêu cầu Python 3.11 trở lên.

```powershell
Copy-Item .env.example .env
python scripts/run_abm_demo.py
python scripts/run_dashboard.py
```

Trên máy đang dùng Codex, có thể chạy gọn bằng:

```powershell
.\start_demo.ps1
```

Mở `http://127.0.0.1:8080`. Lệnh đầu tạo dữ liệu ABM có nhãn đã biết, temporal graph, cảnh báo và metrics.

## Lấy dữ liệu USDC thật từ Mainnet

Đặt `MAINNET_RPC_URL` trong `.env`, sau đó:

```powershell
python scripts/run_mainnet.py --blocks 120
python scripts/run_dashboard.py
```

Hoặc:

```powershell
.\start_demo.ps1 -UseMainnet -Blocks 120
```

Pipeline lấy block mới nhất, trừ số confirmation, quét log theo từng chunk và lưu:

- `data/raw/mainnet_usdc_<from>_<to>.csv`
- `data/raw/mainnet_usdc_<from>_<to>.manifest.json`
- `data/processed/graph.json`
- `data/processed/alerts.json`
- `data/processed/metrics.json`

Nếu endpoint công cộng giới hạn `eth_getLogs`, giảm `RPC_BLOCK_CHUNK` hoặc dùng RPC riêng. Dữ liệu đầu vào được khóa bằng phạm vi block và SHA-256 trong manifest.

## Chạy kiểm thử

```powershell
python -m unittest discover -s tests -v
```

## Sepolia

Phần hợp đồng dùng Hardhat 3 và Node.js 22 trở lên:

```powershell
cd contracts
npm ci
npx hardhat test
npx hardhat ignition deploy ignition/modules/RiskFlow.ts --network sepolia
```

Kiểm thử local không cần RPC hoặc khóa ví Sepolia. Khi chuyển project giữa Windows, macOS hoặc Linux, chạy lại `npm ci` trong `contracts` để cài đúng binary và quyền thực thi; không sao chép `node_modules` từ máy khác. Xem [runbook](docs/SEPOLIA_RUNBOOK.md) nếu gặp lỗi khởi động Hardhat.

Trước khi deploy, đặt `SEPOLIA_RPC_URL` và `SEPOLIA_PRIVATE_KEY` trong `.env` ở thư mục gốc. Chỉ dùng ví thử nghiệm không chứa tài sản Mainnet. Sau khi deploy, dùng `python scripts/export_sepolia_scenario.py` để tạo payload replay từ artifact ABM.

## Giới hạn

- Một địa chỉ không tương đương một cá nhân hoặc tổ chức.
- Fan-in, fan-out và relay cũng xuất hiện trong hoạt động hợp pháp.
- Endpoint RPC công cộng có thể giới hạn truy vấn.
- ABM là stress test có kiểm soát, không thay thế bằng chứng Mainnet.
- Sepolia chỉ chứng minh luồng kỹ thuật, không đại diện thanh khoản hay chi phí Mainnet.

## Nguồn kỹ thuật chính

- Google Cloud Blockchain Analytics Ethereum schema: https://docs.cloud.google.com/blockchain-analytics/docs/schema
- Ethereum network documentation: https://ethereum.org/developers/docs/networks/
- Circle USDC on Ethereum: https://www.circle.com/multi-chain-usdc/ethereum
- Hardhat 3: https://hardhat.org/docs/getting-started

