import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.contrib.auth.models import User
from marketplace.models import Marketplace, Tag, Comment, SavedMarketplace, Notification


print("БАЗА ДАННЫХ")
print(f"Пользователи: {User.objects.count()}")
print(f"Товары: {Marketplace.objects.count()}")
print(f"Теги: {Tag.objects.count()}")
print(f"Комментарии: {Comment.objects.count()}")
print(f"Избранное: {SavedMarketplace.objects.count()}")
print(f"Уведомления: {Notification.objects.count()}")

print("ПРИМЕРЫ ДАННЫХ:")
print("Последние 5 товаров:")
for item in Marketplace.objects.order_by('-pub_date')[:5]:
    status = "опубликовано" if item.is_public else "на модерации"
    print(f"{status} {item.title} — {item.price}₽")

print("Последние 5 комментариев:")
for comment in Comment.objects.order_by('-created_at')[:5]:
    status = "опубликовано" if comment.is_approved else "на модерации"
    print(f"{status} {comment.user.username}: {comment.text[:50]}...")