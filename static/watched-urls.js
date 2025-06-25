document.getElementById('show-form-button').addEventListener('click', function() {
    const hiddenClass = 'hidden-item';
    this.classList.add(hiddenClass);
    document.querySelector(".watched-page-card.hidden-item").classList.remove(hiddenClass)
});