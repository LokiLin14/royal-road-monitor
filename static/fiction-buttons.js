// Hack, ideally i want to use url_for('view')
const view_url_endpoint = '/view'

async function view_fiction(fiction_url, interested) {
    try {
        const form_data = new FormData();
        form_data.append('url', fiction_url);
        form_data.append('interested', interested);
        const response = await fetch(view_url_endpoint, {
            method: 'POST',
            body: form_data
        });
        if (!response.ok) {
            const resp_data = await response.json()
            console.log('Request failed:', resp_data.message);
        }
        return response.ok;
    } catch (error) {
        console.error('Request failed:', error);
        return false;
    }
}

// Add event listeners to follow buttons
const followButtons = document.querySelectorAll('.follow-fiction');
followButtons.forEach(button => {
    button.addEventListener('click', async function() {
        const fictionItem = this.closest('.fiction-list-item');
        const link = fictionItem.querySelector('a').href;
        const success = await view_fiction(link, true);
        if (success) {
            fictionItem.style.display = 'None';
        }
    });
});

// Add event listeners to discard buttons
const discardButtons = document.querySelectorAll('.discard-fiction');
discardButtons.forEach(button => {
    button.addEventListener('click', async function() {
        const fictionItem = this.closest('.fiction-list-item');
        const link = fictionItem.querySelector('a').href;
        const success = await view_fiction(link, false);
        if (success) {
            fictionItem.style.display = 'None';
        }
    });
});