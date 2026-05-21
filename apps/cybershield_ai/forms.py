from django import forms


class UrlScanForm(forms.Form):
    url = forms.URLField(
        label='Ссылка',
        widget=forms.URLInput(attrs={'placeholder': 'https://example.com/login', 'class': 'field'}),
    )


class TextScanForm(forms.Form):
    text = forms.CharField(
        label='Текст сообщения',
        widget=forms.Textarea(attrs={
            'placeholder': 'Вставьте SMS, письмо или сообщение из мессенджера',
            'class': 'field field-area',
            'rows': 7,
        }),
    )


class MediaScanForm(forms.Form):
    media = forms.FileField(
        label='Фото или видео',
        widget=forms.ClearableFileInput(attrs={'class': 'field', 'accept': 'image/*,video/*'}),
    )


class TrainerAnswerForm(forms.Form):
    scenario_id = forms.CharField(widget=forms.HiddenInput)
    answer = forms.ChoiceField(
        label='Ваш ответ',
        choices=(('fraud', 'Это мошенничество'), ('safe', 'Это безопасно')),
        widget=forms.RadioSelect,
    )
