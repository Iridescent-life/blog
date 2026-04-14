from django.urls import path

from .feeds import LatestPostsFeed
from .views import (
    AddCommentView,
    AboutView,
    ArchivesView,
    DigestDetailView,
    DigestListView,
    HomeView,
    PostDetailView,
    PostListView,
    SearchView,
    TagDetailView,
    TagsView,
)

app_name = "blog"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("posts/", PostListView.as_view(), name="posts"),
    path("posts/<slug:slug>/", PostDetailView.as_view(), name="post_detail"),
    path("digest/", DigestListView.as_view(), name="digest"),
    path("digest/<slug:slug>/", DigestDetailView.as_view(), name="digest_detail"),
    path("comment/<slug:slug>/", AddCommentView.as_view(), name="add_comment"),
    path("tags/", TagsView.as_view(), name="tags"),
    path("tags/<slug:slug>/", TagDetailView.as_view(), name="tag_detail"),
    path("archives/", ArchivesView.as_view(), name="archives"),
    path("search/", SearchView.as_view(), name="search"),
    path("about/", AboutView.as_view(), name="about"),
    path("rss.xml", LatestPostsFeed(), name="rss"),
]
