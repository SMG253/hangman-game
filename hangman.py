import random
import re
from collections import Counter

class HangmanSolver:
    VOWELS = set('aeiou')
    
    def __init__(self, word_list, max_tries=6):
        self.word_list = word_list
        self.max_tries = max_tries
        self.reset()

    def reset(self):
        self.tries_left = self.max_tries
        self.guessed = set()
        self.correct = set()
        self.current_pattern = []
        self.secret_word = ''
        self.possible_words = []
        self.last_list = []  # Final possible words

    def start_game(self, secret_word):
        self.reset()
        self.secret_word = secret_word.lower()
        self.current_pattern = ['_'] * len(secret_word)
        self.possible_words = [w for w in self.word_list if len(w) == len(secret_word)]
        print(f"The secret word has {len(secret_word)} letters.")

        if "ff" in self.secret_word:
            pattern = r".*ff.*"
            ff_words = [w for w in self.possible_words if re.search(pattern, w)]
            print(f"Words containing 'ff': {ff_words}")

    def update_pattern(self, guess):
        for i, ch in enumerate(self.secret_word):
            if ch == guess:
                self.current_pattern[i] = guess

    def pattern_to_regex(self):
        return '^' + ''.join(ch if ch != '_' else '.' for ch in self.current_pattern) + '$'

    def filter_possible_words(self):
        regex = re.compile(self.pattern_to_regex())
        wrong_letters = self.guessed - set(self.current_pattern)
        
        survivors = []
        rejected = []

        for word in self.possible_words:
            if regex.match(word) and not any(l in word for l in wrong_letters):
                survivors.append(word)
            else:
                rejected.append(word)

        self.possible_words = survivors
        self.last_list = survivors.copy()

        # Show 2–3 rejected words for debugging
        if rejected:
            sample_rejected = rejected[:3]
            print(f"Filtered out (sample): {sample_rejected}")

    def get_letter_frequencies(self):
        counts = Counter()
        for word in self.possible_words:
            unique_letters = set(word) - self.guessed
            counts.update(unique_letters)
        return counts

    def next_guess(self):
        self.filter_possible_words()
        freqs = self.get_letter_frequencies()

        if not freqs:
            return None

        vowels_left = [v for v in self.VOWELS if v not in self.guessed and v in freqs]
        if vowels_left:
            return max(vowels_left, key=lambda v: freqs[v])

        consonants = [(l, c) for l, c in freqs.items() if l not in self.VOWELS]
        if consonants:
            consonants.sort(key=lambda x: x[1], reverse=True)
            return consonants[0][0]

        return None

    def play(self):
        while self.tries_left > 0 and '_' in self.current_pattern:
            guess = self.next_guess()
            if guess is None:
                break

            self.guessed.add(guess)
            if guess in self.secret_word:
                self.correct.add(guess)
                self.update_pattern(guess)
                print(f"Correct guess: '{guess}'")
            else:
                self.tries_left -= 1
                print(f"Wrong guess: '{guess}', tries left: {self.tries_left}")

            print("Progress: " + ' '.join(self.current_pattern))

        print("\nFinal possible words list:", self.last_list)
        return '_' not in self.current_pattern


if __name__ == "__main__":
    with open("word.txt", "r", encoding="utf-8") as file:
        words = [line.strip().lower() for line in file if line.strip()]

    solver = HangmanSolver(words, max_tries=6)
    secret = random.choice(words)
    solver.start_game(secret)
    won = solver.play()

    if won:
        print(f"Game WON! The word was '{secret}'.")
    else:
        print(f"Game LOST! The word was '{secret}'.")
