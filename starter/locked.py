"""Запустить команду под именованной блокировкой на всю машину.
Зачем: синтез голоса и рендер в Chromium тяжёлые; два параллельных запуска делят GPU/память и падают
или идут втрое дольше. Блокировка ставит их в очередь.
Пример: python3 locked.py voice -- python voice/gen_omni.py
        python3 locked.py render -- python tools/render.py
Каталог файлов блокировки: $LOCK_DIR (по умолчанию /tmp); файлы называются not-a-blogger-<имя>.lock."""
import fcntl, os, re, stat, sys

USAGE = 'использование: python3 locked.py <имя> -- <команда...>   (имя: буквы, цифры, _ . -)'
if len(sys.argv) < 4 or sys.argv[2] != '--':
    sys.exit(USAGE)
name = sys.argv[1]
if not re.fullmatch(r'[a-zA-Z0-9_.-]+', name):
    sys.exit('Недопустимое имя блокировки. ' + USAGE)
cmd = sys.argv[3:]
lock_dir = os.environ.get('LOCK_DIR', '/tmp')
try:
    fd = os.open(os.path.join(lock_dir, f'not-a-blogger-{name}.lock'), os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
except OSError as e:
    sys.exit(f'Не удалось безопасно открыть блокировку: {e}')
with os.fdopen(fd, 'r+') as f:
    info = os.fstat(f.fileno())
    if info.st_uid != os.getuid() or not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
        sys.exit('Небезопасный файл блокировки: проверьте владельца и тип файла')
    fcntl.flock(f, fcntl.LOCK_EX)   # ждём, пока предыдущий держатель не отпустит
    # Replace the wrapper: signals and exit status belong to the actual command.
    # flock survives exec only if the descriptor is inherited by the worker.
    os.set_inheritable(f.fileno(), True)
    try:
        os.execvp(cmd[0], cmd)
    except OSError as e:
        sys.exit(f'Не удалось запустить команду: {e}')
