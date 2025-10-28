from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import date
from django.core.validators import FileExtensionValidator




class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL")
    image = models.ImageField(null=True, blank=True, upload_to='category_images/', validators=[FileExtensionValidator(allowed_extensions=['png', 'jpeg', 'jpg'])])

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class Subcategory(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL")
    image = models.ImageField(null=True, blank=True, upload_to='subcategory_images/', validators=[FileExtensionValidator(allowed_extensions=['png', 'jpeg', 'jpg'])])
    category_name = models.ForeignKey(Category, null=True, verbose_name="Категория", on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Подкатегория"
        verbose_name_plural = "Подкатегории"


class Country(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URl")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Страна"
        verbose_name_plural = "Страны"


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"


User = get_user_model()


class Article(models.Model):
    title = models.CharField(max_length=300, verbose_name='Заголовок')
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL", blank=True)
    short_description = models.CharField(max_length=900, verbose_name="Описание статьи")
    content = models.TextField(verbose_name="Текст статьи")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор", blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Категория")
    subcategory = models.ForeignKey(Subcategory, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Подкатегория")
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Страна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_published = models.BooleanField(blank=True, default=False, verbose_name="Опубликовано")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Теги")
    views = models.PositiveIntegerField(default=0, verbose_name="Просмотры")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"
        ordering = ['-created_at']

    def get_absolute_url(self):
        return reverse('article_detail', kwargs={'slug': self.slug})

    def increment_views(self, request):
        session_key = f'article_{self.id}_viewed'
        ip_key = f'article_{self.id}_ip'

        user_ip = request.META.get('REMOTE_ADDR')
        current_time = timezone.now()

        if not request.session.get(session_key):
            last_view_ip = request.session.get(ip_key, {})
            last_view_date = last_view_ip.get('date')

            if last_view_date:
                try:
                    last_view_date = date.fromisoformat(last_view_date)
                except (ValueError, TypeError):
                    last_view_date = None

            if last_view_ip.get('ip') != user_ip or \
                    last_view_date != current_time.date():
                # Обновляем напрямую в БД
                Article.objects.filter(id=self.id).update(
                    views=models.F('views') + 1
                )

                # Обязательно обновляем объект из БД
                self.refresh_from_db()

                request.session[session_key] = True
                request.session[ip_key] = {
                    'ip': user_ip,
                    'date': current_time.date().isoformat()
                }
                request.session.modified = True
                return True
        return False

    def get_comments_count(self):
        return self.comments.count()


def article_image_directory_path(instance, filename):
    """
    Генерирует путь для сохранения изображений статьи в формате:
    images/ГГГГ/ММ/ДД/slug-статьи/имя_файла
    """
    # Вместо полного заголовка используйте ID статьи или укороченную версию
    article = instance.article

    # Вариант 2: укороченный slug (первые 50 символов)
    short_slug = article.slug[:50] if article.slug else f"article_{article.id}"
    path = f"images/{article.created_at:%Y/%m/%d}/{short_slug}/{filename}"

    return path


class ArticleImage(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(
        upload_to=article_image_directory_path,  # Используем функцию
        verbose_name="Изображение",
        max_length=250
    )
    caption = models.CharField(max_length=100, blank=True, verbose_name="Подпись")

    class Meta:
        verbose_name = "Изображение"
        verbose_name_plural = "Изображения"


"""
# На случай создания отдельной модели для хранения информации о просмотрах каждой статьи
class ArticleView(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    session_key = models.CharField(max_length=40)
    view_date = models.DateField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['article', 'ip_address', 'view_date']  # Один просмотр в день с одного IP

# В модели Article
def increment_views(self, request):
    from datetime import date
    
    user_ip = request.META.get('REMOTE_ADDR', '')
    session_key = request.session.session_key or 'anonymous'
    current_date = date.today()
    
    # Пытаемся создать запись о просмотре
    view, created = ArticleView.objects.get_or_create(
        article=self,
        ip_address=user_ip,
        view_date=current_date,
        defaults={'session_key': session_key}
    )
    
    # Если создана новая запись (уникальный просмотр) - увеличиваем счетчик
    if created:
        self.views = models.F('views') + 1
        self.save(update_fields=['views'])
        return True
    
    return False
"""