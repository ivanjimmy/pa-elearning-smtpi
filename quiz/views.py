import datetime
from django.shortcuts import render, redirect, get_object_or_404
from .models import Quiz, Question, SiswaAnswer
from main.models import Siswa, Jenjang, Pengasuh
from main.views import is_pengasuh_authorised, is_siswa_authorised
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Sum, F, FloatField, Q, Prefetch
from django.db.models.functions import Cast


def quiz(request, code):
    try:
        jenjang = Jenjang.objects.get(code=code)
        if is_pengasuh_authorised(request, code):
            if request.method == 'POST':
                title = request.POST.get('title')
                description = request.POST.get('description')
                start = request.POST.get('start')
                end = request.POST.get('end')
                publish_status = request.POST.get('checkbox')
                quiz = Quiz(title=title, description=description, start=start,
                            end=end, publish_status=publish_status, jenjang=jenjang)
                quiz.save()
                return redirect('addQuestion', code=code, quiz_id=quiz.id)
            else:
                return render(request, 'quiz/quiz.html', {'jenjang': jenjang, 'pengasuh': Pengasuh.objects.get(pengasuh_id=request.session['pengasuh_id'])})

        else:
            return redirect('std_login')
    except:
        return render(request, 'error.html')


def addQuestion(request, code, quiz_id):
    try:
        jenjang = Jenjang.objects.get(code=code)
        if is_pengasuh_authorised(request, code):
            quiz = Quiz.objects.get(id=quiz_id)
            if request.method == 'POST':
                question = request.POST.get('question')
                option1 = request.POST.get('option1')
                option2 = request.POST.get('option2')
                option3 = request.POST.get('option3')
                option4 = request.POST.get('option4')
                answer = request.POST.get('answer')
                marks = request.POST.get('marks')
                explanation = request.POST.get('explanation')
                question = Question(question=question, option1=option1, option2=option2,
                                    option3=option3, option4=option4, answer=answer, quiz=quiz, marks=marks, explanation=explanation)
                question.save()
                messages.success(request, 'Question added successfully')
            else:
                return render(request, 'quiz/addQuestion.html', {'jenjang': jenjang, 'quiz': quiz, 'pengasuh': Pengasuh.objects.get(pengasuh_id=request.session['pengasuh_id'])})
            if 'saveOnly' in request.POST:
                return redirect('allQuizzes', code=code)
            return render(request, 'quiz/addQuestion.html', {'jenjang': jenjang, 'quiz': quiz, 'pengasuh': Pengasuh.objects.get(pengasuh_id=request.session['pengasuh_id'])})
        else:
            return redirect('std_login')
    except:
        return render(request, 'error.html')


def allQuizzes(request, code):
    if is_pengasuh_authorised(request, code):
        jenjang = Jenjang.objects.get(code=code)
        quizzes = Quiz.objects.filter(jenjang=jenjang)
        for quiz in quizzes:
            quiz.total_questions = Question.objects.filter(quiz=quiz).count()
            if quiz.start < datetime.datetime.now():
                quiz.started = True
            else:
                quiz.started = False
            quiz.save()
        return render(request, 'quiz/allQuizzes.html', {'jenjang': jenjang, 'quizzes': quizzes, 'pengasuh': Pengasuh.objects.get(pengasuh_id=request.session['pengasuh_id'])})
    else:
        return redirect('std_login')


def myQuizzes(request, code):
    if is_siswa_authorised(request, code):
        jenjang = Jenjang.objects.get(code=code)
        quizzes = Quiz.objects.filter(jenjang=jenjang)
        siswa = Siswa.objects.get(siswa_id=request.session['siswa_id'])

        # Determine which quizzes are active and which are previous
        active_quizzes = []
        previous_quizzes = []
        for quiz in quizzes:
            if quiz.end < timezone.now() or quiz.siswaanswer_set.filter(siswa=siswa).exists():
                previous_quizzes.append(quiz)
            else:
                active_quizzes.append(quiz)

        # Add attempted flag to quizzes
        for quiz in quizzes:
            quiz.attempted = quiz.siswaanswer_set.filter(
                siswa=siswa).exists()

        # Add total marks obtained, percentage, and total questions for previous quizzes
        for quiz in previous_quizzes:
            siswa_answers = quiz.siswaanswer_set.filter(siswa=siswa)
            total_marks_obtained = sum([siswa_answer.question.marks if siswa_answer.answer ==
                                       siswa_answer.question.answer else 0 for siswa_answer in siswa_answers])
            quiz.total_marks_obtained = total_marks_obtained
            quiz.total_marks = sum(
                [question.marks for question in quiz.question_set.all()])
            quiz.percentage = round(
                total_marks_obtained / quiz.total_marks * 100, 2) if quiz.total_marks != 0 else 0
            quiz.total_questions = quiz.question_set.count()

        # Add total questions for active quizzes
        for quiz in active_quizzes:
            quiz.total_questions = quiz.question_set.count()

        return render(request, 'quiz/myQuizzes.html', {
            'jenjang': jenjang,
            'quizzes': quizzes,
            'active_quizzes': active_quizzes,
            'previous_quizzes': previous_quizzes,
            'siswa': siswa,
        })
    else:
        return redirect('std_login')


