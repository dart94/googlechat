document.addEventListener('DOMContentLoaded', function() {
    const userInput = document.getElementById('user_input');
    const sendButton = document.getElementById('send-button');
    const toggleButton = document.getElementById('toggleChatbot');
    const chatbot = document.getElementById('chatbot');

    // Función para enviar el mensaje
    function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            displayMessage('user', message);
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({message: message}),
            })
            .then(response => response.json())
            .then(data => {
                displayMessage('bot', data.response);
            })
            .catch((error) => {
                console.error('Error:', error);
                displayMessage('bot', 'Lo siento, ha ocurrido un error.');
            });
            userInput.value = '';
        }
    }

    // Función para mostrar los mensajes en el chat
    function displayMessage(sender, message) {
        const messagesContainer = document.getElementById('messages');
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        const contentElement = document.createElement('div');
        contentElement.classList.add('message-content');
        contentElement.textContent = message;
        messageElement.appendChild(contentElement);
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Evento para enviar el mensaje al hacer clic en el botón
    sendButton.addEventListener('click', sendMessage);

    // Evento para enviar el mensaje al presionar la tecla Enter
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Evento para mostrar/ocultar el chatbot al hacer clic en el botón de toggle
    toggleButton.addEventListener('click', function() {
        if (chatbot.style.display === 'none' || chatbot.style.display === '') {
            chatbot.style.display = 'block';
        } else {
            chatbot.style.display = 'none';
        }
    });
});
