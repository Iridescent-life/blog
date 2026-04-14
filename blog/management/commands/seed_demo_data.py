from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from blog.models import NavigationItem, Post, SiteSetting, SocialLink, Tag


class Command(BaseCommand):
    help = "Create demo blog data"

    def handle(self, *args, **options):
        SiteSetting.get_solo()

        if not NavigationItem.objects.exists():
            NavigationItem.objects.bulk_create(
                [
                    NavigationItem(label="文章", url="/posts/", sort_order=10),
                    NavigationItem(label="日报", url="/digest/", sort_order=20),
                    NavigationItem(label="标签", url="/tags/", sort_order=30),
                    NavigationItem(label="关于", url="/about/", sort_order=40),
                    NavigationItem(label="归档", url="/archives/", sort_order=50),
                    NavigationItem(label="搜索", url="/search/", sort_order=60),
                ]
            )

        if not SocialLink.objects.exists():
            SocialLink.objects.bulk_create(
                [
                    SocialLink(label="GitHub", url="#", sort_order=10),
                    SocialLink(label="X", url="#", sort_order=20),
                    SocialLink(label="Email", url="mailto:hello@example.com", sort_order=30),
                    SocialLink(label="RSS", url="/rss.xml", sort_order=40),
                ]
            )

        tag_names = ["AI", "Python", "Django", "Automation", "Product"]
        tags = {}
        for name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=name, slug=name.lower())
            tags[name] = tag

        now = timezone.now()

        post_defs = [
            {
                "title": "Django 博客系统实践",
                "slug": "django-blog-system-practice",
                "summary": "从零实现一个内容驱动的个人博客系统。",
                "content": "这篇文章介绍如何用 Django 构建一个可运营的博客系统。",
                "seo_title": "Django 博客系统实践：从零搭建",
                "seo_description": "使用 Django 构建一个带后台管理、标签、归档、搜索与评论的博客系统。",
                "seo_keywords": "django, blog, cms, python",
                "post_type": Post.PostType.POST,
                "status": Post.Status.PUBLISHED,
                "published_at": now - timedelta(days=4),
                "tags": ["Django", "Python"],
            },
            {
                "title": "AI 日报 #001",
                "slug": "ai-digest-001",
                "summary": "今日重点 AI 资讯与工具更新。",
                "content": "这里是 AI 日报正文，覆盖模型发布、应用案例和行业观察。",
                "seo_title": "AI 日报 #001",
                "seo_description": "每日 AI 资讯摘要，快速了解最新模型、产品与行业趋势。",
                "seo_keywords": "ai, digest, llm, news",
                "post_type": Post.PostType.DIGEST,
                "status": Post.Status.PUBLISHED,
                "published_at": now - timedelta(days=1),
                "tags": ["AI", "Product"],
            },
            {
                "title": "自动化工作流提升效率",
                "slug": "automation-workflow-efficiency",
                "summary": "如何把重复工作流程化。",
                "content": "把重复任务拆解成步骤，再交给自动化系统执行。",
                "seo_title": "自动化工作流提升效率",
                "seo_description": "从流程拆解到自动化执行，降低重复劳动并提升产出效率。",
                "seo_keywords": "automation, workflow, productivity",
                "post_type": Post.PostType.POST,
                "status": Post.Status.PUBLISHED,
                "published_at": now - timedelta(days=2),
                "tags": ["Automation", "Product"],
            },
        ]

        for item in post_defs:
            post, _ = Post.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "title": item["title"],
                    "summary": item["summary"],
                    "content": item["content"],
                    "seo_title": item["seo_title"],
                    "seo_description": item["seo_description"],
                    "seo_keywords": item["seo_keywords"],
                    "post_type": item["post_type"],
                    "status": item["status"],
                    "published_at": item["published_at"],
                },
            )
            post.tags.set([tags[name] for name in item["tags"]])

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