def startQuiz(request, code, quiz_id):
    if is_siswa_authorised(request, code):
        jenjang = Jenjang.objects.get(code=code)
        quiz = Quiz.objects.get(id=quiz_id)
        questions = Question.objects.filter(quiz=quiz)
        total_questions = questions.count()

        marks = 0
        for question in questions:
            marks += question.marks
        quiz.total_marks = marks

        return render(request, 'quiz/portalStdNew.html', {'jenjang': jenjang, 'quiz': quiz, 'questions': questions, 'total_questions': total_questions, 'siswa': Siswa.objects.get(siswa_id=request.session['siswa_id'])})
    else:
        return redirect('std_login')


def siswaAnswer(request, code, quiz_id):
    if is_siswa_authorised(request, code):
        jenjang = Jenjang.objects.get(code=code)
        quiz = Quiz.objects.get(id=quiz_id)
        questions = Question.objects.filter(quiz=quiz)
        siswa = Siswa.objects.get(siswa_id=request.session['siswa_id'])

        for question in questions:
            answer = request.POST.get(str(question.id))
            siswa_answer = SiswaAnswer(siswa=siswa, quiz=quiz, question=question,
                                           answer=answer, marks=question.marks if answer == question.answer else 0)
            # prevent duplicate answers & multiple attempts
            try:
                siswa_answer.save()
            except:
                redirect('myQuizzes', code=code)
        return redirect('myQuizzes', code=code)
    else:
        return redirect('std_login')


def quizResult(request, code, quiz_id):
    if is_siswa_authorised(request, code):
        jenjang = Jenjang.objects.get(code=code)
        quiz = Quiz.objects.get(id=quiz_id)
        questions = Question.objects.filter(quiz=quiz)
        try:
            siswa = Siswa.objects.get(
                siswa_id=request.session['siswa_id'])
            siswa_answers = SiswaAnswer.objects.filter(
                siswa=siswa, quiz=quiz)
            total_marks_obtained = 0
            for siswa_answer in siswa_answers:
                total_marks_obtained += siswa_answer.question.marks if siswa_answer.answer == siswa_answer.question.answer else 0
            quiz.total_marks_obtained = total_marks_obtained
            quiz.total_marks = 0
            for question in questions:
                quiz.total_marks += question.marks
            quiz.percentage = (total_marks_obtained / quiz.total_marks) * 100
            quiz.percentage = round(quiz.percentage, 2)
        except:
            quiz.total_marks_obtained = 0
            quiz.total_marks = 0
            quiz.percentage = 0

        for question in questions:
            siswa_answer = SiswaAnswer.objects.get(
                siswa=siswa, question=question)
            question.siswa_answer = siswa_answer.answer

        siswa_answers = SiswaAnswer.objects.filter(
            siswa=siswa, quiz=quiz)
        for siswa_answer in siswa_answers:
            quiz.time_taken = siswa_answer.created_at - quiz.start
            quiz.time_taken = quiz.time_taken.total_seconds()
            quiz.time_taken = round(quiz.time_taken, 2)
            quiz.submission_time = siswa_answer.created_at.strftime(
                "%a, %d-%b-%y at %I:%M %p")
        return render(request, 'quiz/quizResult.html', {'jenjang': jenjang, 'quiz': quiz, 'questions': questions, 'siswa': siswa})
    else:
        return redirect('std_login')


def quizSummary(request, code, quiz_id):
    if is_pengasuh_authorised(request, code):
        jenjang = Jenjang.objects.get(code=code)
        quiz = Quiz.objects.get(id=quiz_id)

        questions = Question.objects.filter(quiz=quiz)
        time = datetime.datetime.now()
        total_siswas = Siswa.objects.filter(jenjang=jenjang).count()
        for question in questions:
            question.A = SiswaAnswer.objects.filter(
                question=question, answer='A').count()
            question.B = SiswaAnswer.objects.filter(
                question=question, answer='B').count()
            question.C = SiswaAnswer.objects.filter(
                question=question, answer='C').count()
            question.D = SiswaAnswer.objects.filter(
                question=question, answer='D').count()
        # siswas who have attempted the quiz and their marks
        siswas = Siswa.objects.filter(jenjang=jenjang)
        for siswa in siswas:
            siswa_answers = SiswaAnswer.objects.filter(
                siswa=siswa, quiz=quiz)
            total_marks_obtained = 0
            for siswa_answer in siswa_answers:
                total_marks_obtained += siswa_answer.question.marks if siswa_answer.answer == siswa_answer.question.answer else 0
            siswa.total_marks_obtained = total_marks_obtained

        if request.method == 'POST':
            quiz.publish_status = True
            quiz.save()
            return redirect('quizSummary', code=code, quiz_id=quiz.id)
        # check if siswa has attempted the quiz
        for siswa in siswas:
            if SiswaAnswer.objects.filter(siswa=siswa, quiz=quiz).count() > 0:
                siswa.attempted = True
            else:
                siswa.attempted = False
        for siswa in siswas:
            siswa_answers = SiswaAnswer.objects.filter(
                siswa=siswa, quiz=quiz)
            for siswa_answer in siswa_answers:
                siswa.submission_time = siswa_answer.created_at.strftime(
                    "%a, %d-%b-%y at %I:%M %p")

        context = {'jenjang': jenjang, 'quiz': quiz, 'questions': questions, 'time': time, 'total_siswas': total_siswas,
                   'siswas': siswas, 'pengasuh': Pengasuh.objects.get(pengasuh_id=request.session['pengasuh_id'])}
        return render(request, 'quiz/quizSummaryPengasuh.html', context)

    else:
        return redirect('std_login')


