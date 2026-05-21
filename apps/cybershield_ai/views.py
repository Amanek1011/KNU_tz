from django.shortcuts import render

from services.dashboard.statistics import build_dashboard
from services.deepfake.detector import analyze_media
from services.phishing.detector import analyze_text, analyze_url
from services.trainer.evaluator import evaluate_answer
from services.trainer.generator import get_scenario

from .forms import MediaScanForm, TextScanForm, TrainerAnswerForm, UrlScanForm
from .models import ScanHistory, TrainerAttempt


def home(request):
    latest_scans = ScanHistory.objects.all()[:5]
    return render(request, 'home.html', {'latest_scans': latest_scans})


def phishing(request):
    url_form = UrlScanForm(prefix='url')
    text_form = TextScanForm(prefix='text')
    result = None

    if request.method == 'POST':
        if request.POST.get('scan_mode') == 'url':
            url_form = UrlScanForm(request.POST, prefix='url')
            if url_form.is_valid():
                result = analyze_url(url_form.cleaned_data['url'])
                ScanHistory.objects.create(scan_type='url', target=url_form.cleaned_data['url'], **result)
        else:
            text_form = TextScanForm(request.POST, prefix='text')
            if text_form.is_valid():
                result = analyze_text(text_form.cleaned_data['text'])
                ScanHistory.objects.create(scan_type='text', target=text_form.cleaned_data['text'], **result)

    return render(request, 'phishing.html', {
        'url_form': url_form,
        'text_form': text_form,
        'result': result,
    })


def deepfake(request):
    form = MediaScanForm()
    result = None

    if request.method == 'POST':
        form = MediaScanForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded = form.cleaned_data['media']
            result = analyze_media(uploaded)
            ScanHistory.objects.create(scan_type='media', target=uploaded.name, **result)

    return render(request, 'deepfake.html', {'form': form, 'result': result})


def trainer(request):
    scenario = get_scenario()
    form = TrainerAnswerForm(initial={'scenario_id': scenario['id']})
    feedback = None

    if request.method == 'POST':
        form = TrainerAnswerForm(request.POST)
        if form.is_valid():
            feedback = evaluate_answer(form.cleaned_data['scenario_id'], form.cleaned_data['answer'])
            TrainerAttempt.objects.create(
                scenario_title=feedback['title'],
                scenario_text=feedback['text'],
                correct_answer=feedback['correct_answer'],
                user_answer=feedback['user_answer'],
                feedback=feedback['feedback'],
            )
            scenario = get_scenario(exclude_id=form.cleaned_data['scenario_id'])
            form = TrainerAnswerForm(initial={'scenario_id': scenario['id']})

    return render(request, 'trainer.html', {'scenario': scenario, 'form': form, 'feedback': feedback})


def dashboard(request):
    return render(request, 'dashboard.html', build_dashboard())

# Create your views here.
