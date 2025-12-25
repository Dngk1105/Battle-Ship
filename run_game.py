from app import app, db
from app.models import Player  # Import model Player
from app import socketio

if __name__ == "__main__":
    
    socketio.run(app, debug=True)