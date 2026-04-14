from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.views.generic import DetailView, ListView, TemplateView

from .forms import CommentForm
from .models import Post, Tag


def _published_posts():
    return Post.objects.published().prefetch_related("tags")


def _client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class HomeView(TemplateView):
    template_name = "blog/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_posts = _published_posts()
        context["latest_posts"] = all_posts.posts()[:8]
        context["latest_digests"] = all_posts.digests()[:8]
        return context


class PostListView(ListView):
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        return _published_posts().posts()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["section_kind"] = "posts"
        return context


class DigestListView(ListView):
    template_name = "blog/post_list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        return _published_posts().digests()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["section_kind"] = "digest"
        return context


class BaseDetailView(DetailView):
    template_name = "blog/post_detail.html"
    context_object_name = "post"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["comments"] = self.object.comments.approved()
        context["comment_form"] = kwargs.get("comment_form", CommentForm())
        return context


class PostDetailView(BaseDetailView):
    def get_queryset(self):
        return _published_posts().posts()


class DigestDetailView(BaseDetailView):
    def get_queryset(self):
        return _published_posts().digests()


class AddCommentView(View):
    def post(self, request, slug):
        post = get_object_or_404(_published_posts(), slug=slug)
        if not post.allow_comments:
            raise Http404("Comment is disabled for this post.")

        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.ip_address = _client_ip(request)
            comment.save()
            return redirect(f"{post.get_absolute_url()}#comments")

        comments = post.comments.approved()
        return render(
            request,
            "blog/post_detail.html",
            {"post": post, "comments": comments, "comment_form": form},
            status=400,
        )


class TagsView(ListView):
    template_name = "blog/tags.html"
    context_object_name = "tags"

    def get_queryset(self):
        return Tag.objects.annotate(
            post_count=Count(
                "posts",
                filter=Q(posts__status=Post.Status.PUBLISHED),
                distinct=True,
            )
        ).order_by("-post_count", "name")


class TagDetailView(ListView):
    template_name = "blog/tag_detail.html"
    context_object_name = "posts"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        self.tag = get_object_or_404(Tag, slug=kwargs["slug"])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return self.tag.posts.published().prefetch_related("tags")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag"] = self.tag
        return context


class ArchivesView(TemplateView):
    template_name = "blog/archives.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        qs = _published_posts()
        month_rows = (
            qs.exclude(published_at__isnull=True)
            .values("published_at__year", "published_at__month")
            .annotate(total=Count("id"))
            .order_by("-published_at__year", "-published_at__month")
        )
        archives = []
        for row in month_rows:
            year = row["published_at__year"]
            month = row["published_at__month"]
            posts = qs.filter(published_at__year=year, published_at__month=month)
            archives.append(
                {
                    "year": year,
                    "month": month,
                    "total": row["total"],
                    "posts": posts,
                }
            )
        context["archives"] = archives
        context["total_posts"] = qs.count()
        return context


class SearchView(ListView):
    template_name = "blog/search.html"
    context_object_name = "results"
    paginate_by = 10

    def get_queryset(self):
        query = self.request.GET.get("q", "").strip()
        if not query:
            return Post.objects.none()
        return _published_posts().filter(
            Q(title__icontains=query)
            | Q(summary__icontains=query)
            | Q(content__icontains=query)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["query"] = self.request.GET.get("q", "").strip()
        return context


class AboutView(TemplateView):
    template_name = "blog/about.html"
