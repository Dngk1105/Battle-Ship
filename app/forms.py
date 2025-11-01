from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired
from app.models import AI
import sqlalchemy as sa
from app import db


class EnterNameForm(FlaskForm):
    playername = StringField('Tên', validators=[DataRequired()])
    remember = BooleanField('Lưu tên tao nhé!',)
    submit = SubmitField('Vào Thôi')
    
class NewGameForm(FlaskForm):
     
    mode = SelectField(
        "Chế độ chơi",
        choices=[('ai', 'Đấu với máy'), ('human', 'đấu với người')], 
        validators=[DataRequired()],
    )
    
    ai_type = SelectField(
        "Chọn AI",
        choices=[]
    )
    
    submit = SubmitField('Vào Thôi')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        ais = db.session.scalars(sa.select(AI)).all()
        self.ai_type.choices = [(ai.name, ai.name) for ai in ais]
        
        
class StartGameForm(FlaskForm):
    submit = SubmitField("Vào")

class CancelGameForm(FlaskForm):
    submit = SubmitField("Hủy")
        
class JoinGame(FlaskForm):
    game_id = StringField('Nhập id phòng', validators=[DataRequired()])
    submit = SubmitField('Vào Thôi')