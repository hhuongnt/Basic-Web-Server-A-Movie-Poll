from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views import generic

from .models import Choice, Question


class IndexView(generic.ListView):
    """The home page for Intek Movie Friday Poll app"""
    template_name = 'IntekMovieFridayPoll/index.html'
    context_object_name = 'latest_question_list'

    def get_queryset(self):
        """
        Return the last five published questions (not including those set to be
        published in the future).
        """
        return Question.objects.filter(
            pub_date__lte=timezone.now()
        ).order_by('-pub_date')[:5]


class DetailView(generic.DetailView):
    """Displays a question text, with no results but with a form to vote."""
    model = Question
    template_name = 'IntekMovieFridayPoll/detail.html'

    def get_queryset(self):
        """
        Excludes any questions that aren't published yet.
        """
        return Question.objects.filter(pub_date__lte=timezone.now())


class ResultsView(generic.DetailView):
    """Displays results for a particular question."""
    model = Question
    template_name = 'IntekMovieFridayPoll/results.html'


def vote(request, question_id):
    """Handles voting for a particular choice in a particular question."""
    question = get_object_or_404(Question, pk=question_id)
    try:
        selected_choice = question.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        # Redisplay the question voting form.
        return render(request, 'IntekMovieFridayPoll/detail.html', {
            'question': question,
            'error_message': "You didn't select a choice.",
        })
    else:
        selected_choice.votes += 1
        selected_choice.save()
        question.votes += 1
        question.save()
        for choice in question.choice_set.all():
            choice.ratio = round(choice.votes / question.votes * 100, 0)
            choice.save()
        # Always return an HttpResponseRedirect after successfully dealing
        # with POST data. This prevents data from being posted twice if a
        # user hits the Back button.
        return HttpResponseRedirect(reverse('IntekMovieFridayPoll:results', args=(question.id,)))
