let selectedFiles = [];

			document.getElementById('file-input').addEventListener('change', function(event) {
				const files = Array.from(event.target.files);
				selectedFiles = selectedFiles.concat(files); // Сохраняем старые файлы

				updateFileList();
			});

			function updateFileList() {
				const fileList = document.getElementById('file-list');
				fileList.innerHTML = ''; // Очистить предыдущий список

				selectedFiles.forEach((file, index) => {
					const fileItem = document.createElement('div');
					fileItem.classList.add('file-item');

					const img = document.createElement('img');
					img.src = URL.createObjectURL(file); // Создаем URL для миниатюры
					img.style.width = '100px'; // Устанавливаем ширину миниатюры
					img.style.height = '100px'; // Устанавливаем высоту миниатюры
					img.alt = file.name;

					const fileName = document.createElement('span');
					fileName.textContent = file.name;

					const removeButton = document.createElement('button');
					removeButton.textContent = 'Удалить';
					removeButton.classList.add('btn', 'btn-danger', 'btn-sm');
					removeButton.onclick = () => {
						selectedFiles.splice(index, 1); // Удаляем файл из массива
						updateFileInput(); // Обновляем элемент input
						updateFileList(); // Обновляем список
					};

					fileItem.appendChild(img);
					fileItem.appendChild(fileName);
					fileItem.appendChild(removeButton);
					fileList.appendChild(fileItem);
				});
			}

			function updateFileInput() {
				const dataTransfer = new DataTransfer();
				selectedFiles.forEach(file => {
					dataTransfer.items.add(file); // Добавляем оставшиеся файлы
				});
				document.getElementById('file-input').files = dataTransfer.files; // Обновляем input
			}