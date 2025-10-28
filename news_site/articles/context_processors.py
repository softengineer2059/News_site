from articles.models import *




def get_context(request):
    categories = Category.objects.all()
    subcategories = Subcategory.objects.all()
    popular_articles = Article.objects.order_by('-views')[:5] #.filter(is_published=True)
    return {'categories': categories, 'subcategories': subcategories, 'popular_articles': popular_articles}

