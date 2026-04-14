from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("name", "email", "website", "content")
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "你的名字"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com"}),
            "website": forms.URLInput(attrs={"placeholder": "可选：个人网站"}),
            "content": forms.Textarea(
                attrs={"rows": 5, "placeholder": "写下你的评论...", "maxlength": 2000}
            ),
        }
