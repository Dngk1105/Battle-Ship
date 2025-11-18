import numpy
from app import db
from app.models import Player
from app.ai.ai_interface import BaseAI

class ProbAI():
    """
    AI dùng phổ xác xuất để quyết định phát bắn
    """
    
    def __init__(self, game, name = None):
        super.__init__(game, name)
        self.init_matrix = self.init_prob_matrix()
            
    def place_ships(self):
        """
        
        """
        return 
    
    def make_shot(self):
        return
    
    def init_prob_matrix(self):
        return 

    def calc_prob_matrix(self, board):
        return
    
    def miss_update(self, prob_matrix, x, y,):
        return 
    
    def hit_update(self, prob_matrix, x, y):
        return
    
    def sunk_update(self, prob_matrix, target_name, x, y):
        return 