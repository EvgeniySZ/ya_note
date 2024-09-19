from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()

# Константы для магических чисел
NOTE_COUNT_USER_FIRST = 10
NOTE_COUNT_USER_SECOND = 5


class TestNoteListPage(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.first_user = User.objects.create(username='Пользователь1')
        cls.second_user = User.objects.create(username='Пользователь2')

        cls.notes_user_first = [
            Note(
                title=f'Заметка 1-{index}',
                text='Просто текст.',
                author=cls.first_user,
                slug=f'user_first-note-{index}',
            )
            for index in range(NOTE_COUNT_USER_FIRST)
        ]
        cls.notes_user_second = [
            Note(
                title=f'Заметка 2-{index}',
                text='Просто текст.',
                author=cls.second_user,
                slug=f'user_second-note-{index}',
            )
            for index in range(NOTE_COUNT_USER_SECOND)
        ]
        Note.objects.bulk_create(cls.notes_user_first)
        Note.objects.bulk_create(cls.notes_user_second)

        cls.url = reverse('notes:list')  # Вынесение URL в setUpTestData

        cls.user = User.objects.create(username='Пользователь')
        cls.note = Note.objects.create(
            title='Заметка',
            text='Просто текст.',
            author=cls.user,
            slug='user-note'
        )

    def test_note_list(self):
        self.client.force_login(self.first_user)
        response = self.client.get(self.url)
        self.assertIn('object_list', response.context)
        object_list = response.context['object_list']
        self.assertEqual(object_list.count(), NOTE_COUNT_USER_FIRST)

    def test_another_user_notes_not_in_list(self):
        self.client.force_login(self.first_user)
        response = self.client.get(self.url)
        object_list = response.context['object_list']

        for note in object_list:
            self.assertFalse(Note.objects.filter(
                author=self.second_user,
                slug=note.slug).exists()
            )

    def test_create_form(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('notes:add'))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_update_form(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('notes:edit',
                                           args=(self.note.slug,))
                                   )
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
