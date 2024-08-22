document.addEventListener('DOMContentLoaded', function() {
    const userInput = document.getElementById('user_input');
    const sendButton = document.getElementById('send-button');
    const toggleButton = document.getElementById('toggleChatbot');
    const chatbot = document.getElementById('chatbot');
    const chatLink = document.getElementById('chatLink');

    // Función para el desplazamiento suave
    function scrollToSection(sectionId) {
        const section = document.getElementById(sectionId);
        if (section) {
            const headerHeight = document.querySelector('.main-header').offsetHeight;
            const sectionTop = section.getBoundingClientRect().top + window.pageYOffset - headerHeight;
            window.scrollTo({
                top: sectionTop,
                behavior: 'smooth'
            });
        }
    }

    // Manejador de eventos para los enlaces de navegación
    document.querySelectorAll('.nav-links a, .logo-img').forEach(link => {
        link.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            console.log('Clicked link href:', href); // Agregar esto para debuggear
            if (href === '/' || href.includes('index')) {
                return;
            }
            if (href.startsWith('#')) {
                e.preventDefault();
                const sectionId = href.substring(1);
                scrollToSection(sectionId);
                if (sectionId === 'chat') {
                    chatbot.style.display = 'block';
                }
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
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }

    // Evento para enviar el mensaje al presionar la tecla Enter
    if (userInput) {
        userInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }

    // Evento para mostrar/ocultar el chatbot
    if (toggleButton) {
        toggleButton.addEventListener('click', function() {
            chatbot.style.display = chatbot.style.display === 'none' || chatbot.style.display === '' ? 'block' : 'none';
            if (chatbot.style.display === 'block') {
                scrollToSection('chat');
            }
        });
    }

    // Evento para el enlace del chat en el header
    if (chatLink) {
        chatLink.addEventListener('click', function(e) {
            if (this.getAttribute('href') === '#chago') {
                e.preventDefault();
                chatbot.style.display = 'block';
                scrollToSection('chat');
            }
            // Si el href no es #chat, permitirá la navegación normal
        });
    }
});