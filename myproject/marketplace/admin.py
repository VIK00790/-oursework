from django.contrib import admin
from django.utils.safestring import mark_safe
from .models import Marketplace, Tag, SavedMarketplace, Comment, Notification 
 
@admin.register(Tag) 
class TagAdmin(admin.ModelAdmin): 
    list_display = ['name', 'slug'] 
    prepopulated_fields = {'slug': ('name',)} 
 
@admin.register(Marketplace) 
class MarketplaceAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'author', 'pub_date', 'moderation_status', 
        'image_preview', 'price'
    ]
    list_filter = ['is_public', 'pub_date', 'author', 'tags']
    search_fields = ['title', 'content']
    filter_horizontal = ['tags']
    
    # Действия модерации
    actions = ['approve_items', 'reject_items']
    
    def moderation_status(self, obj):
        if obj.is_public:
            return mark_safe('<span style="color: green; font-weight: bold;"> Одобрено</span>')
        return mark_safe('<span style="color: orange; font-weight: bold;"> На модерации</span>')
    moderation_status.short_description = 'Статус модерации'
    
    def image_preview(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="80" />')
        return "Нет изображения"
    image_preview.short_description = 'Превью'

    def get_queryset(self, request):
        """По умолчанию показываем только товары на модерации"""
        qs = super().get_queryset(request)
        # Можно оставить все, но добавить фильтр по умолчанию
        return qs

    def get_list_filter(self, request):
        return ['is_public', 'pub_date', 'author', 'tags']
 
@admin.register(SavedMarketplace) 
class SavedMarketplaceAdmin(admin.ModelAdmin): 
    list_display = ['user', 'marketplace', 'saved_at'] 
    list_filter = ['saved_at', 'user', 'marketplace']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin): 
    list_display = ['user', 'marketplace', 'created_at'] 
    list_filter = ['created_at', 'user', 'marketplace'] 
    search_fields = ['text', 'user__username']
    actions = ['approve_comments', 'reject_comments']
    
    def short_text(self, obj):
        return obj.text[:50] + '...' if len(obj.text) > 50 else obj.text
    short_text.short_description = 'Текст'
    
    def moderation_status(self, obj):
        if obj.is_approved:
            return mark_safe('<span style="color: green; font-weight: bold;"> Одобрено</span>')
        return mark_safe('<span style="color: orange; font-weight: bold;"> На модерации</span>')
    moderation_status.short_description = 'Статус'

    def get_queryset(self, request):
        """По умолчанию показываем только комментарии на модерации"""
        qs = super().get_queryset(request)
        return qs.filter(is_approved=False) 

# модерация для карточек
@admin.action(description='Одобрить выбранные товары')
def approve_items(self, request, queryset):
    count = queryset.update(is_public=True)
    
    # Уведомляем авторов
    for item in queryset:
        Notification.objects.create(
            user=item.author,
            title='Товар одобрен!',
            message=f'Ваш товар «{item.title}» успешно прошёл модерацию и теперь доступен в каталоге.',
            notification_type='system',
        )
    
    self.message_user(request, f'Одобрено товаров: {count}')

@admin.action(description='Отклонить выбранные товары')
def reject_items(self, request, queryset):
    count = queryset.update(is_public=False)
    
    # Уведомляем авторов
    for item in queryset:
        Notification.objects.create(
            user=item.author,
            title='Товар отклонён',
            message=f'Ваш товар «{item.title}» не прошёл модерацию. Пожалуйста, исправьте нарушения и отправьте на повторную проверку.',
            notification_type='system',
        )
    
    self.message_user(request, f'Отклонено товаров: {count}')

# модерация для коментариев
@admin.action(description='Одобрить выбранные комментарии')
def approve_comments(self, request, queryset):
    count = queryset.update(is_approved=True)
    
    for comment in queryset:
        Notification.objects.create(
            user=comment.user,
            title='Комментарий опубликован',
            message=f'Ваш комментарий к товару «{comment.marketplace.title}» одобрен и теперь виден другим пользователям.',
            notification_type='system',
        )
    
    self.message_user(request, f'Одобрено комментариев: {count}')


@admin.action(description='Отклонить выбранные комментарии')
def reject_comments(self, request, queryset):
    count = queryset.update(is_approved=False)
    
    for comment in queryset:
        Notification.objects.create(
            user=comment.user,
            title='Комментарий отклонён',
            message=f'Ваш комментарий к товару «{comment.marketplace.title}» не прошёл модерацию.',
            notification_type='system',
        )
    
    self.message_user(request, f'Отклонено комментариев: {count}')
