# 🧭 GIT CHEAT SHEET — LỆNH GIT THÔNG DỤNG

## 🧩 1. Cấu hình và khởi tạo

| Mục đích | Lệnh | Giải thích |
|-----------|------|------------|
| Kiểm tra phiên bản Git | `git --version` | Xem Git đã cài chưa |
| Cấu hình tên | `git config --global user.name "Tên của bạn"` | Ghi thông tin commit |
| Cấu hình email | `git config --global user.email "email@cua-ban.com"` | Ghi thông tin commit |
| Khởi tạo repo mới | `git init` | Tạo thư mục `.git` trong project |
| Kết nối với repo GitHub | `git remote add origin <url>` | Gắn repo GitHub với local |
| Kiểm tra remote | `git remote -v` | Xem địa chỉ repo GitHub hiện tại |

---

## 📦 2. Làm việc với file (status, add, commit)

| Mục đích | Lệnh | Giải thích |
|-----------|------|------------|
| Kiểm tra trạng thái file | `git status` | Xem file mới, sửa, xoá |
| Thêm file vào stage | `git add <file>` | Đưa file vào danh sách commit |
| Thêm tất cả file | `git add .` | Đưa toàn bộ file thay đổi vào stage |
| Tạo commit | `git commit -m "Thông điệp"` | Lưu thay đổi cục bộ |
| Sửa commit gần nhất | `git commit --amend` | Thay đổi message commit mới nhất |
| Xem lịch sử commit | `git log` | Hiển thị lịch sử commit |
| Xem ngắn gọn lịch sử | `git log --oneline` | Mỗi commit hiển thị 1 dòng |

---

## 🌿 3. Làm việc với nhánh (branch)

| Mục đích | Lệnh | Giải thích |
|-----------|------|------------|
| Tạo nhánh mới | `git branch <tên-nhánh>` | Tạo nhánh nhưng chưa chuyển qua |
| Tạo và chuyển sang nhánh mới | `git checkout -b <tên-nhánh>` | Tạo + chuyển luôn |
| Liệt kê các nhánh | `git branch` | Xem danh sách nhánh hiện có |
| Chuyển sang nhánh khác | `git checkout <tên-nhánh>` | Di chuyển qua nhánh khác |
| Xoá nhánh đã hoàn thành | `git branch -d <tên-nhánh>` | Xoá nhánh sau khi merge |
| Merge nhánh vào main | `git merge <tên-nhánh>` | Hợp code từ nhánh vào nhánh hiện tại |

---

## ☁️ 4. Làm việc với GitHub (remote)

| Mục đích | Lệnh | Giải thích |
|-----------|------|------------|
| Kéo code mới nhất | `git pull origin main` | Cập nhật code từ GitHub |
| Đẩy code lên GitHub | `git push origin main` | Gửi code local lên GitHub |
| Push lần đầu nhánh mới | `git push -u origin <tên-nhánh>` | Liên kết nhánh local với remote |
| Clone repo về máy | `git clone <url>` | Sao chép repo về máy |
| Xem chi tiết remote | `git remote show origin` | Thông tin kết nối GitHub |

---

## ⚙️ 5. Sửa lỗi, khôi phục, xử lý conflict

| Mục đích | Lệnh | Giải thích |
|-----------|------|------------|
| Hủy thay đổi trong file | `git checkout -- <file>` | Quay lại phiên bản cũ |
| Bỏ file khỏi stage | `git reset <file>` | Gỡ khỏi danh sách commit |
| Hoàn tác commit (giữ code) | `git reset --soft HEAD~1` | Quay lại trước commit gần nhất |
| Hoàn tác commit (mất code) | `git reset --hard HEAD~1` | Xóa commit + code |
| Tạm lưu code chưa xong | `git stash` | Ẩn tạm thay đổi để chuyển nhánh |
| Khôi phục lại code tạm | `git stash pop` | Lấy lại thay đổi đã stash |
| Xem danh sách stash | `git stash list` | Kiểm tra các stash tạm |
| Hủy merge đang bị lỗi | `git merge --abort` | Dừng merge, quay lại trước đó |

---

## 🧠 6. Kiểm tra và hỗ trợ

| Mục đích | Lệnh | Giải thích |
|-----------|------|------------|
| Xem thông tin branch hiện tại | `git branch -vv` | Hiển thị thông tin nhánh và remote |
| So sánh thay đổi | `git diff` | Xem khác biệt giữa code trước/sau |
| Kiểm tra file nào bị sửa | `git diff --name-only` | Chỉ hiển thị tên file thay đổi |
| Xem ai commit dòng nào | `git blame <file>` | Cho biết từng dòng do ai viết |
| Kiểm tra repo sạch chưa | `git status` | Repo sạch nếu không còn file chưa commit |

---

## 🧾 7. Một số tổ hợp lệnh thường dùng

| Tình huống | Lệnh thực hiện |
|------------|----------------|
| Code xong và muốn gửi lên GitHub | `git add . && git commit -m "..." && git push` |
| Cập nhật code mới nhất về máy | `git pull origin main` |
| Tạo nhánh mới để làm tính năng | `git checkout -b feature/...` |
| Merge code sau khi review xong | `git checkout main && git merge feature/... && git push` |

---

❤️ **Mẹo:** Luôn `git pull` trước khi code và luôn làm việc trên nhánh riêng (`feature/...`, `fix/...`).
