import datetime
from django.shortcuts import redirect, render
from django.contrib import messages
from .models import Siswa, Jenjang, Announcement, Assignment, Submission, Material, Pengasuh, TahunAjaran
from django.template.defaulttags import register
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from .forms import AnnouncementForm, AssignmentForm, MaterialForm
from django import forms
from django.core import validators


from django import forms


class LoginForm(forms.Form):
    id = forms.CharField(label='ID', max_length=10, validators=[
                         validators.RegexValidator(r'^\d+$', 'Please enter a valid number.')])
    password = forms.CharField(widget=forms.PasswordInput)


def is_siswa_authorised(request, code):
    jenjang = Jenjang.objects.get(code=code)
    if request.session.get('siswa_id') and jenjang in Siswa.objects.get(siswa_id=request.session['siswa_id']).jenjang.all():
        return True
    else:
        return False


def is_pengasuh_authorised(request, code):
    if request.session.get('pengasuh_id') and code in Jenjang.objects.filter(pengasuh_id=request.session['pengasuh_id']).values_list('code', flat=True):
        return True
    else:
        return False


# Custom Login page for both siswa and pengasuh
def std_login(request):
    error_messages = []

    if request.method == 'POST':
        form = LoginForm(request.POST)

        if form.is_valid():
            id = form.cleaned_data['id']
            password = form.cleaned_data['password']

            if Siswa.objects.filter(siswa_id=id, password=password).exists():
                request.session['siswa_id'] = id
                return redirect('myJenjangs')
            elif Pengasuh.objects.filter(pengasuh_id=id, password=password).exists():
                request.session['pengasuh_id'] = id
                return redirect('pengasuhJenjangs')
            else:
                error_messages.append('Invalid login credentials.')
        else:
            error_messages.append('Invalid form data.')
    else:
        form = LoginForm()

    if 'siswa_id' in request.session:
        return redirect('/my/')
    elif 'pengasuh_id' in request.session:
        return redirect('/pengasuhJenjangs/')

    context = {'form': form, 'error_messages': error_messages}
    return render(request, 'login_page.html', context)

# Clears the session on logout


def std_logout(request):
    request.session.flush()
    return redirect('std_login')


# Display all jenjangs (siswa view)
def myJenjangs(request):
    try:
        if request.session.get('siswa_id'):
            siswa = Siswa.objects.get(
                siswa_id=request.session['siswa_id'])
            jenjangs = siswa.jenjang.all()
            pengasuh = siswa.jenjang.all().values_list('pengasuh_id', flat=True)

            context = {
                'jenjangs': jenjangs,
                'siswa': siswa,
                'pengasuh': pengasuh
            }

            return render(request, 'main/myJenjangs.html', context)
        else:
            return redirect('std_login')
    except:
        return render(request, 'error.html')


# Display all jenjangs (pengasuh view)
def pengasuhJenjangs(request):
    try:
        if request.session['pengasuh_id']:
            pengasuh = Pengasuh.objects.get(
                pengasuh_id=request.session['pengasuh_id'])
            jenjangs = Jenjang.objects.filter(
                pengasuh_id=request.session['pengasuh_id'])
            # Siswa count of each jenjang to show on the pengasuh page
            siswaCount = Jenjang.objects.all().annotate(siswa_count=Count('siswas'))

            siswaCountDict = {}

            for jenjang in siswaCount:
                siswaCountDict[jenjang.code] = jenjang.siswa_count

            @register.filter
            def get_item(dictionary, jenjang_code):
                return dictionary.get(jenjang_code)

            context = {
                'jenjangs': jenjangs,
                'pengasuh': pengasuh,
                'siswaCount': siswaCountDict
            }

            return render(request, 'main/pengasuhJenjangs.html', context)

        else:
            return redirect('std_login')
    except:

        return redirect('std_login')


