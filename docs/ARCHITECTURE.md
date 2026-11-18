# Kiến trúc hệ thống

```text
Ethereum Mainnet RPC
        |
        v
USDC Transfer ingestion --> CSV + manifest SHA-256
        |
        v
Temporal graph builder --> node/edge features
        |                         ^
        v                         |
Explainable risk score         ABM scenario engine
        |                         |
        +-----------+-------------+
                    v
          JSON artifacts + dashboard
                    |
                    v
          Sepolia replay payload
                    |
                    v
   MockUSDC + registries + event evidence
```

## Ranh giới tin cậy

- Mainnet được đọc, không ký giao dịch và không di chuyển tài sản.
- ABM sinh dữ liệu có ground truth để stress test, không được gọi là bằng chứng Mainnet.
- Sepolia chỉ ghi hành vi thử nghiệm bằng MockUSDC và event.
- Private key chỉ được đọc từ biến môi trường, không lưu trong repository.

## Artifact

| Artifact | Mục đích |
|---|---|
| `mainnet_usdc_*.csv` | Sự kiện Transfer đã chuẩn hóa |
| `*.manifest.json` | Block range, confirmation, checksum và nguồn |
| `graph.json` | Graph rút gọn cho dashboard |
| `alerts.json` | Score, severity và reason codes |
| `metrics.json` | Thống kê dữ liệu hoặc đánh giá ABM |
| `sepolia_payload.json` | Tập giao dịch đại diện để replay |

