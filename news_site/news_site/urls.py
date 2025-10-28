from django.contrib import admin
from django.urls import path, include
from articles import views
from django.conf import settings
from django.conf.urls.static import static




urlpatterns = [
    path('admin/', admin.site.urls),
    path('account/', include('account.urls')),
    path('comments/', include('comments.urls')),
    path('article/edit/<slug:slug>', views.ArticleEditView.as_view(), name='edit_article'),
    path('article/edit_category/<int:category_id>', views.edit_category, name='edit_category'),
    path('article/edit_subcategory/<int:subcategory_id>', views.edit_subcategory, name='edit_subcategory'),
    path('article/edit_tag/<int:tag_id>', views.edit_tag, name='edit_tag'),
    path('article/edit_country/<int:country_id>', views.edit_country, name='edit_country'),
    path('article/delete_image/<slug:pk>', views.Delete_article_image.as_view(), name='delete_image'),
    path('article/delete_article/<slug:pk>', views.Delete_article.as_view(), name='delete_article'),
    path('article/delete_category/<slug:pk>', views.Delete_category.as_view(), name='delete_category'),
    path('article/delete_subcategory/<slug:pk>', views.Delete_subcategory.as_view(), name='delete_subcategory'),
    path('article/delete_tag/<slug:pk>', views.Delete_tag.as_view(), name='delete_tag'),
    path('article/delete_country/<slug:pk>', views.Delete_country.as_view(), name='delete_country'),
    path('article/create/', views.ArticleCreateView.as_view(), name='create_article'),
    path('article/category_list/', views.Category_list.as_view(), name='category_list'),
    path('article/subcategory_list/', views.Subcategory_list.as_view(), name='subcategory_list'),
    path('article/tags_list/', views.Tags_list.as_view(), name='tags_list'),
    path('article/create_category/', views.create_article_category, name='create_art_cat'),
    path('article/create_subcategory/', views.create_article_subcategory, name='create_art_subcat'),
    path('article/create_tag/', views.create_article_tag, name='create_art_tag'),
    path('article/country_list/', views.Country_list.as_view(), name='country_list'),
    path('article/create_country', views.create_article_country, name='create_country'),
    path('article/<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    path('', views.Main.as_view(), name='main'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)