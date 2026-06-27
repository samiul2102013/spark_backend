from django.contrib.auth import get_user_model
User = get_user_model()
u = User.objects.filter(phone_number="01856669532").first()
if u:
    print(f"Found: {u.full_name} ({u.role}) is_active={u.is_active} has_pw={u.has_usable_password()}")
else:
    print("NOT FOUND")
