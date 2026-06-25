from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Marketplace, Tag, SavedMarketplace, Comment
from .forms import CommentForm
from django.db.models import Q, Min, Max
from django.db import models

# Create your views here.
def index(request):
    marketplaces = Marketplace.objects.filter(is_public=True).order_by('-pub_date')

    #Пагинация
    paginator = Paginator(marketplaces, 10) # 10 статей на страниц
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render (request, 'marketplaces/index.html', {'page_obj': page_obj})

def marketplace_list(request):
    marketplaces = Marketplace.objects.filter(is_public=True)
    
    sort_by = request.GET.get('sort', 'date')
    if sort_by == 'price_low':
        marketplaces = marketplaces.order_by('price')  # Сначала дешёвые
    elif sort_by == 'price_high':
        marketplaces = marketplaces.order_by('-price')  # Сначала дорогие
    elif sort_by == 'tags':
        marketplaces = marketplaces.order_by('tags__name')  # По тегам
    elif sort_by == 'author':
        marketplaces = marketplaces.order_by('author__username')  # По автору
    else:  # date (по умолчанию)
        marketplaces = marketplaces.order_by('-pub_date')  # Сначала новые
    
    # Поиск
    query = request.GET.get('q', '')
    if query:
        marketplaces = marketplaces.filter(Q(title__icontains = query) | Q(content__icontains = query))
    
    selected_tags = request.GET.getlist('tags') # Фильтр по тегам
    if selected_tags:
        # Фильтруем по нескольким тегам (товары, у которых есть ВСЕ выбранные теги)
        for tag_id in selected_tags:
            marketplaces = marketplaces.filter(tags__id=tag_id)
        marketplaces = marketplaces.distinct()

    price_min = request.GET.get('price_min', '') # Фильтр по цене
    if price_min:
        try:
            marketplaces = marketplaces.filter(price__gte=float(price_min))
        except ValueError:
            pass

    price_max = request.GET.get('price_max', '') # Фильтр по цене
    if price_max:
        try:
            marketplaces = marketplaces.filter(price__lte=float(price_max)) 
        except ValueError:
            pass

    tag_id = request.GET.get('tag', '')
    all_tags = Tag.objects.all().order_by('name')
    
    price_range = Marketplace.objects.filter(is_public=True).aggregate(
        min_price = models.Min('price'),
        max_price = models.Max('price'),
    )

    active_filters_count = len(selected_tags)
    if price_min or price_max:
        active_filters_count += 1
    if query:
        active_filters_count += 1
    
    #Пагинация
    paginator = Paginator(marketplaces, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'query': query,
        'current_sort': sort_by,
        'selected_tags': selected_tags, 
        'all_tags': all_tags,
        'price_min': price_min,
        'price_max': price_max,
        'price_range': price_range,
        'active_filters_count': active_filters_count,
    }
    return render (request, 'marketplaces/marketplaces_list.html', context)

    

def marketplace_detail(request, pk):
    marketplace = get_object_or_404(Marketplace, pk=pk)
    comments = Comment.objects.filter(marketplace=marketplace)

    is_saved = False
    if request.user.is_authenticated:
        is_saved = SavedMarketplace.objects.filter(
            user=request.user, 
            marketplace=marketplace
        ).exists()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.marketplace = marketplace
            comment.user = request.user
            comment.save()
            return redirect('marketplace:marketplace_detail', pk=pk)
    else:
        form = CommentForm()
    
    context = {
        'marketplace': marketplace,
        'comments': comments,
        'form': form,
        'is_saved': is_saved,
    }
    return render (request, 'marketplaces/marketplace_detail.html', context)

@login_required
def save_marketplace(request, pk):
    marketplace = get_object_or_404(Marketplace, pk=pk)
    saved_marketplace, created = SavedMarketplace.objects.get_or_create( 
        user=request.user,  
        marketplace = marketplace
    )
    return redirect('marketplace:marketplace_detail', pk=pk)
    

@login_required
def unsave_marketplace(request, pk):
    marketplace = get_object_or_404(Marketplace, pk=pk)
    deleted_count, _ = SavedMarketplace.objects.filter(
        user = request.user, 
        marketplace = marketplace
    ).delete()
    return redirect('marketplace:marketplace_detail', pk=pk)

@login_required
def saved_marketplaces(request):
    saved_marketplaces = SavedMarketplace.objects.filter(user = request.user).select_related('marketplace')
    return render(request, 'marketplaces/saved_marketplaces.html', {'saved_marketplaces': saved_marketplaces})

def custom_login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data = request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                return redirect('marketplace:index')
    else:
        form = AuthenticationForm()
    
    next_url = request.GET.get('next')
    
    return render(request, 'registration/login.html', {
        'form': form,
        'next': next_url
    })
    

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import MarketplaceForm

@login_required
def profile(request):
    """Страница профиля пользователя"""
    # Товары пользователя
    user_marketplaces = Marketplace.objects.filter(author=request.user).order_by('-pub_date')
    
    # Комментарии пользователя
    user_comments = Comment.objects.filter(user=request.user).select_related('marketplace').order_by('-created_at')
    
    context = {
        'user_marketplaces': user_marketplaces,
        'user_comments': user_comments,
    }
    return render(request, 'marketplaces/profile.html', context)

@login_required
def profile_add_marketplace(request):
    """Добавление нового товара"""
    if request.method == 'POST':
        form = MarketplaceForm(request.POST, request.FILES)
        if form.is_valid():
            marketplace = form.save(commit=False)
            marketplace.author = request.user
            marketplace.save()
            form.save_m2m()  # Сохраняем теги (ManyToMany)
            messages.success(request, f'Товар «{marketplace.title}» успешно добавлен!')
            return redirect('marketplace:profile')
    else:
        form = MarketplaceForm()
    
    return render(request, 'marketplaces/profile_form.html', {
        'form': form,
        'title': 'Добавить товар',
        'action': 'Добавить',
    })

