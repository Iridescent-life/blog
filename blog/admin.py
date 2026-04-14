from django import forms
from django.contrib import admin
from django.utils.html import format_html

from .models import Comment, NavigationItem, Post, SiteSetting, SocialLink, Tag


class PostAdminForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = "__all__"
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "rich-text-editor",
                    "rows": 24,
                }
            ),
        }


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm
    list_display = (
        "title",
        "post_type",
        "status",
        "published_at",
        "allow_comments",
        "tag_summary",
    )
    list_filter = ("post_type", "status", "allow_comments", "tags")
    search_fields = ("title", "summary", "content", "seo_title", "seo_description")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    filter_horizontal = ("tags",)
    ordering = ("-published_at", "-created_at")
    readonly_fields = ("cover_preview",)

    fieldsets = (
        ("基础信息", {"fields": ("title", "slug", "summary", "cover_image", "cover_preview")}),
        ("正文内容", {"fields": ("content",)}),
        ("SEO 配置", {"fields": ("seo_title", "seo_description", "seo_keywords")}),
        (
            "发布配置",
            {"fields": ("post_type", "status", "published_at", "tags", "allow_comments")},
        ),
    )

    class Media:
        css = {"all": ("blog/admin-richtext.css",)}
        js = ("blog/admin-richtext.js",)

    @admin.display(description="标签")
    def tag_summary(self, obj: Post):
        tag_names = ", ".join(tag.name for tag in obj.tags.all())
        return format_html("<span>{}</span>", tag_names or "-")

    @admin.display(description="封面预览")
    def cover_preview(self, obj: Post):
        if not obj.cover_image:
            return "-"
        return format_html(
            '<img src="{}" alt="cover" style="max-height:90px;border-radius:8px;" />',
            obj.cover_image.url,
        )


@admin.action(description="将所选评论标记为已通过")
def approve_comments(modeladmin, request, queryset):
    queryset.update(status=Comment.Status.APPROVED)


@admin.action(description="将所选评论标记为垃圾")
def mark_as_spam(modeladmin, request, queryset):
    queryset.update(status=Comment.Status.SPAM)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("post", "name", "email", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "website", "content", "post__title")
    autocomplete_fields = ("post",)
    actions = (approve_comments, mark_as_spam)


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("site_name", "brand_text", "updated_at")

    fieldsets = (
        ("全局设置", {"fields": ("site_name", "site_tagline", "brand_text", "admin_link_text")}),
        ("Meta 设置", {"fields": ("meta_description_default", "meta_keywords_default")}),
        ("侧栏卡片", {"fields": ("profile_name", "profile_role", "profile_description")}),
        (
            "首页功能块",
            {
                "fields": (
                    "home_hero_title",
                    "home_hero_subtitle",
                    "home_posts_title",
                    "home_posts_more_text",
                    "home_posts_empty_text",
                    "home_digest_title",
                    "home_digest_more_text",
                    "home_digest_empty_text",
                )
            },
        ),
        (
            "列表页功能块",
            {
                "fields": (
                    "posts_title",
                    "posts_hint",
                    "posts_empty_text",
                    "digest_title",
                    "digest_hint",
                    "digest_empty_text",
                )
            },
        ),
        (
            "页面功能块",
            {
                "fields": (
                    "tags_title",
                    "tags_hint",
                    "tags_empty_text",
                    "archives_title",
                    "archives_empty_text",
                    "search_title",
                    "search_hint",
                    "search_placeholder",
                    "search_button_text",
                    "search_empty_text",
                    "about_title",
                    "about_subtitle",
                    "about_body_1",
                    "about_body_2",
                )
            },
        ),
        (
            "评论与页脚",
            {
                "fields": (
                    "comments_title",
                    "comments_empty_text",
                    "comments_submit_text",
                    "comments_closed_text",
                    "footer_left_text",
                    "footer_right_text",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        if SiteSetting.objects.exists():
            return False
        return super().has_add_permission(request)


@admin.register(NavigationItem)
class NavigationItemAdmin(admin.ModelAdmin):
    list_display = ("label", "url", "sort_order", "is_enabled", "open_in_new_tab")
    list_editable = ("sort_order", "is_enabled", "open_in_new_tab")
    search_fields = ("label", "url")
    ordering = ("sort_order", "id")


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("label", "url", "sort_order", "is_enabled", "open_in_new_tab")
    list_editable = ("sort_order", "is_enabled", "open_in_new_tab")
    search_fields = ("label", "url")
    ordering = ("sort_order", "id")


admin.site.site_header = "博客管理后台"
admin.site.site_title = "博客后台"
admin.site.index_title = "内容与配置管理"
