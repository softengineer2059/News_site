
// Глобальные переменные
let currentImageIndex = 0;
let images = [];

// Инициализация массива изображений при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Собираем все изображения из галереи
    const imageElements = document.querySelectorAll('.card-body_comments img');
    images = Array.from(imageElements).map(img => img.src);
});

// Открытие модального окна
function openImageModal(imageSrc, index) {
    currentImageIndex = index;
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');

    modalImage.src = imageSrc;
    modal.style.display = 'block';
    document.body.style.overflow = 'hidden'; // Блокируем прокрутку страницы
}

// Закрытие модального окна
function closeModal() {
    const modal = document.getElementById('imageModal');
    modal.style.display = 'none';
    document.body.style.overflow = 'auto'; // Восстанавливаем прокрутку
}

// Переключение изображений
function changeImage(direction) {
    currentImageIndex += direction;

    // Зацикливание изображений
    if (currentImageIndex >= images.length) {
        currentImageIndex = 0;
    } else if (currentImageIndex < 0) {
        currentImageIndex = images.length - 1;
    }

    document.getElementById('modalImage').src = images[currentImageIndex];
}

// Обработка клавиатуры
document.addEventListener('keydown', function(event) {
    const modal = document.getElementById('imageModal');
    if (modal.style.display === 'block') {
        switch(event.key) {
            case 'Escape':
                closeModal();
                break;
            case 'ArrowLeft':
                changeImage(-1);
                break;
            case 'ArrowRight':
                changeImage(1);
                break;
        }
    }
});

// Закрытие по клику вне изображения
document.getElementById('imageModal').addEventListener('click', function(event) {
    if (event.target === this) {
        closeModal();
    }
});
