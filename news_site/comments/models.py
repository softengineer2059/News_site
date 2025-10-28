from django.db import models
from articles.models import Article
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator




class Comments(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    parent = models.ForeignKey(
        'self',  # Ссылка на себя же (для вложенности)
        on_delete=models.CASCADE,
        null=True,  # Если `null` — это корневой комментарий
        blank=True,
        related_name="replies"  # Позволит получать все ответы через `comment.replies`
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username}: {self.text[:20]}..."

    @property
    def is_reply(self):
        """Проверяет, является ли комментарий ответом."""
        return self.parent is not None


class CommentReaction(models.Model):
    LIKE = 1
    DISLIKE = -1
    REACTION_TYPES = (
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
    )

    comment = models.ForeignKey(Comments, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reaction = models.SmallIntegerField(choices=REACTION_TYPES)

    class Meta:
        unique_together = ('comment', 'user')  # Один пользователь — одна реакция


class Comment_images(models.Model):
    comment = models.ForeignKey(Comments, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(null=True, blank=True, upload_to='comment_images/', validators=[FileExtensionValidator(allowed_extensions=['png', 'jpeg', 'jpg'])])