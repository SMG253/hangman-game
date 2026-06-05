let currentPattern = [];
let triesLeft = 6;
let guessedLetters = [];
let gameOver = false;

let score = 0;
let streak = 0;
let wins = 0;
let losses = 0;

// Sound Effects
const wrongSound =
    new Audio("/static/sounds/wrong.mp3");

const winSound =
    new Audio("/static/sounds/win.mp3");

const parts = [
    "head",
    "body",
    "left-arm",
    "right-arm",
    "left-leg",
    "right-leg"
];

function createKeyboard() {

    const keyboard =
        document.getElementById("keyboard");

    keyboard.innerHTML = "";

    const letters =
        "abcdefghijklmnopqrstuvwxyz";

    letters.split('').forEach(letter => {

        const button =
            document.createElement("button");

        button.innerText =
            letter.toUpperCase();

        button.classList.add("key");

        button.onclick = function () {

            makeGuess(letter);

        };

        keyboard.appendChild(button);
    });
}

function updateHangman(triesLeft) {

    const wrongGuesses =
        6 - triesLeft;

    if (
        wrongGuesses > 0 &&
        wrongGuesses <= parts.length
    ) {

        document.getElementById(
            parts[wrongGuesses - 1]
        ).style.display = "block";
    }
}

function shakeScreen() {

    const container =
        document.querySelector(".container");

    container.classList.add("shake");

    setTimeout(() => {

        container.classList.remove("shake");

    }, 400);
}

async function startGame() {

    const difficulty =
        document.getElementById("difficulty").value;

    const aiButton =
        document.getElementById("ai-btn");

    const hintButton =
        document.getElementById("hint-btn");

    // Reset Hint Button
    hintButton.disabled = false;

    hintButton.style.opacity = "1";

    hintButton.style.cursor = "pointer";

    // Impossible Mode
    if (difficulty === "impossible") {

        aiButton.style.display =
            "inline-block";

        hintButton.style.display =
            "none";

    } else {

        aiButton.style.display =
            "none";

        hintButton.style.display =
            "inline-block";
    }

    const res = await fetch("/start", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            difficulty: difficulty
        })
    });

    const data = await res.json();

    currentPattern =
        data.current_pattern;

    triesLeft =
        data.tries_left;

    guessedLetters = [];

    gameOver = false;

    parts.forEach(part => {

        document.getElementById(part)
            .style.display = "none";
    });

    document.getElementById("word").innerText =
        currentPattern.join(" ");

    document.getElementById("tries").innerText =
        `Tries Left: ${triesLeft}`;

    document.getElementById("guessed").innerText =
        "Guessed Letters:";

    document.getElementById("message").innerText =
        "";

    const container =
        document.querySelector(".container");

    container.classList.remove("win-glow");

    container.classList.remove("lose-glow");

    createKeyboard();

    updateStats();
}

async function makeGuess(letter) {

    if (gameOver) return;

    if (guessedLetters.includes(letter)) {

        showMessage(
            "Letter already guessed",
            "wrong"
        );

        return;
    }

    guessedLetters.push(letter);

    const keys =
        document.querySelectorAll(".key");

    keys.forEach(key => {

        if (
            key.innerText.toLowerCase()
            === letter
        ) {

            key.disabled = true;
        }
    });

    const res = await fetch("/guess", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            letter: letter
        })
    });

    const data = await res.json();

    updateUI(data, letter);
}

async function aiGuess() {

    if (gameOver) return;

    const res = await fetch("/ai_guess", {

        method: "POST"
    });

    const data = await res.json();

    if (data.error) {

        showMessage(
            data.error,
            "wrong"
        );

        return;
    }

    guessedLetters.push(data.ai_guess);

    const keys =
        document.querySelectorAll(".key");

    keys.forEach(key => {

        if (
            key.innerText.toLowerCase()
            === data.ai_guess
        ) {

            key.disabled = true;
        }
    });

    updateUI(
        data,
        data.ai_guess
    );

    showMessage(
        `AI guesses left: ${data.ai_uses_left}`,
        "correct"
    );
}

async function getHint() {

    if (gameOver) return;

    const hintButton =
        document.getElementById("hint-btn");

    const res =
        await fetch("/hint");

    const data =
        await res.json();

    if (data.error) {

        showMessage(
            data.error,
            "wrong"
        );

        return;
    }

    currentPattern =
        data.current_pattern;

    document.getElementById("word").innerText =
        currentPattern.join(" ");

    showMessage(
        `Hint revealed: ${data.hint_letters.join(", ")} | Hints left: ${data.hints_left}`,
        "correct"
    );

    // Disable Hint Button
    if (data.hints_left <= 0) {

        hintButton.disabled = true;

        hintButton.style.opacity =
            "0.6";

        hintButton.style.cursor =
            "not-allowed";
    }
}

function updateUI(data, guessedLetter) {

    currentPattern =
        data.current_pattern;

    triesLeft =
        data.tries_left;

    updateHangman(triesLeft);

    document.getElementById("word").innerText =
        currentPattern.join(" ");

    document.getElementById("tries").innerText =
        `Tries Left: ${triesLeft}`;

    document.getElementById("guessed").innerText =
        `Guessed Letters: ${guessedLetters.join(", ")}`;

    const keys =
        document.querySelectorAll(".key");

    keys.forEach(key => {

        if (
            key.innerText.toLowerCase()
            === guessedLetter
        ) {

            if (data.correct) {

                key.classList.add(
                    "correct"
                );

            } else {

                key.classList.add(
                    "wrong"
                );
            }
        }
    });

    if (data.game_over) {

        gameOver = true;

        const container =
            document.querySelector(".container");

        if (currentPattern.includes("_")) {

            losses++;

            streak = 0;

            container.classList.add(
                "lose-glow"
            );

            wrongSound.currentTime = 0;

            wrongSound.play();

            showMessage(
                `💀 Game Over! Word was "${data.secret_word}"`,
                "lose"
            );

        } else {

            wins++;

            streak++;

            score += 10;

            container.classList.add(
                "win-glow"
            );

            winSound.currentTime = 0;

            winSound.play();

            showMessage(
                "🎉 You Won!",
                "win"
            );
        }

        updateStats();

    } else {

        if (data.correct) {

            score += 1;

            updateStats();

            showMessage(
                "Correct Guess",
                "correct"
            );

        } else {

            shakeScreen();

            wrongSound.currentTime = 0;

            wrongSound.play();

            showMessage(
                "Wrong Guess",
                "wrong"
            );
        }
    }
}

function updateStats() {

    document.getElementById("score")
        .innerText = score;

    document.getElementById("streak")
        .innerText = streak;

    document.getElementById("wins")
        .innerText = wins;

    document.getElementById("losses")
        .innerText = losses;
}

function showMessage(text, className) {

    const message =
        document.getElementById("message");

    message.className =
        className;

    message.innerText =
        text;
}

window.onload = startGame;

document
    .getElementById("difficulty")
    .addEventListener(
        "change",
        startGame
    );
