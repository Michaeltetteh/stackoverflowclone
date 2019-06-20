from django.urls import path
from .views import AskQuestionView

app_name = 'qanda'
urlpatterns = [
    path('ask',AskQuestionView.as_view(), name='ask'),

]