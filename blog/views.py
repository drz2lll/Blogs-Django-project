from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from .models import News
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from users.forms import MessageForm
from django.conf import settings

def home(request):
    context = {
        "title": "Главная страница",
        "welcome": "Добро пожаловать на сайт!",
        "description": "Здесь вы найдёте самые свежие новости, статьи и полезную информацию."
    }
    return render(request, "blog/home.html", context)

class ShowNewsView(ListView):
    model = News
    template_name = 'blog/contact.html'
    context_object_name = 'news'
    ordering = ['-date']
    paginate_by = 4

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'Новости сайта'
        return ctx
    
class UserAllNewsView(ListView):
    model = News
    template_name = 'blog/user_news.html'
    context_object_name = 'news'
    paginate_by = 4

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return News.objects.filter(avtor=user).order_by('-date')

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = f'Статьи от пользователя {self.kwargs.get("username")}'
        return ctx

class NewsDetailView(DetailView):
    model = News
    template_name = 'blog/news_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = self.object.title
        return ctx
    
class DeleteNewsView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = News
    success_url = '/'
    template_name =  'blog/delete_news.html'

    def test_func(self):
        news = self.get_object()
        if self.request.user == news.avtor:
            return True
        
        return False


class CreateNewsView(LoginRequiredMixin, CreateView):
    model = News
    template_name = 'blog/create_news.html'
    fields = ['title', 'text']
    success_url = reverse_lazy('contact')

    def form_valid(self, form):
        form.instance.avtor = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление статьи'
        context['btn_text'] = 'Добавить статью'
        return context


class UpdateNewsView(LoginRequiredMixin,  UserPassesTestMixin, UpdateView):
    model = News
    template_name = 'blog/create_news.html'
    fields = ['title', 'text']
    success_url = reverse_lazy('contact')

    def form_valid(self, form):
        form.instance.avtor = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Обновление статьи'
        context['btn_text'] = 'Обновить статью'
        return context
    
    def test_func(self):
        news = self.get_object()
        if self.request.user == news.avtor:
            return True
        
        return False
    
def send_message(request):
    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message_text = form.cleaned_data['message']

            subject = f"Сообщение от {name}"
            plain_message = f"От: {name} <{email}>\n\n{message_text}"
            from_email = settings.EMAIL_HOST_USER
            to = 'egorbabenkoboxer@gmail.com'  

            send_mail(subject, plain_message, from_email, [to])

            messages.success(request, "Сообщение отправлено!")
            return redirect('message')
        else:
            messages.error(request, "Ошибка! Проверьте форму.")
    else:
        form = MessageForm()

    return render(request, 'blog/message.html', {'form': form})