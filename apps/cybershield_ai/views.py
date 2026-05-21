from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from django.http import HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render

from services.dashboard.statistics import build_dashboard
from services.deepfake.detector import analyze_media
from services.phishing.detector import analyze_text, analyze_url
from services.trainer.evaluator import evaluate_answer
from services.trainer.generator import get_scenario

from .forms import (
    ForumCommentForm,
    ForumPostForm,
    LoginForm,
    MediaScanForm,
    RegisterForm,
    TextScanForm,
    TrainerAnswerForm,
    UrlScanForm,
)
from .models import ForumLike, ForumPost, ScanHistory, TrainerAttempt
from .i18n import LANGUAGES, get_language


def _language(request):
    return get_language(request)


@login_required
def home(request):
    latest_scans = ScanHistory.objects.all()[:5]
    latest_posts = ForumPost.objects.annotate(
        likes_count=Count('likes'),
        comments_count=Count('comments'),
    )[:3]
    return render(request, 'home.html', {'latest_scans': latest_scans, 'latest_posts': latest_posts})


@login_required
def phishing(request):
    language = _language(request)
    url_form = UrlScanForm(prefix='url', language=language)
    text_form = TextScanForm(prefix='text', language=language)
    result = None

    if request.method == 'POST':
        if request.POST.get('scan_mode') == 'url':
            url_form = UrlScanForm(request.POST, prefix='url', language=language)
            if url_form.is_valid():
                result = analyze_url(url_form.cleaned_data['url'])
                ScanHistory.objects.create(
                    scan_type='url',
                    user=request.user if request.user.is_authenticated else None,
                    target=url_form.cleaned_data['url'],
                    **result,
                )
        else:
            text_form = TextScanForm(request.POST, prefix='text', language=language)
            if text_form.is_valid():
                result = analyze_text(text_form.cleaned_data['text'])
                ScanHistory.objects.create(
                    scan_type='text',
                    user=request.user if request.user.is_authenticated else None,
                    target=text_form.cleaned_data['text'],
                    **result,
                )

    return render(request, 'phishing.html', {
        'url_form': url_form,
        'text_form': text_form,
        'result': result,
    })


@login_required
def deepfake(request):
    language = _language(request)
    form = MediaScanForm(language=language)
    result = None

    if request.method == 'POST':
        form = MediaScanForm(request.POST, request.FILES, language=language)
        if form.is_valid():
            uploaded = form.cleaned_data['media']
            result = analyze_media(uploaded)
            ScanHistory.objects.create(
                scan_type='media',
                user=request.user if request.user.is_authenticated else None,
                target=uploaded.name,
                **result,
            )

    return render(request, 'deepfake.html', {'form': form, 'result': result})


@login_required
def trainer(request):
    language = _language(request)
    feedback = None

    if request.method == 'POST':
        form = TrainerAnswerForm(request.POST, language=language)
        if form.is_valid():
            scenario_id = form.cleaned_data['scenario_id']
            answered_scenario = _get_remembered_scenario(request, scenario_id)
            feedback = evaluate_answer(scenario_id, form.cleaned_data['answer'], scenario=answered_scenario)
            TrainerAttempt.objects.create(
                user=request.user if request.user.is_authenticated else None,
                scenario_title=feedback['title'],
                scenario_text=feedback['text'],
                correct_answer=feedback['correct_answer'],
                user_answer=feedback['user_answer'],
                feedback=feedback['feedback'],
            )
            scenario = get_scenario(exclude_id=scenario_id)
            _remember_scenario(request, scenario)
            form = TrainerAnswerForm(initial={'scenario_id': scenario['id']}, language=language)
        else:
            scenario = get_scenario()
            _remember_scenario(request, scenario)
    else:
        scenario = get_scenario()
        _remember_scenario(request, scenario)
        form = TrainerAnswerForm(initial={'scenario_id': scenario['id']}, language=language)

    return render(request, 'trainer.html', {'scenario': scenario, 'form': form, 'feedback': feedback})


@login_required
def dashboard(request):
    return render(request, 'dashboard.html', build_dashboard())


def register(request):
    if request.user.is_authenticated:
        return redirect('cybershield:profile')

    form = RegisterForm(request.POST or None, language=_language(request))
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('cybershield:profile')

    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('cybershield:profile')

    form = LoginForm(request, data=request.POST or None, language=_language(request))
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('cybershield:profile')

    return render(request, 'registration/login.html', {'form': form})


