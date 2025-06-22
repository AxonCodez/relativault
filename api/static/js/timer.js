document.addEventListener('DOMContentLoaded', function() {
    const timerElement = document.getElementById('timer');
    let startTime = Date.now();

    setInterval(() => {
        const elapsed = Math.floor((Date.now() - startTime) / 1000);
        timerElement.textContent = elapsed;
    }, 1000);
});
