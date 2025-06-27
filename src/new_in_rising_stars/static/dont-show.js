const delete_dont_show_url_endpoint = '/api/delete_dont_show'

async function delete_dont_show(fiction_url) {
    try {
        const form_data = new FormData();
        form_data.append('url', fiction_url);
        const response = await fetch(delete_dont_show_url_endpoint, {
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

// Add event listeners to undo don't show entries
const dontShowButtons = document.querySelectorAll('.undo-dont-show-fiction');
dontShowButtons.forEach(button => {
    button.addEventListener('click', async function() {
        const dont_show_entry = this.closest('.content-item');
        const link = dont_show_entry.querySelector('a').href;
        const success = await delete_dont_show(link);
        if (success) {
            dont_show_entry.style.display = 'None';
        }
    });
});