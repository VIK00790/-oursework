from django.contrib import admin

# Register your models here.
from .models import Marketplace, Tag, SavedMarketplace, Comment 
 
@admin.register(Tag) 
class TagAdmin(admin.ModelAdmin): 
    list_display = ['name', 'slug'] 
    prepopulated_fields = {'slug': ('name',)} 
 
@admin.register(Marketplace) 
class MarketplaceAdmin(admin.ModelAdmin): 
    list_display = ['title', 'author', 'pub_date', 'is_public', 'image_preview', 'price'] 
    list_filter = ['pub_date', 'author', 'tags', 'is_public'] 
    search_fields = ['title', 'content'] 
    filter_horizontal = ['tags'] 
    def image_preview(self, obj):
        if obj.image:
            from django.utils.safestring import mark_safe
            return mark_safe(f'<img src="{obj.image.url}" width="100" />')
        return "Нет изображения"
    image_preview.short_description = 'Превью'
 
@admin.register(SavedMarketplace) 
class SavedMarketplaceAdmin(admin.ModelAdmin): 
    list_display = ['user', 'marketplace', 'saved_at'] 
    list_filter = ['saved_at', 'user', 'marketplace']

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin): 
    list_display = ['user', 'marketplace', 'created_at'] 
    list_filter = ['created_at', 'user', 'marketplace'] 
    search_fields = ['text', 'user__username']

