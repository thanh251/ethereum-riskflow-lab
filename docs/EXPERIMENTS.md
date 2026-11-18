# Thiết kế thực nghiệm

## E1 Chất lượng dữ liệu Mainnet

- Đối chiếu một mẫu log với RPC receipt/explorer.
- Kiểm tra khóa duy nhất `(transaction_hash, log_index)`.
- Ghi số block, confirmation, số bản ghi và SHA-256.

## E2 Baseline

- Baseline số tiền: cảnh báo theo percentile của amount.
- Baseline cấu trúc: luật fan-in/fan-out tĩnh.
- Mô hình đề xuất: fan-in, fan-out, fast-forward, relay, burst và seed exposure.

## E3 Fidelity của ABM

So sánh Mainnet và ABM theo:

- phân phối amount;
- in/out degree;
- số đối tác;
- inter-arrival time;
- tỷ lệ relay và motif nhiều bước.

## E4 Stress test thích nghi

Chạy nhiều giá trị `adaptive_intensity` và nhiều seed. Báo cáo precision, recall, F1, false-positive rate và khoảng biến thiên. Không chọn ngưỡng trên tập dùng để báo cáo cuối.

## E5 Sepolia

Đối chiếu số giao dịch kỳ vọng, event `ScenarioTransfer`, event `AlertRaised`, transaction receipt và tổng MockUSDC. Lỗi faucet, nonce hoặc gas được phân loại là lỗi triển khai, không phải hiệu năng detector.

