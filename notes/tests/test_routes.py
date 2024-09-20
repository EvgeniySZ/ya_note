from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    NOTE_SLUG = 'zagolovok'
    USER_AUTHOR = 'Лев Толстой'
    USER_READER = 'Читатель простой'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create_user(username=cls.USER_AUTHOR)
        cls.reader = User.objects.create_user(username=cls.USER_READER)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug=cls.NOTE_SLUG,
            author=cls.author
        )

        cls.URL_EDIT = reverse('notes:edit', args=(cls.NOTE_SLUG,))
        cls.URL_DELETE = reverse('notes:delete', args=(cls.NOTE_SLUG,))
        cls.URL_DETAIL = reverse('notes:detail', args=(cls.NOTE_SLUG,))
        cls.URL_NOTES_HOME = reverse('notes:home')
        cls.URL_USERS_LOGIN = reverse('users:login')
        cls.URL_USERS_LOGOUT = reverse('users:logout')
        cls.URL_USERS_SIGNUP = reverse('users:signup')
        cls.URL_NOTES_ADD = reverse('notes:add')
        cls.URL_NOTES_LIST = reverse('notes:list')

    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for url in (self.URL_EDIT, self.URL_DELETE):
                with self.subTest(user=user, url=url):
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_pages_availability(self):
        self.client.force_login(self.author)

        urls = (
            self.URL_NOTES_HOME,
            self.URL_DETAIL,
            self.URL_USERS_LOGIN,
            self.URL_USERS_LOGOUT,
            self.URL_USERS_SIGNUP
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        login_url = self.URL_USERS_LOGIN
        urls = (
            self.URL_NOTES_ADD,
            self.URL_NOTES_LIST,
            self.URL_EDIT,
            self.URL_DELETE,
            self.URL_DETAIL,
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
