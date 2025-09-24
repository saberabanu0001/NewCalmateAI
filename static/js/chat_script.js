// Wait for the DOM content to be fully loaded before running the script
document.addEventListener('DOMContentLoaded', () => {
    console.log('Chat script loaded successfully!');

    // --- DOM ELEMENT SELECTION ---
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessagesContainer = document.getElementById('chat-messages');
    const suggestionsContainer = document.getElementById('seriousness-suggestions-container');
    const seriousnessOutput = document.getElementById('seriousness-output');
    const suggestionsOutput = document.getElementById('suggestions-output');
    const typingIndicator = document.getElementById('typing-indicator');
    const emergencyBanner = document.getElementById('emergency-banner');

    // Chips container and crisis actions
    const quickResponsesContainer = document.getElementById('quick-responses');
    const quickResponseChips = document.getElementById('quick-response-chips');
    const crisisActions = document.getElementById('crisis-actions');

    console.log('DOM elements found:', {
        chatForm: !!chatForm,
        userInput: !!userInput,
        chatMessagesContainer: !!chatMessagesContainer,
        suggestionsContainer: !!suggestionsContainer
    });

    // --- HELPER FUNCTION: APPEND MESSAGE TO CHAT UI ---
    const appendMessage = (sender, text) => {
        const messageElement = document.createElement('div');
        let avatar, bubbleClass, contentClass, avatarContent;

        if (sender === 'user') {
            avatarContent = 'You';
            avatar = document.createElement('div');
            avatar.className = 'flex-shrink-0 w-8 h-8 rounded-full bg-[var(--bubble-user)] flex items-center justify-center text-sm font-bold';
            avatar.style.color = 'var(--bubble-user-text)';
            avatar.textContent = avatarContent;

            bubbleClass = 'ml-auto';
            contentClass = 'bg-[var(--bubble-user)] text-[var(--bubble-user-text)]';
        } else { // 'ai'
            avatarContent = 'AI';
            avatar = document.createElement('div');
            avatar.className = 'flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-br from-indigo-500 to-purple-500 flex items-center justify-center text-sm font-bold text-white';
            avatar.textContent = avatarContent;
            bubbleClass = '';
            // Use dark text for readability in light theme
            contentClass = 'bg-[var(--bubble-ai)] text-slate-900';
        }

        messageElement.className = `flex items-start message space-x-3 w-full max-w-[80%] md:max-w-[60%] ${bubbleClass}`;

        const contentContainer = document.createElement('div');
        contentContainer.className = `p-4 rounded-2xl shadow-lg break-words ${contentClass}`;

        const messageText = document.createElement('p');
        messageText.textContent = text;
        contentContainer.appendChild(messageText);
        
        const timestamp = document.createElement('div');
        timestamp.className = 'timestamp';
        timestamp.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        contentContainer.appendChild(timestamp);

        if (sender === 'user') {
            messageElement.appendChild(contentContainer);
            messageElement.appendChild(avatar);
        } else {
            messageElement.appendChild(avatar);
            messageElement.appendChild(contentContainer);
        }

        chatMessagesContainer.appendChild(messageElement);

        setTimeout(() => {
            chatMessagesContainer.scrollTo({ top: chatMessagesContainer.scrollHeight, behavior: 'smooth' });
        }, 100);

        return messageElement;
    };
    
    // --- API CALL FOR CHAT ---
    const sendMessage = async () => {
        const message = userInput.value.trim();
        console.log('Sending message:', message);
        if (message === '') return;

        userInput.value = '';
        appendMessage('user', message);

        if (typingIndicator) typingIndicator.classList.remove('hidden');

        const loadingMessage = appendMessage('ai', '...');
        const loadingElement = loadingMessage.querySelector('p');
        let dots = 0;
        const loadingInterval = setInterval(() => {
            dots = (dots + 1) % 4;
            if (loadingElement) {
                loadingElement.textContent = '.'.repeat(dots);
            }
        }, 400);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });

            clearInterval(loadingInterval);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Received response:', data);
            
            loadingMessage.remove();
            if (typingIndicator) typingIndicator.classList.add('hidden');
            
            if (data.ai_response) {
                appendMessage('ai', data.ai_response);
            }

            if (data.seriousness_level && data.suggestions) {
                suggestionsContainer.classList.remove('hidden');
                if (window.innerWidth <= 768) {
                    suggestionsContainer.classList.add('show');
                }

                seriousnessOutput.textContent = `Seriousness Level: ${data.seriousness_level}`;
                
                const level = (data.seriousness_level || '').toLowerCase();
                if (emergencyBanner) {
                    if (level.includes('high') || level.includes('emergency') || level.includes('critical')) {
                        emergencyBanner.classList.remove('hidden');
                    } else {
                        emergencyBanner.classList.add('hidden');
                    }
                }

                suggestionsOutput.classList.remove('text-gray-200', 'text-white', 'seriousness-low', 'seriousness-medium', 'seriousness-high', 'seriousness-critical');
                suggestionsOutput.classList.add('text-slate-800', 'markdown-content');
                let colorClass;
                if (level.includes('low')) {
                    colorClass = 'seriousness-low';
                } else if (level.includes('medium')) {
                    colorClass = 'seriousness-medium';
                } else if (level.includes('high') || level.includes('critical') || level.includes('emergency')) {
                    colorClass = 'seriousness-high';
                }
                suggestionsOutput.classList.add(colorClass);
                suggestionsOutput.innerHTML = marked.parse(data.suggestions);
            } else {
                suggestionsContainer.classList.add('hidden');
                suggestionsContainer.classList.remove('show');
                if (emergencyBanner) emergencyBanner.classList.add('hidden');
            }

        } catch (error) {
            clearInterval(loadingInterval);
            loadingMessage.remove();
            if (typingIndicator) typingIndicator.classList.add('hidden');
            console.error('Error fetching chat response:', error);
            
            let errorMessage = "I'm sorry, I am unable to connect right now. Please try again later.";
            if (error.message.includes('Failed to fetch')) {
                errorMessage = "I'm having trouble connecting to the server. Please check your internet connection and try again.";
            } else if (error.message.includes('500')) {
                errorMessage = "I'm experiencing some technical difficulties. Please try again in a moment.";
            }
            appendMessage('ai', errorMessage);
        }
    };

    // --- VOICE INPUT FUNCTIONALITY ---
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;

    const voiceBtn = document.getElementById('voice-btn');
    const voiceStatus = document.getElementById('voice-status');

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => { audioChunks.push(event.data); };
            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                const formData = new FormData();
                formData.append('audio', audioBlob, 'recording.wav');

                try {
                    const response = await fetch('/upload_voice', { method: 'POST', body: formData });
                    const data = await response.json();
                    if (data.transcribed_text && data.transcribed_text !== "Sorry, I could not understand the audio.") {
                        userInput.value = data.transcribed_text;
                        sendMessage();
                    } else {
                        appendMessage('ai', "I couldn't understand what you said. Please try speaking more clearly or type your message instead.");
                    }
                } catch (error) {
                    console.error('Error uploading voice:', error);
                    appendMessage('ai', "I'm having trouble processing your voice input. Please type your message instead.");
                }
            };

            mediaRecorder.start();
            isRecording = true;
            if (voiceStatus) voiceStatus.classList.remove('hidden');
            if (voiceBtn) {
            voiceBtn.classList.add('bg-red-500', 'hover:bg-red-600');
            voiceBtn.classList.remove('bg-[#3a3a5a]', 'hover:bg-[#2a2a4a]');
            }
        } catch (error) {
            console.error('Error accessing microphone:', error);
            appendMessage('ai', "I can't access your microphone. Please check your browser permissions and try again, or type your message instead.");
        }
    };

    const stopRecording = () => {
        if (mediaRecorder && isRecording) {
            mediaRecorder.stop();
            mediaRecorder.stream.getTracks().forEach(track => track.stop());
            isRecording = false;
            if (voiceStatus) voiceStatus.classList.add('hidden');
            if (voiceBtn) {
            voiceBtn.classList.remove('bg-red-500', 'hover:bg-red-600');
            voiceBtn.classList.add('bg-[#3a3a5a]', 'hover:bg-[#2a2a4a]');
            }
        }
    };

    if (voiceBtn) {
        voiceBtn.addEventListener('click', () => { if (!isRecording) startRecording(); else stopRecording(); });
    }

    // --- EVENT LISTENERS ---
    if (chatForm) {
        console.log('Adding submit event listener to chat form');
        chatForm.addEventListener('submit', (e) => {
            console.log('Form submitted!');
            e.preventDefault();
            sendMessage();
        });
    } else {
        console.error('Chat form not found!');
    }

    if (userInput) {
        userInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }

    // --- QUICK RESPONSE BUTTONS ---
    const quickResponseBtns = document.querySelectorAll('.quick-response-btn');
    console.log('Found quick response buttons:', quickResponseBtns.length);
    quickResponseBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const message = btn.getAttribute('data-message');
            if (userInput) {
                userInput.value = message;
                sendMessage();
            }
        });
    });

    // Hide only the chips after first message, keep crisis actions visible
    const hideQuickResponses = () => {
        if (quickResponseChips) { quickResponseChips.style.display = 'none'; }
        if (crisisActions) { crisisActions.style.display = 'flex'; }
        if (quickResponsesContainer) { quickResponsesContainer.classList.remove('hidden'); }
    };

    const originalSendMessage = sendMessage;
    const newSendMessage = async () => {
        hideQuickResponses();
        await originalSendMessage();
    };
    sendMessage = newSendMessage;

    // --- CLEAR CHAT FUNCTIONALITY ---
    function performClearChat() {
        // Rebuild a fresh welcome message bubble (light theme)
        chatMessagesContainer.innerHTML = '';
        const wrapper = document.createElement('div');
        wrapper.className = 'flex items-start message space-x-3 w-full max-w-[75%]';
        const avatar = document.createElement('div');
        avatar.className = 'flex-shrink-0 w-8 h-8 rounded-full bg-indigo-400 text-white flex items-center justify-center text-sm font-bold';
        avatar.textContent = 'AI';
        const bubble = document.createElement('div');
        bubble.className = 'card p-4';
        const p = document.createElement('p');
        p.textContent = "Hello! I'm here to listen. How are you feeling today?";
        const ts = document.createElement('div');
        ts.className = 'timestamp';
        ts.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        bubble.appendChild(p);
        bubble.appendChild(ts);
        wrapper.appendChild(avatar);
        wrapper.appendChild(bubble);
        chatMessagesContainer.appendChild(wrapper);

        // Show quick responses and crisis actions again
        if (quickResponseChips) { quickResponseChips.style.display = 'flex'; }
        if (crisisActions) { crisisActions.style.display = 'flex'; }
        if (quickResponsesContainer) { quickResponsesContainer.classList.remove('hidden'); quickResponsesContainer.style.display = 'block'; }

        // Hide suggestions container and emergency banner
        if (suggestionsContainer) {
            suggestionsContainer.classList.add('hidden');
            suggestionsContainer.classList.remove('show');
        }
        if (emergencyBanner) emergencyBanner.classList.add('hidden');

        // Close menu if open
        const menuDropdown = document.getElementById('menu-dropdown');
        if (menuDropdown) menuDropdown.classList.add('hidden');
    }

    // Expose globally for inline handler
    window.performClearChat = performClearChat;

    const clearChatBtn = document.getElementById('clear-chat');
    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('[ClearChat] direct button click');
            if (confirm('Are you sure you want to clear the chat history?')) {
                performClearChat();
            }
        });
    }

    // Capture-phase delegation to ensure it works even if dropdown swallows events
    document.addEventListener('click', (e) => {
        const el = e.target;
        const isClear = el && (el.id === 'clear-chat' || (el.closest && el.closest('#clear-chat')));
        if (isClear) {
            e.preventDefault();
            e.stopPropagation();
            console.log('[ClearChat] delegated capture click');
            if (confirm('Are you sure you want to clear the chat history?')) {
                performClearChat();
            }
        }
    }, { capture: true });

    // --- CLOSE SIDEBAR FUNCTIONALITY ---
    const closeSidebarBtn = document.getElementById('close-sidebar');
    if (closeSidebarBtn) {
        closeSidebarBtn.addEventListener('click', () => {
            suggestionsContainer.classList.remove('show');
        });
    }
});

