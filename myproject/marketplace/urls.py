from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.index, name='index'),
    path('marketplaces/', views.marketplace_list, name='marketplace_list'),
    path('marketplace/<int:pk>/', views.marketplace_detail, name='marketplace_detail'),
    path('save/<int:pk>/', views.save_marketplace, name='save_marketplace'),
    path('unsave/<int:pk>/', views.unsave_marketplace, name='unsave_marketplace'),
    path('saved/', views.saved_marketplaces, name='saved_marketplaces'),

    path('profile/', views.profile, name='profile'),
    path('profile/add/', views.profile_add_marketplace, name='profile_add'),
    path('profile/edit/<int:pk>/', views.profile_edit_marketplace, name='profile_edit'),
    path('profile/delete/<int:pk>/', views.profile_delete_marketplace, name='profile_delete'),
    path('profile/comments/', views.profile_comments, name='profile_comments'),

    path('profile/comments/edit/<int:comment_id>/', views.profile_edit_comment, name='profile_comment_edit'),
    path('profile/comments/delete/<int:comment_id>/', views.profile_delete_comment, name='profile_comment_delete'),

    path('profile/sales-stats/', views.profile_sales_stats, name='profile_sales_stats'),
    path('notifications/', views.notification_list, name='notifications'),
    path('notifications/read/<int:notification_id>/', views.mark_notification_read, name='notification_read'),
    path('notifications/delete/<int:notification_id>/', views.delete_notification, name='notification_delete'),
    path('notifications/delete-all/', views.delete_all_notifications, name='notifications_delete_all'),
]
