# AI Blog System

一个可用于生产环境的 Django 博客系统，含后台管理、内容模块配置、评论审核、SEO 与封面图。

## 生产配置项

项目通过环境变量控制生产配置，示例见 `.env.example`。

必须配置：

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=False`
- `DJANGO_ALLOWED_HOSTS`
- `DJANGO_CSRF_TRUSTED_ORIGINS`
- 数据库配置（推荐 PostgreSQL）：`DB_ENGINE=postgres`、`DB_NAME`、`DB_USER`、`DB_PASSWORD`、`DB_HOST`、`DB_PORT`

建议配置：

- `DJANGO_SECURE_SSL_REDIRECT=True`
- `DJANGO_SESSION_COOKIE_SECURE=True`
- `DJANGO_CSRF_COOKIE_SECURE=True`
- `DJANGO_SECURE_HSTS_SECONDS=31536000`

## 本地开发

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo_data
python manage.py runserver
```

## 生产部署流程（Ubuntu 22.04）

### 1. 安装基础环境

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-dev build-essential nginx postgresql postgresql-contrib
```

### 2. 创建目录并拉取代码

```bash
sudo mkdir -p /srv/blog
sudo chown -R $USER:$USER /srv/blog
cd /srv/blog
git clone https://github.com/Iridescent-life/blog.git .
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入真实值
nano .env
```

### 4. 配置 PostgreSQL

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE blogdb;
CREATE USER bloguser WITH PASSWORD 'replace-with-strong-password';
GRANT ALL PRIVILEGES ON DATABASE blogdb TO bloguser;
\q
```

### 5. 初始化 Django

```bash
cd /srv/blog
source .venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
python manage.py seed_demo_data
python manage.py check --deploy
```

### 6. 配置 Gunicorn(systemd)

```bash
sudo cp deploy/systemd/blog.service /etc/systemd/system/blog.service
sudo systemctl daemon-reload
sudo systemctl enable --now blog
sudo systemctl status blog
```

### 7. 配置 Nginx

```bash
sudo cp deploy/nginx/blog.conf /etc/nginx/sites-available/blog
sudo ln -sf /etc/nginx/sites-available/blog /etc/nginx/sites-enabled/blog
sudo nginx -t
sudo systemctl restart nginx
```

### 8. 配置 HTTPS（Certbot）

```bash
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d blog.example.com
```

## 发布更新操作流程

每次发布执行：

```bash
cd /srv/blog
bash deploy/scripts/deploy.sh
```

脚本会自动：

1. 拉取 `origin/main`
2. 安装依赖
3. 执行迁移
4. 收集静态文件
5. 运行 `check --deploy`
6. 重启 Gunicorn 并 reload Nginx

## 运行验证

```bash
python manage.py test
python manage.py check
```
