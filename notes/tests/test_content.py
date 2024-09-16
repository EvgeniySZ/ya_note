from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm

from datetime import datetime
from django.contrib.auth import get_user_model

User = get_user_model()


class TestNoteListPage(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = User.objects.create(username='Пользователь1')
        cls.user2 = User.objects.create(username='Пользователь2')

        # Убедитесь, что слаги уникальны
        cls.notes1 = [
            Note(
                title=f'Заметка 1-{index}',
                text='Просто текст.',
                author=cls.user1,
                slug=f'user1-note-{index}',  # Уникальный slug для пользователя 1
            )
            for index in range(10)
        ]
        cls.notes2 = [
            Note(
                title=f'Заметка 2-{index}',
                text='Просто текст.',
                author=cls.user2,
                slug=f'user2-note-{index}',  # Уникальный slug для пользователя 2
            )
            for index in range(5)
        ]
        Note.objects.bulk_create(cls.notes1)
        Note.objects.bulk_create(cls.notes2)

    def test_note_list(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse('notes:list'))
        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']
        self.assertEqual(len(object_list), 10)

    def test_another_user_notes_not_in_list(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse('notes:list'))
        object_list = response.context['object_list']
        for note in object_list:
            self.assertNotEqual(note.author, self.user2)


class TestNoteCreatePage(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Пользователь')

    def test_create_form(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('notes:add'))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)


class TestNoteUpdatePage(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Пользователь')
        cls.note = Note.objects.create(title='Заметка', text='Просто текст.', author=cls.user, slug='user-note')

    def test_update_form(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('notes:edit', args=(self.note.slug,)))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
