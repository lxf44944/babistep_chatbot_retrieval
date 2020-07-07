from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('answer/', views.ask, name='ask'),
    path('', views.home, name='home'),
    # path('questions/', views.IndexView.as_view(), name='index'),
    # path('<int:pk>/', views.DetailView.as_view(), name='detail'),
    # path('<int:pk>/results/', views.ResultsView.as_view(), name='results'),
    # # path('index_result/', views.IndexResultsView.as_view(), name='index_result'),
    # path('index_result/', views.index_result, name='index_result'),
    # path('<int:question_id>/vote/', views.vote, name='vote'),
]