@login_required
def profile_edit_marketplace(request, pk):
    """Редактирование товара"""
    marketplace = get_object_or_404(Marketplace, pk=pk, author=request.user)
    
    if request.method == 'POST':
        form = MarketplaceForm(request.POST, request.FILES, instance=marketplace)
        if form.is_valid():
            form.save()
            messages.success(request, f'Товар «{marketplace.title}» обновлён!')
            return redirect('marketplace:profile')
    else:
        form = MarketplaceForm(instance=marketplace)
    
    return render(request, 'marketplaces/profile_form.html', {
        'form': form,
        'title': f'Редактировать: {marketplace.title}',
        'action': 'Сохранить изменения',
        'marketplace': marketplace,
    })

@login_required
def profile_delete_marketplace(request, pk):
    """Удаление товара"""
    marketplace = get_object_or_404(Marketplace, pk=pk, author=request.user)
    
    if request.method == 'POST':
        title = marketplace.title
        marketplace.delete()
        messages.success(request, f'Товар «{title}» удалён!')
        return redirect('marketplace:profile')
    
    return render(request, 'marketplaces/profile_confirm_delete.html', {
        'marketplace': marketplace,
    })

@login_required
def profile_comments(request):
    """Просмотр всех комментариев пользователя"""
    comments = Comment.objects.filter(user=request.user).select_related('marketplace').order_by('-created_at')
    return render(request, 'marketplaces/profile_comments.html', {'comments': comments})
    

from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Comment

@login_required
def profile_edit_comment(request, comment_id):
    """Редактирование своего комментария"""
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text:
            comment.text = text
            comment.save()
            messages.success(request, 'Отзыв обновлён!')
        else:
            messages.error(request, 'Комментарий не может быть пустым.')
        return redirect('marketplace:profile_comments')
    
    return render(request, 'marketplaces/profile_comment_form.html', {
        'comment': comment,
        'action': 'Сохранить изменения',
        'title': 'Редактировать отзыв',
    })

@login_required
def profile_delete_comment(request, comment_id):
    """Удаление своего комментария"""
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    
    if request.method == 'POST':
        marketplace_title = comment.marketplace.title
        comment.delete()
        messages.success(request, f'Отзыв к «{marketplace_title}» удалён!')
        return redirect('marketplace:profile_comments')
    
    return render(request, 'marketplaces/profile_comment_confirm_delete.html', {
        'comment': comment,
    })

from django.db.models import Sum, Count, Avg
from .models import Notification

@login_required
def profile_sales_stats(request):
    """Страница детальной статистики продаж"""
    user = request.user
    
    # Все товары пользователя
    user_marketplaces = Marketplace.objects.filter(author=user)
    
    # Общая статистика
    stats = {
        'total_items': user_marketplaces.count(),
        'published_items': user_marketplaces.filter(is_public=True).count(),
        'draft_items': user_marketplaces.filter(is_public=False).count(),
        'total_value': user_marketplaces.aggregate(total=Sum('price'))['total'] or 0,
        'avg_price': user_marketplaces.aggregate(avg=Avg('price'))['avg'] or 0,
        'total_saves': user_marketplaces.aggregate(
            total_saves=Count('savedmarketplace')
        )['total_saves'] or 0,
    }
    
    # Топ-5 самых популярных товаров (по добавлениям в избранное)
    top_items = user_marketplaces.annotate(
        saves_count=Count('savedmarketplace')
    ).order_by('-saves_count')[:5]
    
    # Последние добавленные товары
    recent_items = user_marketplaces.order_by('-pub_date')[:5]
    
    # Статистика по месяцам (последние 6 месяцев)
    from django.utils import timezone
    from datetime import timedelta
    
    six_months_ago = timezone.now() - timedelta(days=180)
    monthly_stats = user_marketplaces.filter(
        pub_date__gte=six_months_ago
    ).extra(
        select={'month': "strftime('%%Y-%%m', pub_date)"}
    ).values('month').annotate(
        count=Count('id'),
        total=Sum('price')
    ).order_by('month')
    
    context = {
        'stats': stats,
        'top_items': top_items,
        'recent_items': recent_items,
        'monthly_stats': list(monthly_stats),
    }
    
    return render(request, 'marketplaces/profile_sales_stats.html', context)


@login_required
def notification_list(request):
    """Список всех уведомлений пользователя"""
    notifications = Notification.objects.filter(user=request.user)
    
    # Помечаем все как прочитанные
    notifications.filter(is_read=False).update(is_read=True)
    
    return render(request, 'marketplaces/notifications.html', {
        'notifications': notifications,
    })


@login_required
def mark_notification_read(request, notification_id):
    """Отметить одно уведомление как прочитанное"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('marketplace:notifications')

@login_required
def delete_notification(request, notification_id):
    """Удаление одного уведомления"""
    notification = get_object_or_404(
        Notification, 
        id=notification_id, 
        user=request.user  # Защита: только свои уведомления
    )
    
    if request.method == 'POST':
        title = notification.title
        notification.delete()
        messages.success(request, f'Уведомление «{title}» удалено.')
        return redirect('marketplace:notifications')
    
    # Если GET-запрос, просто редиректим обратно
    return redirect('marketplace:notifications')


@login_required
def delete_all_notifications(request):
    """Удаление всех уведомлений пользователя"""
    if request.method == 'POST':
        count = Notification.objects.filter(user=request.user).count()
        Notification.objects.filter(user=request.user).delete()
        messages.success(request, f'Удалено уведомлений: {count}')
        return redirect('marketplace:notifications')
    
    return redirect('marketplace:notifications')