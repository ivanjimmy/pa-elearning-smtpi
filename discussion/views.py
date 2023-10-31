from django.shortcuts import redirect, render
from discussion.models import PengasuhDiscussion, SiswaDiscussion
from main.models import Siswa, Pengasuh, Jenjang
from main.views import is_pengasuh_authorised, is_siswa_authorised
from itertools import chain
from .forms import SiswaDiscussionForm, PengasuhDiscussionForm


# Create your views here.


''' We have two different user models.
    That's why we are filtering the discussions based on the user type and then combining them.'''


def context_list(jenjang):
    try:
        siswaDis = SiswaDiscussion.objects.filter(jenjang=jenjang)
        pengasuhDis = PengasuhDiscussion.objects.filter(jenjang=jenjang)
        discussions = list(chain(siswaDis, pengasuhDis))
        discussions.sort(key=lambda x: x.sent_at, reverse=True)

        for dis in discussions:
            if dis.__class__.__name__ == 'SiswaDiscussion':
                dis.author = Siswa.objects.get(siswa_id=dis.sent_by_id)
            else:
                dis.author = Pengasuh.objects.get(pengasuh_id=dis.sent_by_id)
    except:

        discussions = []

    return discussions


def discussion(request, code):
    if is_siswa_authorised(request, code):
        jenjang = Jenjang.objects.get(code=code)
        siswa = Siswa.objects.get(siswa_id=request.session['siswa_id'])
        discussions = context_list(jenjang)
        form = SiswaDiscussionForm()
        context = {
            'jenjang': jenjang,
            'siswa': siswa,
            'discussions': discussions,
            'form': form,
        }
        return render(request, 'discussion/discussion.html', context)

    elif is_pengasuh_authorised(request, code):
        jenjang = Jenjang.objects.get(code=code)
        pengasuh = Pengasuh.objects.get(pengasuh_id=request.session['pengasuh_id'])
        discussions = context_list(jenjang)
        form = PengasuhDiscussionForm()
        context = {
            'jenjang': jenjang,
            'pengasuh': pengasuh,
            'discussions': discussions,
            'form': form,
        }
        return render(request, 'discussion/discussion.html', context)
    else:
        return redirect('std_login')


def send(request, code, std_id):
    if is_siswa_authorised(request, code):
        if request.method == 'POST':
            form = SiswaDiscussionForm(request.POST)
            if form.is_valid():
                content = form.cleaned_data['content']
                jenjang = Jenjang.objects.get(code=code)
                try:
                    siswa = Siswa.objects.get(siswa_id=std_id)
                except:
                    return redirect('discussion', code=code)
                SiswaDiscussion.objects.create(
                    content=content, jenjang=jenjang, sent_by=siswa)
                return redirect('discussion', code=code)
            else:
                return redirect('discussion', code=code)
        else:
            return redirect('discussion', code=code)
    else:
        return render(request, 'std_login.html')


def send_fac(request, code, fac_id):
    if is_pengasuh_authorised(request, code):
        if request.method == 'POST':
            form = PengasuhDiscussionForm(request.POST)
            if form.is_valid():
                content = form.cleaned_data['content']
                jenjang = Jenjang.objects.get(code=code)
                try:
                    pengasuh = Pengasuh.objects.get(pengasuh_id=fac_id)
                except:
                    return redirect('discussion', code=code)
                PengasuhDiscussion.objects.create(
                    content=content, jenjang=jenjang, sent_by=pengasuh)
                return redirect('discussion', code=code)
            else:
                return redirect('discussion', code=code)
        else:
            return redirect('discussion', code=code)
    else:
        return render(request, 'std_login.html')
