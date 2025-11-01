from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from datetime import datetime, timedelta
import sqlalchemy as sa
from flask_socketio import SocketIO  # ✅ thêm dòng này

app = Flask(__name__)
app.config.from_object(Config)
socketio = SocketIO(app, cors_allowed_origins="*")
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'entername'
login.login_message = "Nhập tên trước khi vào bạn nhé!"


# def cleanup_old_games():
#     from app.models import Game
#     expired = db.session.scalars(
#         sa.select(Game).where(
#             Game.status == "pending",
#             Game.timestamp < datetime.utcnow() - timedelta(hours=2)
#         )
#     ).all()
#     for g in expired:
#         db.session.delete(g)
#     db.session.commit()
#     print(f" Dọn {len(expired)} game quá hạn")

# with app.app_context():
#     cleanup_old_games()

from app import routes, models, socket_events
