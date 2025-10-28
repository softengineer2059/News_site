document.getElementById('file-input').addEventListener('change', function() {
    // Автоматически отправляем форму при выборе файла
    document.getElementById('avatar-form').submit();
});