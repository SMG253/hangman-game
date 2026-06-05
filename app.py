
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import random

from hangman import HangmanSolver

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}})

# Global Game Objects
solver = None
secret_word = None
current_difficulty = None

ai_uses = 0
hint_uses = 0


# Home Route
@app.route("/")
def home():

    return render_template("index.html")


# Start Game Route
@app.route("/start", methods=["POST"])
def start():

    global solver
    global secret_word
    global current_difficulty
    global ai_uses
    global hint_uses

    data = request.get_json()

    difficulty = data.get("difficulty", "easy")

    allowed_difficulties = [
        "easy",
        "medium",
        "hard",
        "impossible"
    ]

    if difficulty not in allowed_difficulties:

        return jsonify({
            "error": "Invalid difficulty"
        }), 400

    current_difficulty = difficulty

    # Reset Uses
    ai_uses = 0
    hint_uses = 0

    filename = f"words/{difficulty}.txt"

    with open(filename, "r", encoding="utf-8") as file:

        words = [
            line.strip().lower()
            for line in file
            if line.strip()
        ]

    solver = HangmanSolver(
        words,
        max_tries=6
    )

    secret_word = random.choice(words)

    solver.start_game(secret_word)

    return jsonify({

        "message": "Game started",

        "difficulty": difficulty,

        "length": len(secret_word),

        "current_pattern":
            solver.current_pattern,

        "tries_left":
            solver.tries_left
    })


# Guess Route
@app.route("/guess", methods=["POST"])
def guess():

    global solver

    if not solver:

        return jsonify({
            "error": "Game not started"
        }), 400

    data = request.get_json()

    letter = data.get(
        "letter",
        ""
    ).lower()

    if not letter.isalpha() or len(letter) != 1:

        return jsonify({
            "error": "Invalid letter"
        }), 400

    if letter in solver.guessed:

        return jsonify({
            "error": "Letter already guessed"
        }), 400

    solver.guessed.add(letter)

    if letter in solver.secret_word:

        solver.correct.add(letter)

        solver.update_pattern(letter)

        correct = True

    else:

        solver.tries_left -= 1

        correct = False

    game_over = (

        solver.tries_left == 0
        or
        '_' not in solver.current_pattern
    )

    response = {

        "correct": correct,

        "current_pattern":
            solver.current_pattern,

        "tries_left":
            solver.tries_left,

        "game_over":
            game_over
    }

    if game_over:

        response["secret_word"] = (
            solver.secret_word
        )

    return jsonify(response)


# AI Guess Route
@app.route("/ai_guess", methods=["POST"])
def ai_guess():

    global solver
    global current_difficulty
    global ai_uses

    if not solver:

        return jsonify({
            "error": "Game not started"
        }), 400

    if current_difficulty != "impossible":

        return jsonify({
            "error":
                "AI Guess only available in Impossible mode"
        }), 400

    word_length = len(solver.secret_word)

    max_ai_uses = 2

    if word_length >= 8:
        max_ai_uses = 3

    if ai_uses >= max_ai_uses:

        return jsonify({
            "error":
                f"Maximum {max_ai_uses} AI guesses allowed"
        }), 400

    guess = solver.next_guess()

    if guess is None:

        return jsonify({
            "error": "No valid guess found"
        }), 400

    solver.guessed.add(guess)

    if guess in solver.secret_word:

        solver.correct.add(guess)

        solver.update_pattern(guess)

        correct = True

    else:

        solver.tries_left -= 1

        correct = False

    ai_uses += 1

    game_over = (

        solver.tries_left == 0
        or
        '_' not in solver.current_pattern
    )

    response = {

        "ai_guess": guess,

        "correct": correct,

        "current_pattern":
            solver.current_pattern,

        "tries_left":
            solver.tries_left,

        "game_over":
            game_over,

        "ai_uses_left":
            max_ai_uses - ai_uses
    }

    if game_over:

        response["secret_word"] = (
            solver.secret_word
        )

    return jsonify(response)


# Hint Route
@app.route("/hint", methods=["GET"])
def hint():

    global solver
    global current_difficulty
    global hint_uses

    if not solver:

        return jsonify({
            "error": "Game not started"
        }), 400

    # Disable hints in impossible mode
    if current_difficulty == "impossible":

        return jsonify({
            "error":
                "Hints are disabled in Impossible mode"
        }), 400

    # Maximum 2 hints
    if hint_uses >= 2:

        return jsonify({
            "error":
                "Maximum 2 hints allowed"
        }), 400

    hidden_indexes = []

    for i, ch in enumerate(solver.current_pattern):

        if ch == '_':
            hidden_indexes.append(i)

    if not hidden_indexes:

        return jsonify({

            "hint_letters": [],

            "current_pattern":
                solver.current_pattern,

            "hints_left":
                0
        })

    # Reveal ONLY ONE LETTER
    random_index = random.choice(hidden_indexes)

    letter = solver.secret_word[random_index]

    solver.current_pattern[random_index] = letter

    solver.correct.add(letter)

    hint_uses += 1

    return jsonify({

        "hint_letters":
            [letter],

        "current_pattern":
            solver.current_pattern,

        "hints_left":
            2 - hint_uses
    })


# Run Flask App
if __name__ == "__main__":

    app.run(

        debug=True,

        host="0.0.0.0",

        port=8000
    )

