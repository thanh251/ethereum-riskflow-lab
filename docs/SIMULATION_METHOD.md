# Phương pháp mô phỏng và giới hạn suy luận

## 1. Mục tiêu và phạm vi

Agent-Based Model (ABM) là phương pháp chính để tạo các luồng chuyển tiền có kịch bản và nhãn được kiểm soát. Temporal transaction graph là công cụ hỗ trợ tổng hợp giao dịch, trích xuất đặc trưng và chấm điểm theo luật. Hệ thống hiện tại là nguyên mẫu nghiên cứu, không phải mô hình xác định hành vi phạm pháp.

Tài liệu mô tả cách triển khai hiện có trong [abm.py](../src/riskflow/abm.py), [graph.py](../src/riskflow/graph.py), [risk.py](../src/riskflow/risk.py), [metrics.py](../src/riskflow/metrics.py) và [pipeline.py](../src/riskflow/pipeline.py). Các kế hoạch thí nghiệm trong [EXPERIMENTS.md](EXPERIMENTS.md) cần được phân biệt với kết quả đã thực sự chạy.

| Nguồn | Vai trò | Phạm vi kết luận |
|---|---|---|
| ABM | Sinh giao dịch và nhãn kịch bản để kiểm thử detector | Khả năng nhận diện mẫu do bộ sinh quy định |
| Ethereum Mainnet | Đọc log Transfer USDC trong phạm vi block đã chọn | Đặc trưng và cảnh báo trên tập quan sát, không có nhãn phạm pháp mặc định |
| Sepolia | Kiểm chứng luồng triển khai, replay MockUSDC và ghi sự kiện | Tính hoạt động của luồng kỹ thuật; không chứng minh độ chính xác detector trên Mainnet |

## 2. Cấu hình và các loại tác tử

Mặc định `SimulationConfig` có 300 tác tử, 24 bước, seed ngẫu nhiên `20261021`, mốc thời gian Unix `1770000000`, mỗi bước 300 giây và `adaptive_intensity = 0.55`. Đây là cấu hình mô phỏng; mốc thời gian không phải ngày thực hiện thí nghiệm. Địa chỉ tổng hợp được sinh từ SHA-256 của seed và chỉ số tác tử.

Số dư ban đầu được lấy đều trong khoảng 4.000–20.000 đơn vị mô phỏng. Trọng số chọn loại dưới đây là trọng số lấy mẫu, không phải tỷ lệ cố định: các vị trí đầu được gán lần lượt sáu loại để bảo đảm có đủ loại khi số tác tử cho phép.

| Loại | Trọng số | Hành vi khi được chọn hoạt động |
|---|---|---|
| `normal` | 0.68 | Xác suất 0.35 gửi 20–450 tới một tác tử ngẫu nhiên; thời điểm trong bước |
| `payment` | 0.12 | Khi `step % 6 == 0`, gửi 15–120 tới tối đa 6 tác tử, độ lệch 0–89 giây; nhãn giao dịch `legitimate_fanout` |
| `disperse` | 0.06 | Khi `step % 8 == 1`, gửi 90–260 tới tối đa 9 tác tử, độ lệch 0–119 giây; nhãn `risk_fanout` |
| `consolidate` | 0.05 | Khi `step % 8 == 3`, nhận 70–220 từ tối đa 9 tác tử được chọn, độ lệch 0–119 giây; nhãn `risk_fanin` |
| `relay` | 0.05 | Xác suất 0.70 gửi 120–550 tới một tác tử ngẫu nhiên, độ trễ 0–59 giây |
| `adaptive` | 0.04 | Xác suất 0.70 gửi với số tiền và độ trễ phụ thuộc `adaptive_intensity` |

Với `adaptive`, nếu số tiền cơ sở là `b` và cường độ là `a`, số tiền yêu cầu bằng `b × max(0.15, 1 − a)` và độ trễ bằng `int(step_seconds × a)`. Mặc định số tiền bằng 45% cơ sở và độ trễ 165 giây. Đây là luật tham số hóa do người chạy chọn; tác tử không quan sát cảnh báo để cập nhật chính sách, không tối ưu hàm thưởng và chưa có khả năng tự học. Mã hiện chưa kiểm tra miền giá trị cấu hình; khi khảo sát cường độ nên nêu rõ miền dùng, chẳng hạn `[0, 1]`, thay vì coi đó là ràng buộc đã được chương trình thực thi.

