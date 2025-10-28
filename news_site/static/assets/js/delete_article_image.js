function deleteImage(url, csrfToken) {
    fetch(url, {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
        },
    })
    .then(response => {
        if (!response.ok) throw new Error('Ошибка сети');
        return response.json();
    })
    .then(data => {
        if (data.success) {
            document.querySelector('.images-list').innerHTML = data.html;
        } else {
            alert(data.error || 'Ошибка при удалении');
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        alert('Не удалось удалить изображение');
    });
}