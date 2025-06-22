document.addEventListener('DOMContentLoaded', function() {
    const timerElement = document.getElementById('timer');
    const timerBar = document.querySelector('.timer-bar');
    const timeLimit = parseInt(timerElement.textContent, 10);
    let timeLeft = timeLimit;

    window.timer = setInterval(() => {
        timeLeft--;
        timerElement.textContent = timeLeft;
        if (timeLeft <= 0) {
            clearInterval(window.timer);
            alert("Time's up!");
        }
    }, 1000);
});