# Particular jenjang page (siswa view)
def jenjang_page(request, code):
    try:
        jenjang = Jenjang.objects.get(code=code)
        if is_siswa_authorised(request, code):
            try:
                announcements = Announcement.objects.filter(jenjang_code=jenjang)
                assignments = Assignment.objects.filter(
                    jenjang_code=jenjang.code)
                materials = Material.objects.filter(jenjang_code=jenjang.code)

            except:
                announcements = None
                assignments = None
                materials = None

            context = {
                'jenjang': jenjang,
                'announcements': announcements,
                'assignments': assignments[:3],
                'materials': materials,
                'siswa': Siswa.objects.get(siswa_id=request.session['siswa_id'])
            }

            return render(request, 'main/jenjang.html', context)

        else:
            return redirect('std_login')
    except:
        return render(request, 'error.html')


# Particular jenjang page (pengasuh view)
def jenjang_page_pengasuh(request, code):
    jenjang = Jenjang.objects.get(code=code)
    if request.session.get('pengasuh_id'):
        try:
            announcements = Announcement.objects.filter(jenjang_code=jenjang)
            assignments = Assignment.objects.filter(
                jenjang_code=jenjang.code)
            materials = Material.objects.filter(jenjang_code=jenjang.code)
            siswaCount = Siswa.objects.filter(jenjang=jenjang).count()

        except:
            announcements = None
            assignments = None
            materials = None

        context = {
            'jenjang': jenjang,
            'announcements': announcements,
            'assignments': assignments[:3],
            'materials': materials,
            'pengasuh': Pengasuh.objects.get(pengasuh_id=request.session['pengasuh_id']),
            'siswaCount': siswaCount
        }

        return render(request, 'main/pengasuh_jenjang.html', context)
    else:
        return redirect('std_login')


def error(request):
    return render(request, 'error.html')


# Display user profile(siswa & pengasuh)
def profile(request, id):
    try:
        if request.session['siswa_id'] == id:
            siswa = Siswa.objects.get(siswa_id=id)
            return render(request, 'main/profile.html', {'siswa': siswa})
        else:
            return redirect('std_login')
    except:
        try:
            if request.session['pengasuh_id'] == id:
                pengasuh = Pengasuh.objects.get(pengasuh_id=id)
                return render(request, 'main/pengasuh_profile.html', {'pengasuh': pengasuh})
            else:
                return redirect('std_login')
        except:
            return render(request, 'error.html')


def addAnnouncement(request, code):
    if is_pengasuh_authorised(request, code):
        if request.method == 'POST':
            form = AnnouncementForm(request.POST)
            form.instance.jenjang_code = Jenjang.objects.get(code=code)
            if form.is_valid():
                form.save()
                messages.success(
                    request, 'Announcement added successfully.')
                return redirect('/pengasuh/' + str(code))
        else:
            form = AnnouncementForm()
        return render(request, 'main/announcement.html', {'jenjang': Jenjang.objects.get(code=code), 'pengasuh': Pengasuh.objects.get(pengasuh_id=request.session['pengasuh_id']), 'form': form})
    else:
        return redirect('std_login')


def deleteAnnouncement(request, code, id):
    if is_pengasuh_authorised(request, code):
        try:
            announcement = Announcement.objects.get(jenjang_code=code, id=id)
            announcement.delete()
            messages.warning(request, 'Announcement deleted successfully.')
            return redirect('/pengasuh/' + str(code))
        except:
            return redirect('/pengasuh/' + str(code))
    else:
        return redirect('std_login')


def editAnnouncement(request, code, id):
    if is_pengasuh_authorised(request, code):
        announcement = Announcement.objects.get(jenjang_code_id=code, id=id)
        form = AnnouncementForm(instance=announcement)
        context = {
            'announcement': announcement,
            'jenjang': Jenjang.objects.get(code=code),
            'pengasuh': Pengasuh.objects.get(pengasuh_id=request.session['pengasuh_id']),
            'form': form
        }
        return render(request, 'main/update-announcement.html', context)
    else:
        return redirect('std_login')


def updateAnnouncement(request, code, id):
    if is_pengasuh_authorised(request, code):
        try:
            announcement = Announcement.objects.get(jenjang_code_id=code, id=id)
            form = AnnouncementForm(request.POST, instance=announcement)
            if form.is_valid():
                form.save()
                messages.info(request, 'Announcement updated successfully.')
                return redirect('/pengasuh/' + str(code))
        except:
            return redirect('/pengasuh/' + str(code))

    else:
        return redirect('std_login')


