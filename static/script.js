function showLoading() {
    document.getElementById('overlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('overlay').style.display = 'none';
}

// Simulate loading
setTimeout(hideLoading, 5000); // Esconde o loading depois de 5 segundos (simulation)