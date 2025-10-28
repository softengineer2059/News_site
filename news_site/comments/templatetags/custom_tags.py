from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_likes(dictionary, key):
    return dictionary.get(key, {}).get('likes', 0)

@register.filter
def get_dislikes(dictionary, key):
    return dictionary.get(key, {}).get('dislikes', 0)