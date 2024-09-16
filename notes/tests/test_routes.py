from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создаём пользователей
        cls.author = User.objects.create_user(username='Лев Толстой')
        cls.reader = User.objects.create_user(username='Читатель простой')
        # Создаём заметку, привязанную к автору
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='zagolovok',
            author=cls.author
        )

    def test_availability_for_note_edit_and_delete(self):
        users_statuses = (
            (self.author, HTTPStatus.OK),       # Автор должен иметь доступ
            # Другие пользователи не должны иметь доступ
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            # Для каждой пары "пользователь - ожидаемый ответ" проверяем доступ к страницам
            for name in ('notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_pages_availability(self):
        # Логиним пользователя для тестирования страниц, которые должны быть доступны только авторизованным пользователям
        self.client.force_login(self.author)

        urls = (
            ('notes:home', None),  # Главная страница доступна для всех
            ('notes:detail', (self.note.slug,)),  # Страница заметки
            ('users:login', None),  # Страница логина
            ('users:logout', None),  # Страница выхода
            ('users:signup', None),  # Страница регистрации
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        login_url = reverse('users:login')
        # Проверяем редирект для анонимного пользователя
        urls = (
            ('notes:add', None),  # Добавление заметки
            ('notes:list', None),  # Список заметок
            ('notes:edit', (self.note.slug,)),  # Редактирование
            ('notes:delete', (self.note.slug,)),  # Удаление
            ('notes:detail', (self.note.slug,)),  # Просмотр заметки
        )
        for name, args in urls:
            with self.subTest(name=name):
                url = reverse(name, args=args)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
