// Wait for the DOM content to be fully loaded before running the script
document.addEventListener('DOMContentLoaded', () => {

    // --- DOM ELEMENT SELECTION ---
    // Select the chat form, user input field, and the main chat messages container
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessagesContainer = document.getElementById('chat-messages');
    const suggestionsContainer = document.getElementById('seriousness-suggestions-container');
    const seriousnessOutput = document.getElementById('seriousness-output');
    const suggestionsOutput = document.getElementById('suggestions-output');

    // --- HELPER FUNCTION: APPEND MESSAGE TO CHAT UI ---
    /**
     * Appends a new message bubble to the chat interface.
     * @param {string} sender - The sender of the message ('user' or 'ai').
     * @param {string} text - The content of the message.
     */
    const appendMessage = (sender, text) => {
        // Create a new div element for the message bubble
        const messageElement = document.createElement('div');
        let avatar, bubbleClass, contentClass, avatarContent;

        // Determine the styling and content based on the sender
        if (sender === 'user') {
            avatarContent = 'You';
            avatar = document.createElement('div');
            avatar.className = 'flex-shrink-0 w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center text-sm font-bold text-white';
            avatar.textContent = avatarContent;

            bubbleClass = 'ml-auto';
            contentClass = 'bg-[#4a4a6e] text-white';
        } else { // 'ai'
            avatarContent = 'AI';
            avatar = document.createElement('div');
            avatar.className = 'flex-shrink-0 w-8 h-8 rounded-full bg-purple-500 flex items-center justify-center text-sm font-bold text-white';
            avatar.textContent = avatarContent;
            
            bubbleClass = ''; // Default alignment for AI messages
            contentClass = 'bg-[#1e1e3e] text-gray-200';
        }

        // Apply classes to the message element
        messageElement.className = `flex items-start mb-4 space-x-3 w-full max-w-[80%] md:max-w-[60%] ${bubbleClass}`;

        // Create the bubble content container
        const contentContainer = document.createElement('div');
        contentContainer.className = `p-4 rounded-xl shadow-lg break-words ${contentClass}`;

        // Create the paragraph for the message text and set its content
        const messageText = document.createElement('p');
        messageText.textContent = text;
        contentContainer.appendChild(messageText);
        
        // Append avatar and content to the message element
        if (sender === 'user') {
            messageElement.appendChild(contentContainer);
            messageElement.appendChild(avatar);
        } else {
            messageElement.appendChild(avatar);
            messageElement.appendChild(contentContainer);
        }

        // Add the message to the main chat container
        chatMessagesContainer.appendChild(messageElement);

        // Scroll to the bottom of the chat container
        chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    };
    
    // --- API CALL FOR CHAT ---
    const sendMessage = async () => {
        const message = userInput.value.trim();
        if (message === '') return;

        // Clear input field and add user message to UI
        userInput.value = '';
        appendMessage('user', message);

        try {
            // Send the user's message to the backend API
            const response = await fetch('/chat', { // Corrected endpoint from /api/chat to /chat
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message })
            });

            // Parse the JSON response from the backend
            const data = await response.json();
            
            // Handle AI's response text if it exists
            if (data.ai_response) {
                appendMessage('ai', data.ai_response);
            }

            // Handle seriousness level and suggestions if they exist
            if (data.seriousness_level && data.suggestions) {
                // Show the container
                suggestionsContainer.classList.remove('hidden');

                // Set seriousness level text and apply color class
                seriousnessOutput.textContent = `Seriousness Level: ${data.seriousness_level}`;
                
                // Clear any previous color classes and apply the new one
                suggestionsOutput.className = 'text-sm text-gray-200 markdown-content';
                let colorClass;
                const level = data.seriousness_level.toLowerCase();
                if (level.includes('low')) {
                    colorClass = 'seriousness-low';
                } else if (level.includes('medium')) {
                    colorClass = 'seriousness-medium';
                } else if (level.includes('high') || level.includes('critical')) {
                    colorClass = 'seriousness-high';
                }
                suggestionsOutput.classList.add(colorClass);

                // Use marked.js to convert markdown to HTML and set the content
                suggestionsOutput.innerHTML = marked.parse(data.suggestions);
            } else {
                // If no suggestions, hide the container
                suggestionsContainer.classList.add('hidden');
            }

        } catch (error) {
            console.error('Error fetching chat response:', error);
            appendMessage('ai', "I'm sorry, I am unable to connect right now. Please try again later.");
        }
    };

    // --- EVENT LISTENERS ---
    // Handle form submission and enter key press
    if (chatForm) {
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault(); // Prevent default form submission
            sendMessage();
        });
    }
});
