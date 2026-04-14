from django.contrib.syndication.views import Feed

from .models import Post


class LatestPostsFeed(Feed):
    title = "DeepAI Blog"
    description = "个人技术博客与 AI 日报"
    link = "/rss.xml"

    def items(self):
        return Post.objects.published()[:20]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        if item.summary:
            return item.summary
        return item.content[:140]

    def item_link(self, item):
        return item.get_absolute_url()
