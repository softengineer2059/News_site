from django.urls import path
from comments import views




urlpatterns = [
    #path('comment_like_dislike/<int:comment_id>/<str:action>/', views.comment_add_like_dislike, name='comment_like_dislike'),
    path("comment_reply/<int:article_id>/<int:parent_id>/", views.add_comment, name="reply_comment"),
    path('edit_comment/<int:comment_id>/', views.edit_comment, name='edit_comment'),
    path('remove_comment/<slug:pk>/', views.Remove_comment.as_view(), name='remove_comment'),
    path("add_comment/<int:article_id>/", views.add_comment, name="add_comment"),
    path('react_to_comment/', views.react_to_comment, name='react_to_comment'),
]