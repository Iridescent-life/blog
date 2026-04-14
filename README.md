# DeepAI Blog System

一个类似 `blog.deepai.wiki` 的个人博客系统，包含前台内容站和后台管理。

## 已实现功能

- 首页：个人简介 + 最新文章 + 最新日报
- 文章列表：`/posts/`（分页）
- 日报列表：`/digest/`（分页）
- 详情页：`/posts/<slug>/`、`/digest/<slug>/`
  - 支持封面图展示
  - 支持 SEO 标题/描述/关键词输出
- 标签页：`/tags/`、`/tags/<slug>/`
- 归档页：`/archives/`（按年月聚合）
- 搜索页：`/search/?q=关键词`
- 关于页：`/about/`
- RSS：`/rss.xml`
- 管理后台：`/admin/`
  - 文章富文本编辑器（TinyMCE）
  - 封面图上传与预览
  - 评论审核（待审/通过/垃圾）
  - 站点配置（`Site Setting`：全站功能块文案）
  - 导航配置（`Navigation Items`）
  - 社交链接配置（`Social Links`）

## 技术栈

- Django 5
- SQLite
- Django Admin（内容管理后台）

## 快速启动

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_demo_data
python manage.py runserver
```

启动后访问：

- 前台首页：http://127.0.0.1:8000/
- 管理后台：http://127.0.0.1:8000/admin/

## 测试

```bash
python manage.py test
```