## 3. Trình tự sinh giao dịch và ràng buộc số dư

1. Khởi tạo bộ sinh ngẫu nhiên theo seed, loại tác tử và số dư. Mọi địa chỉ ban đầu có nhãn địa chỉ `normal`.
2. Với mỗi bước, tính `ts = start_timestamp + step × step_seconds`, rồi lấy mẫu không hoàn lại `max(2, int(agents × 0.08))` tác tử hoạt động. Cấu hình cần ít nhất 2 tác tử để phép lấy mẫu này hợp lệ.
3. Duyệt tác tử hoạt động và áp dụng luật theo loại trong bảng trên. Người nhận/người gửi có thể trùng chính tác tử; hàm phát giao dịch sẽ loại tự chuyển.
4. Tại các bước 4, 12 và 20 nếu bước đó có trong lần chạy, chèn mẫu có kiểm soát: tối đa 2 nguồn `disperse` gửi tới tối đa 6 trung gian từ danh sách `relay` rồi `adaptive`; trung gian chuyển tới một đích `consolidate`. Nếu nhóm tương ứng rỗng, mã dùng danh sách tác tử làm dự phòng. Số tiền đầu vào được lấy trong khoảng 150–310; yêu cầu chuyển tiếp bằng 98.5% số tiền này. Giao dịch đầu có độ lệch 0–19 giây; giao dịch chuyển tiếp có độ lệch 45–64 giây. Phần chèn này không áp dụng công thức giảm tiền/độ trễ của `adaptive`.
5. Trả về giao dịch đã sắp theo `(timestamp, tx_hash)` và bảng nhãn địa chỉ. Pipeline lưu CSV, dựng graph, chấm điểm và xuất artifact.

Trong hàm `emit`, với số tiền yêu cầu `q` và số dư nguồn `B`, số tiền thực hiện là `round(min(q, max(0, B)), 6)`. Giao dịch không dương hoặc tự chuyển bị bỏ qua; giao dịch được chấp nhận trừ tiền nguồn và cộng đúng số tiền đó cho đích. Vì vậy số dư được bảo toàn theo từng phép chuyển về mặt mô hình, với sai số số thực và làm tròn; chưa mô phỏng phí gas, giá token hay thanh khoản thị trường.

Số dư được cập nhật theo thứ tự gọi `emit`, trước khi sắp xếp kết quả theo timestamp. Do độ lệch thời gian ngẫu nhiên, thứ tự kiểm tra số dư có thể khác thứ tự thời gian của CSV. Không nên diễn giải đầu ra như một sổ cái được kiểm tra số dư lại theo thời gian blockchain. `block_number = counter // 8` và transaction hash tổng hợp cũng không phải block hay giao dịch Mainnet.

## 4. Nhãn đánh giá

Nhãn giao dịch (`scenario_label`) và nhãn địa chỉ là hai đối tượng khác nhau. `risk_ground_truth` chọn địa chỉ có nhãn `disperse`, `consolidate`, `relay` hoặc `adaptive` làm tập dương.

Nhãn địa chỉ `disperse`/`consolidate` được đặt khi nhánh hành vi tương ứng được kích hoạt; mẫu chèn cũng đặt nhãn cho nguồn, trung gian và đích. Riêng hành vi gửi ngẫu nhiên của `relay`/`adaptive` không tự cập nhật nhãn địa chỉ. Nhãn còn được đặt trước khi biết `emit` có bỏ giao dịch do hết tiền hoặc tự chuyển hay không. Do đó không thể coi mọi giao dịch có nhãn `risk_*` đều biến các địa chỉ liên quan thành mẫu dương, hoặc khẳng định nhãn luôn bảo đảm có giao dịch thành công.

Nhãn này mô tả vai trò trong kịch bản tổng hợp, không phải ground truth pháp lý. `payment` tạo fan-out hợp lệ để quan sát cảnh báo nhầm, nhưng một địa chỉ có thể tham gia nhiều luồng và có nhãn được cập nhật bởi mẫu chèn.

