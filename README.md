# Network Programming - OS Simulation Projects

## 📚 Mô tả
Repository chứa các project mô phỏng thuật toán hệ điều hành với giao diện GUI.

## 🎯 Các Project

### 1. CPU Scheduling Algorithms Simulator
**File:** `cpu_scheduler_gui.py`

Mô phỏng các thuật toán lập lịch CPU với animation và thống kê chi tiết.

#### Các thuật toán:
- ✅ **FCFS** (First Come First Served)
- ✅ **SJF** (Shortest Job First)
- ✅ **Priority Scheduling**
- ✅ **Round Robin**

#### Tính năng:
- 🎬 Animation realtime từng bước thực thi
- 📊 Gantt Chart trực quan
- 📈 Thống kê: TAT, WT, RT, CT
- ⏸️ Pause/Resume/Stop controls
- ⚡ Điều chỉnh tốc độ animation
- 🎨 Màu sắc phân biệt tiến trình

#### Sử dụng:
```bash
python cpu_scheduler_gui.py
```

---

### 2. Dining Philosophers Problem Simulator
**File:** `dining_philosophers_gui.py`

Mô phỏng bài toán Dining Philosophers cổ điển với 4 giải pháp đồng bộ hóa.

#### Các giải pháp:
1. 🔴 **Naive Solution** - Dễ gây deadlock
2. 🟢 **Resource Ordering** - Sắp xếp theo thứ tự
3. 🟡 **Limit N-1 Philosophers** - Giới hạn đồng thời
4. 🔵 **Asymmetric Pick** - Chọn không đối xứng ⭐ (Khuyến nghị)

#### Tính năng:
- 🍽️ Visualization bàn tròn với animation
- 🥢 Hiển thị trạng thái forks realtime
- 📊 Thống kê chi tiết từng philosopher
- ⚡ Performance metrics
- 🔴 Phát hiện deadlock tự động
- 🎮 Điều chỉnh 3-10 philosophers

#### Sử dụng:
```bash
python dining_philosophers_gui.py
```

---

## 🛠️ Yêu cầu

### Dependencies:
```bash
pip install matplotlib
```

### Python version:
- Python 3.7+

---

## 📦 Cài đặt

1. Clone repository:
```bash
git clone https://github.com/it2kvku/network-programming.git
cd network-programming
```

2. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

3. Chạy ứng dụng:
```bash
# CPU Scheduler
python cpu_scheduler_gui.py

# Dining Philosophers
python dining_philosophers_gui.py
```

---

## 📸 Screenshots

### CPU Scheduler
- Animation từng bước thực thi
- Gantt Chart với màu sắc
- Thống kê hiệu suất

### Dining Philosophers
- Layout 3 cột chuyên nghiệp
- Bàn tròn với triết gia và đũa
- Thống kê realtime và performance summary

---

## 🎓 Mục đích học tập

### CPU Scheduling:
- Hiểu rõ cách OS quyết định tiến trình nào được chạy
- So sánh hiệu suất các thuật toán
- Nhận biết convoy effect, starvation

### Dining Philosophers:
- Hiểu deadlock và cách phòng tránh
- Các kỹ thuật đồng bộ hóa
- Trade-off giữa hiệu suất và an toàn

---

## 👨‍💻 Tác giả
- GitHub: [@it2kvku](https://github.com/it2kvku)

---

## 📝 License
MIT License

---

## 🤝 Đóng góp
Pull requests are welcome! For major changes, please open an issue first.

---

## 📧 Liên hệ
Nếu có câu hỏi hoặc góp ý, vui lòng tạo issue trên GitHub.

---

**⭐ Nếu thấy project hữu ích, hãy star repo nhé!**
