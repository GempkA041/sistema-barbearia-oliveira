# 💈 Barbearia Oliveira — Sistema de Agendamento (MVP)

Sistema web de agendamento online Mobile-First para a **Barbearia Oliveira**, desenvolvido em **Python + Django 5.0** com suporte a banco de dados **PostgreSQL (Supabase)** e configurado para deploy contínuo no **Render**.

---

## 🚀 Tecnologias e Arquitetura

- **Backend:** Python 3.12 + Django 5.0 (Padrão MVC / MVT)
- **Banco de Dados:** PostgreSQL (via Supabase em produção / SQLite em desenvolvimento local)
- **Segurança:**
  - Proteção nativa contra **SQL Injection (SQLi)** via Django ORM.
  - Proteção contra **Cross-Site Scripting (XSS)** via Auto-Escape dos Templates Django + sanitização com `strip_tags` nos formulários.
  - Proteção contra **CSRF** via `CsrfViewMiddleware` e `{% csrf_token %}`.
- **Acessibilidade e UI (Mobile-First):**
  - Alto contraste (fundo escuro `#121212` com destaque âmbar `#F59E0B` e texto branco `#FFFFFF`).
  - Áreas de toque e botões com altura mínima de `48px` (acima da recomendação WCAG de `44x44px`).

---

## 💻 Como Executar Localmente

1. **Clone o repositório e acesse a pasta:**
   ```bash
   git clone <URL_DO_SEU_REPOSITORIO>
   cd barbearia_oliveira
   ```

2. **Crie e ative o ambiente virtual:**
   ```bash
   python -m venv venv
   # No Windows:
   venv\Scripts\activate
   # No Linux/macOS:
   source venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure o arquivo `.env` (opcional para rodar com Supabase ou deixe sem para usar SQLite local):**
   ```bash
   cp .env.example .env
   ```

5. **Execute as migrações e crie o usuário do barbeiro (Admin):**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Inicie o servidor:**
   ```bash
   python manage.py runserver
   ```
   Acesse `http://127.0.0.1:8000` no navegador.

---

## ☁️ Como Fazer Deploy no Render + Supabase

1. Crie um projeto gratuito no [Supabase](https://supabase.com/), vá em **Project Settings > Database** e copie a **Connection String (URI)** (modo *Session* ou *Transaction*).
2. Suba este repositório para o seu **GitHub**.
3. No [Render](https://render.com/), clique em **New + > Web Service** e conecte seu repositório do GitHub.
4. Configure os campos:
   - **Build Command:** `pip install -r requirements.txt && python manage.py collectstatic --no-input && python manage.py migrate`
   - **Start Command:** `gunicorn config.wsgi:application`
5. Na aba **Environment**, adicione as variáveis:
   - `DATABASE_URL`: Cole a URI do Supabase (trocando `[YOUR-PASSWORD]` pela senha do banco).
   - `SECRET_KEY`: Uma frase ou hash aleatório seguro.
   - `DEBUG`: `False`
   - `ALLOWED_HOSTS`: `.onrender.com`
6. Para criar o login do barbeiro em produção, você também pode conectar o seu `.env` local apontando para a `DATABASE_URL` do Supabase e rodar `python manage.py createsuperuser`.