## 5. Temporal transaction graph và đặc trưng

`build_graph` sắp giao dịch theo `(timestamp, block_number, log_index)`, chuẩn hóa địa chỉ chữ thường và bỏ giao dịch có một đầu là zero address. Đỉnh là địa chỉ; cạnh có hướng tổng hợp các giao dịch cùng cặp nguồn–đích, gồm tổng tiền, số giao dịch và thời điểm đầu/cuối. Các đặc trưng được tính trên toàn bộ tập đầu vào của lần xử lý, chưa phải cửa sổ trượt tự cập nhật.

- `tx_count = in_count + out_count`; fan-in/fan-out sử dụng số địa chỉ gửi/nhận phân biệt.
- `active_span = max(0, last_seen − first_seen)`. Đây là thời gian hoạt động trong tập quan sát, không phải tuổi thật của ví.
- `fast_forward_ratio = fast_out / max(1, out_count)`. Một lần gửi được tính là nhanh nếu nguồn đã có ít nhất một lần nhận được xử lý trước đó trong khoảng không quá 900 giây. Một lần nhận có thể hỗ trợ nhiều lần gửi; không ghép cặp theo số tiền hoặc chứng minh cùng một khoản tiền đã đi tiếp.
- `relay_ratio = min(in_amount, out_amount) / max(in_amount, out_amount, 1e-9)`.
- `seed_hops` được tính bằng BFS tối đa 3 bước trên quan hệ kề **không hướng**, dù cạnh giao dịch có hướng. Khoảng cách này không áp đặt thứ tự thời gian hay hướng dòng tiền. Seed ngẫu nhiên của ABM khác với danh sách địa chỉ seed `SEED_ADDRESSES`; danh sách địa chỉ mặc định rỗng.

Điểm được tính trên tất cả đỉnh trước khi xuất graph cho dashboard. `graph.json` mặc định chỉ giữ tối đa 250 đỉnh và 700 cạnh, nên phần hiển thị không phải toàn bộ tập đã chấm điểm.

## 6. Cách chấm điểm và các ngưỡng

Theo `RiskThresholds` và `score_node`, điểm là tổng điểm luật thỏa điều kiện, chặn trên ở 100. Các luật có thể cùng kích hoạt; không có bước huấn luyện hay hiệu chuẩn xác suất.

| Reason code | Điều kiện mặc định | Điểm cộng |
|---|---|---|
| `FAN_OUT` | Ít nhất 5 địa chỉ nhận phân biệt | 25 |
| `FAN_IN` | Ít nhất 5 địa chỉ gửi phân biệt | 25 |
| `FAST_FORWARD` | `out_count >= 2` và `fast_forward_ratio >= 0.60` | 25 |
| `RELAY_BALANCE` | `in_count >= 2`, `out_count >= 2`, `relay_ratio >= 0.80` | 17 |
| `BURST_NEW` | `tx_count >= 4` và `active_span <= 3600` giây | 15 |
| `SEED_EXPOSURE` | Khoảng cách seed 0 / 1 / 2 / 3 bước | 40 / 30 / 20 / 10 |

`score_graph` mặc định chỉ xuất cảnh báo có điểm từ 20. Mức độ là `low` khi dưới 40, `medium` từ 40 đến 69, `high` từ 70. Ngưỡng đánh giá phân loại mặc định là 40; cần phân biệt ngưỡng này với ngưỡng xuất cảnh báo 20. Mỗi cảnh báo kèm reason codes, giá trị quan sát và ngưỡng. Điểm 80 không có nghĩa là xác suất phạm pháp 80%.

## 7. Chỉ tiêu đánh giá và khả năng tái lập

`dataset_metrics` xuất số giao dịch, số đỉnh/cạnh, tổng tiền, trung vị số tiền và timestamp đầu/cuối. Tổng tiền là tổng giá trị các lần chuyển, có thể tính nhiều lần cùng một lượng tiền qua các bước relay; không phải tổng tài sản ban đầu.

Khi có bảng nhãn ABM, `detection_metrics` dùng tập dự đoán `P` gồm địa chỉ có cảnh báo đạt ngưỡng 40, tập dương `T = risk_ground_truth(labels)` và tập quan sát `U = set(graph.nodes)`:

