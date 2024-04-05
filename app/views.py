# app/views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import Board
from .forms import BoardForm
from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

def index(request):
    boards = Board.objects.all().order_by('-updated_at')
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
            form.save()
            return redirect('index')
    else:
        form = BoardForm()
    return render(request, 'new.html', {'form': form})

@login_required
def show(request, pk):
    board = Board.objects.get(pk=pk)
    return render(request, 'show.html', {'board': board})

@login_required
def edit(request, pk):
    board = Board.objects.get(pk=pk)
    form = BoardForm(instance=board)
    return render(request, 'edit.html', {'form': form, 'board': board})

@login_required
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
def delete(request, pk):
    board = get_object_or_404(Board, pk=pk)
    if request.method == 'POST':
        board.delete()
        return redirect('index')
    return redirect('show', pk=pk)

# ログインページのビュー
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'

# ログアウト
def logout_view(request):
    logout(request)
    return redirect('index')

# サインアップページのビュー
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # サインアップ成功時はログインページにリダイレクト
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

# プロフィールページのビュー
@login_required
def profile(request):
    user = request.user
    context = {
        'user': user
    }
    return render(request, 'accounts/profile.html', context)