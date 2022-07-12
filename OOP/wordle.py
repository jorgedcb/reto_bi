import requests
import pandas as pd
import numpy as np
import json
from os import path
import string
import datetime
from connect import Postgres_connection
from datetime import datetime as dt
from datetime import timezone
from datetime import timedelta


class Wordle:

    default_user = ("jorge.castilla", "5cbdaf7e3c844ec882f576ec2ec4c9a4")
    parameters_endpoint = (
        "https://7b8uflffq0.execute-api.us-east-1.amazonaws.com/game/get_params"
    )
    results_endpoint = "https://7b8uflffq0.execute-api.us-east-1.amazonaws.com/game/check_results"
    filename = "/home/castilla/Desktop/sofka/reto_bi/OOP/responses.json"

    def __init__(
        self,
        words_list,
        user=default_user,
        parameters_endpoint=parameters_endpoint,
        results_endpoint=results_endpoint,
        filename=filename,
    ):
        # Assign to self object
        self.__start_time = datetime.datetime.now()
        self.parameters_endpoint = parameters_endpoint
        self.results_endpoint = results_endpoint
        self.filename = filename
        self.__num_attempts = 0
        self.__attempt_list = []
        self.__last_attempt = ""
        self.__list_results = []
        self.__user = user
        parameters = self._get_parameters()
        self.__parameters = parameters.json()
        self.__id = self.__parameters["id"]
        self.__length_word = self.__parameters["length_word"]
        self.__vowels = self.__parameters["vowels"]
        self.__consonants = self.__parameters["consonants"]
        self.__words_list = words_list
        self.__df_game = self._get_df_game()
        self.__wrong_letters = []
        self.__must_letters = []
        self.__list_letter_index_incorrect = []
        self._insert_parameters()

    @property
    def num_attempts(self):
        return self.__num_attempts

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

    def _set_last_attempt(self, word):
        self.__last_attempt = word

    @property
    def list_results(self):
        return self.__list_results

    @property
    def user(self):
        return self.__user

    def _append_result(self, result):
        self.__list_results.append(result)
        print(result.json())

    def print_results(self):
        for response in self.list_results:
            print(response.json())

    def _get_parameters(self):
        """The format of the response is:
        {"id": "string",
        "length_word": int,
        "vowels": int,
        "consonants": int
        }
        """
        response = requests.get(self.parameters_endpoint, auth=self.user)
        self.__mycode_time = datetime.datetime.now()
        self._append_response("nuevo juego")
        self._append_response(response.json())
        print(response.json())
        return response

    def _insert_parameters(self):
        tuple_parameters = (
            self.id,
            self.length_word,
            self.vowels,
            self.consonants,
            self.__start_time,
        )
        Postgres_connection.insert_game(tuple_parameters)

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

    @property
    def must_letters(self):
        return self.__must_letters

    @property
    def wrong_letters(self):
        return self.__wrong_letters

    def _create_df_from_list(self):
        self.df_all_words = pd.DataFrame(self.words_list, columns=["Words"])

    def _add_number_letters_column(self):
        self.df_all_words["Number of letters"] = self.df_all_words[
            "Words"
        ].str.len()

    def _add_vowels_column(self):
        self.df_all_words["Number of vowels"] = self.df_all_words[
            "Words"
        ].str.count(r"[aeiou]")

    def _add_consonant_column(self):
        self.df_all_words["Number of consonants"] = (
            self.df_all_words["Number of letters"]
            - self.df_all_words["Number of vowels"]
        )

    def _add_score_column(self):
        self.__df_game["score"] = self.df_game["Words"].apply(self.get_score)

    def _restrict_df_by_parameter(self):
        conditions = (
            (self.df_all_words["Number of letters"] == self.__length_word)
            & (self.df_all_words["Number of vowels"] == self.__vowels)
            & (self.df_all_words["Number of consonants"] == self.consonants)
        )
        return self.df_all_words.loc[conditions]

    def _get_df_game(self):
        """Return a Pandas Dataframe created from the list of possible words."""
        self._create_df_from_list()
        self._add_number_letters_column()
        self._add_vowels_column()
        self._add_consonant_column()
        return self._restrict_df_by_parameter()

    def _valid_words_list(self):
        return list(self.df_game["Words"].values)

    def _filter_df(self, valid_words):
        """Filter words that aren't in valid words"""
        df = self.df_game
        self.__df_game = df[df["Words"].isin(valid_words)]

    def _create_df_scores(self):
        """Return a dataframe with how many words are per letter 
        and index in the words that are still valids."""

        alphabet_list = list(string.ascii_lowercase)
        alphabet_list.append("ñ")
        columns = [*range(1, self.length_word + 1)]
        df_score = pd.DataFrame(columns=columns)
        for letter in alphabet_list:
            position_list = []
            for word in self.df_game["Words"]:
                if letter in word:
                    position_list.extend(
                        [
                            pos + 1
                            for pos, char in enumerate(word)
                            if char == letter
                        ]
                    )

            dicts = {"Letters": letter}
            for i in range(1, self.length_word + 1):
                count = position_list.count(i)
                dicts[i] = count
            df_score = pd.concat([df_score, pd.DataFrame.from_records([dicts])])
        df_score = df_score.set_index("Letters")
        self.__df_score = df_score
        return df_score

    def get_score(self, word):
        """Set a score for each word that are still valid."""
        position = 0
        score = 0
        for letter in word:
            position += 1
            score += self.__df_score.at[letter, position]
        return score * len(set(word))

    def _select_best_word(self, list_words):
        """Select the word with the best score, this score is set by how common each
        letter is in a specific position in the remaining valid words."""
        print(f"There are {len(list_words)} possible words left")
        self._filter_df(list_words)
        self._create_df_scores()
        self._add_score_column()
        return self.df_game[self.df_game.score == self.df_game.score.max()][
            "Words"
        ].values[0]

    def _valid_words(self, index_correct_letters):
        """Get words that match the letter and position which the api return True.
        I.e: If i send jorge and the api return [False, True, False, False, False]
        get the words with an 'o' in second position."""
        list_letter_index_correct = [
            (index, letter)
            for index, letter in enumerate(self.last_attempt)
            if index in index_correct_letters
        ]
        df = self.df_game
        if list_letter_index_correct:
            bool_words = [
                df["Words"].str[index].eq(letter)
                for index, letter in list_letter_index_correct
            ]
            list_words = list(
                df.loc[np.logical_and.reduce(bool_words), "Words"].values
            )
            return list_words
        else:
            return self._valid_words_list()

    def _invalid_words(self, index_correct_letters):
        incorrect_index_try = [
            index
            for index, letter in enumerate(self.last_attempt)
            if (
                letter in set(self.must_letters)
                and index not in index_correct_letters
            )
        ]
        self.__list_letter_index_incorrect.extend(
            [
                (index, letter)
                for index, letter in enumerate(self.last_attempt)
                if index in incorrect_index_try
            ]
        )
        df = self.df_game
        if self.__list_letter_index_incorrect:
            bool_words = [
                df["Words"].str[index].eq(letter)
                for index, letter in self.__list_letter_index_incorrect
            ]
            list_words = list(
                df.loc[np.logical_or.reduce(bool_words), "Words"].values
            )
            return list_words
        else:
            return []

    def _update_must_letters(self, index_correct_letters):
        """Letters that must be in the word."""
        letter_correct_position = [
            self.last_attempt[j] for j in index_correct_letters
        ]
        right_letters = self.__last_result_json[
            "right_letters_in_wrong_positions"
        ]
        right_letters.extend(letter_correct_position)
        self.__must_letters = right_letters
        return self.must_letters

    def _update_wrongs_letters(self):
        """Letters that can't be in the word."""
        wrong_letters_last_try = list(
            set(self.last_attempt) - set(self.must_letters)
        )
        self.__wrong_letters.extend(wrong_letters_last_try)

    def _final_list(self, valid_words, invalid_words):
        """Return list of words that watch all the filters."""
        right_letters = self.must_letters
        valid_list = [word for word in valid_words if word not in invalid_words]
        a_list = [
            word
            for word in valid_list
            if all(
                invalid_letter not in word
                for invalid_letter in self.wrong_letters
            )
        ]
        final_list = [
            word
            for word in a_list
            if all(
                right_letters.count(valid_letter) <= word.count(valid_letter)
                for valid_letter in right_letters
            )
        ]
        return final_list

    def _first_attempt(self):
        word = self._select_best_word(self._valid_words_list())
        return word

    def _new_attempt(self):
        """Thit method is used to get any attempt after the first one."""
        correct_index_letters_try = np.where(
            self.__last_result_json["position_array"]
        )[0]
        self._update_must_letters(correct_index_letters_try)
        self._update_wrongs_letters()
        valid_words = self._valid_words(correct_index_letters_try)
        invalid_words = self._invalid_words(correct_index_letters_try)
        final_list = self._final_list(valid_words, invalid_words)
        new_try = self._select_best_word(final_list)
        return new_try

    def get_attempt(self):
        """Return a new attempt."""
        if self.num_attempts == 0:
            return self._first_attempt()
        else:
            return self._new_attempt()

    def _update_data(self, word):
        self._increase_num_attempts()
        self._set_last_attempt(word)
        self._append_attempt()

    def send_attemp(self, word):
        self._update_data(word)
        result = requests.post(
            self.results_endpoint, json={"result_word": word}, auth=self.user
        )
        self._append_response(result.json())
        self._append_result(result)
        self.__last_result_json = result.json()
        self._insert_attempt()
        return result

    def _insert_attempt(self):
        result = self.__last_result_json
        last_id = Postgres_connection.get_last_id()
        utc_datetime = dt.fromisoformat(result["try_datetime"]).astimezone(
            timezone.utc
        )
        offset = timedelta(hours=10)
        time = utc_datetime - offset
        tuple_attempt = (
            last_id,
            result["word_sent"],
            result["score"],
            time,
            result["position_array"],
            result["right_letters_in_wrong_positions"],
            result["current_attemps"],
        )
        Postgres_connection.insert_attempt(tuple_attempt)

    def _security(self):
        x = input("Write stop for stop:")
        if x == "stop":
            return 1
        else:
            return self.__last_result_json["score"]

    def play(self):
        score = 0
        while score != 1:
            self.send_attemp(self.get_attempt())
            score = self._security()
        self._save_time()

    def play_automatic(self):
        score = 0
        while score != 1:
            self.send_attemp(self.get_attempt())
            score = self.__last_result_json["score"]
        self._save_time()

    def _save_time(self):
        end = datetime.datetime.now()
        code_time = end - self.__mycode_time
        overall_time = end - self.__start_time
        self._append_response({"overall_time": str(overall_time)})
        self._append_response({"code_time": str(code_time)})
        last_id = Postgres_connection.get_last_id()
        tuple_information = (
            last_id,
            end,
            code_time,
            overall_time,
            self.last_attempt,
            self.num_attempts,
        )
        Postgres_connection.insert_information(tuple_information)

    def _append_response(self, response):
        """Add the responses to the json file """
        listObj = []
        if path.isfile(self.filename) is False:
            raise Exception("File not found")
        with open(self.filename) as fp:
            listObj = json.load(fp)
        listObj.append(response)
        with open(self.filename, "w") as json_file:
            json.dump(listObj, json_file, indent=4, separators=(",", ": "))

    @classmethod
    def responses_json(cls):
        """Return all responses stored in the json file"""
        if path.isfile(cls.filename) is False:
            raise Exception("File not found")
        with open(cls.filename) as fp:
            list_responses = json.load(fp)
        return list_responses

    @classmethod
    def send_try(cls, word):
        result = requests.post(
            cls.results_endpoint,
            json={"result_word": word},
            auth=cls.default_user,
        )
        return result

    @classmethod
    def append_response(cls, response):
        """Return all responses stored in the json file."""
        listObj = []
        if path.isfile(cls.filename) is False:
            raise Exception("File not found")
        with open(cls.filename) as fp:
            listObj = json.load(fp)
        listObj.append(response)
        with open(cls.filename, "w") as json_file:
            json.dump(listObj, json_file, indent=4, separators=(",", ": "))
