from django.views.generic import ListView, DetailView, DeleteView
from django.views.generic.edit import CreateView, UpdateView
from articles.models import *
from comments.models import *
from account.models import *
from articles.forms import *
from django.db.models.signals import pre_save
from django.dispatch import receiver
from slugify import slugify
from django.db.models import Q
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.http import HttpResponseRedirect
import os
from django.db.models.signals import post_delete
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect
from django.db.models import Count, Case, When, IntegerField
from django.shortcuts import get_object_or_404
from django.core.files.storage import default_storage
from django.contrib import messages




class Main(ListView):

    model = Article
    template_name = 'main_page.html'
    context_object_name = 'articles'

    paginate_by = 9

    def get_queryset(self):
        get_search = self.request.GET.get("search")
        get_category = self.request.GET.get("category")
        get_subcategory = self.request.GET.get("subcategory")
        get_ordering = self.request.GET.get("orderby", "-created_at")
        get_country = self.request.GET.get("country")

        # Оптимизация запросов с select_related и prefetch_related
        base_queryset = Article.objects.select_related(
            'category', 'subcategory', 'country', 'author'
        ).prefetch_related('tags', 'images')

        if get_search:
            queryset = base_queryset.filter(Q(content__icontains=get_search) |
                                              Q(short_description__icontains=get_search) |
                                              Q(title__icontains=get_search)).order_by(get_ordering)
        elif get_category:
            queryset = base_queryset.filter(category=get_category).order_by(get_ordering)
        elif get_subcategory:
            queryset = base_queryset.filter(subcategory=get_subcategory).order_by(get_ordering)
        elif get_country:
            country = get_object_or_404(Country, slug=get_country)
            queryset = base_queryset.filter(country=country).order_by(get_ordering)
        else:
            queryset = base_queryset.all().order_by(get_ordering)

        return queryset

    def get_context_data(self, **kwargs):
        #articles = Article.objects.prefetch_related('tags').all() Это предотвратит проблему N+1 запросов при обращении к тегам каждой статьи в цикле.
        context = super().get_context_data(**kwargs)

        context['country_list'] = Country.objects.all()
        context['current_category_id'] = self.request.GET.get('category', '')
        return context

    def get_paginate_by(self, queryset):
        return self.request.GET.get('paginate_by', self.paginate_by)


class ArticleDetailView(DetailView):
    model = Article
    template_name = 'article_details.html'
    context_object_name = 'article'
    slug_field = 'slug'# поле для поиска по slug (если используете)
    slug_url_kwarg = 'slug'# параметр из URL (если используете)
    # или можно использовать pk_url_kwarg = 'pk' для поиска по ID

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем текущую статью (self.object уже содержит загруженный объект)
        current_article = self.object

        # Получаем все комментарии к статье и аннотируем их счетчиками лайков и дизлайков
        comments = self.object.comments.select_related('user').prefetch_related('replies').filter(parent=None).annotate(
            likes_count=Count(
                Case(
                    When(commentreaction__reaction=CommentReaction.LIKE, then=1),
                    output_field=IntegerField(),
                )
            ),
            dislikes_count=Count(
                Case(
                    When(commentreaction__reaction=CommentReaction.DISLIKE, then=1),
                    output_field=IntegerField(),
                )
            )
        )

        comments_count = comments.count()

        # Получаем всех пользователей, оставивших комментарии
        comment_users = [comment.user for comment in comments]
        # Получаем аватары для этих пользователей
        user_avatars = Profile.objects.filter(user__in=comment_users)
        # Создаем словарь {user_id: avatar_url} для удобного доступа
        avatars_dict = {profile.user.id: profile.avatar.url if profile.avatar else '' for profile in user_avatars}

        context['comments'] = comments
        context['comments_count'] = comments_count
        context['avatars_dict'] = avatars_dict

        return context

    def get_object(self, queryset=None): # Вызов метода модели для подсчета количества просмотров
        obj = super().get_object(queryset)
        obj.increment_views(self.request)  # С защитой от накрутки
        return obj


class ArticleCreateView(PermissionRequiredMixin, LoginRequiredMixin, CreateView):
    model = Article
    form_class = ArticleForm  # или fields = '__all__' (если нет формы)
    template_name = 'create_article.html'  # путь к шаблону
    success_url = reverse_lazy('main')  # куда перенаправить после успеха
    permission_required = 'articles.add_article'

    def handle_no_permission(self):
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_select'] = Category.objects.values('id', 'name')
        context['subcategory_select'] = {i['id']: list(Subcategory.objects.filter(category_name=i['id']).values('id', 'name')) for i in context['category_select']}
        context['country_select'] = Country.objects.values('id', 'name')
        context['tags'] = Tag.objects.values('id', 'name')
        return context

    def form_valid(self, form):
        article = form.save(commit=False)
        form.instance.author = self.request.user  # автоматически назначаем автора
        article.save()

        images = self.request.FILES.getlist('images')
        if images:
            for img in images:
                ArticleImage.objects.create(article=article, image=img)

        if not form.instance.slug:
            form.instance.slug = slugify(form.instance.tittle)

        return super().form_valid(form)


