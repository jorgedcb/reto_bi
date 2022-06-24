from unittest import result
import requests
import pandas as pd
import numpy as np
class Wordle:
    all = []
    parameters_endpoint = 'https://7b8uflffq0.execute-api.us-east-1.amazonaws.com/game/get_params'
    results_endpoint = 'https://7b8uflffq0.execute-api.us-east-1.amazonaws.com/game/check_results'
    def __init__(self,words_list,user:tuple):

        #add a check for the user


        # Run validations to the received arguments
        # assert price >= 0, f"Price {price} is not greater than or equal to zero!"
        
        # Assign to self object
        self.list_letter_index_incorrect = [] #check if this is the best way to do it
        self.wrong_letters = [] #check if this is the best way to do it
        self.__num_attempts  = 0
        self.__attempt_list = []
        self.__last_attempt = ''
        self.__list_results = []
        self.user = user
        self.__parameters = self._get_parameters(user) # tengo que decirle .json cuando sea el de verdad
        self.__id = self.__parameters['id']
        self.__length_word = self.__parameters['length_word']
        self.__vowels = self.__parameters['vowels']
        self.__consonants = self.__parameters['consonants']
        self.__words_list = words_list
        self.__df_game = self._get_df_game()
    @property
    def num_attempts(self):
        return self.__num_attempts #add funtionality that can't find the word in 6 attempps

    def _increase_num_attempts(self):
        self.__num_attempts += 1 

    @property
    def attempt_list(self):
        return self.__attempt_list
    
    def _append_attempt(self):
        self.__attempt_list.append(self.last_attempt)
        print(f"{self.last_attempt} - attempt #{self.num_attempts}")

    @property
    def last_attempt(self):
        return self.__last_attempt

    def _set_last_attempt(self,word):
        self.__last_attempt = word
    
    @property
    def list_results(self):
        return self.__list_results
    
    def _append_result(self,json):
        self.__list_results.append(json)
        print(json) #add .json cuando sea el de verdad y arreglar como se ve

    def _get_parameters(self,user):
        """The format of the response is:
        {"id": "string",
        "length_word": int,
        "vowels": int,
        "consonants": int
        }
        """
        just_prove = {"id": "1234d3",
            "length_word": 5,
            "vowels": 3,
            "consonants": 2}
        return just_prove
        #return requests.get(self.parameters_endpoint, auth = user)

    @property
    def parameters(self):
        return self.__parameters

    @property
    def id(self):
        return self.__id

    @property
    def length_word(self):
        return self.__length_word
    
    @property
    def vowels(self):
        return self.__vowels
    
    @property
    def consonants(self):
        return self.__consonants

    @property
    def words_list(self):
        return self.__words_list

    
    @property
    def df_game(self):
        return self.__df_game
    
    def _create_df_from_list(self):
        self.df_all_words = pd.DataFrame(self.words_list, columns =['Words'])

    def _add_number_letters_column(self):
        self.df_all_words['Number of letters'] = self.df_all_words['Words'].str.len()    
    
    def _add_vowels_column(self):
        self.df_all_words['Number of vowels'] = self.df_all_words['Words'].str.count(r'[aeiou]')

    def _add_consonant_column(self):
        self.df_all_words['Number of consonants'] = (self.df_all_words['Number of letters'] 
                                                     - self.df_all_words['Number of vowels'])
                                            
    def _restrict_df_by_parameter(self):
        conditions = (self.df_all_words['Number of letters'] == self.__length_word)  & (self.df_all_words['Number of vowels'] == self.__vowels) & (self.df_all_words['Number of consonants'] == self.consonants)
        return self.df_all_words.loc[conditions]

    def _get_df_game(self):
        self._create_df_from_list()
        self._add_number_letters_column()
        self._add_vowels_column()
        self._add_consonant_column()
        return self._restrict_df_by_parameter()

    def valid_words_list(self):
        return list(self.df_game['Words'].values)

    def word_from_list(self,list_words):
        new_attempt = max(list_words, key=lambda word: len(set(word)))
        return new_attempt


    def first_attempt(self):
        word = self.word_from_list(self.valid_words_list())
        return word


    def filter_position_letter(self, list_tupple):
        #add a comment

        df = self.df_game
        if list_tupple:
            bool_words = [df['Words'].str[index].eq(letter) for index, letter in list_tupple]
            list_words = list(df.loc[np.logical_and.reduce(bool_words), 'Words'].values)
            return list_words
        else: 
            return []
    
    def new_attempt(self):
        #index where the list of bools were true
        correct_index_letters_try = np.where(self.last_result_json['position_array'])[0]
        #getting index from letters that are in the word but are in wrong position
        index_letters_wrong_position = [index for index,letter in enumerate(self.last_attempt) if letter in self.last_result_json['right_letters_in_wrong_positions']] #cambiar 0 por current attempt
        #erase the index if are in the index of correct words
        incorrect_index_try = [index for index in index_letters_wrong_position if index not in correct_index_letters_try]
        #enumerate the atempt ex jorge = [(j,0),(o,1)]
        position_try = list(enumerate(self.last_attempt))
        #get the tuples that are right
        list_letter_index_correct = [position_try[j] for j in correct_index_letters_try]
        #get tupples that the letter exits on the word but are in wrong position
        self.list_letter_index_incorrect.extend([position_try[j] for j in incorrect_index_try])
        #list of letters that are in the correct position
        letter_correct_position = [self.last_attempt[j] for j in correct_index_letters_try]
        #list of letters that definitely aren't in the word
        wrong_letters_last_try = list(set(self.last_attempt) - set(self.last_result_json['right_letters_in_wrong_positions']) - set(letter_correct_position))
        self.wrong_letters.extend(wrong_letters_last_try)
        if list_letter_index_correct:
            valid_words = self.filter_position_letter(list_letter_index_correct)
        else:
            valid_words = self.valid_words_list
        invalid_words = self.filter_position_letter(self.list_letter_index_incorrect)
        valid_list = [word for word in valid_words if word not in invalid_words]
        final_list = [word for word in valid_list if all(invalid_letter not in word for invalid_letter in self.wrong_letters)]
        new_try = self.word_from_list(final_list)
        return new_try


    def update_data(self,word):
        self._increase_num_attempts()
        self._set_last_attempt(word)
        self._append_attempt()
        

    def send_attemp(self,word):
        self.update_data(word)
        #result = requests.post(self.results_endpoint,json = {"result_word": word}, auth = self.user)
        result = {
                "word_sent": "abeto",
                "score": 0.5,
                "try_datetime": 'no importa por ahora',
                "position_array": [False,False,False,False,True],
                "right_letters_in_wrong_positions": []
                }
        self._append_result(result)
        self.last_result_json = result  #ponerle el .json
        return result

    def send_attemp1(self,word):
        print('wtd',word)
        self.update_data(word)
        #result = requests.post(self.results_endpoint,json = {"result_word": word}, auth = self.user)
        result = {
                "word_sent": "guido",
                "score": 0.88,
                "try_datetime": 'no importa por ahora',
                "position_array": [False,False,True,False,True],
                "right_letters_in_wrong_positions": ['u']
                }
        self._append_result(result)
        self.last_result_json = result  #ponerle el .json
        return result
    
    def play(self):
        #sending first attemp to the endpoint
        self.send_attemp(self.first_attempt())
        self.send_attemp1(self.new_attempt())
        print(self.new_attempt())