from .models import NavigationItem, SiteSetting, SocialLink


def _ensure_navigation_defaults():
    if NavigationItem.objects.exists():
        return
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


def _ensure_social_defaults():
    if SocialLink.objects.exists():
        return
    SocialLink.objects.bulk_create(
        [
            SocialLink(label="GitHub", url="#", sort_order=10),
            SocialLink(label="X", url="#", sort_order=20),
            SocialLink(label="Email", url="mailto:hello@example.com", sort_order=30),
            SocialLink(label="RSS", url="/rss.xml", sort_order=40),
        ]
    )


def site_customization(request):
    from django.utils import timezone

    site_config = SiteSetting.get_solo()
    _ensure_navigation_defaults()
    _ensure_social_defaults()
    year = str(timezone.now().year)

    return {
        "site_config": site_config,
        "nav_items": NavigationItem.objects.filter(is_enabled=True),
        "social_links": SocialLink.objects.filter(is_enabled=True),
        "footer_left_text": site_config.footer_left_text.replace("{year}", year),
    }