def addAssignment(request, code):
    if is_pengasuh_authorised(request, code):
        if request.method == 'POST':
            form = AssignmentForm(request.POST, request.FILES)
            form.instance.jenjang_code = Jenjang.objects.get(code=code)
            if form.is_valid():
                form.save()
                messages.success(request, 'Assignment added successfully.')
                return redirect('/pengasuh/' + str(code))
        else:
            form = AssignmentForm()
        return render(request, 'main/assignment.html', {'jenjang': Jenjang.objects.get(code=code), 'pengasuh': Pengasuh.objects.get(pengasuh_id=request.session['pengasuh_id']), 'form': form})
    else:
        return redirect('std_login')


def assignmentPage(request, code, id):
    jenjang = Jenjang.objects.get(code=code)
    if is_siswa_authorised(request, code):
        assignment = Assignment.objects.get(jenjang_code=jenjang.code, id=id)
        try:

            submission = Submission.objects.get(assignment=assignment, siswa=Siswa.objects.get(
                siswa_id=request.session['siswa_id']))

            context = {
                'assignment': assignment,
                'jenjang': jenjang,
                'submission': submission,
                'time': datetime.datetime.now(),
                'siswa': Siswa.objects.get(siswa_id=request.session['siswa_id']),
                'jenjangs': Siswa.objects.get(siswa_id=request.session['siswa_id']).jenjang.all()
            }

            return render(request, 'main/assignment-portal.html', context)

        except:
            submission = None

        context = {
            'assignment': assignment,
            'jenjang': jenjang,
            'submission': submission,
            'time': datetime.datetime.now(),
            'siswa': Siswa.objects.get(siswa_id=request.session['siswa_id']),
            'jenjangs': Siswa.objects.get(siswa_id=request.session['siswa_id']).jenjang.all()
        }

        return render(request, 'main/assignment-portal.html', context)
    else:

        return redirect('std_login')


def allAssignments(request, code):
    if is_pengasuh_authorised(request, code):
        jenjang = Jenjang.objects.get(code=code)
        assignments = Assignment.objects.filter(jenjang_code=jenjang)
        siswaCount = Siswa.objects.filter(jenjang=jenjang).count()

        context = {
            'assignments': assignments,
            'jenjang': jenjang,
            'pengasuh': Pengasuh.objects.get(pengasuh_id=request.session['pengasuh_id']),
            'siswaCount': siswaCount

        }
        return render(request, 'main/all-assignments.html', context)
    else:
        return redirect('std_login')


def allAssignmentsSTD(request, code):
    if is_siswa_authorised(request, code):
        jenjang = Jenjang.objects.get(code=code)
        assignments = Assignment.objects.filter(jenjang_code=jenjang)
        context = {
            'assignments': assignments,
            'jenjang': jenjang,
            'siswa': Siswa.objects.get(siswa_id=request.session['siswa_id']),

        }
        return render(request, 'main/all-assignments-std.html', context)
    else:
        return redirect('std_login')


def addSubmission(request, code, id):
    try:
        jenjang = Jenjang.objects.get(code=code)
        if is_siswa_authorised(request, code):
            # check if assignment is open
            assignment = Assignment.objects.get(jenjang_code=jenjang.code, id=id)
            if assignment.deadline < datetime.datetime.now():

                return redirect('/assignment/' + str(code) + '/' + str(id))

            if request.method == 'POST' and request.FILES['file']:
                assignment = Assignment.objects.get(
                    jenjang_code=jenjang.code, id=id)
                submission = Submission(assignment=assignment, siswa=Siswa.objects.get(
                    siswa_id=request.session['siswa_id']), file=request.FILES['file'],)
                submission.status = 'Submitted'
                submission.save()
                return HttpResponseRedirect(request.path_info)
            else:
                assignment = Assignment.objects.get(
                    jenjang_code=jenjang.code, id=id)
                submission = Submission.objects.get(assignment=assignment, siswa=Siswa.objects.get(
                    siswa_id=request.session['siswa_id']))
                context = {
                    'assignment': assignment,
                    'jenjang': jenjang,
                    'submission': submission,
                    'time': datetime.datetime.now(),
                    'siswa': Siswa.objects.get(siswa_id=request.session['siswa_id']),
                    'jenjangs': Siswa.objects.get(siswa_id=request.session['siswa_id']).jenjang.all()
                }

                return render(request, 'main/assignment-portal.html', context)
        else:
            return redirect('std_login')
    except:
        return HttpResponseRedirect(request.path_info)


