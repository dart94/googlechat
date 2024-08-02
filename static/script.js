function sendMessage() {
    var userInput = document.getElementById('user-message');
    var message = userInput.value;
    if (message.trim() === '') return;

    addMessageToChat('user', message);
    userInput.value = '';

    // Enviar mensaje al servidor
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({message: message}),
    })
    .then(response => response.json())
    .then(data => {
        addMessageToChat('bot', data.response);
    })
    .catch(error => {
        console.error('Error:', error);
        addMessageToChat('bot', 'Lo siento, ha ocurrido un error. Por favor, intenta de nuevo.');
    });
}

function addMessageToChat(sender, message) {
    var chatMessages = document.getElementById('chat-messages');
    var messageElement = document.createElement('div');
    messageElement.classList.add('message');
    messageElement.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
    messageElement.textContent = message;
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

document.getElementById('user-message').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});