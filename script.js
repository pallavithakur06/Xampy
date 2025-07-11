let questions = [];
let selectedAnswers = [];

async function startTimer() {
    const timerOverlay = document.getElementById('timer-overlay');
    try {
        const res = await fetch('timer.json');
        const data = await res.json();
        let totalSeconds = data.minutes * 60;

        function formatTime(s) {
            const m = Math.floor(s / 60).toString().padStart(2, '0');
            const sec = (s % 60).toString().padStart(2, '0');
            return `${m}:${sec}`;
        }

        timerOverlay.style.display = 'flex';
        timerOverlay.classList.remove('blinking');
        timerOverlay.style.backgroundColor = 'transparent';

        const intervalId = setInterval(() => {
            if (totalSeconds <= 0) {
                clearInterval(intervalId);
                timerOverlay.textContent = "Time's Up!";
                timerOverlay.style.color = 'red';
                timerOverlay.classList.add('blinking');
                submitQuiz();
            } else {
                timerOverlay.textContent = formatTime(totalSeconds);
                totalSeconds--;
            }
        }, 1000);

    } catch (e) {
        console.error("Failed to fetch timer", e);
        timerOverlay.style.display = 'none';
    }
}

function submitQuiz() {
    document.getElementById('submit-btn').click();
}

window.onload = async () => {
    await startTimer();

    const res = await fetch('questions.json');
    questions = await res.json();
    renderQuestions();
};

function renderQuestions() {
    const container = document.getElementById('quiz-container');
    container.innerHTML = '';

    questions.forEach((q, index) => {
        const qDiv = document.createElement('div');
        qDiv.classList.add('question');

        let imgHTML = '';
        if (q.question_image) {
            imgHTML = `<img src="${q.question_image}" alt="Question Image" class="question-image" style="max-width:100%; margin-top:10px;">`;
        }

        qDiv.innerHTML = `<p><strong>Q${index + 1}:</strong> ${q.question}</p>${imgHTML}`;

        q.options.forEach((opt) => {
            const optDiv = document.createElement('div');
            optDiv.classList.add('option');
            optDiv.textContent = opt;
            optDiv.onclick = () => {
                selectedAnswers[index] = opt;
                Array.from(qDiv.getElementsByClassName('option')).forEach(o => o.classList.remove('selected'));
                optDiv.classList.add('selected');
            };
            qDiv.appendChild(optDiv);
        });

        const expDiv = document.createElement('div');
        expDiv.classList.add('explanation');
        expDiv.style.display = 'none';
        qDiv.appendChild(expDiv);

        container.appendChild(qDiv);
    });
}

document.getElementById('submit-btn').onclick = async () => {
    let correct = 0;
    const quizDivs = document.getElementsByClassName('question');

    questions.forEach((q, index) => {
        const options = quizDivs[index].getElementsByClassName('option');
        const explanationDiv = quizDivs[index].getElementsByClassName('explanation')[0];

        for (let opt of options) {
            opt.classList.remove('correct', 'wrong', 'selected');
            if (opt.textContent === q.answer) {
                opt.classList.add('correct');
                if (selectedAnswers[index] === q.answer) {
                    correct++;
                }
            } else if (opt.textContent === selectedAnswers[index]) {
                opt.classList.add('wrong');
            }
        }

        explanationDiv.style.display = 'block';
        let explanationHTML = `<strong>Explanation:</strong> ${q.explanation || 'No explanation provided.'}`;
        if (q.explanation_image) {
            explanationHTML += `<br><img src="${q.explanation_image}" alt="Explanation Image" style="max-width:100%; margin-top:10px;">`;
        }
        explanationDiv.innerHTML = explanationHTML;
    });

    const result = document.getElementById('result-container');
    const percent = Math.round((correct / questions.length) * 100);
    let rating = '';

    if (percent === 100) rating = "Perfect! You're a genius!";
    else if (percent >= 95) rating = "Outstanding!";
    else if (percent >= 90) rating = "Excellent work!";
    else if (percent >= 85) rating = "Very impressive!";
    else if (percent >= 80) rating = "Great job!";
    else if (percent >= 75) rating = "Well done!";
    else if (percent >= 70) rating = "Good effort!";
    else if (percent >= 65) rating = "You're getting there!";
    else if (percent >= 60) rating = "Fair try!";
    else if (percent >= 55) rating = "Needs improvement!";
    else if (percent >= 50) rating = "Just made it!";
    else if (percent >= 45) rating = "Almost there!";
    else if (percent >= 40) rating = "Don't give up!";
    else if (percent >= 35) rating = "Keep trying!";
    else if (percent >= 30) rating = "Review the material!";
    else if (percent >= 25) rating = "More practice needed!";
    else if (percent >= 20) rating = "Learning takes time!";
    else if (percent >= 15) rating = "You can do better!";
    else if (percent >= 10) rating = "Keep going!";
    else if (percent >= 5) rating = "Just started!";
    else rating = "Start from scratch. You got this!";

    result.innerHTML = `Score: ${correct}/${questions.length} (${percent}%)<br/>Rating: ${rating}`;

    const studentName = document.getElementById('student-name').value.trim();
    if (!studentName) {
        alert("Please enter your name before submitting.");
        return;
    }

    try {
        await fetch('/submit_result', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: studentName,
                score: correct,
                total: questions.length,
                percent: percent,
                rating: rating
            }),
        });
    } catch (err) {
        console.error('Failed to send result to server:', err);
    }
};

document.getElementById('download-btn').onclick = () => {
    const element = document.getElementById('main-container');
    document.getElementById('submit-btn').style.display = 'none';
    document.getElementById('download-btn').style.display = 'none';

    html2pdf()
        .from(element)
        .save('Quiz-Result.pdf')
        .then(() => {
            document.getElementById('submit-btn').style.display = 'inline-block';
            document.getElementById('download-btn').style.display = 'inline-block';
        });
};