def viewSubmission(request, code, id):
    jenjang = Jenjang.objects.get(code=code)
    if is_pengasuh_authorised(request, code):
        try:
            assignment = Assignment.objects.get(jenjang_code_id=code, id=id)
            submissions = Submission.objects.filter(
                assignment_id=assignment.id)

            context = {
                'jenjang': jenjang,
                'submissions': submissions,
                'assignment': assignment,
                'totalSiswas': len(Siswa.objects.filter(jenjang=jenjang)),
                'pengasuh': Pengasuh.objects.get(pengasuh_id=request.session['pengasuh_id']),
                'jenjangs': Jenjang.objects.filter(pengasuh_id=request.session['pengasuh_id'])
            }

            return render(request, 'main/assignment-view.html', context)

        except:
            return redirect('/pengasuh/' + str(code))
    else:
        return redirect('std_login')


def gradeSubmission(request, code, id, sub_id):
    try:
        jenjang = Jenjang.objects.get(code=code)
        if is_pengasuh_authorised(request, code):
            if request.method == 'POST':
                assignment = Assignment.objects.get(jenjang_code_id=code, id=id)
                submissions = Submission.objects.filter(
                    assignment_id=assignment.id)
                submission = Submission.objects.get(
                    assignment_id=id, id=sub_id)
                submission.marks = request.POST['marks']
                if request.POST['marks'] == 0:
                    submission.marks = 0
                submission.save()
                return HttpResponseRedirect(request.path_info)
            else:
                assignment = Assignment.objects.get(jenjang_code_id=code, id=id)
                submissions = Submission.objects.filter(
                    assignment_id=assignment.id)
                submission = Submission.objects.get(
                    assignment_id=id, id=sub_id)

                context = {
                    'jenjang': jenjang,
                    'submissions': submissions,
                    'assignment': assignment,
                    'totalSiswas': len(Siswa.objects.filter(jenjang=jenjang)),
                    'pengasuh': Pengasuh.objects.get(pengasuh_id=request.session['pengasuh_id']),
                    'jenjangs': Jenjang.objects.filter(pengasuh_id=request.session['pengasuh_id'])
                }

                return render(request, 'main/assignment-view.html', context)

        else:
            return redirect('std_login')
    except:
        return redirect('/error/')


def addJenjangMaterial(request, code):
    if is_pengasuh_authorised(request, code):
        if request.method == 'POST':
            form = MaterialForm(request.POST, request.FILES)
            form.instance.jenjang_code = Jenjang.objects.get(code=code)
            if form.is_valid():
                form.save()
                messages.success(request, 'New jenjang material added')
                return redirect('/pengasuh/' + str(code))
            else:
                return render(request, 'main/jenjang-material.html', {'jenjang': Jenjang.objects.get(code=code), 'pengasuh': Pengasuh.objects.get(pengasuh_id=request.session['pengasuh_id']), 'form': form})
        else:
            form = MaterialForm()
            return render(request, 'main/jenjang-material.html', {'jenjang': Jenjang.objects.get(code=code), 'pengasuh': Pengasuh.objects.get(pengasuh_id=request.session['pengasuh_id']), 'form': form})
    else:
        return redirect('std_login')


def deleteJenjangMaterial(request, code, id):
    if is_pengasuh_authorised(request, code):
        jenjang = Jenjang.objects.get(code=code)
        jenjang_material = Material.objects.get(jenjang_code=jenjang, id=id)
        jenjang_material.delete()
        messages.warning(request, 'Jenjang material deleted')
        return redirect('/pengasuh/' + str(code))
    else:
        return redirect('std_login')


