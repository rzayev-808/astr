module.exports = {
  apps: [{
    name: "astr-daphne",
    script: "/root/astr/env/bin/daphne",
    args: "-b 0.0.0.0 -p 80 app.asgi:application",
    interpreter: "none",
    cwd: "/root/astr/apps",
    env: {
      DJANGO_SETTINGS_MODULE: "app.settings",
      PYTHONPATH: "/root/astr/apps",   // <-- əsas düzəliş budur
      PORT: "80"
    },
    autorestart: true,
    watch: false,
    max_restarts: 45,
    min_uptime: "10s",
    restart_delay: 3000,
    max_memory_restart: "500M",
    error_file: "/root/astr/logs/err.log",
    out_file: "/root/astr/logs/out.log",
    time: true
  }]
}
