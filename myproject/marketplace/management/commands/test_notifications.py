from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils import timezone


class Command(BaseCommand):
    help = 'Тестовая отправка уведомлений о статистике продаж'
    
    def handle(self, *args, **options):
        # Получаем модели через apps
        Notification = apps.get_model('marketplace', 'Notification')
        Marketplace = apps.get_model('marketplace', 'Marketplace')
        
        from django.contrib.auth.models import User
        from django.db.models import Sum, Count
        
        self.stdout.write('Запуск тестовой рассылки...')
        
        today = timezone.now()
        self.stdout.write(f'Сегодня: {today.strftime("%d.%m.%Y")}')
        
        # Получаем всех активных пользователей
        users = User.objects.filter(is_active=True)
        self.stdout.write(f'Найдено пользователей: {users.count()}')
        
        for user in users:
            try:
                marketplaces = Marketplace.objects.filter(author=user)
                
                stats = {
                    'total_items': marketplaces.count(),
                    'published_items': marketplaces.filter(is_public=True).count(),
                    'total_saves': marketplaces.aggregate(
                        total_saves=Count('savedmarketplace')
                    )['total_saves'] or 0,
                    'total_value': marketplaces.aggregate(
                        total=Sum('price')
                    )['total'] or 0,
                }
                
                message = (
                    f"Здравствуйте, {user.username}!\n\n"
                    f"Всего товаров: {stats['total_items']}\n"
                    f"Опубликовано: {stats['published_items']}\n"
                    f"Добавлений в избранное: {stats['total_saves']}\n"
                    f"Общая стоимость товаров: {stats['total_value']:.2f} ₽"
                )
                
                Notification.objects.create(
                    user=user,
                    title='Проверьте статистику продаж (ТЕСТ)',
                    message=message,
                    notification_type='sales_stats',
                )
                
                self.stdout.write(
                    self.style.SUCCESS(f"Отправлено: {user.username}")
                )
                
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Ошибка для {user.username}: {e}")
                )
        
        self.stdout.write(self.style.SUCCESS('\nРассылка завершена!'))

# python manage.py test_notifications