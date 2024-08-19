document.addEventListener('DOMContentLoaded', function() {
    const userInput = document.getElementById('user_input');
    const sendButton = document.getElementById('send-button');
    const toggleButton = document.getElementById('toggleChatbot');
    const chatbot = document.getElementById('chatbot');
    const chatLink = document.getElementById('chatLink');

    // Función para el desplazamiento suave
    function scrollToSection(sectionId) {
        const section = document.getElementById(sectionId);
        const headerHeight = document.querySelector('.main-header').offsetHeight;
        const sectionTop = section.getBoundingClientRect().top + window.pageYOffset - headerHeight;
        window.scrollTo({
            top: sectionTop,
            behavior: 'smooth'
        });
    }

    // Manejador de eventos para los enlaces de navegación
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const sectionId = this.getAttribute('href').substring(1);
            scrollToSection(sectionId);
            if (sectionId === 'chat') {
                chatbot.style.display = 'block';
            }
        });
    });

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

    // Evento para mostrar/ocultar el chatbot
    toggleButton.addEventListener('click', function() {
        chatbot.style.display = chatbot.style.display === 'none' || chatbot.style.display === '' ? 'block' : 'none';
        if (chatbot.style.display === 'block') {
            scrollToSection('chat');
        }
    });

    // Evento para el enlace del chat en el header
    chatLink.addEventListener('click', function(e) {
        e.preventDefault();
        chatbot.style.display = 'block';
        scrollToSection('chat');
    });
});