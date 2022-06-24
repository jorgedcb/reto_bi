from wordle import Wordle
import json

with open('/home/castilla/Desktop/sofka/reto_bi/OOP/test.txt', 'r') as f:
    list_words = json.loads(f.read())

#user = ('jorge.castilla','5cbdaf7e3c844ec882f576ec2ec4c9a4')
user = ('jorge','sofka')



game = Wordle(list_words,user)

first_attempt = game.get_attempt()
print(first_attempt)
game.send_attemp(first_attempt)
second_attemp = game.get_attempt()
print(second_attemp)
game.send_attemp1(second_attemp)
third_attemp = game.get_attempt()
print(third_attemp)
game.send_attemp2(third_attemp)
#print(game.list_results)

#print(game.list_letter_index_incorrect)
print(game.get_attempt())
#game.send_attemp2(game.get_attempt())
#game.send_attemp2(game.get_attempt())



#print(game1.attempt_list)
# print(game1.user)
# print(game1.parameters)
# print(game1.id)
# print(game1.length_word)
# print(game1.vowels)
# print(game1.consonants)
