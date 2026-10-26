from django.shortcuts import render, get_object_or_404
from .models import News, Category
from django.utils import timezone
from datetime import timedelta



def index(request):
    end_date = timezone.now()
    start_date = end_date - timedelta(days=7)
    latest_news = News.objects.filter(created_at__range=(start_date, end_date))
    categories = Category.objects.all()
    context = {'latest_news': latest_news, 'categories': categories}
    return render(request, 'news/index.html', context)


def detail(request, news_id):
    news = get_object_or_404(News, id=news_id)
    context = {'news': news}
    return render(request, "news/detail.html", context)


def category(request, selected_category):
    category_news = News.objects.filter(category__name=selected_category)
    print(category_news)
    context = {'category_news': category_news, 'selected_category': selected_category}
    return render(request, "news/category.html", context)