```text
TP = |P ∩ T|              FP = |P − T|
FN = |T − P|              TN = |U − T − P|
precision = TP / (TP + FP)
recall = TP / (TP + FN)
F1 = 2 × precision × recall / (precision + recall)
false_positive_rate = FP / (FP + TN)
```

Mẫu số bằng 0 trả về 0; các tỷ lệ được làm tròn 4 chữ số thập phân. Lưu ý mã chưa giới hạn `T` vào `U`, nên địa chỉ đã được gán nhãn dương nhưng vắng trong graph vẫn có thể được tính FN. `agent_labels` đếm nhãn địa chỉ sau mô phỏng, không phải phân bố loại tác tử lúc khởi tạo.

Để chạy lại, ghi cấu hình đầy đủ, revision mã nguồn, seed, `SEED_ADDRESSES`, ngưỡng và checksum CSV. `scenario.json` hiện lưu seed, số tác tử, số bước, cường độ, đường dẫn CSV và SHA-256; chưa lưu mọi tham số như `start_timestamp` và `step_seconds`. Cùng cấu hình và triển khai có thể kiểm tra tính lặp lại; kiểm thử hiện có xác nhận hai lần chạy cùng cấu hình cho cùng giao dịch và nhãn.

Kế hoạch đánh giá cần chạy nhiều seed và nhiều cường độ, báo cáo biến thiên precision/recall/F1/FPR; so sánh với baseline số tiền và baseline cấu trúc; đối chiếu phân bố amount, degree, đối tác, inter-arrival time và motif với Mainnet. Đây là các bước đánh giá đề xuất trong `EXPERIMENTS.md`, không phải bằng chứng rằng pipeline đã tự động thực hiện hoặc đã đạt một mức chất lượng. Không chọn ngưỡng trên chính tập dùng báo cáo cuối.

## 8. Phân biệt Mainnet, Sepolia và giới hạn kết luận

Mainnet pipeline đọc log USDC, mặc định lùi 12 confirmation, lấy 120 block theo chunk 20 block, loại trùng `(tx_hash, log_index)` và chuẩn hóa amount bằng cách chia `1_000_000`. Manifest ghi phạm vi block và checksum CSV. Pipeline không truyền nhãn vào bước xử lý Mainnet nên không tự có precision/recall trên dữ liệu này. Mức confirmation là cấu hình thu thập, không bảo đảm tuyệt đối không có reorg.

Sepolia dùng MockUSDC và các registry để kiểm tra đăng ký tác tử, replay và ghi cảnh báo. Script xuất payload lấy tối đa 100 cạnh có tổng tiền lớn nhất từ graph đã rút gọn, đổi tổng tiền cạnh sang micro-USDC; vì vậy payload không phải bản sao đầy đủ của chuỗi giao dịch theo thời gian. Xem [runbook](SEPOLIA_RUNBOOK.md) và [bằng chứng triển khai](SEPOLIA_EVIDENCE.md) để đối chiếu receipt/event, tách biệt với chỉ tiêu detector.

Các giới hạn cần giữ khi báo cáo:

- Mẫu dương được thiết kế gần với các luật detector, nên kết quả ABM có thể thuận lợi hơn khi áp dụng lên dữ liệu chưa biết; chưa đủ để suy rộng sang Mainnet.
- Fan-in, fan-out, burst và relay cũng có thể xuất hiện trong thanh toán hợp lệ. Tên `BURST_NEW` không chứng minh ví mới được tạo.
- Địa chỉ không đồng nhất với cá nhân hay tổ chức; quan hệ gần seed không tự chứng minh quyền sở hữu, ý định hay nguồn tiền bất hợp pháp.
- Mô hình chưa tái hiện đầy đủ gas, mempool, hợp đồng DeFi, bridge, nhiều tài sản hoặc hành vi kinh tế. Các trọng số và ngưỡng hiện là lựa chọn thiết kế, chưa phải tham số đã hiệu chuẩn từ Mainnet.
- Cần phân biệt kiểm thử phần mềm, chất lượng nhận diện kịch bản ABM, độ tương đồng với Mainnet và thành công triển khai Sepolia. Không chỉ tiêu nào trong số này tự thay thế các chỉ tiêu còn lại.