@login_required
def profile(request):
    user = request.user
    attempts = user.trainer_attempts.all()[:10]
    total_attempts = user.trainer_attempts.count()
    correct_attempts = sum(1 for item in user.trainer_attempts.all() if item.is_correct)
    context = {
        'profile_user': user,
        'scans': user.scans.all()[:10],
        'posts': user.forum_posts.annotate(likes_count=Count('likes'), comments_count=Count('comments'))[:10],
        'comments': user.forum_comments.select_related('post')[:10],
        'liked_posts': user.liked_forum_posts.select_related('author')[:10],
        'attempts': attempts,
        'total_scans': user.scans.count(),
        'total_posts': user.forum_posts.count(),
        'total_comments': user.forum_comments.count(),
        'total_likes': user.forum_likes.count(),
        'trainer_accuracy': round((correct_attempts / total_attempts) * 100) if total_attempts else 0,
    }
    return render(request, 'profile.html', context)


@login_required
def forum(request):
    posts = ForumPost.objects.select_related('author').annotate(
        likes_count=Count('likes'),
        comments_count=Count('comments'),
    )
    return render(request, 'forum.html', {'posts': posts})


@login_required
def forum_create(request):
    form = ForumPostForm(request.POST or None, language=_language(request))
    if request.method == 'POST' and form.is_valid():
        post = ForumPost.objects.create(
            author=request.user,
            title=form.cleaned_data['title'],
            body=form.cleaned_data['body'],
        )
        return redirect('cybershield:forum_detail', post_id=post.id)
    return render(request, 'forum_form.html', {'form': form})


@login_required
def forum_detail(request, post_id):
    post = get_object_or_404(
        ForumPost.objects.select_related('author').annotate(likes_count=Count('likes')),
        id=post_id,
    )
    comment_form = ForumCommentForm(language=_language(request))
    is_liked = False
    if request.user.is_authenticated:
        is_liked = ForumLike.objects.filter(post=post, user=request.user).exists()

    return render(request, 'forum_detail.html', {
        'post': post,
        'comments': post.comments.select_related('author'),
        'comment_form': comment_form,
        'is_liked': is_liked,
    })


@login_required
def forum_comment(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    form = ForumCommentForm(request.POST or None, language=_language(request))
    if request.method == 'POST' and form.is_valid():
        post.comments.create(author=request.user, body=form.cleaned_data['body'])
    return redirect('cybershield:forum_detail', post_id=post.id)


@login_required
def forum_like(request, post_id):
    post = get_object_or_404(ForumPost, id=post_id)
    like = ForumLike.objects.filter(post=post, user=request.user).first()
    if like:
        like.delete()
    else:
        ForumLike.objects.create(post=post, user=request.user)
    next_url = request.POST.get('next')
    if next_url:
        return redirect(next_url)
    return redirect('cybershield:forum_detail', post_id=post.id)


@login_required
def public_profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    attempts = profile_user.trainer_attempts.all()
    correct_attempts = sum(1 for item in attempts if item.is_correct)
    total_attempts = len(attempts)
    context = {
        'profile_user': profile_user,
        'is_own_profile': request.user == profile_user,
        'posts': profile_user.forum_posts.annotate(likes_count=Count('likes'), comments_count=Count('comments'))[:10],
        'comments': profile_user.forum_comments.select_related('post')[:10],
        'liked_posts': profile_user.liked_forum_posts.select_related('author')[:10],
        'total_scans': profile_user.scans.count(),
        'total_posts': profile_user.forum_posts.count(),
        'total_comments': profile_user.forum_comments.count(),
        'total_likes': profile_user.forum_likes.count(),
        'trainer_accuracy': round((correct_attempts / total_attempts) * 100) if total_attempts else 0,
    }
    return render(request, 'public_profile.html', context)


@login_required
def logout_confirm(request):
    if request.method == 'POST':
        logout(request)
        return redirect('cybershield:login')
    return render(request, 'registration/logout_confirm.html')


def set_language(request, language):
    if language not in LANGUAGES:
        return HttpResponseBadRequest('Unsupported language')
    request.session['ui_language'] = language
    request.session.modified = True
    return redirect(request.META.get('HTTP_REFERER') or 'cybershield:home')


def _remember_scenario(request, scenario):
    scenarios = request.session.get('trainer_scenarios', {})
    scenarios[scenario['id']] = scenario
    request.session['trainer_scenarios'] = scenarios
    request.session.modified = True


def _get_remembered_scenario(request, scenario_id):
    return request.session.get('trainer_scenarios', {}).get(scenario_id)
