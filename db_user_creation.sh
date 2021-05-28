#twitter db config
USER="admin"
PASS="admin"
MAIL="admin@twitter.com"
script="
from django.contrib.auth.models import User;
username = '$USER';
password = '$PASS';
email = '$MAIL';
if not User.objects.filter(username=username).exists():
  User.objects.create_superuser(username, email, password);
  print('Superuser created.');
else:
  print('Superuser creation skipped.');
"
printf "$script" | python manage.py shell

echo 'All Done!'
