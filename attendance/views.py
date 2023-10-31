from django.contrib import messages
from django.shortcuts import render, redirect
from . models import Attendance
from main.models import Siswa, Jenjang, Pengasuh
from main.views import is_pengasuh_authorised


def attendance(request, code):
    if is_pengasuh_authorised(request, code):
        jenjang = Jenjang.objects.get(code=code)
        siswas = Siswa.objects.filter(jenjang__code=code)

        return render(request, 'attendance/attendance.html', {'siswas': siswas, 'jenjang': jenjang, 'pengasuh': Pengasuh.objects.get(jenjang=jenjang)})


def createRecord(request, code):
    if is_pengasuh_authorised(request, code):
        if request.method == 'POST':
            date = request.POST['dateCreate']
            jenjang = Jenjang.objects.get(code=code)
            siswas = Siswa.objects.filter(jenjang__code=code)
            # check if attendance record already exists for the date
            if Attendance.objects.filter(date=date, jenjang=jenjang).exists():
                return render(request, 'attendance/attendance.html', {'code': code, 'siswas': siswas, 'jenjang': jenjang, 'pengasuh': Pengasuh.objects.get(jenjang=jenjang), 'error': "Attendance record already exists for the date " + date})
            else:
                for siswa in siswas:
                    attendance = Attendance(
                        siswa=siswa, jenjang=jenjang, date=date, status=False)
                    attendance.save()

                messages.success(
                    request, 'Attendance record created successfully for the date ' + date)
                return redirect('/attendance/' + str(code))
        else:
            return redirect('/attendance/' + str(code))
    else:
        return redirect('std_login')


def loadAttendance(request, code):
    if is_pengasuh_authorised(request, code):
        if request.method == 'POST':
            date = request.POST['date']
            jenjang = Jenjang.objects.get(code=code)
            siswas = Siswa.objects.filter(jenjang__code=code)
            attendance = Attendance.objects.filter(jenjang=jenjang, date=date)
            # check if attendance record exists for the date
            if attendance.exists():
                return render(request, 'attendance/attendance.html', {'code': code, 'siswas': siswas, 'jenjang': jenjang, 'pengasuh': Pengasuh.objects.get(jenjang=jenjang), 'attendance': attendance, 'date': date})
            else:
                return render(request, 'attendance/attendance.html', {'code': code, 'siswas': siswas, 'jenjang': jenjang, 'pengasuh': Pengasuh.objects.get(jenjang=jenjang), 'error': 'Could not load. Attendance record does not exist for the date ' + date})

    else:
        return redirect('std_login')


def submitAttendance(request, code):
    if is_pengasuh_authorised(request, code):
        try:
            siswas = Siswa.objects.filter(jenjang__code=code)
            jenjang = Jenjang.objects.get(code=code)
            if request.method == 'POST':
                date = request.POST['datehidden']
                for siswa in siswas:
                    attendance = Attendance.objects.get(
                        siswa=siswa, jenjang=jenjang, date=date)
                    if request.POST.get(str(siswa.siswa_id)) == '1':
                        attendance.status = True
                    else:
                        attendance.status = False
                    attendance.save()
                messages.success(
                    request, 'Attendance record submitted successfully for the date ' + date)
                return redirect('/attendance/' + str(code))

            else:
                return render(request, 'attendance/attendance.html', {'code': code, 'siswas': siswas, 'jenjang': jenjang, 'pengasuh': Pengasuh.objects.get(jenjang=jenjang)})
        except:
            return render(request, 'attendance/attendance.html', {'code': code, 'error': "Error! could not save", 'siswas': siswas, 'jenjang': jenjang, 'pengasuh': Pengasuh.objects.get(jenjang=jenjang)})
