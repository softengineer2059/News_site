from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import CommentForm
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseForbidden
from django.http import JsonResponse
from django.views.decorators.http import require_POST




@login_required
def add_comment(request, article_id, parent_id=None):
    article = get_object_or_404(Article, id=article_id)
    parent_comment = None

    if parent_id:
        parent_comment = get_object_or_404(Comments, id=parent_id)

    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.article = article
            comment.parent = parent_comment
            comment.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def edit_comment(request, comment_id):
    editable_comment = get_object_or_404(Comments, id=comment_id)
    context = {"comment": editable_comment}

    if editable_comment.user != request.user and not request.user.is_staff:
        return redirect(editable_comment.article.get_absolute_url())
    else:
        if request.method == "GET":
            return render(request, "edit_comment.html", context)
        elif request.method == "POST":
            editable_comment.text = request.POST.get("text")
            editable_comment.save()
            return redirect(editable_comment.article.get_absolute_url())


class Remove_comment(LoginRequiredMixin, DeleteView):

    model = Comments

    def dispatch(self, request, *args, **kwargs):
        # Получаем комментарий по ID
        comment = get_object_or_404(Comments, id=self.kwargs['pk'])

        # Проверяем, является ли пользователь автором комментария или администратором
        if comment.user != request.user and not request.user.is_staff:
            return HttpResponseForbidden("У вас нет прав для удаления этого комментария.")

        return super().dispatch(request, *args, **kwargs)

    def handle_no_permission(self):
        return super().handle_no_permission()

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER', '/')


@login_required
@require_POST
def react_to_comment(request):
    comment_id = request.POST.get('comment_id')
    reaction_type = request.POST.get('reaction')

    try:
        comment = Comments.objects.get(pk=comment_id)
        reaction = int(reaction_type)

        if reaction not in [CommentReaction.LIKE, CommentReaction.DISLIKE]:
            return JsonResponse({'status': 'error', 'message': 'Invalid reaction type'}, status=400)

        # Проверяем, есть ли уже реакция от этого пользователя
        reaction_obj, created = CommentReaction.objects.get_or_create(
            comment=comment,
            user=request.user,
            defaults={'reaction': reaction}
        )

        if not created:
            if reaction_obj.reaction == reaction:
                # Если реакция такая же - удаляем (отмена)
                reaction_obj.delete()
                action = 'removed'
            else:
                # Если реакция другая - обновляем
                reaction_obj.reaction = reaction
                reaction_obj.save()
                action = 'updated'
        else:
            action = 'added'

        # Получаем обновленные счетчики
        likes_count = CommentReaction.objects.filter(comment=comment, reaction=CommentReaction.LIKE).count()
        dislikes_count = CommentReaction.objects.filter(comment=comment, reaction=CommentReaction.DISLIKE).count()

        return JsonResponse({
            'status': 'success',
            'action': action,
            'likes_count': likes_count,
            'dislikes_count': dislikes_count
        })

    except Comments.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Comment not found'}, status=404)
    except ValueError:
        return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)