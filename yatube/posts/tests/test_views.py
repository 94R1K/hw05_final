from itertools import islice

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Follow, Group, Post

User = get_user_model()


class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='Yaroslav')
        cls.user_author = User.objects.create_user(username='AvTor')
        cls.user_author_1 = User.objects.create_user(username='AvToRr')
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
        cls.follow = Follow.objects.create(
            user=cls.user_not_follow,
            author=cls.user_author_1,
        )

    def setUp(self):
        self.user = ViewsTests.user
        self.user_not_follow = ViewsTests.user_not_follow
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_not_follow = Client()
        self.authorized_client_not_follow.force_login(self.user_not_follow)
        self.templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}):
            'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': f'{self.user}'}): 'posts/profile.html',
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post.id}'}):
            'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{self.post.id}'}):
            'posts/create_post.html',
        }
        self.form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.Field,
        }

    def test_pages_uses_correct_template(self):
        for reverse_name, template in self.templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_group_list_profile_pages_show_correct_context(self):
        reverses_names = list(self.templates_pages_names.keys())
        for url in reverses_names[:3]:
            response = self.authorized_client.get(url)
            first_obj = response.context['page_obj'][0]
            self.assertEqual(
                first_obj.text,
                self.post.text
            )
            self.assertEqual(
                first_obj.author.username,
                self.post.author.username
            )
            self.assertEqual(
                first_obj.author.id,
                self.post.author.id
            )
            self.assertEqual(
                first_obj.group,
                self.post.group
            )
            self.assertEqual(
                first_obj.group.id,
                self.post.group.id
            )
            self.assertEqual(
                first_obj.group.title,
                self.post.group.title
            )
            self.assertEqual(
                first_obj.id,
                self.post.id
            )
            self.assertEqual(
                first_obj.image,
                self.post.image
            )

    def test_post_detail_page_show_correct_context(self):
        response = (self.authorized_client.
                    get(reverse('posts:post_detail',
                                kwargs={'post_id': f'{self.group.id}'})))
        self.assertEqual(response.context.get('post').id, self.post.id)
        self.assertEqual(response.context.get('post').image, self.post.image)

    def test_post_create_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_page_show_correct_context(self):
        response = (self.authorized_client.
                    get(reverse('posts:post_edit',
                                kwargs={'post_id': f'{self.group.id}'})))
        for value, expected in self.form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context.get('post').id, self.post.id)

    def test_cache(self):
        response_not_del = self.authorized_client.get(reverse('posts:index'))
        Post.objects.all().delete()
        response_del = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response_not_del.content, response_del.content)
        cache.clear()
        response_clear = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response_del.content, response_clear.content)

    def test_follow(self):
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
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        follow = Follow.objects.get(author=self.user_author)
        self.assertEqual(follow.user, follow_data['user'])
        self.assertEqual(follow.author, follow_data['author'])

    def test_unfollow(self):
        follow_count = Follow.objects.count()
        Follow.objects.create(
            user=self.user,
            author=self.user_author,
        )
        self.authorized_client.post(
            reverse('posts:profile_unfollow', args=[self.user_author]),
            data={'user': self.user,
                  'author': self.user_author},
            follow=True,
        )
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_the_subscribed_user_has_a_post_in_the_feed(self):
        Follow.objects.create(
            user=self.user,
            author=self.user_author,
        )
        post_author = Post.objects.create(
            text='Текст автора',
            author=self.user_author,
            group=self.group,
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        first_obj = response.context['page_obj'][0]
        self.assertEqual(
            first_obj.text,
            post_author.text
        )
        self.assertEqual(
            first_obj.author,
            post_author.author
        )

    def test_an_unsubscribed_user_has_a_post_in_the_feed(self):
        Post.objects.create(
            text='new_author',
            author=self.user_author_1,
            group=self.group,
        )
        Follow.objects.create(
            user=self.user,
            author=self.user_author,
        )
        post_author = Post.objects.create(
            text='Текст автора',
            author=self.user_author,
            group=self.group,
        )
        response = self.authorized_client_not_follow.get(
            reverse('posts:follow_index'))
        first_obj = response.context['page_obj'][0]
        self.assertNotEqual(
            first_obj.text,
            post_author.text
        )
        self.assertNotEqual(
            first_obj.author,
            post_author.author
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='Yaroslav')
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

    def setUp(self):
        self.user = PaginatorViewsTest.user
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.batch_size = 100
        objs = (Post(group=self.group, author=self.user, text='Test %s' % i)
                for i in range(1000))
        while True:
            batch = list(islice(objs, self.batch_size))
            if not batch:
                break
            Post.objects.bulk_create(batch, self.batch_size)
        self.application_addresses = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': f'{self.group.slug}'}),
            reverse('posts:profile', kwargs={'username': f'{self.user}'}),
        ]

    def test_index_group_list_profile_pages_contains_ten_records(self):
        for address in self.application_addresses:
            response = self.authorized_client.get(address)
            self.assertEqual(len(response.context['page_obj']),
                             settings.ITEMS_COUNT)

    def test_index_group_list_profile_pages_contains_remaining_records(self):
        for address in self.application_addresses:
            total_pages = self.batch_size // settings.ITEMS_COUNT
            response = self.authorized_client.get(address + '?page=2')
            self.assertEqual(len(response.context['page_obj']), total_pages)
