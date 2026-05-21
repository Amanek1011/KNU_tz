document.querySelectorAll('.field').forEach((field) => {
    field.addEventListener('input', () => field.classList.toggle('has-value', Boolean(field.value)));
});
