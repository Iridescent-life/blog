from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone


class Tag(models.Model):
    name = models.CharField("标签名称", max_length=50, unique=True)
    slug = models.SlugField("标签标识", max_length=64, unique=True)
    description = models.TextField("标签说明", blank=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "标签"
        verbose_name_plural = "标签"

    def __str__(self) -> str:
        return self.name


class PostQuerySet(models.QuerySet):
    def published(self):
        now = timezone.now()
        return self.filter(status=Post.Status.PUBLISHED).filter(
            Q(published_at__isnull=True) | Q(published_at__lte=now)
        )

    def posts(self):
        return self.filter(post_type=Post.PostType.POST)

    def digests(self):
        return self.filter(post_type=Post.PostType.DIGEST)


class Post(models.Model):
    class PostType(models.TextChoices):
        POST = "post", "文章"
        DIGEST = "digest", "日报"

    class Status(models.TextChoices):
        DRAFT = "draft", "草稿"
        PUBLISHED = "published", "已发布"

    title = models.CharField("标题", max_length=200)
    slug = models.SlugField("链接标识", max_length=220, unique=True)
    summary = models.CharField("摘要", max_length=300, blank=True)
    content = models.TextField("正文")
    cover_image = models.ImageField("封面图", upload_to="covers/%Y/%m/", blank=True, null=True)

    seo_title = models.CharField("SEO 标题", max_length=255, blank=True)
    seo_description = models.CharField("SEO 描述", max_length=320, blank=True)
    seo_keywords = models.CharField("SEO 关键词", max_length=255, blank=True)

    post_type = models.CharField("内容类型", max_length=20, choices=PostType.choices, default=PostType.POST)
    status = models.CharField("发布状态", max_length=20, choices=Status.choices, default=Status.DRAFT)
    tags = models.ManyToManyField(Tag, related_name="posts", blank=True, verbose_name="标签")
    allow_comments = models.BooleanField("允许评论", default=True)

    published_at = models.DateTimeField("发布时间", blank=True, null=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    objects = PostQuerySet.as_manager()

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = "文章"
        verbose_name_plural = "文章"

    def __str__(self) -> str:
        return self.title

    @property
    def meta_title(self):
        return self.seo_title or self.title

    @property
    def meta_description(self):
        return self.seo_description or self.summary or self.content[:160]

    @property
    def meta_keywords(self):
        return self.seo_keywords

    def get_absolute_url(self):
        if self.post_type == self.PostType.DIGEST:
            return reverse("blog:digest_detail", kwargs={"slug": self.slug})
        return reverse("blog:post_detail", kwargs={"slug": self.slug})


class CommentQuerySet(models.QuerySet):
    def approved(self):
        return self.filter(status=Comment.Status.APPROVED)


class Comment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "待审核"
        APPROVED = "approved", "已通过"
        SPAM = "spam", "垃圾"

    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE, verbose_name="所属文章")
    name = models.CharField("昵称", max_length=80)
    email = models.EmailField("邮箱")
    website = models.URLField("网站", blank=True)
    content = models.TextField("评论内容", max_length=2000)
    status = models.CharField("审核状态", max_length=20, choices=Status.choices, default=Status.PENDING)
    ip_address = models.GenericIPAddressField("IP 地址", blank=True, null=True)
    created_at = models.DateTimeField("创建时间", auto_now_add=True)
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    objects = CommentQuerySet.as_manager()

    class Meta:
        ordering = ["created_at"]
        verbose_name = "评论"
        verbose_name_plural = "评论"

    def __str__(self) -> str:
        return f"{self.name} - {self.post.title}"


class SiteSetting(models.Model):
    site_name = models.CharField("站点名称", max_length=120, default="DeepAI Blog")
    site_tagline = models.CharField("站点副标题", max_length=180, default="个人技术博客与 AI 日报")
    brand_text = models.CharField("顶部品牌文案", max_length=120, default="DeepAI Blog")
    admin_link_text = models.CharField("后台入口文案", max_length=40, default="管理后台")
    meta_description_default = models.CharField(
        "默认 Meta 描述", max_length=320, default="个人技术博客与 AI 日报"
    )
    meta_keywords_default = models.CharField(
        "默认 Meta 关键词", max_length=255, default="ai,blog,django"
    )

    profile_name = models.CharField("侧栏昵称", max_length=80, default="Yuxia")
    profile_role = models.CharField("侧栏角色", max_length=120, default="AI 工程师 / 创作者")
    profile_description = models.CharField(
        "侧栏简介", max_length=255, default="记录 AI、编程、自动化和个人产品实践。"
    )

    home_hero_title = models.CharField("首页主标题", max_length=255, default="个人技术博客 + AI 日报")
    home_hero_subtitle = models.CharField(
        "首页副标题", max_length=255, default="分享开发经验、产品实验和 AI 领域一线动态。"
    )
    home_posts_title = models.CharField("首页文章区标题", max_length=80, default="最新文章")
    home_posts_more_text = models.CharField("首页文章区“更多”文案", max_length=40, default="查看全部")
    home_posts_empty_text = models.CharField("首页文章区空状态文案", max_length=80, default="还没有发布文章。")
    home_digest_title = models.CharField("首页日报区标题", max_length=80, default="最新日报")
    home_digest_more_text = models.CharField("首页日报区“更多”文案", max_length=40, default="查看全部")
    home_digest_empty_text = models.CharField("首页日报区空状态文案", max_length=80, default="还没有发布日报。")

    posts_title = models.CharField("文章列表页标题", max_length=80, default="文章")
    posts_hint = models.CharField("文章列表页说明", max_length=180, default="技术实践、开发总结与项目复盘")
    posts_empty_text = models.CharField("文章列表页空状态文案", max_length=80, default="暂无内容。")
    digest_title = models.CharField("日报列表页标题", max_length=80, default="AI 日报")
    digest_hint = models.CharField("日报列表页说明", max_length=180, default="每日 AI 新闻与关键信息速览")
    digest_empty_text = models.CharField("日报列表页空状态文案", max_length=80, default="暂无内容。")

    tags_title = models.CharField("标签页标题", max_length=80, default="标签")
    tags_hint = models.CharField("标签页说明", max_length=180, default="按主题快速浏览内容")
    tags_empty_text = models.CharField("标签页空状态文案", max_length=80, default="暂无标签。")
    archives_title = models.CharField("归档页标题", max_length=80, default="归档")
    archives_empty_text = models.CharField("归档页空状态文案", max_length=80, default="暂无归档内容。")

    search_title = models.CharField("搜索页标题", max_length=80, default="搜索")
    search_hint = models.CharField("搜索页说明", max_length=180, default="搜索任意文章内容")
    search_placeholder = models.CharField(
        "搜索输入框占位文案", max_length=120, default="输入标题、摘要或正文关键词"
    )
    search_button_text = models.CharField("搜索按钮文案", max_length=30, default="搜索")
    search_empty_text = models.CharField("搜索页空状态文案", max_length=80, default="没有找到匹配内容。")

    about_title = models.CharField("关于页标题", max_length=80, default="关于我")
    about_subtitle = models.CharField(
        "关于页副标题", max_length=180, default="专注 AI 应用开发、自动化工作流和独立产品构建。"
    )
    about_body_1 = models.CharField(
        "关于页正文段落一", max_length=255, default="这个博客用于记录开发实践、项目反思和 AI 领域的新动态。"
    )
    about_body_2 = models.CharField(
        "关于页正文段落二", max_length=255, default="如果你想交流合作，欢迎通过 Email 联系。"
    )

    comments_title = models.CharField("评论区标题", max_length=40, default="评论")
    comments_empty_text = models.CharField(
        "评论区空状态文案", max_length=120, default="还没有评论，欢迎来抢沙发。"
    )
    comments_submit_text = models.CharField("评论提交按钮文案", max_length=80, default="提交评论（需审核）")
    comments_closed_text = models.CharField("评论关闭提示文案", max_length=80, default="该文章已关闭评论。")

    footer_left_text = models.CharField("页脚左侧文案", max_length=120, default="© {year} DeepAI Blog")
    footer_right_text = models.CharField("页脚右侧文案", max_length=120, default="基于 Django 构建")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "站点配置"
        verbose_name_plural = "站点配置"

    def __str__(self) -> str:
        return f"站点配置 #{self.pk}"

    @classmethod
    def get_solo(cls):
        setting, _ = cls.objects.get_or_create(pk=1)
        return setting


class NavigationItem(models.Model):
    label = models.CharField("导航文案", max_length=40)
    url = models.CharField("导航链接", max_length=255)
    sort_order = models.PositiveIntegerField("排序", default=100)
    open_in_new_tab = models.BooleanField("新窗口打开", default=False)
    is_enabled = models.BooleanField("是否启用", default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "导航项"
        verbose_name_plural = "导航项"

    def __str__(self) -> str:
        return self.label


class SocialLink(models.Model):
    label = models.CharField("社交文案", max_length=40)
    url = models.CharField("社交链接", max_length=255)
    sort_order = models.PositiveIntegerField("排序", default=100)
    open_in_new_tab = models.BooleanField("新窗口打开", default=True)
    is_enabled = models.BooleanField("是否启用", default=True)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "社交链接"
        verbose_name_plural = "社交链接"

    def __str__(self) -> str:
        return self.label
