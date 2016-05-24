from django.contrib.auth.models import User

# Create your views here.

# Auth needs a Django Auth Model User
# Create a dummy one if not exists
try:
    User.objects.get(pk=2)

except User.DoesNotExist:
    user = User()
    user.username = 'dummy'
    user.save()
