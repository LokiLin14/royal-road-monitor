// Hack, ideally i want to use url_for('view')
const dont_show_url_endpoint = '/api/dont_show_again'

async function mark_dont_show_fiction(fiction_id) {
    try {
        const form_data = new FormData();
        form_data.append('fiction_id', fiction_id);
        const response = await fetch(dont_show_url_endpoint, {
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

// Add event listeners to mark fictions as dont show again
const dontShowButtons = document.querySelectorAll('.dont-show-fiction');
dontShowButtons.forEach(button => {
    button.addEventListener('click', async function() {
        const fictionItem = this.closest('.content-item');
        const link = fictionItem.querySelector('.fiction-id').textContent;
        const success = await mark_dont_show_fiction(link);
        if (success) {
            fictionItem.style.display = 'None';
        }
    });
});

const expandButtons = document.querySelectorAll('.expand-button')
expandButtons.forEach(button => {
    button.addEventListener('click', function () {
        const fictionItem = this.closest('.fiction-card');
        fictionItem.classList.remove('fiction-card-minimised')
    })
})

const shrinkButtons = document.querySelectorAll('.shrink-button')
shrinkButtons.forEach(button => {
    button.addEventListener('click', function () {
        const fictionItem = this.closest('.fiction-card');
        fictionItem.classList.add('fiction-card-minimised')
    })
})