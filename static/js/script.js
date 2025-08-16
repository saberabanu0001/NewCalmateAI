// static/js/script.js

document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const seriousnessLevelSpan = document.getElementById('seriousness-level');
    const suggestionsOutput = document.getElementById('suggestions-output');

    // Chat history stored in the client-side for this simple example
    let chatHistory = [];
    
    // --- Chat Logic ---
    if (sendButton) {
        sendButton.addEventListener('click', sendMessage);
    }
    if (userInput) {
        userInput.addEventListener('keypress', function(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        });
    }

    async function sendMessage() {
        const message = userInput.value.trim();
        if (message === '') return;

        userInput.value = ''; // Clear input

        // Add user message to UI immediately
        addMessageToChat(message, 'user');

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: message, history: chatHistory })
            });
            const data = await response.json();

            // Update chat history with AI's response for next turn
            chatHistory.push({ role: 'user', content: message });
            chatHistory.push({ role: 'assistant', content: data.response });

            addMessageToChat(data.response, 'ai');
            seriousnessLevelSpan.textContent = data.seriousness;
            suggestionsOutput.innerHTML = marked.parse(data.suggestions); // Use marked.js for Markdown

        } catch (error) {
            console.error('Error sending message:', error);
            addMessageToChat('Error: Could not connect to the AI.', 'ai');
        }
    }

    function addMessageToChat(text, role) {
        const messageElement = document.createElement('div');
        messageElement.classList.add(role === 'user' ? 'user-message' : 'ai-message');
        messageElement.innerHTML = marked.parse(text); // Use marked.js to render Markdown
        chatMessages.appendChild(messageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight; // Auto-scroll to bottom
    }

    // --- Accordion Logic ---
    document.querySelectorAll('.accordion-header').forEach(header => {
        header.addEventListener('click', function() {
            const content = this.nextElementSibling;
            if (content.style.maxHeight) {
                content.style.maxHeight = null;
            } else {
                content.style.maxHeight = content.scrollHeight + "px";
            }
        });
    });

    // --- Emergency Contacts Logic ---
    const countryDropdown = document.getElementById('country-dropdown');
    const cityDropdown = document.getElementById('city-dropdown');
    const showHelplinesButton = document.getElementById('show-helplines');
    const showDoctorsButton = document.getElementById('show-doctors');
    const emergencyOutput = document.getElementById('emergency-output');

    // Populate countries on load
    async function loadCountries() {
        try {
            const response = await fetch('/api/countries');
            const countries = await response.json();
            countryDropdown.innerHTML = '<option value="">Select a Country</option>';
            countries.forEach(country => {
                const option = document.createElement('option');
                option.value = country;
                option.textContent = country;
                countryDropdown.appendChild(option);
            });
        } catch (error) {
            console.error('Error loading countries:', error);
            countryDropdown.innerHTML = '<option value="">Error loading countries</option>';
        }
    }

    // Populate cities when country changes
    if (countryDropdown) {
        countryDropdown.addEventListener('change', async function() {
            const selectedCountry = this.value;
            if (selectedCountry) {
                try {
                    const response = await fetch(`/api/cities/${encodeURIComponent(selectedCountry)}`);
                    const cities = await response.json();
                    cityDropdown.innerHTML = '<option value="">Select a City</option>';
                    cities.forEach(city => {
                        const option = document.createElement('option');
                        option.value = city;
                        option.textContent = city;
                        cityDropdown.appendChild(option);
                    });
                    cityDropdown.disabled = false;
                } catch (error) {
                    console.error('Error loading cities:', error);
                    cityDropdown.innerHTML = '<option value="">Error loading cities</option>';
                    cityDropdown.disabled = true;
                }
            } else {
                cityDropdown.innerHTML = '<option value="">Select a country first</option>';
                cityDropdown.disabled = true;
            }
            emergencyOutput.innerHTML = ''; // Clear previous output
        });
    }

    if (showHelplinesButton) {
        showHelplinesButton.addEventListener('click', function() {
            getEmergencyContacts('helplines');
        });
    }

    if (showDoctorsButton) {
        showDoctorsButton.addEventListener('click', function() {
            getEmergencyContacts('doctors');
        });
    }

    async function getEmergencyContacts(category) {
        const selectedCountry = countryDropdown.value;
        const selectedCity = cityDropdown.value;

        if (!selectedCountry || !selectedCity) {
            emergencyOutput.innerHTML = 'Please select both a country and a city.';
            return;
        }

        try {
            const response = await fetch('/api/contacts', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ country: selectedCountry, city: selectedCity, category: category })
            });
            const data = await response.json();
            if (data.error) {
                emergencyOutput.innerHTML = `Error: ${data.error}`;
            } else {
                emergencyOutput.innerHTML = marked.parse(data.contacts_markdown);
            }
        } catch (error) {
            console.error('Error fetching contacts:', error);
            emergencyOutput.innerHTML = 'Error fetching contacts. Please try again.';
        }
    }

    loadCountries(); // Call on page load
});
