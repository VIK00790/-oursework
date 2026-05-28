from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Marketplace, Tag, SavedMarketplace, Comment
from .forms import CommentForm

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

    tag_id = request.GET.get('tag', '')
    all_tags = Tag.objects.all().order_by('name')
    if tag_id:
        try:
            tag_id = int(tag_id)  # ← Преобразуем в число
            marketplaces = marketplaces.filter(tags__id=tag_id).distinct()  # ← distinct() убирает дубли
        except (ValueError, TypeError):
            pass
    
    #Пагинация
    paginator = Paginator(marketplaces, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'query': query,
        'current_sort': sort_by,
        'selected_tag': tag_id,
        'all_tags': all_tags,
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