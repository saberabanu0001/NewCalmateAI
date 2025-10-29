// Wait for the DOM content to be fully loaded before running the script
document.addEventListener('DOMContentLoaded', () => {
    console.log('Chat script loaded successfully!');

    // --- DOM ELEMENT SELECTION ---
    // Select the chat form, user input field, and the main chat messages container
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatMessagesContainer = document.getElementById('chat-messages');
    const suggestionsContainer = document.getElementById('seriousness-suggestions-container');
    const seriousnessOutput = document.getElementById('seriousness-output');
    const suggestionsOutput = document.getElementById('suggestions-output');

    // Header controls
    const settingsBtn = document.getElementById('settings-btn');
    const settingsMenu = document.getElementById('settings-menu');
    const clearChatBtn = document.getElementById('clear-chat');
    const fontIncrease = document.getElementById('font-increase');
    const fontDecrease = document.getElementById('font-decrease');
    const calmToggle = document.getElementById('calm-toggle');
    const calmOverlay = document.getElementById('calm-overlay');
    const exitCalm = document.getElementById('exit-calm');
    const toggleSidebarBtn = document.getElementById('toggle-sidebar');
    const closeSidebarBtn = document.getElementById('close-sidebar');
    const inputArea = document.querySelector('.input-area');
    const quickResponses = document.getElementById('quick-responses');

    console.log('DOM elements found:', {
        chatForm: !!chatForm,
        userInput: !!userInput,
        chatMessagesContainer: !!chatMessagesContainer,
        suggestionsContainer: !!suggestionsContainer
    });

    // Ensure chat scrolls to bottom on page load
    const scrollToBottom = () => {
        if (chatMessagesContainer) {
            chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
        }
    };
    
    // Scroll to bottom when page loads
    scrollToBottom();
    setTimeout(scrollToBottom, 100);

    // Scroll to bottom button functionality
    const scrollToBottomBtn = document.getElementById('scroll-to-bottom');
    let isAtBottom = true;
    
    const checkScrollPosition = () => {
        if (!chatMessagesContainer) return;
        const threshold = 100;
        const isNearBottom = chatMessagesContainer.scrollTop + chatMessagesContainer.clientHeight >= chatMessagesContainer.scrollHeight - threshold;
        
        if (isNearBottom !== isAtBottom) {
            isAtBottom = isNearBottom;
            if (scrollToBottomBtn) {
                if (isAtBottom) {
                    scrollToBottomBtn.style.opacity = '0';
                    scrollToBottomBtn.style.pointerEvents = 'none';
                } else {
                    scrollToBottomBtn.style.opacity = '1';
                    scrollToBottomBtn.style.pointerEvents = 'auto';
                }
            }
        }
    };
    
    if (chatMessagesContainer) {
        chatMessagesContainer.addEventListener('scroll', checkScrollPosition);
    }
    
    if (scrollToBottomBtn) {
        scrollToBottomBtn.addEventListener('click', () => {
            scrollToBottom();
        });
    }

    // --- ACCESSIBILITY: dynamic font size ---
    let baseFontSize = 16;
    const applyFontSize = () => {
        document.documentElement.style.fontSize = `${baseFontSize}px`;
    };
    if (fontIncrease) fontIncrease.addEventListener('click', () => { baseFontSize = Math.min(20, baseFontSize + 1); applyFontSize(); });
    if (fontDecrease) fontDecrease.addEventListener('click', () => { baseFontSize = Math.max(14, baseFontSize - 1); applyFontSize(); });
    applyFontSize();

    // No need for dynamic padding since input is now properly positioned within chat container

    // --- Settings menu toggle ---
    if (settingsBtn) {
        settingsBtn.addEventListener('click', () => {
            settingsMenu.classList.toggle('hidden');
        });
        document.addEventListener('click', (e) => {
            if (!settingsBtn.contains(e.target) && !settingsMenu.contains(e.target)) {
                settingsMenu.classList.add('hidden');
            }
        });
    }

    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', () => {
            chatMessagesContainer.innerHTML = '';
        });
    }

    // Sidebar toggle
    const setSidebar = (open) => {
        if (!suggestionsContainer) return;
        if (open) suggestionsContainer.classList.remove('hidden'); else suggestionsContainer.classList.add('hidden');
        if (toggleSidebarBtn) toggleSidebarBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
    };
    if (toggleSidebarBtn) toggleSidebarBtn.addEventListener('click', () => setSidebar(suggestionsContainer.classList.contains('hidden')));
    if (closeSidebarBtn) closeSidebarBtn.addEventListener('click', () => setSidebar(false));

    // --- Calm Mode ---
    const setCalmMode = (on) => {
        if (!calmOverlay || !calmToggle) return;
        calmOverlay.style.display = on ? 'flex' : 'none';
        calmToggle.setAttribute('aria-pressed', on ? 'true' : 'false');
    };
    if (calmToggle) calmToggle.addEventListener('click', () => setCalmMode(calmOverlay.style.display !== 'flex'));
    if (exitCalm) exitCalm.addEventListener('click', () => setCalmMode(false));

    // --- HELPER FUNCTION: APPEND MESSAGE TO CHAT UI ---
    /**
     * Appends a new message bubble to the chat interface.
     * @param {string} sender - The sender of the message ('user' or 'ai').
     * @param {string} text - The content of the message.
     * @returns {HTMLElement} The created message element
     */
    const appendMessage = (sender, text) => {
        const wrapper = document.createElement('div');
        let avatar, bubbleClass, bubbleStyles;

        if (sender === 'user') {
            avatar = '<div class="flex-shrink-0 w-8 h-8 rounded-full bg-sky-400 flex items-center justify-center text-sm font-bold text-white">You</div>';
            bubbleClass = 'ml-auto';
            bubbleStyles = 'bg-slate-100 text-slate-800 border border-slate-200';
        } else {
            avatar = '<div class="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-400 flex items-center justify-center text-sm font-bold text-white">🌿</div>';
            bubbleClass = '';
            bubbleStyles = 'bg-white ai-bubble text-slate-800 border border-slate-200';
        }

        wrapper.className = `flex items-start mb-6 space-x-3 w-full max-w-[80%] md:max-w-[60%] ${bubbleClass}`;

        const bubble = document.createElement('div');
        bubble.className = `p-4 rounded-2xl shadow-sm ${bubbleStyles}`;
        bubble.innerHTML = `<p>${text}</p><div class="mt-1 text-[10px] text-slate-400">${new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>`;

        if (sender === 'user') {
            wrapper.appendChild(bubble);
            wrapper.insertAdjacentHTML('beforeend', avatar);
        } else {
            wrapper.insertAdjacentHTML('beforeend', avatar);
            wrapper.appendChild(bubble);
        }

        chatMessagesContainer.appendChild(wrapper);
        
        // Force scroll to bottom immediately and smoothly
        scrollToBottom();
        setTimeout(scrollToBottom, 50);
        setTimeout(scrollToBottom, 100);
        requestAnimationFrame(scrollToBottom);
        
        return wrapper;
    };
    
    // --- API CALL FOR CHAT ---
    const sendMessage = async () => {
        const message = userInput.value.trim();
        if (message === '') return;

        userInput.value = '';
        appendMessage('user', message);

        // Typing indicator
        const loadingMessage = appendMessage('ai', '...');
        const loadingElement = loadingMessage.querySelector('p');
        let dots = 0;
        const loadingInterval = setInterval(() => {
            dots = (dots + 1) % 4;
            if (loadingElement) loadingElement.textContent = '.'.repeat(dots);
        }, 500);

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            });

            clearInterval(loadingInterval);
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            const data = await response.json();
            loadingMessage.remove();
            if (data.ai_response) {
                appendMessage('ai', data.ai_response);
                // Ensure scroll after AI response
                setTimeout(scrollToBottom, 100);
            }

            // Sidebar content
            if (data.seriousness_level && data.suggestions) {
                suggestionsContainer.classList.remove('hidden');
                if (window.innerWidth <= 768) suggestionsContainer.classList.add('show');

                seriousnessOutput.textContent = `Seriousness Level: ${data.seriousness_level}`;
                suggestionsOutput.className = 'text-sm text-slate-700 markdown-content';
                let colorClass;
                const level = data.seriousness_level.toLowerCase();
                if (level.includes('low')) colorClass = 'seriousness-low';
                else if (level.includes('medium')) colorClass = 'seriousness-medium';
                else if (level.includes('high') || level.includes('critical') || level.includes('emergency')) colorClass = 'seriousness-high';
                suggestionsOutput.classList.add(colorClass);
                const mdHtml = marked.parse(data.suggestions);
                const decorated = mdHtml
                  .replace(/<li>(Take a short walk|Go for a walk|Stretch)/gi, '<li>🚶 $1')
                  .replace(/<li>(Practice .*breathing|Deep breathing)/gi, '<li>🫁 $1')
                  .replace(/<li>(5-minute meditation|meditation)/gi, '<li>🧘 $1')
                  .replace(/<li>(Listen to .*music)/gi, '<li>🎶 $1')
                  .replace(/<li>(Connect with .*friend|family)/gi, '<li>🤝 $1')
                  .replace(/<li>(Call .*emergency|hotline|helpline)/gi, '<li>📞 $1');
                suggestionsOutput.innerHTML = decorated;

                // Emphasize emergency
                const emergencyBanner = document.getElementById('emergency-banner');
                if (emergencyBanner) {
                    if (level.includes('high') || level.includes('emergency') || level.includes('critical')) emergencyBanner.classList.remove('hidden');
                    else emergencyBanner.classList.add('hidden');
                }
            } else {
                suggestionsContainer.classList.add('hidden');
                suggestionsContainer.classList.remove('show');
            }
        } catch (error) {
            clearInterval(loadingInterval);
            loadingMessage.remove();
            console.error('Error fetching chat response:', error);
            appendMessage('ai', "I'm sorry, I am unable to connect right now. Please try again later.");
        }
    };

    // Submit handler
    if (chatForm) {
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            sendMessage();
        });
    }

    // Quick responses
    document.querySelectorAll('.quick-response-btn').forEach((btn, idx) => {
        btn.setAttribute('role', 'button');
        btn.setAttribute('tabindex', '0');
        btn.addEventListener('click', () => {
            userInput.value = btn.dataset.message || '';
            sendMessage();
        });
        // Keyboard shortcuts 1–9
        document.addEventListener('keydown', (e) => {
            const n = parseInt(e.key, 10);
            if (!Number.isNaN(n) && n >= 1 && n <= 9) {
                const target = document.querySelectorAll('.quick-response-btn')[n - 1];
                if (target) {
                    userInput.value = target.dataset.message || '';
                    sendMessage();
                }
            }
        });
    });

    // --- VOICE INPUT FUNCTIONALITY ---
    let mediaRecorder;
    let audioChunks = [];
    let isRecording = false;
    let currentStream = null;

    // Web Speech API (browser speech-to-text)
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    let interimTranscript = '';
    let finalTranscript = '';
    let timerId = null;
    let startedAt = 0;

    const voiceBtn = document.getElementById('voice-btn');
    const voiceStatus = document.getElementById('voice-status');

    const formatElapsed = (ms) => {
        const s = Math.floor(ms / 1000);
        const mm = String(Math.floor(s / 60)).padStart(2,'0');
        const ss = String(s % 60).padStart(2,'0');
        return `${mm}:${ss}`;
    };

    const startTimer = () => {
        startedAt = Date.now();
        if (timerId) clearInterval(timerId);
        timerId = setInterval(() => {
            if (!voiceStatus) return;
            const base = finalTranscript || interimTranscript ? `${finalTranscript || ''}${interimTranscript ? ' ' + interimTranscript : ''}`.slice(0,80) : 'Recording...';
            voiceStatus.querySelector('span').textContent = `${base}  • ${formatElapsed(Date.now() - startedAt)}  (Click to stop)`;
        }, 250);
    };

    const stopTimer = () => { if (timerId) { clearInterval(timerId); timerId = null; } };

    const startSpeechRecognition = () => {
        if (!SpeechRecognition) return false;
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';
        interimTranscript = '';
        finalTranscript = '';
        recognition.onresult = (event) => {
            interimTranscript = '';
            for (let i = event.resultIndex; i < event.results.length; ++i) {
                const txt = event.results[i][0].transcript.trim();
                if (event.results[i].isFinal) finalTranscript += (finalTranscript ? ' ' : '') + txt;
                else interimTranscript += ' ' + txt;
            }
        };
        recognition.onerror = (e) => { console.warn('SpeechRecognition error', e); };
        recognition.onend = () => { /* will be stopped in stopRecording */ };
        try { recognition.start(); return true; } catch(e) { console.warn('SpeechRecognition start failed', e); return false; }
    };

    const stopSpeechRecognition = () => { try { recognition && recognition.stop(); } catch(e){} recognition = null; };

    const startRecording = async () => {
        try {
            // Prefer Web Speech API for immediate transcript if available
            const srStarted = startSpeechRecognition();

            // Also start MediaRecorder to keep future option to upload audio
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            mediaRecorder = new MediaRecorder(stream);
            currentStream = stream;
            audioChunks = [];

            mediaRecorder.ondataavailable = (event) => { audioChunks.push(event.data); };
            mediaRecorder.onstop = async () => {
                const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
                // If we have a transcript, auto-send it
                const transcript = (finalTranscript || interimTranscript || '').trim();
                if (transcript) {
                    userInput.value = transcript;
                    sendMessage();
                }
                voiceStatus.classList.add('hidden');
                stopTimer();
            };

            mediaRecorder.start();
            isRecording = true;
            if (voiceStatus) voiceStatus.classList.remove('hidden');
            if (voiceBtn) voiceBtn.setAttribute('aria-pressed', 'true');
            startTimer();
        } catch (error) {
            console.error('Error starting voice recording:', error);
        }
    };

    const stopRecording = () => {
        if (isRecording) {
            try { mediaRecorder && mediaRecorder.stop(); } catch (e) { /* ignore */ }
            stopSpeechRecognition();
            if (currentStream) {
                currentStream.getTracks().forEach(t => { try { t.stop(); } catch(e){} });
                currentStream = null;
            }
            isRecording = false;
            if (voiceStatus) voiceStatus.classList.add('hidden');
            if (voiceBtn) voiceBtn.setAttribute('aria-pressed', 'false');
            stopTimer();
        }
    };

    if (voiceBtn) {
        voiceBtn.addEventListener('click', () => { if (!isRecording) startRecording(); else stopRecording(); });
    }

    // Allow clicking the red status pill to stop
    if (voiceStatus) { voiceStatus.addEventListener('click', stopRecording); }

    // ESC key stops recording
    document.addEventListener('keydown', (e) => { if (e.key === 'Escape' && isRecording) stopRecording(); });
});

