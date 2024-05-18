# app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Board, Comment, Favorite
from .forms import BoardForm, SignUpForm, CommentForm, FavoriteForm, ContactForm
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from functools import wraps
from django.http import JsonResponse
from django.db.models import Count
from django.db import models
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.core.paginator import Paginator
from django.contrib import messages

def user_owns_board(view_func):
    @wraps(view_func)
    def wrapper(request, pk):
        board = get_object_or_404(Board, pk=pk)
        if board.user == request.user:
            return view_func(request, pk)
        else:
            return redirect('index')
    return wrapper

def index(request):
    user = request.user

    if user.is_authenticated:
        boards_query = Board.objects.annotate(is_favorite=Count('favorite', filter=models.Q(favorite__user=user))).order_by('-updated_at')
    else:
        boards_query = Board.objects.all().order_by('-updated_at')

    paginator = Paginator(boards_query, 10)
    page_number = request.GET.get('page')
    boards = paginator.get_page(page_number)

    return render(request, 'index.html', {'boards': boards})

@login_required
def new(request):
    form = BoardForm()
    return render(request, 'new.html', {'form': form})

@login_required
def create(request):
    if request.method == 'POST':
        form = BoardForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            messages.success(request, '投稿が成功しました！')
            return redirect('index')
        else:
            messages.error(request, '入力内容にエラーがあります。')
    else:
        form = BoardForm()
    return render(request, 'new.html', {'form': form})

@login_required
def show(request, pk):
    board = Board.objects.get(pk=pk)
    comments = Comment.objects.filter(board=pk).order_by('-created_at')
    comment_form = CommentForm()
    return render(request, 'show.html', {'board': board, 'comments': comments, 'comment_form': comment_form})

@login_required
@user_owns_board
def edit(request, pk):
    board = Board.objects.get(pk=pk)
    form = BoardForm(instance=board)
    return render(request, 'edit.html', {'form': form, 'board': board})

@login_required
@user_owns_board
def update(request, pk):
    board = Board.objects.get(pk=pk)
    if request.method == 'POST':
        form = BoardForm(request.POST, instance=board)
        if form.is_valid():
            form.save()
            return redirect('show', pk=pk)
    else:
        form = BoardForm(instance=board)
    return render(request, 'edit.html', {'form': form, 'board': board})

@login_required
@user_owns_board
def delete(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.method == 'POST':
        board.delete()
        return redirect('index')
    return redirect('index', pk=pk)

@login_required
def my_boards(request):
    user = request.user
    boards = user.boards.all()
    return render(request, 'my_boards.html', {'boards': boards})

@login_required
def comment_create(request, pk):
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment_form.instance.user = request.user
            comment_form.instance.board_id = pk
            comment = comment_form.save()

        # 掲示板所有者とお気に入りに登録しているユーザーにメール通知
        favorite_users = Board.objects.get(pk=pk).favorited_by.values_list('email', flat=True)
        recipient_list = [Board.objects.get(pk=pk).user.email] + list(favorite_users)
        subject = '新しいコメントが投稿されました。'
        message = render_to_string('mail/comment_notification_email.html', {
            'title': Board.objects.get(pk=pk).title,
            'url': 'http://127.0.0.1:8000/'+ str(pk) + '/',
            'user': request.user.username,
            'comment': comment.content,
        })
        email = EmailMessage(subject, message, settings.EMAIL_HOST_USER, [], bcc=recipient_list)
        email.send()

    return redirect('show', pk=pk)

@login_required
def comment_delete(request, board_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)

    if request.user == comment.user:
        comment.delete()

    return redirect('show', pk=board_pk)

def board_search(request):
    query = request.GET.get('query')
    search_type = request.GET.get('search_type')
    boards = Board.objects.all()

    if search_type == 'prefix':
        # 前方一致
        boards = boards.filter(title__startswith=query)
    elif search_type == 'suffix':
        # 後方一致
        boards = boards.filter(title__endswith=query)
    elif search_type == 'partial':
        # 部分一致
        boards = boards.filter(title__icontains=query)
    else:
        # デフォルトは部分一致
        boards = boards.filter(title__icontains=query)

    return render(request, 'index.html', {'boards': boards})

def board_sort(request):
    sort_by = request.GET.get('sort')
    direction = request.GET.get('direction')

    # 次のソート順を制御
    if direction == 'asc':
        next_direction = 'desc'
    else:
        next_direction = 'asc'

    # ソート順をクエリパラメーターで制御
    if sort_by:
        if direction == 'desc':
            boards = Board.objects.all().order_by(f'-{sort_by}')
        else:
            boards = Board.objects.all().order_by(sort_by)
    else:
        boards = Board.objects.all()  # デフォルトのソート順

    context = {
        'boards': boards,
        'sort_by': sort_by,
        'direction': direction,
        'next_direction': next_direction
    }
    return render(request, 'index.html', context)

@login_required
def add_favorite(request):
    if request.method == 'POST':
        form = FavoriteForm(request.POST)
        if form.is_valid():
            form.instance.user = request.user
            form.save()
            return JsonResponse({'status': 'ok', 'is_favorite': True})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

@login_required
def remove_favorite(request):
    if request.method == 'POST':
        try:
            favorite = Favorite.objects.get(user=request.user, board=request.POST.get('board'))
            favorite.delete()
            return JsonResponse({'status': 'ok', 'is_favorite': False})
        except Favorite.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Favorite not found'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            contact = form.save()

            # ユーザーへのメール
            user_subject = 'お問い合わせを受け付けました'
            user_message = 'お問い合わせ内容：\n\n{}'.format(contact.message)
            send_mail(user_subject, user_message, settings.EMAIL_HOST_USER, [contact.email])

            # 運営者へのメール
            admin_subject = '新しいお問い合わせがありました'
            admin_message = 'お問い合わせ内容：\n\n{}'.format(contact.message)
            send_mail(admin_subject, admin_message, settings.EMAIL_HOST_USER, [settings.EMAIL_HOST_USER])

            return redirect('contact_success')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})

def contact_success(request):
    return render(request, 'contact_success.html')

# ログインページのビュー
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        # ログインに成功した場合の処理
        messages.success(self.request, 'ログインに成功しました。')
        return super().form_valid(form)

    def form_invalid(self, form):
        # ログインに失敗した場合の処理
        messages.error(self.request, 'ログインに失敗しました。ユーザー名とパスワードを確認してください。')
        return super().form_invalid(form)

# ログアウト
def logout_view(request):
    logout(request)
    messages.success(request, 'ログアウトに成功しました。')
    return redirect('index')

# サインアップページのビュー
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'サインアップに成功しました。')
            return redirect('login')
        else:
            messages.error(request, '入力内容にエラーがあります。')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

# プロフィールページのビュー
@login_required
def profile(request):
    user = request.user
    context = {
        'user': user
    }
    return render(request, 'accounts/profile.html', context)

