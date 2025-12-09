document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('recommendation-form');
    const submitButton = document.getElementById('submit-button');
    const loadingSpinner = document.getElementById('loading-spinner');
    const statusMessageContainer = document.getElementById('status-message');
    const resultsContainer = document.getElementById('results-container');

    form.addEventListener('submit', async (event) => {
        event.preventDefault(); // Prevent default form submission
        const playlistUrl = document.getElementById('playlist-url').value.trim();
        const userPrompt = document.getElementById('user-prompt').value.trim();

        if (!playlistUrl || !userPrompt) {
            displayMessage('error', 'Please fill out both fields.');
            return;
        }
        submitButton.disabled = true;
        submitButton.textContent = 'Thinking...';
        loadingSpinner.style.display = 'block';
        statusMessageContainer.style.display = 'none';
        resultsContainer.innerHTML = '';

        try {
            const response = await fetch('/api/recommend/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    playlist_url: playlistUrl,
                    user_prompt: userPrompt
                })
            });
            const data = await response.json();
            if (!response.ok) {
                throw new Error(data.message || 'An unknown error occurred.');
            }
            if (data.status === 'success') {
                handleSuccess(data.track_ids);
            } else {
                throw new Error(data.message);
            }
        } catch (error) {
            displayMessage('error', error.message);
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = 'Get Recommendations';
            loadingSpinner.style.display = 'none';
        }
    });

    function handleSuccess(trackIds) {
        resultsContainer.innerHTML = ''; // Clear previous results
        if (trackIds && trackIds.length > 0) {
            displayMessage('info', `Found ${trackIds.length} matching songs for you!`);
            trackIds.forEach(trackId => {
                const iframe = document.createElement('iframe');
                iframe.style.borderRadius = '12px';
                iframe.src = `https://open.spotify.com/embed/track/${trackId}?utm_source=generator`;
                iframe.width = '100%';
                iframe.height = '80'; // Compact view
                iframe.frameBorder = '0';
                iframe.allow = 'autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture';
                iframe.loading = 'lazy';
                resultsContainer.appendChild(iframe);
            });
        } else {
            displayMessage('info', 'No matching songs were found in this playlist for your request. Try a different prompt!');
        }
    }

    function displayMessage(type, message) {
        statusMessageContainer.className = type;
        statusMessageContainer.textContent = message;
        statusMessageContainer.style.display = 'block';
    }
});