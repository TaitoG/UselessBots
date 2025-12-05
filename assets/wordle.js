function normalizeString(str) {
    return str
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .replace(/ł/g, 'l') 
        .replace(/Ł/g, 'L')
        .replace(/ß/g, 'ss')
        .replace(/æ/g, 'ae')
        .replace(/ø/g, 'o');
}

const SECRET_WORD = normalizeString(window.secretWord).toUpperCase();
let attempts = 6;
const tg = window.Telegram.WebApp;
tg.ready();
if (tg.isExpanded) {
    tg.expand(); 
} else {
    document.documentElement.style.height = "100vh";
}

function checkGuess() {
    if (attempts <= 0) return;

    const userInput = document.getElementById('guessInput').value.toUpperCase().replace(/[^A-Z]/g, '');
    const attemptsDiv = document.getElementById('attempts');
    console.log(userInput, userInput.length);
    console.log(window.secretWord, window.wordLength)
    const messageDiv = document.getElementById('message');

    if (userInput.length !== window.wordLength) {
        shakeInput();
        messageDiv.textContent = "Word must contain " + window.wordLength + " letters!";
        return;
    }

    attempts--;
    document.getElementById('attempts-left').textContent = attempts;
    const result = analyzeWord(userInput);
    displayResult(userInput, result);

    if (userInput === SECRET_WORD) {
        const remainingAttempts = 6 - attempts;
        messageDiv.textContent = `🎉 Congrats! You guessed it from ${remainingAttempts} ${getAttemptsText(remainingAttempts)}!`;
    } else if (attempts === 0) {
        messageDiv.textContent = "❌ No attempts left! Secret word was: " + SECRET_WORD;
    }
}

function getAttemptsText(num) {
    if (num === 1) return "attempt";
    else return "attempts";
}

function shakeInput() {
    const input = document.getElementById('guessInput');
    input.classList.add('shake');
    setTimeout(() => input.classList.remove('shake'), 500);
}

function analyzeWord(guess) {
    const secretLetters = SECRET_WORD.split('');
    const result = Array(window.wordLength).fill('gray');
    const used = Array(window.wordLength).fill(false);

    for (let i = 0; i < window.wordLength; i++) {
        if (guess[i] === secretLetters[i]) {
            result[i] = 'green';
            used[i] = true;
        }
    }

    for (let i = 0; i < window.wordLength; i++) {
        if (result[i] !== 'green') {
            for (let j = 0; j < window.wordLength; j++) {
                if (!used[j] && guess[i] === secretLetters[j]) {
                    result[i] = 'yellow';
                    used[j] = true;
                    break;
                }
            }
        }
    }

    return result.map(color => color === 'gray' ? 'red' : color);
}

function displayResult(guess, colors) {
    const attemptsDiv = document.getElementById('attempts');
    const row = document.createElement('div');
    row.className = 'letter-row fade-in';

    guess.split('').forEach((letter, i) => {
        const letterDiv = document.createElement('div');
        letterDiv.className = 'letter ' + colors[i];
        letterDiv.textContent = letter;
        row.appendChild(letterDiv);
    });

    attemptsDiv.appendChild(row);
}