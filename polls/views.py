from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views import generic
from django.utils import timezone

from .models import Answer, Question

from .documents import QuestionDocument

import random


class IndexView(generic.ListView):
    template_name = 'polls/questions.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """Return the last five published questions."""
        return Question.objects.order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    model = Question
    template_name = 'polls/detail.html'


class ResultsView(generic.DetailView):
    model = Question
    template_name = 'polls/results.html'


# def index(request):
#     latest_question_list = Question.objects.order_by('-pub_date')[:5]
#     context = {'latest_question_list': latest_question_list}
#     return render(request, 'polls/questions.html', context)
#
#
# def detail(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/detail.html', {'question': question})

def vote(request, question_id):
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_answer = question.answer_set.get(pk=request.POST['answer'])
    except (KeyError, Answer.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'polls/detail.html', {
            'question': question,
            'error_message': "You didn't select a answer.",
        })
    else:
        selected_answer.votes += 1
        selected_answer.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))


# 主页
def home(request):
    # latest_question_list = Question.objects.order_by('-pub_date')[:5]
    # context = {'latest_question_list': latest_question_list}
    return render(request, 'polls/index.html')


# 结果页
def index_result(request):
    # question = get_object_or_404(Question, pk=question_id)
    return render(request, 'polls/index_result.html')


# 提问模块
def ask(request):
    question_text = request.POST['question'].strip()  # 获取提的问题
    print('question_text:', question_text)
    answer = get_similar_question_answer(question_text)  # 获取答案
    # 查找是否有人问过相同问题
    questions = Question.objects.filter(question_text=question_text)
    questions_len = len(questions)
    # print('questions_len:', questions_len)
    if questions_len > 0:
        # 相同问题记录
        question = questions[random.randrange(questions_len)]
        question.votes += 1
        question.save()
        print('find:', question.id, ' ', question.question_text)
    else:
        # 新问题保存
        question = Question(question_text=question_text, pub_date=timezone.now())
        question.save()
        print('save:', question.id)

    return render(request, 'polls/index_result.html', {'question': question, 'answer': answer})


# 获取相似问题答案
def get_similar_question_answer(question_text):
    answer = Answer()  # 空答案初始化
    # seg_list = jieba.cut(question_text)  # 默认是精确模式
    # print("jeiba:" + "%".join(seg_list))
    # 查找是否有人问过相似问题
    s = QuestionDocument.search().query("match", question_text=question_text)
    qs = s.to_queryset()
    # qs is just a django queryset and it is called with order_by to keep the same order as the elasticsearch result
    print("qs:", qs)
    for q in qs:
        print(q.question_text, '-', q.id, '-', q.answer_set.all())
        if len(q.answer_set.all()) > 0:
            answer = get_best_answer(q)
            break
    return answer


# 获取最佳答案
def get_best_answer(question):
    answer = Answer()  # 空答案初始化
    answers = question.answer_set.all()
    answers_len = len(answers)
    if answers_len > 0:
        # 在相同问题中随机选则votes最多的答案
        answer = answers.order_by('votes').last()
        print('answer:', answer.id, ' ', answer.answer_text)
    return answer
