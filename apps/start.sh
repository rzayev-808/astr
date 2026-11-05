#!/bin/sh
# Production başlanğıc: əvvəl migration-lar, sonra ASGI server (Daphne).
# Daphne həm adi HTTP, həm də WebSocket (canlı chat) sorğularına xidmət edir.
# runserver WebSocket-i tam dəstəkləmir — ona görə production-da Daphne işlədilir.

python manage.py migrate --noinput

# PORT mühit dəyişəni ilə portu dəyişmək olar (default 80).
#daphe -b 0.0.0.0 -p "${PORT:-80}" app.asgi:application
# uvicorn WebSocket-i (canlı chat) yalnız "uvicorn[standard]" quraşdırılanda açır
# (bax: req.txt). Adi "pip install uvicorn" ilə WebSocket sorğusu 404 qaytarır.
uvicorn app.asgi:application --host 0.0.0.0 --port "${PORT:-8000}"
