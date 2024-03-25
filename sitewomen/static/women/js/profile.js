document.getElementById('profile-form').addEventListener('submit', function(event) {
    event.preventDefault();  // Предотвращаем отправку формы по умолчанию
    var formData = new FormData(this);
    fetch('{{ request.path }}', {
        method: 'PATCH',
        body: formData,
        headers: {
            'X-CSRFToken': '{{ csrf_token }}'  // Подставьте ваш CSRF токен
        }
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        // Обработка успешного ответа
        console.log('Успешно');
    })
    .catch(error => {
        // Обработка ошибки
        console.error('There was a problem with the fetch operation:', error);
    });
});
