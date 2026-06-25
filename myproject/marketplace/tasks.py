import schedule
import time
import threading
import logging
from datetime import datetime
from django.contrib.auth.models import User
from django.db.models import Sum, Count, Q
from .models import Notification, Marketplace

logger = logging.getLogger(__name__)


def get_user_sales_stats(user):
    marketplaces = Marketplace.objects.filter(author=user)
    
    total_items = marketplaces.count()
    published_items = marketplaces.filter(is_public=True).count()
    total_views = 0  # Если есть счётчик просмотров
    
    # Подсчёт товаров в избранном у других пользователей (показатель интереса)
    total_saves = marketplaces.aggregate(
        total_saves=Count('savedmarketplace')
    )['total_saves'] or 0
    
    # Общая сумма цен товаров
    total_value = marketplaces.aggregate(
        total=Sum('price')
    )['total'] or 0
    
    return {
        'total_items': total_items,
        'published_items': published_items,
        'total_saves': total_saves,
        'total_value': total_value,
    }


def send_monthly_sales_notification():

    today = datetime.now()
    
    # Проверяем, что сегодня 25 число
    #if today.day != 25:
    #    return
    
    logger.info(f"[{today}] Запуск рассылки уведомлений о статистике продаж")
    
    # Получаем всех активных пользователей
    users = User.objects.filter(is_active=True)
    
    for user in users:
        try:
            # Получаем статистику пользователя
            stats = get_user_sales_stats(user)
            
            # Формируем сообщение
            message = (
                f"Здравствуйте, {user.username}!\n\n"
                f"Пришло время проверить вашу статистику продаж за этот месяц:\n\n"
                f"Всего товаров: {stats['total_items']}\n"
                f"Опубликовано: {stats['published_items']}\n"
                f"Добавлений в избранное: {stats['total_saves']}\n"
                f"Общая стоимость товаров: {stats['total_value']:.2f} ₽\n\n"
                f"Перейдите в личный кабинет, чтобы просмотреть подробную статистику "
                f"и обновить свои объявления."
            )
            
            # Создаём уведомление
            Notification.objects.create(
                user=user,
                title='Проверьте статистику продаж',
                message=message,
                notification_type='sales_stats',
            )
            
            logger.info(f"Уведомление отправлено пользователю {user.username}")
            
        except Exception as e:
            logger.error(f"Ошибка при отправке уведомления {user.username}: {e}")
    
    logger.info("Рассылка уведомлений завершена")


def run_scheduler():
    """Запуск планировщика в отдельном потоке"""
    # Запускаем задачу каждый день в 10:00
    schedule.every().day.at("10:00").do(send_monthly_sales_notification)
    
    logger.info("Планировщик уведомлений запущен")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # Проверяем каждую минуту


def start_scheduler_thread():
    """Запуск планировщика в фоновом потоке"""
    thread = threading.Thread(target=run_scheduler, daemon=True)
    thread.start()
    logger.info("Поток планировщика запущен")