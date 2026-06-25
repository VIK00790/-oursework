from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone

# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

class Marketplace(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    price = models.DecimalField(verbose_name='Цена', max_digits=10, decimal_places=2, default=0.00)
    content = models.TextField(verbose_name='Содержание')
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Автор')
    pub_date = models.DateTimeField(default=timezone.now, verbose_name='Дата публикации')
    tags = models.ManyToManyField(Tag, blank=True, verbose_name='Теги')
    is_public = models.BooleanField(default=True, verbose_name='Публичная статья')
    image = models.ImageField('Изображение', upload_to='marketplaces/', blank=True, null=True)

    def __str__(self):
        return self.title
    class Meta:
        verbose_name = 'Статья'
        verbose_name_plural = 'Статьи'
    def get_absolute_url(self):
        return reverse("marketplace_detail", kwargs={"pk": self.pk})
    
class SavedMarketplace(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    marketplace = models.ForeignKey(Marketplace, on_delete=models.CASCADE, verbose_name='Статья')
    saved_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата сохранения')
    def __str__(self):
        return f'{self.user.username} - {self.marketplace.title}'
    class Meta:
        unique_together = ['user', 'marketplace']
        verbose_name = 'Сохраненная статья'
        verbose_name_plural = 'Сохраненные статьи'

class Comment(models.Model):
    marketplace = models.ForeignKey(Marketplace, on_delete=models.CASCADE, verbose_name='Статья')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    text = models.TextField(verbose_name='Комментарий')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    def __str__(self):
        return f'Коментарий от {self.user.username} к статье {self.marketplace.title}'
    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('sales_stats', 'Статистика продаж'),
        ('system', 'Системное'),
        ('promo', 'Акция'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    message = models.TextField(verbose_name='Сообщение')
    notification_type = models.CharField(
        max_length=20, 
        choices=NOTIFICATION_TYPES, 
        default='system',
        verbose_name='Тип'
    )
    is_read = models.BooleanField(default=False, verbose_name='Прочитано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Уведомление'
        verbose_name_plural = 'Уведомления'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.user.username}: {self.title}'