# HƯỚNG DẪN TEAMWORK VỚI GIT & GITHUB

> Repository: https://github.com/Dngk1105/Battle-Ship

---

##  1. Chuẩn bị ban đầu

### Cấu hình Git
Chạy lệnh sau (chỉ cần làm 1 lần trên máy):

git config --global user.name "Tên của bạn"
git config --global user.email "email@cua-ban.com"

### Clone project về máy
git clone https://github.com/Dngk1105/Battle-Ship.git
cd Battle-Ship

---

## 2. Quy trình làm việc chuẩn

### Bước 1: Lấy code mới nhất
git checkout main
git pull origin main

### Bước 2: Tạo nhánh mới để làm việc
git checkout -b feature/ten-tinh-nang

### Bước 3: Lưu và commit thay đổi
git add .
git commit -m "Mô tả ngắn gọn thay đổi"

### Bước 4: Push code lên GitHub
git push -u origin feature/ten-tinh-nang

### Bước 5: Tạo Pull Request (PR)
1. Lên GitHub → mở repo → chọn nhánh vừa push  
2. Bấm “Compare & Pull Request”  
3. Ghi mô tả thay đổi → bấm Create Pull Request

### Bước 6: Sau khi PR được merge (Nên có ai đó review trước)
git checkout main
git pull origin main

Xóa nhánh đã xong (tùy chọn):
git branch -d feature/ten-tinh-nang

---

## 3. Chú ý

1. Không code trực tiếp trên nhánh main  
2. Luôn git pull trước khi code và trước khi push 
3. Commit ngắn gọn, dễ hiểu  
4. Luôn tạo Pull Request để merge  
5. Không force push trừ khi hật cần thiết  

---