def jenjangs(request):
    if request.session.get('siswa_id') or request.session.get('pengasuh_id'):

        jenjangs = Jenjang.objects.all()
        if request.session.get('siswa_id'):
            siswa = Siswa.objects.get(
                siswa_id=request.session['siswa_id'])
        else:
            siswa = None
        if request.session.get('pengasuh_id'):
            pengasuh = Pengasuh.objects.get(
                pengasuh_id=request.session['pengasuh_id'])
        else:
            pengasuh = None

        enrolled = siswa.jenjang.all() if siswa else None
        accessed = Jenjang.objects.filter(
            pengasuh_id=pengasuh.pengasuh_id) if pengasuh else None

        context = {
            'pengasuh': pengasuh,
            'jenjangs': jenjangs,
            'siswa': siswa,
            'enrolled': enrolled,
            'accessed': accessed
        }

        return render(request, 'main/all-jenjangs.html', context)

    else:
        return redirect('std_login')


def tahunajarans(request):
    if request.session.get('siswa_id') or request.session.get('pengasuh_id'):
        tahunajarans = TahunAjaran.objects.all()
        if request.session.get('siswa_id'):
            siswa = Siswa.objects.get(
                siswa_id=request.session['siswa_id'])
        else:
            siswa = None
        if request.session.get('pengasuh_id'):
            pengasuh = Pengasuh.objects.get(
                pengasuh_id=request.session['pengasuh_id'])
        else:
            pengasuh = None
        context = {
            'pengasuh': pengasuh,
            'siswa': siswa,
            'deps': tahunajarans
        }

        return render(request, 'main/tahunajarans.html', context)

    else:
        return redirect('std_login')


def access(request, code):
    if request.session.get('siswa_id'):
        jenjang = Jenjang.objects.get(code=code)
        siswa = Siswa.objects.get(siswa_id=request.session['siswa_id'])
        if request.method == 'POST':
            if (request.POST['key']) == str(jenjang.siswaKey):
                siswa.jenjang.add(jenjang)
                siswa.save()
                return redirect('/my/')
            else:
                messages.error(request, 'Invalid key')
                return HttpResponseRedirect(request.path_info)
        else:
            return render(request, 'main/access.html', {'jenjang': jenjang, 'siswa': siswa})

    else:
        return redirect('std_login')


def search(request):
    if request.session.get('siswa_id') or request.session.get('pengasuh_id'):
        if request.method == 'GET' and request.GET['q']:
            q = request.GET['q']
            jenjangs = Jenjang.objects.filter(Q(code__icontains=q) | Q(
                name__icontains=q) | Q(pengasuh__name__icontains=q))

            if request.session.get('siswa_id'):
                siswa = Siswa.objects.get(
                    siswa_id=request.session['siswa_id'])
            else:
                siswa = None
            if request.session.get('pengasuh_id'):
                pengasuh = Pengasuh.objects.get(
                    pengasuh_id=request.session['pengasuh_id'])
            else:
                pengasuh = None
            enrolled = siswa.jenjang.all() if siswa else None
            accessed = Jenjang.objects.filter(
                pengasuh_id=pengasuh.pengasuh_id) if pengasuh else None

            context = {
                'jenjangs': jenjangs,
                'pengasuh': pengasuh,
                'siswa': siswa,
                'enrolled': enrolled,
                'accessed': accessed,
                'q': q
            }
            return render(request, 'main/search.html', context)
        else:
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    else:
        return redirect('std_login')


def changePasswordPrompt(request):
    if request.session.get('siswa_id'):
        siswa = Siswa.objects.get(siswa_id=request.session['siswa_id'])
        return render(request, 'main/changePassword.html', {'siswa': siswa})
    elif request.session.get('pengasuh_id'):
        pengasuh = Pengasuh.objects.get(pengasuh_id=request.session['pengasuh_id'])
        return render(request, 'main/changePasswordPengasuh.html', {'pengasuh': pengasuh})
    else:
        return redirect('std_login')


