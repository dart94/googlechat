document.addEventListener('DOMContentLoaded', function() {
    const userInput = document.getElementById('user_input');
    const sendButton = document.getElementById('send-button');
    const toggleButton = document.getElementById('toggleChatbot');
    const chatbot = document.getElementById('chatbot');
    const chatLink = document.getElementById('chatLink');
    const loadingIndicator = document.getElementById('loading-indicator');

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
            console.log('Clicked link href:', href);
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

    // Función para mostrar el indicador de carga
    function showLoadingIndicator() {
        loadingIndicator.style.display = 'flex';
        const messagesContainer = document.getElementById('messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    // Función para ocultar el indicador de carga
    function hideLoadingIndicator() {
        loadingIndicator.style.display = 'none';
    }

    // Función para enviar el mensaje
    function sendMessage() {
        const message = userInput.value.trim();
        if (message) {
            displayMessage('user', message);
            showLoadingIndicator();
            fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({message: message}),
            })
            .then(response => response.json())
            .then(data => {
                hideLoadingIndicator();
                displayMessage('bot', data.response, true);
            })
            .catch((error) => {
                console.error('Error:', error);
                hideLoadingIndicator();
                displayMessage('bot', '<p>Lo siento, ha ocurrido un error.</p>', true);
            });
            userInput.value = '';
        }
    }

    // Función actualizada para mostrar los mensajes en el chat
    function displayMessage(sender, message, isHtml = false) {
        const messagesContainer = document.getElementById('messages');
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', `${sender}-message`);
        const contentElement = document.createElement('div');
        contentElement.classList.add('message-content');
        if (isHtml) {
            contentElement.innerHTML = message;
        } else {
            contentElement.textContent = message;
        }
        messageElement.appendChild(contentElement);
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        // Aplicar animación de entrada
        messageElement.style.opacity = '0';
        messageElement.style.transform = 'translateY(20px)';
        setTimeout(() => {
            messageElement.style.transition = 'opacity 0.3s ease-out, transform 0.3s ease-out';
            messageElement.style.opacity = '1';
            messageElement.style.transform = 'translateY(0)';
        }, 10);
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

    // Evento para el enlace del chat en el header
    if (chatLink) {
        chatLink.addEventListener('click', function(e) {
            if (this.getAttribute('href') === '#chat') {
                e.preventDefault();
                chatbot.style.display = 'block';
                scrollToSection('chat');
            }
        });
    }

    // Evento de click para el botón toggleChatbot
    if (toggleButton) {
        toggleButton.addEventListener('click', function() {
            window.location.href = '/chatgo';
        });
    }
});