class ArticleEditView(PermissionRequiredMixin, LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Article
    form_class = ArticleForm  # или fields = [...]
    template_name = 'edit_article.html'
    success_url = reverse_lazy('main')
    permission_required = 'articles.edit_article'

    def handle_no_permission(self):
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Получаем текущий объект (публикацию)
        current_post = self.object

        context['category_select'] = Category.objects.values('id', 'name')
        context['subcategory_select'] = {i['id']: list(Subcategory.objects.filter(category_name=i['id']).values('id', 'name')) for i in context['category_select']}
        context['editable_article_images'] = [u for u in ArticleImage.objects.filter(article=current_post.id).values_list('id', 'image')]
        context['tags'] = Tag.objects.values('id', 'name')
        context['country_select'] = Country.objects.values('id', 'name')

        # Добавляем текущие теги статьи в форму
        if self.request.method == 'GET':
            context['form'].fields['tags'].initial = current_post.tags.values_list('id', flat=True)

        return context

    def form_valid(self, form):
        article = form.save(commit=False)
        form.instance.author = self.request.user  # автоматически назначаем автора
        article.save()

        images = self.request.FILES.getlist('images')
        if images:
            for img in images:
                ArticleImage.objects.create(article=article, image=img)

        if not form.instance.slug:
            form.instance.slug = slugify(form.instance.tittle)

        return super().form_valid(form)

    def test_func(self):
        article = self.get_object()
        return self.request.user == article.author or self.request.user.is_staff  # Проверка прав


class Delete_article(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):

    model = Article
    permission_required = 'articles.delete_article'
    success_url = reverse_lazy('main')

    def handle_no_permission(self):
        return super().handle_no_permission()


class Delete_article_image(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):

    model = ArticleImage
    permission_required = 'articles.delete_article'

    def handle_no_permission(self):
        return JsonResponse({'success': False, 'error': 'Доступ запрещен'}, status=403)

    def get_success_url(self):
        # На страницу редактирования статьи
        #return self.request.META.get('HTTP_REFERER', '/')
        return reverse('edit_article', kwargs={'slug': self.object.article.slug})

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        article_id = self.object.article.id
        self.object.delete()

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'html': self.get_updated_images_html(request, article_id)
            })
        else:
            # Для не-AJAX запросов выполняем стандартное поведение
            return HttpResponseRedirect(self.get_success_url())

    def get_updated_images_html(self, request, article_id):
        """Генерирует HTML списка изображений после удаления."""
        images = ArticleImage.objects.filter(article_id=article_id)
        return render_to_string('article_images_list.html', {
            'editable_article_images': [(img.id, img.image) for img in images]
        }, request=request)