def changePhotoPrompt(request):
    if request.session.get('siswa_id'):
        siswa = Siswa.objects.get(siswa_id=request.session['siswa_id'])
        return render(request, 'main/changePhoto.html', {'siswa': siswa})
    elif request.session.get('pengasuh_id'):
        pengasuh = Pengasuh.objects.get(pengasuh_id=request.session['pengasuh_id'])
        return render(request, 'main/changePhotoPengasuh.html', {'pengasuh': pengasuh})
    else:
        return redirect('std_login')


def changePassword(request):
    if request.session.get('siswa_id'):
        siswa = Siswa.objects.get(
            siswa_id=request.session['siswa_id'])
        if request.method == 'POST':
            if siswa.password == request.POST['oldPassword']:
                # New and confirm password check is done in the client side
                siswa.password = request.POST['newPassword']
                siswa.save()
                messages.success(request, 'Password was changed successfully')
                return redirect('/profile/' + str(siswa.siswa_id))
            else:
                messages.error(
                    request, 'Password is incorrect. Please try again')
                return redirect('/changePassword/')
        else:
            return render(request, 'main/changePassword.html', {'siswa': siswa})
    else:
        return redirect('std_login')


def changePasswordPengasuh(request):
    if request.session.get('pengasuh_id'):
        pengasuh = Pengasuh.objects.get(
            pengasuh_id=request.session['pengasuh_id'])
        if request.method == 'POST':
            if pengasuh.password == request.POST['oldPassword']:
                # New and confirm password check is done in the client side
                pengasuh.password = request.POST['newPassword']
                pengasuh.save()
                messages.success(request, 'Password was changed successfully')
                return redirect('/pengasuhProfile/' + str(pengasuh.pengasuh_id))
            else:
                print('error')
                messages.error(
                    request, 'Password is incorrect. Please try again')
                return redirect('/changePasswordPengasuh/')
        else:
            print(pengasuh)
            return render(request, 'main/changePasswordPengasuh.html', {'pengasuh': pengasuh})
    else:
        return redirect('std_login')


def changePhoto(request):
    if request.session.get('siswa_id'):
        siswa = Siswa.objects.get(
            siswa_id=request.session['siswa_id'])
        if request.method == 'POST':
            if request.FILES['photo']:
                siswa.photo = request.FILES['photo']
                siswa.save()
                messages.success(request, 'Photo was changed successfully')
                return redirect('/profile/' + str(siswa.siswa_id))
            else:
                messages.error(
                    request, 'Please select a photo')
                return redirect('/changePhoto/')
        else:
            return render(request, 'main/changePhoto.html', {'siswa': siswa})
    else:
        return redirect('std_login')


def changePhotoPengasuh(request):
    if request.session.get('pengasuh_id'):
        pengasuh = Pengasuh.objects.get(
            pengasuh_id=request.session['pengasuh_id'])
        if request.method == 'POST':
            if request.FILES['photo']:
                pengasuh.photo = request.FILES['photo']
                pengasuh.save()
                messages.success(request, 'Photo was changed successfully')
                return redirect('/pengasuhProfile/' + str(pengasuh.pengasuh_id))
            else:
                messages.error(
                    request, 'Please select a photo')
                return redirect('/changePhotoPengasuh/')
        else:
            return render(request, 'main/changePhotoPengasuh.html', {'pengasuh': pengasuh})
    else:
        return redirect('std_login')


def guestSiswa(request):
    request.session.flush()
    try:
        siswa = Siswa.objects.get(name='Guest Siswa')
        request.session['siswa_id'] = str(siswa.siswa_id)
        return redirect('myJenjangs')
    except:
        return redirect('std_login')


def guestPengasuh(request):
    request.session.flush()
    try:
        pengasuh = Pengasuh.objects.get(name='Guest Pengasuh')
        request.session['pengasuh_id'] = str(pengasuh.pengasuh_id)
        return redirect('pengasuhJenjangs')
    except:
        return redirect('std_login')
