import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Follow, Group, Post

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='Yaroslav')
        cls.user_author = User.objects.create_user(username='ABTOR')
        cls.user_not_follow = User.objects.create_user(username='NotFollow')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый коммент',
        )
        cls.post_author = Post.objects.create(
            text='Текст автора',
            author=cls.user_author,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = PostFormTests.user
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post_authorized(self):
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовая форма',
            'group': self.group.id,
            'author': self.user,
            'image': uploaded,
        }
        response_authorized = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response_authorized,
                             reverse('posts:profile',
                                     kwargs={'username': f'{self.user}'}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        last_post = Post.objects.first()
        self.assertEqual(last_post.text, form_data['text'])
        self.assertEqual(last_post.group.id, form_data['group'])
        self.assertEqual(last_post.author, form_data['author'])

    def test_create_post_guest(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовая форма',
            'group': self.group.id,
            'author': self.user
        }
        response_guest = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        login = reverse('users:login')
        post_create = reverse('posts:post_create')
        self.assertRedirects(response_guest, f'{login}?next={post_create}')
        self.assertEqual(Post.objects.count(), posts_count)

    def test_edit_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовая форма',
            'group': self.group.id,
            'author': self.user
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        form_data = {
            'text': 'Изменили текст',
            'group': self.group.id,
            'author': self.user
        }
        response_edit = self.authorized_client.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response_edit,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': self.post.id}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        modified_post = Post.objects.get(id=self.post.id)
        self.assertEqual(modified_post.text, form_data['text'])
        self.assertEqual(modified_post.group.id, form_data['group'])
        self.assertEqual(modified_post.author, form_data['author'])

    def test_comment_post(self):
        comment_count = Comment.objects.count()
        form_data = {
            'post': self.post,
            'author': self.user,
            'text': 'Тестовый коммент_гостя'
        }
        response_guest = self.guest_client.post(
            reverse('posts:add_comment', args=[self.post.id]),
            data=form_data,
            follow=True
        )
        login = reverse('users:login')
        add_comment = reverse('posts:add_comment', args=[self.post.id])
        self.assertRedirects(response_guest, f'{login}?next={add_comment}')
        self.assertEqual(Comment.objects.count(), comment_count)
        form_data = {
            'post': self.post,
            'author': self.user,
            'text': 'Тестовый коммент_авторизованного'
        }
        response_authorized = self.authorized_client.post(
            reverse('posts:add_comment', args=[self.post.id]),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response_authorized,
                             reverse('posts:post_detail',
                                     kwargs={'post_id': self.post.id}))
        self.assertEqual(Comment.objects.count(), comment_count + 1)

    def test_cache(self):
        response_not_del = self.authorized_client.get(reverse('posts:index'))
        Post.objects.all().delete()
        response_del = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response_not_del.content, response_del.content)
        cache.clear()
        response_clear = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response_del.content, response_clear.content)

    def test_follow_and_unfollow(self):
        follow_count = Follow.objects.count()
        follow_data = {
            'user': self.user,
            'author': self.user_author
        }
        self.authorized_client.post(
            reverse('posts:profile_follow', args=[self.user_author]),
            data=follow_data,
            follow=True,
        )
        response_follow = self.authorized_client.get(
            reverse('posts:follow_index'))
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.authorized_client.post(
            reverse('posts:profile_unfollow', args=[self.user_author]),
            data=follow_data,
            follow=True,
        )
        response_not_follow = self.authorized_client.get(
            reverse('posts:follow_index'))
        self.assertEqual(Follow.objects.count(), follow_count)
        self.assertNotEqual(response_follow.content,
                            response_not_follow.content)
