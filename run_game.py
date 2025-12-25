from app import app, db
from app.models import Player  # Import model Player
from app import socketio

def seed_database():
    """Hàm này chuyên dùng để tạo dữ liệu mẫu (AI)"""
    with app.app_context():
        db.create_all()
        db.session.commit()
        print("Hoàn tất kiểm tra dữ liệu mẫu.")

if __name__ == "__main__":
    # Tự động chạy hàm tạo AI mỗi khi bật server
    seed_database() 
    
    socketio.run(app, debug=True)