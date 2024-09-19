from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()

class TestRoutes(TestCase):
    
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username='Лев Толстой')
        cls.reader = User.objects.create_user(username='Читатель простой')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='zagolovok',
            author=cls.author
        )
        
        # URL constants for cleaner access
        cls.urls = {
            'edit': reverse('notes:edit', args=(cls.note.slug,)),
            'delete': reverse('notes:delete', args=(cls.note.slug,)),
            'detail': reverse('notes:detail', args=(cls.note.slug,)),
            'notes_home': reverse('notes:home'),
            'users_login': reverse('users:login'),
            'users_logout': reverse('users:logout'),
            'users_signup': reverse('users:signup'),
            'notes_add': reverse('notes:add'),
            'notes_list': reverse('notes:list'),
        }

    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('edit', 'delete'):
                with self.subTest(user=user, name=name):
                    response = self.client.get(self.urls[name])
                    self.assertEqual(response.status_code, status)

    def test_pages_availability(self):
        self.client.force_login(self.author)

        urls = (
            ('notes_home', None),
            ('detail', None),
            ('users_login', None),
            ('users_logout', None),
            ('users_signup', None),
        )
        for name, _ in urls:
            with self.subTest(name=name):
                response = self.client.get(self.urls[name])
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        login_url = self.urls['users_login']
        urls = (
            ('notes_add', None),
            ('notes_list', None),
            ('edit', None),
            ('delete', None),
            ('detail', None),
        )
        for name, _ in urls:
            with self.subTest(name=name):
                redirect_url = f'{login_url}?next={self.urls[name]}'
                response = self.client.get(self.urls[name])
                self.assertRedirects(response, redirect_url)
