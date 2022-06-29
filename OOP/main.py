from example import Wordle
import json

with open('/home/castilla/Desktop/sofka/reto_bi/OOP/test.txt', 'r') as f:
    list_words = json.loads(f.read())

game = Wordle(list_words)
game.play()

