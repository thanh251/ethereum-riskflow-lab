# Quy trình đóng góp và lịch sử Git

Repository chính: https://github.com/thanh251/ethereum-riskflow-lab

Repository đã có lịch sử nhập mã nguồn và các cập nhật của nhóm. Tiếp tục commit trên lịch sử hiện có; không chạy script tạo lại các commit nhập mã, lùi ngày hoặc đổi tác giả của các commit cũ. Commit nhập mã ban đầu ghi nhận lần đưa mã nguồn vào Git, không đại diện cho toàn bộ thời gian phát triển trước đó.

## Lấy dự án và khai báo người đóng góp

```powershell
git clone https://github.com/thanh251/ethereum-riskflow-lab.git
cd ethereum-riskflow-lab
git config user.name "TEN_CUA_BAN"
git config user.email "EMAIL_GITHUB_CUA_BAN"
git log --oneline -10
```

Mỗi thành viên sử dụng tên, email và tài khoản của chính mình. Có thể lấy email noreply từ GitHub Settings > Emails. Không đổi tên Git để đứng tên phần việc của thành viên khác.

## Thực hiện một thay đổi

Trước khi sửa, cập nhật nhánh chính rồi tạo nhánh công việc:

```powershell
git switch main
git pull --ff-only
git switch -c test/abm-regression
```

Sau khi thực sự bổ sung kiểm thử vào `tests/test_abm.py`, chạy và xem lại thay đổi:

```powershell
python -m unittest discover -s tests -v
git diff -- tests/test_abm.py
git add -- tests/test_abm.py
git diff --cached
git commit -m "test: extend ABM regression coverage"
git push -u origin test/abm-regression
```

Ví dụ trên chỉ dùng khi có thay đổi tương ứng. Mở pull request trên GitHub, mô tả phần đã sửa và kết quả kiểm thử để các thành viên khác xem trước khi gộp vào main. Không tạo commit rỗng để tăng số lượng.

## Kiểm tra trước khi nộp

```powershell
git status --short
git log --format="%h | %an | %ad | %s" --date=short -15
git remote -v
```

Thầy có thể xem lịch sử tại https://github.com/thanh251/ethereum-riskflow-lab/commits/main/ và mở từng commit để kiểm tra thay đổi thực tế. Người nộp cần cấp quyền truy cập nếu sau này chuyển repository sang riêng tư.

## Tệp công khai và cấu hình riêng

Không commit `.env`, khóa ví, keystore hoặc `node_modules`. Bằng chứng triển khai công khai được lưu riêng trong `data/results/sepolia_evidence.json` và các ảnh explorer được liệt kê trong `.gitignore`; ví thử nghiệm và kết quả phát sinh khác vẫn được bỏ qua. Địa chỉ hợp đồng và transaction hash là dữ liệu công khai; khóa ký giao dịch phải giữ riêng.
