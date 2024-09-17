from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestNoteCreation(TestCase):
    NOTE_TITLE = 'Заголовок заметки'
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'zagolovok-zametki'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {'title': cls.NOTE_TITLE, 'text': cls.NOTE_TEXT, 'slug': cls.NOTE_SLUG}

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(reverse('notes:add'), data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_can_create_note(self):
        response = self.auth_client.post(reverse('notes:add'), data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.slug, self.NOTE_SLUG)
        self.assertEqual(note.author, self.user)

    def test_user_cant_create_note_with_existing_slug(self):
        Note.objects.create(title=self.NOTE_TITLE, text=self.NOTE_TEXT, slug=self.NOTE_SLUG, author=self.user)
        response = self.auth_client.post(reverse('notes:add'), data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertFormError(response, 'form', 'slug', self.NOTE_SLUG + WARNING)
        self.assertEqual(Note.objects.count(), 1)

    def test_user_can_create_note_without_slug(self):
        form_data = {'title': self.NOTE_TITLE, 'text': self.NOTE_TEXT}
        response = self.auth_client.post(reverse('notes:add'), data=form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        note = Note.objects.get()
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertIsNotNone(note.slug)
        self.assertEqual(note.author, self.user)


class TestNoteEditDelete(TestCase):
    NOTE_TITLE = 'Заголовок заметки'
    NOTE_TEXT = 'Текст заметки'
    NOTE_SLUG = 'zagolovok-zametki'
    NEW_NOTE_TITLE = 'Новый заголовок заметки'
    NEW_NOTE_TEXT = 'Новый текст заметки'

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.note = Note.objects.create(title=cls.NOTE_TITLE, text=cls.NOTE_TEXT, slug=cls.NOTE_SLUG, author=cls.user)
        cls.form_data = {'title': cls.NEW_NOTE_TITLE, 'text': cls.NEW_NOTE_TEXT}

    def test_user_can_edit_note(self):
        response = self.auth_client.post(reverse('notes:edit', args=(self.note.slug,)), data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NEW_NOTE_TITLE)
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_user_cant_edit_note_of_another_user(self):
        new_user = User.objects.create(username='Новый пользователь')
        new_auth_client = Client()
        new_auth_client.force_login(new_user)
        response = new_auth_client.post(reverse('notes:edit', args=(self.note.slug,)), data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, self.NOTE_TITLE)
        self.assertEqual(self.note.text, self.NOTE_TEXT)

    def test_user_can_delete_note(self):
        response = self.auth_client.post(reverse('notes:delete', args=(self.note.slug,)))
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_user_cant_delete_note_of_another_user(self):
        new_user = User.objects.create(username='Новый пользователь')
        new_auth_client = Client()
        new_auth_client.force_login(new_user)
        response = new_auth_client.post(reverse('notes:delete', args=(self.note.slug,)))
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)
