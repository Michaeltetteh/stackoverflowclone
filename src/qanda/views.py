from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (
    CreateView,
    DetailView,
    RedirectView,
    DayArchiveView,
    UpdateView,
    TemplateView,
)
from django.shortcuts import render
from .forms import (
    QuestionForm,
    AnswerForm,
    AnswerAcceptanceForm,
)
from .models import Question,Answer
from django.http import HttpResponseBadRequest
from django.urls import reverse
from django.utils import timezone

from .service.elasticsearch import search_for_questions


class AskQuestionView(LoginRequiredMixin,CreateView):
    form_class = QuestionForm
    template_name = 'qanda/ask.html'

    def get_initial(self):
        return {
            'user': self.request.user.id
        }

    def form_valid(self,form):
        action = self.request.POST.get('action')
        if action == 'SAVE':
            return super().form_valid(form)
        elif action == 'PREVIEW':
            preview = Question(
                question = form.cleaned_data['question'],
                title = form.cleaned_data['title']
            )
            ctx = self.get_context_data(preview=preview)
            return self.render_to_response(context=ctx)
        return HttpResponseBadRequest()


class QuestionDetailView(DetailView):
    model = Question

    ACCEPT_FORM = AnswerAcceptanceForm(initial={'accepted':True})
    REJECTED_FORM = AnswerAcceptanceForm(initial={'accepted': False})

    def get_context_data(self,**kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'answer_form': AnswerForm(initial={
                'user': self.request.user.id,
                'question': self.object.id,
            })
        })
        if self.object.can_accept_answers(self.request.user):
            ctx.update({
                'accept_form': self.ACCEPT_FORM,
                'reject_form': self.REJECTED_FORM,
            })
        return ctx

class CreateAnswerView(LoginRequiredMixin,CreateView):
    form_class = AnswerForm
    template_name = 'qanda/create_answer.html'

    def get_initial(self):
        return {
            'question': self.get_question().id,
            'user': self.request.user.id,
        }

    def get_context_data(self,**kwargs):
        return super().get_context_data(question=self.get_question(),**kwargs)

    def get_success_url(self):
        return self.object.question.get_absolute_url()

    def form_valid(self,form):
        action = self.request.POST.get('action')
        if action == 'SAVE':
            return super().form_valid(form)
        elif action == 'PREVIEW':
            ctx = self.get_context_data(preview=form.cleaned_data['answer'])
            return self.render_to_response(context=ctx)
        return HttpResponseBadRequest()

    def get_question(self):
        return Question.objects.get(pk=self.kwargs['pk'])   



class UpdateAnswerAccepetance(LoginRequiredMixin,UpdateView):
    form_class = AnswerAcceptanceForm
    queryset = Answer.objects.all()
    template_name = "qanda/common/list_answers.html"
    def get_success_url(self):
        return self.object.question.get_absolute_url()

    def form_invalid(self,form):
        return HttpResponseBadRequest(
            redirect_to=self.object.question.get_absolute_url()
        )



class DailyQuestionList(DayArchiveView):
    queryset = Question.objects.all()
    date_field = 'created'
    month_format = '%m'
    allow_empty = True

class TodaysQuestionList(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        today = timezone.now()
        return reverse('qanda:daily_questions',
                        kwargs={
                            'day': today.day,
                            'month': today.month,
                            'year': today.year,
                        }
        )



class SearchView(TemplateView):
    template_name = 'qanda/search.html'

    def get_context_data(self,**kwargs):
        query = self.request.GET.get('q',None)
        ctx = super().get_context_data(query=query,**kwargs)
        if query:
            result = search_for_questions(query)
            ctx['hits'] = result
        return ctx
