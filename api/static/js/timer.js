// Initialize timer when the page loads
document.addEventListener('DOMContentLoaded', function() {
    const timerElement = document.getElementById('timer');
    const timerBar = document.querySelector('.timer-bar');
    const timeLimit = parseInt(timerElement.textContent, 10);
    let timeLeft = timeLimit;

    // Update the timer every second
    window.timer = setInterval(() => {
        timeLeft--;
        timerElement.textContent = timeLeft;

        // Update the timer bar width (optional, but matches your CSS)
        // If you want the bar to update dynamically (not just via CSS animation)
        // timerBar.style.width = (timeLeft / timeLimit * 100) + '%';

        if (timeLeft <= 0) {
            clearInterval(window.timer);
            // Time's up! You can optionally auto-submit here if you want.
            // For now, just alert and let the user proceed
            alert("Time's up!");
        }
    }, 1000);

    // If you want the timer to stop when an answer is clicked,
    // you already clearInterval(window.timer) in your submitAnswer function
});
