from django import forms
from django.utils.translation import gettext_lazy as _

from .models import Comment, Post


class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {
            'text': _('Текст записи'),
            'group': _('Группа'),
        }
        help_texts = {
            'text': _('Текст новой записи'),
            'group': _('Группа, к которой будет относиться запись'),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': _('Текст комментария'),
        }
        help_texts = {
            'text': _('Текст нового комментария'),
        }
