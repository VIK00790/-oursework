from django.apps import AppConfig
import logging


class MarketplaceConfig(AppConfig):
    name = 'marketplace'

logger = logging.getLogger(__name__)


class MarketplaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'marketplace'
    verbose_name = 'Торговая площадка'
    
    def ready(self):
        """Запускается один раз при старте Django"""
        # Импортируем здесь, чтобы избежать circular imports
        from django.conf import settings
        
        # Запускаем планировщик только один раз (не при каждой перезагрузке)
        # и только если это не команда migrate
        import sys
        if 'runserver' in sys.argv or 'gunicorn' in sys.argv:
            try:
                from .tasks import start_scheduler_thread
                start_scheduler_thread()
                logger.info("Планировщик успешно запущен")
            except Exception as e:
                logger.error(f"Ошибка запуска планировщика: {e}")