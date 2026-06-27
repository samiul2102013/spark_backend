import paramiko, sys
sys.stdout.reconfigure(encoding='utf-8')

host, port = '72.62.248.97', 22
user = 'root'
password = '@Admin@42Enter'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port, user, password, look_for_keys=False, allow_agent=False, timeout=30)

cmd = (
    "cd /home/tamiz/web/spark.kodevio.com/code/backend/spark_backend && "
    "docker exec spark_backend-django-1 python manage.py shell -c "
    '"from django.contrib.auth import get_user_model; '
    "User=get_user_model(); "
    "u=User.objects.filter(phone_number='01856669532').first(); "
    "print(f'Found: {u.full_name} ({u.role}) is_active={u.is_active} has_pw={u.has_usable_password()}' if u else 'NOT FOUND')"
    '" 2>&1'
)

stdin, stdout, stderr = client.exec_command(cmd)
out = stdout.read().decode('utf-8', errors='replace')
print(out[:2000])
err = stderr.read().decode('utf-8', errors='replace')
if err.strip():
    print('ERR:', err[:500])
client.close()
