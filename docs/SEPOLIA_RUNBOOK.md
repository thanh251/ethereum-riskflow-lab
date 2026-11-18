# Runbook Sepolia

## Chuẩn bị

1. Tạo một ví test riêng, không dùng ví chứa tài sản Mainnet.
2. Nhận Sepolia ETH từ faucet được liên kết trên ethereum.org.
3. Sao chép `.env.example` thành `.env`.
4. Điền `SEPOLIA_RPC_URL` và `SEPOLIA_PRIVATE_KEY`.

## Kiểm tra local

Kiểm thử chạy trên mạng mô phỏng local, không cần `.env`, RPC hoặc private key. Cấu hình chỉ đọc thông tin xác thực Sepolia khi chọn `--network sepolia`.

```powershell
cd contracts
npm ci
npm run compile
npm test
```

Nếu gặp `hardhat: Permission denied` hoặc `HHE21` sau khi sao chép project từ máy khác, chạy lại `npm ci` trong `contracts`. Lệnh này thay thế `node_modules` bằng các dependency trong lockfile, tạo lại launcher có quyền thực thi và cài binary native đúng hệ điều hành. Không sao chép `node_modules`, `artifacts` hoặc `cache` giữa các máy. Nếu lỗi vẫn còn, chạy `npx hardhat test --show-stack-traces` để kiểm tra nguyên nhân cụ thể.

## Deploy

```powershell
python scripts/run_abm_demo.py
python scripts/export_sepolia_scenario.py
cd contracts
npm run deploy:sepolia:full
```

Lệnh trên triển khai bốn hợp đồng, replay ba giao dịch mẫu, phát `AlertRaised` và tự lưu:

- `data/results/sepolia_evidence.json`;
- `docs/SEPOLIA_EVIDENCE.md`;
- contract address, deployment transaction hash, receipt status, gas và liên kết Sepolia Etherscan.

## Tạo payload replay

Ở thư mục gốc:

```powershell
python scripts/run_abm_demo.py
python scripts/export_sepolia_scenario.py
```

Payload không chứa số dư Mainnet. Mỗi amount được biểu diễn bằng micro-USDC, phù hợp `decimals = 6` của MockUSDC.

## Bằng chứng demo phải lưu

- chain ID `11155111`;
- địa chỉ hợp đồng;
- transaction hash;
- receipt thành công;
- `ScenarioStarted`, `ScenarioTransfer`, `ScenarioCompleted`;
- `AlertRaised` gồm score, reason code và evidence hash.