@receiver(post_delete, sender=ArticleImage)
def delete_product_image(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


#------------------------------------------CRUD категории--------------------------------------
class Category_list(PermissionRequiredMixin, LoginRequiredMixin, ListView):

    model = Category
    context_object_name = 'data'
    template_name = 'category_list.html'
    permission_required = 'articles.view_category'

    def handle_no_permission(self):
        return super().handle_no_permission()


@permission_required('articles.add_category', raise_exception=True)
@login_required
def create_article_category(request):
    category_name = request.POST.get("name")
    category_slug = request.POST.get("slug")

    if category_name:
        image = request.FILES.get('image')

        try:
            if image:
                category = Category(name=category_name, slug=category_slug, image=image)
            else:
                category = Category(name=category_name, slug=category_slug)

            category.save()
            # Добавьте сообщение об успехе
            messages.success(request, 'Категория успешно создана')

        except Exception as e:
            # Добавьте сообщение об ошибке
            messages.error(request, f'Ошибка при создании категории: {str(e)}')
    else:
        messages.error(request, 'Заполните все обязательные поля')

    return redirect('category_list')


class Delete_category(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):

    model = Category
    success_url = reverse_lazy('category_list')
    permission_required = 'articles.delete_category'

    def handle_no_permission(self):
        return super().handle_no_permission()


@login_required
@permission_required('change_category', raise_exception=True)
def edit_category(request, category_id):
    editable_category = get_object_or_404(Category, id=category_id)
    current_url = request.META.get('HTTP_REFERER', '/')

    if request.method == "POST":
        editable_category.name = request.POST.get("name")
        editable_category.slug = request.POST.get("slug")
        if editable_category.image:
            default_storage.delete(editable_category.image.path)

        editable_category.image = request.FILES.get("image")
        editable_category.save()
        return redirect(current_url)


@receiver(post_delete, sender=Category)
def delete_category_image(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

#------------------------------------------CRUD подкатегории--------------------------------------

class Subcategory_list(PermissionRequiredMixin, LoginRequiredMixin, ListView):

    model = Subcategory
    context_object_name = "data"
    template_name = 'subcategory_list.html'
    permission_required = 'articles.view_subcategory'

    def handle_no_permission(self):
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = Category.objects.values('id', 'name')
        return context


@permission_required('articles.add_subcategory', raise_exception=True)
@login_required
def create_article_subcategory(request):
    subcategory_name = request.POST.get("name")
    subcategory_slug = request.POST.get("slug")
    category = Category.objects.get(id=int(request.POST.get("category")))
    if subcategory_name:
        subcategory = Subcategory(name=subcategory_name, slug=subcategory_slug, category_name=category)
        subcategory.save()
        return redirect('subcategory_list')
    else:
        return redirect('subcategory_list')


class Delete_subcategory(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):

    model = Subcategory
    success_url = reverse_lazy('subcategory_list')
    permission_required = 'articles.delete_subcategory'

    def handle_no_permission(self):
        return super().handle_no_permission()


@login_required
@permission_required('change_subcategory', raise_exception=True)
def edit_subcategory(request, subcategory_id):
    editable_subcategory = get_object_or_404(Subcategory, id=subcategory_id)
    current_url = request.META.get('HTTP_REFERER', '/')

    if request.method == "POST":
        editable_subcategory.name = request.POST.get("name")
        editable_subcategory.slug = request.POST.get("slug")
        editable_subcategory.category_name = Category.objects.get(id=int(request.POST.get("category")))
        editable_subcategory.save()
        return redirect(current_url)


#------------------------------------------CRUD теги--------------------------------------
class Tags_list(PermissionRequiredMixin, LoginRequiredMixin, ListView):

    model = Tag
    context_object_name = 'data'
    template_name = 'tags_list.html'
    permission_required = 'articles.view_tag'

    def handle_no_permission(self):
        return super().handle_no_permission()


@permission_required('articles.add_tag', raise_exception=True)
@login_required
def create_article_tag(request):
    tag_name = request.POST.get("name")
    tag_slug = request.POST.get("slug")
    if tag_name:
        tag = Tag(name=tag_name, slug=tag_slug)
        tag.save()
        return redirect('tags_list')
    else:
        return redirect('tags_list')


class Delete_tag(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):

    model = Tag
    success_url = reverse_lazy('tags_list')
    permission_required = 'articles.delete_tag'

    def handle_no_permission(self):
        return super().handle_no_permission()


@login_required
@permission_required('change_tag', raise_exception=True)
def edit_tag(request, tag_id):
    editable_tag = get_object_or_404(Tag, id=tag_id)
    current_url = request.META.get('HTTP_REFERER', '/')

    if request.method == "POST":
        editable_tag.name = request.POST.get("name")
        editable_tag.slug = request.POST.get("slug")
        editable_tag.save()
        return redirect(current_url)


#------------------------------------------CRUD страны--------------------------------------
class Country_list(PermissionRequiredMixin, LoginRequiredMixin, ListView):

    model = Country
    context_object_name = 'data'
    template_name = 'country_list.html'
    permission_required = 'articles.view_country'

    def hadle_no_permission(self):
        return super().handle_no_permission()


@permission_required('articles.add_country', raise_exception=True)
@login_required
def create_article_country(request):
    country_name = request.POST.get('name')
    country_slug = request.POST.get('slug')
    if country_name:
        country = Country(name=country_name, slug=country_slug)
        country.save()
        return redirect('country_list')
    else:
        return redirect('country_list')


class Delete_country(PermissionRequiredMixin, LoginRequiredMixin, DeleteView):

    model = Country
    success_url = reverse_lazy('country_list')
    permission_required = 'articles.delete_country'


@login_required
@permission_required('change_country', raise_exception=True)
def edit_country(request, country_id):
    editable_country = get_object_or_404(Country, id=country_id)
    current_url = request.META.get('HTTP_REFERER', '/')

    if request.method == "POST":
        editable_country.name = request.POST.get("name")
        editable_country.slug = request.POST.get("slug")
        editable_country.save()
        return redirect(current_url)


#------------------------------------------Генерация слагов(url)--------------------------------------
@receiver(pre_save, sender=Article)# Для автоматического создания слагов если не введен вручную (срабатывает сам когда происходит запись в указанную базу)
def generate_article_slug(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)


@receiver(pre_save, sender=Category)
def generate_category_slug(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)


@receiver(pre_save, sender=Subcategory)
def generate_subcategory_slug(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)


@receiver(pre_save, sender=Tag)
def generate_tag_slug(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)


@receiver(pre_save, sender=Country)
def generate_country_slug(sender, instance, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.name)