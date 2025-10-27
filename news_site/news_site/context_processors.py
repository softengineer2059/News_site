from account.models import *



def get_context(request):
    if request.user.is_authenticated:
        user_info = Profile.objects.get(user=request.user)
        return {'user_info': user_info}
    else:
        return {'user_info': 'nothing'}
