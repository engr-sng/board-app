# app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.new, name='new'),
    path('<int:pk>/', views.show, name='show'),
    path('<int:pk>/edit/', views.edit, name='edit'),
    path('<int:pk>/delete/', views.delete, name='delete'),
]

# 一覧表示（index）
# 個別表示（show）
# 登録画面表示（create）
# 登録処理（store）
# 更新画面表示（edit）
# 更新処理（update）
# 削除処理（destroy）

# GET	/photos	photos#index	すべての写真の一覧を表示
# GET	/photos/new	photos#new	写真を1つ作成するためのHTMLフォームを返す
# POST	/photos	photos#create	写真を1つ作成する
# GET	/photos/:id	photos#show	特定の写真を表示する
# GET	/photos/:id/edit	photos#edit	写真編集用のHTMLフォームを1つ返す
# PATCH/PUT	/photos/:id	photos#update	特定の写真を更新する
# DELETE	/photos/:id	photos#destroy	特定の写真を削除する