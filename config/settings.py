import os
from pathlib import Path
import dj_database_url
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env em desenvolvimento
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("SECRET_KEY", "django-insecure-chave-padrao-dev-barbearia-oliveira")

DEBUG = os.environ.get("DEBUG", "True").lower() == "true"

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = ["https://*.onrender.com"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # App local
    "core",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


def get_database_config():
    """
    Configura o PostgreSQL (Supabase) via DATABASE_URL.
    Caso a conexão falhe no ambiente de hospedagem (ex.: URL IPv6 direta do Supabase
    no plano gratuito do Render), faz fallback automático para SQLite para evitar erro 500.
    """
    db_url = os.environ.get("DATABASE_URL", "").strip()
    if db_url:
        # Remove colchetes acidentais na senha caso existam: [senha] -> senha
        db_url = db_url.replace("[", "").replace("]", "")
        try:
            import psycopg2
            conn = psycopg2.connect(db_url, connect_timeout=4)
            conn.close()
            return dj_database_url.parse(db_url, conn_max_age=600)
        except Exception as exc:
            print(f"[AVISO] Não foi possível conectar ao DATABASE_URL ({exc}). Usando SQLite local de fallback.")

    return {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }


DATABASES = {
    "default": get_database_config(),
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

LOGIN_URL = "core:login"
LOGIN_REDIRECT_URL = "core:painel_barbeiro"
LOGOUT_REDIRECT_URL = "core:index"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
