from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Comment, NavigationItem, Post, SiteSetting, SocialLink, Tag


class BlogViewsTests(TestCase):
    def setUp(self):
        self.tag_ai = Tag.objects.create(name="AI", slug="ai")
        self.tag_python = Tag.objects.create(name="Python", slug="python")

        now = timezone.now()
        self.post = Post.objects.create(
            title="Django 入门",
            slug="django-start",
            summary="学习 Django",
            content="Django content",
            post_type=Post.PostType.POST,
            status=Post.Status.PUBLISHED,
            published_at=now - timedelta(days=2),
        )
        self.post.tags.add(self.tag_python)

        self.digest = Post.objects.create(
            title="AI 日报 001",
            slug="ai-digest-001",
            summary="每日 AI 动态",
            content="Digest content",
            post_type=Post.PostType.DIGEST,
            status=Post.Status.PUBLISHED,
            published_at=now - timedelta(days=1),
        )
        self.digest.tags.add(self.tag_ai)

        Post.objects.create(
            title="草稿文章",
            slug="draft-post",
            summary="draft",
            content="draft",
            post_type=Post.PostType.POST,
            status=Post.Status.DRAFT,
            published_at=now,
        )

    def test_home_page_shows_latest_content(self):
        response = self.client.get(reverse("blog:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django 入门")
        self.assertContains(response, "AI 日报 001")

    def test_posts_page_only_shows_published_posts(self):
        response = self.client.get(reverse("blog:posts"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django 入门")
        self.assertNotContains(response, "AI 日报 001")
        self.assertNotContains(response, "草稿文章")

    def test_digest_page_only_shows_digest(self):
        response = self.client.get(reverse("blog:digest"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "AI 日报 001")
        self.assertNotContains(response, "Django 入门")

    def test_post_detail_is_accessible(self):
        response = self.client.get(reverse("blog:post_detail", kwargs={"slug": self.post.slug}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django content")

    def test_tags_page_and_tag_detail(self):
        tags_response = self.client.get(reverse("blog:tags"))
        self.assertEqual(tags_response.status_code, 200)
        self.assertContains(tags_response, "AI")

        tag_detail = self.client.get(reverse("blog:tag_detail", kwargs={"slug": "python"}))
        self.assertEqual(tag_detail.status_code, 200)
        self.assertContains(tag_detail, "Django 入门")
        self.assertNotContains(tag_detail, "AI 日报 001")

    def test_archives_page(self):
        response = self.client.get(reverse("blog:archives"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, str(timezone.now().year))

    def test_search(self):
        response = self.client.get(reverse("blog:search"), {"q": "Django"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Django 入门")
        self.assertNotContains(response, "AI 日报 001")

    def test_rss_feed(self):
        response = self.client.get(reverse("blog:rss"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<rss")
        self.assertContains(response, "Django 入门")

    def test_about_page(self):
        response = self.client.get(reverse("blog:about"))
        self.assertEqual(response.status_code, 200)


class BlogEnhancedFeaturesTests(TestCase):
    gif_bytes = (
        b"GIF87a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00"
        b"\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00"
        b"\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;"
    )

    def setUp(self):
        self.post = Post.objects.create(
            title="SEO 测试文章",
            slug="seo-post",
            summary="摘要文本",
            content="正文文本",
            post_type=Post.PostType.POST,
            status=Post.Status.PUBLISHED,
            published_at=timezone.now() - timedelta(hours=2),
            seo_title="自定义 SEO 标题",
            seo_description="这是一段用于测试的 SEO 描述。",
            seo_keywords="django,blog,seo",
        )

    def test_detail_page_renders_seo_meta(self):
        response = self.client.get(self.post.get_absolute_url())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "自定义 SEO 标题")
        self.assertContains(response, "这是一段用于测试的 SEO 描述。")
        self.assertContains(response, "django,blog,seo")

    def test_detail_page_renders_cover_image(self):
        self.post.cover_image = SimpleUploadedFile(
            "cover.gif", self.gif_bytes, content_type="image/gif"
        )
        self.post.save()
        response = self.client.get(self.post.get_absolute_url())
        self.assertContains(response, "post-cover")
        self.assertContains(response, "封面图")

    def test_can_submit_comment(self):
        response = self.client.post(
            reverse("blog:add_comment", kwargs={"slug": self.post.slug}),
            {
                "name": "Tester",
                "email": "tester@example.com",
                "website": "",
                "content": "这是一条评论",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.first()
        self.assertEqual(comment.status, Comment.Status.PENDING)
        self.assertEqual(comment.post, self.post)

    def test_only_approved_comments_are_visible(self):
        Comment.objects.create(
            post=self.post,
            name="A",
            email="a@example.com",
            content="已审核评论",
            status=Comment.Status.APPROVED,
        )
        Comment.objects.create(
            post=self.post,
            name="B",
            email="b@example.com",
            content="待审核评论",
            status=Comment.Status.PENDING,
        )
        response = self.client.get(self.post.get_absolute_url())
        self.assertContains(response, "已审核评论")
        self.assertNotContains(response, "待审核评论")

    def test_admin_add_post_page_has_rich_editor_and_new_fields(self):
        user_model = get_user_model()
        admin_user = user_model.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="admin123456",
        )
        self.client.force_login(admin_user)
        response = self.client.get("/admin/blog/post/add/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "blog/admin-richtext.js")
        self.assertContains(response, 'name="cover_image"')
        self.assertContains(response, 'name="seo_title"')
        self.assertContains(response, 'name="seo_description"')
        self.assertContains(response, 'name="seo_keywords"')


class SiteCustomizationTests(TestCase):
    def setUp(self):
        self.setting = SiteSetting.get_solo()
        self.setting.home_hero_title = "可配置首页标题"
        self.setting.profile_name = "Config Owner"
        self.setting.save()

        NavigationItem.objects.all().delete()
        NavigationItem.objects.create(label="Docs", url="/docs/", sort_order=1)

        SocialLink.objects.all().delete()
        SocialLink.objects.create(label="Custom", url="https://example.com", sort_order=1)

    def test_home_uses_customized_blocks(self):
        response = self.client.get(reverse("blog:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "可配置首页标题")
        self.assertContains(response, "Config Owner")
        self.assertContains(response, "Docs")
        self.assertContains(response, "Custom")
