from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .i18n import DEFAULT_LANGUAGE, get_texts


class LocalizedFormMixin:
    def __init__(self, *args, language=DEFAULT_LANGUAGE, **kwargs):
        self.ui = get_texts(language)
        super().__init__(*args, **kwargs)
        self.localize()

    def localize(self):
        pass


class UrlScanForm(LocalizedFormMixin, forms.Form):
    url = forms.URLField(widget=forms.URLInput(attrs={'class': 'field'}))

    def localize(self):
        self.fields['url'].label = self.ui['form_url']
        self.fields['url'].widget.attrs['placeholder'] = self.ui['placeholder_url']


class TextScanForm(LocalizedFormMixin, forms.Form):
    text = forms.CharField(widget=forms.Textarea(attrs={'class': 'field field-area', 'rows': 7}))

    def localize(self):
        self.fields['text'].label = self.ui['form_text']
        self.fields['text'].widget.attrs['placeholder'] = self.ui['placeholder_text']


class MediaScanForm(LocalizedFormMixin, forms.Form):
    media = forms.FileField(widget=forms.ClearableFileInput(attrs={'class': 'field'}))

    def localize(self):
        self.fields['media'].label = self.ui['form_file']


class TrainerAnswerForm(LocalizedFormMixin, forms.Form):
    scenario_id = forms.CharField(widget=forms.HiddenInput)
    answer = forms.ChoiceField(widget=forms.RadioSelect)

    def localize(self):
        self.fields['answer'].label = self.ui['form_answer']
        self.fields['answer'].choices = (
            ('fraud', self.ui['answer_fraud']),
            ('safe', self.ui['answer_safe']),
        )


class RegisterForm(LocalizedFormMixin, UserCreationForm):
    email = forms.EmailField(
        required=False,
        label='Email',
        widget=forms.EmailInput(attrs={'class': 'field', 'placeholder': 'you@example.com'}),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'field'}),
        }

    def localize(self):
        self.fields['username'].label = self.ui['form_username']
        self.fields['password1'].label = self.ui['form_password']
        self.fields['password2'].label = self.ui['form_password_repeat']
        self.fields['username'].widget.attrs['placeholder'] = self.ui['placeholder_username']
        self.fields['password1'].widget.attrs.update({'class': 'field'})
        self.fields['password2'].widget.attrs.update({'class': 'field'})


class LoginForm(LocalizedFormMixin, AuthenticationForm):
    def localize(self):
        self.fields['username'].label = self.ui['form_username']
        self.fields['password'].label = self.ui['form_password']
        self.fields['username'].widget.attrs.update({
            'class': 'field',
            'placeholder': self.ui['placeholder_username'],
        })
        self.fields['password'].widget.attrs.update({'class': 'field'})


class ForumPostForm(LocalizedFormMixin, forms.Form):
    title = forms.CharField(
        max_length=180,
        widget=forms.TextInput(attrs={'class': 'field'}),
    )
    body = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'field field-area', 'rows': 8}),
    )

    def localize(self):
        self.fields['title'].label = self.ui['form_title']
        self.fields['body'].label = self.ui['form_story']
        self.fields['title'].widget.attrs['placeholder'] = self.ui['placeholder_title']
        self.fields['body'].widget.attrs['placeholder'] = self.ui['placeholder_story']


class ForumCommentForm(LocalizedFormMixin, forms.Form):
    body = forms.CharField(widget=forms.Textarea(attrs={'class': 'field', 'rows': 4}))

    def localize(self):
        self.fields['body'].label = self.ui['form_comment']
        self.fields['body'].widget.attrs['placeholder'] = self.ui['placeholder_comment']
