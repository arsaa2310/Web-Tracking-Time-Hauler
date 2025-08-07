from django.shortcuts import render, redirect
from django.forms.models import model_to_dict
from .models import HaulerActivity
from .forms import HaulerActivityForm
from .models import Driver, LoginLog
from datetime import timedelta, timezone, time
from datetime import datetime
from zoneinfo import ZoneInfo
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

activity_sequence = [
    "Arrived Load", "Start Load", "Finish Load",
    "Arrived Dump", "Start Dump", "Finish Dump"
]

# def activity_list(request):
#     activities = HaulerActivity.objects.all().order_by('-start_time')
#     return render(request, 'tracking/activity_list.html', {'activities': activities})

# def add_activity(request):
#     if request.method == 'POST':
#         form = HaulerActivityForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('activity_list')
#     else:
#         form = HaulerActivityForm()
#     return render(request, 'tracking/add_activity.html', {'form': form})

# views.py
@csrf_exempt
def submit_delay(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        activity = data.get('activity')
        timestamp = data.get('timestamp')
        # Simpan ke database atau log
        print(f"Delay received: {activity} at {timestamp}")
        return JsonResponse({"status": "success"})


def next_activity(request):
    if request.method == 'POST':
        driver = Driver.objects.get(id=request.session['driver_id'])
        last = HaulerActivity.objects.filter(driver=driver).order_by('-start_time').first()

        # last = HaulerActivity.objects.filter(driver=driver).order_by('-start_time').first()
        # if last:
        #     try:
        #         next_index = (activity_sequence.index(last.activity) + 1) % len(activity_sequence)
        #     except:
        #         next_index = 0
        # else:
        #     next_index = 0

        # Ambil aktivitas terakhir
        # last1 = HaulerActivity.objects.filter(driver=driver).order_by('-start_time').all()[2]
        # print(last1)
        # last = HaulerActivity.objects.filter(driver=driver).order_by('-start_time').first()
        # print(last)

        # if last.activity in activity_sequence:

        #     current_activity = last.activity if last else "Belum Mulai"

        #     # Tentukan aktivitas berikutnya
        #     if last:
        #         try:
        #             next_index = (activity_sequence.index(last.activity) + 1) % len(activity_sequence)
        #         except:
        #             next_index = 0
        #     else:
        #         next_index = 0

        #     next_activity = activity_sequence[next_index]
        
        # else:
        #     current_activity = last1.activity if last1 else "Belum Mulai"

        #     # Tentukan aktivitas berikutnya
        #     if last1:
        #         try:
        #             next_index = (activity_sequence.index(last1.activity) + 1) % len(activity_sequence)
        #         except:
        #             next_index = 0
        #     else:
        #         next_index = 0

        #     next_activity = activity_sequence[next_index]
        if last is None or last.activity is None:
            current_activity = "Belum Mulai"
            next_activity = activity_sequence[0]  # default
        else:
            if last.activity in activity_sequence:
                current_activity = last.activity
                try:
                    next_index = (activity_sequence.index(current_activity) + 1) % len(activity_sequence)
                except ValueError:
                    next_index = 0
                next_activity = activity_sequence[next_index]
            else:
                # Ambil aktivitas sebelumnya yang lebih valid
                hauler_activities = HaulerActivity.objects.filter(driver=driver).order_by('-start_time')
                last1 = hauler_activities[2] if hauler_activities.count() > 2 else None

                current_activity = last1.activity if last1 and last1.activity else "Belum Mulai"

                try:
                    next_index = (activity_sequence.index(current_activity) + 1) % len(activity_sequence)
                except ValueError:
                    next_index = 0

                next_activity = activity_sequence[next_index]

        now = datetime.now(ZoneInfo("Asia/Makassar"))
        start_day = time(7, 0)   # 07:00
        end_day = time(19, 0)    # 19:00

        shift = "DAY" if start_day <= now.time() < end_day else "NIGHT"

        HaulerActivity.objects.create(
            hauler=driver.hauler_code,
            driver=driver,
            activity=activity_sequence[next_index],
            start_time=now,
            location="Auto",  # bisa diganti dengan lokasi aktual
            shift=shift
        )
        return redirect('main_menu')

def delay_activity(request):
    if request.method == 'POST':
        delay = request.POST['activity']
        driver = Driver.objects.get(id=request.session['driver_id'])
        HaulerActivity.objects.create(
            hauler=driver.hauler_code,
            driver=driver,
            activity=delay,
            start_time=datetime.now(ZoneInfo("Asia/Makassar")),
            # finish_time=datetime.now(ZoneInfo("Asia/Makassar")),  # bisa kamu pisah jika perlu
            # total_time=timedelta(seconds=0),
            location="Auto"  # bisa diisi sesuai site
        )
        if delay == "Finish Delay":
            return redirect('main_menu')
        else:
            return redirect('delay_site')
    


# def login_driver(request):
#     if request.method == 'POST':
#         driver_id = request.POST['driver_id']
#         password = request.POST['password']
#         try:
#             driver = Driver.objects.get(driver_id=driver_id, password=password)
#             request.session['driver_id'] = driver.id
#             return redirect('main_menu')
#         except:
#             return render(request, 'tracking/login.html', {'error': 'ID atau Password salah'})
#     return render(request, 'tracking/login.html')

# activity_sequence = [
#     "Arrived Load", "Start Load", "Finish Load",
#     "Arrived Dump", "Start Dump", "Finish Dump"
# ]

def login_driver(request):
    if request.method == 'POST':
        driver_id = request.POST['driver_id']
        password = request.POST['password']
        try:
            driver = Driver.objects.get(driver_id=driver_id, password=password)

            # Simpan ID driver ke session
            request.session['driver_id'] = driver.id

            # Buat log login
            login_log = LoginLog.objects.create(driver=driver)
            request.session['login_log_id'] = login_log.id  # simpan ID log untuk logout nanti

            return redirect('main_menu')
        except:
            return render(request, 'tracking/login.html', {'error': 'ID atau Password salah'})

    return render(request, 'tracking/login.html')




def main_menu(request):
    # driver = Driver.objects.get(id=request.session['driver_id'])
    # print(driver)
    driver = Driver.objects.get(id=request.session['driver_id'])
    print(model_to_dict(driver))
    # Ambil aktivitas terakhir
    # print(last1)
    last = HaulerActivity.objects.filter(driver=driver).order_by('-start_time').first()
    # print(last)
    # if last is None or last.activity is None:
    #     current_activity = "Belum Mulai"
    # else:
    #     current_activity = last.activity
    #     if last.activity in activity_sequence:

    #         current_activity = last.activity if last else "Belum Mulai"

    #         # Tentukan aktivitas berikutnya
    #         if last:
    #             try:
    #                 next_index = (activity_sequence.index(last.activity) + 1) % len(activity_sequence)
    #             except:
    #                 next_index = 0
    #         else:
    #             next_index = 0

    #         next_activity = activity_sequence[next_index]
        
    #     else:
    #         last1 = HaulerActivity.objects.filter(driver=driver).order_by('-start_time').all()[2]

    #         current_activity = last1.activity if last1 else "Belum Mulai"

    #         # Tentukan aktivitas berikutnya
    #         if last1:
    #             try:
    #                 next_index = (activity_sequence.index(last1.activity) + 1) % len(activity_sequence)
    #             except:
    #                 next_index = 0
    #         else:
    #             next_index = 0

    #         next_activity = activity_sequence[next_index]
    if last is None or last.activity is None:
        current_activity = "Belum Mulai"
        next_activity = activity_sequence[0]  # default
    else:
        if last.activity in activity_sequence:
            current_activity = last.activity
            try:
                next_index = (activity_sequence.index(current_activity) + 1) % len(activity_sequence)
            except ValueError:
                next_index = 0
            next_activity = activity_sequence[next_index]
        else:
            # Ambil aktivitas sebelumnya yang lebih valid
            hauler_activities = HaulerActivity.objects.filter(driver=driver).order_by('-start_time')
            last1 = hauler_activities[2] if hauler_activities.count() > 2 else None

            current_activity = last1.activity if last1 and last1.activity else "Belum Mulai"

            try:
                next_index = (activity_sequence.index(current_activity) + 1) % len(activity_sequence)
            except ValueError:
                next_index = 0

            next_activity = activity_sequence[next_index]



    return render(request, 'tracking/main_menu.html', {
        'driver': driver,
        'current_activity': current_activity,
        'activity_button_label': next_activity,
        # 'location' : last.location,
        'location': last.location if last else '-',
        'shift' : last.shift,

    })


list_delay = [
    'REFUELING', 'WAIT BLASTING', 'WAIT FOR FUEL', 'OPERATOR CHANGE', 'TYRE CHECK', 'BENCH CLEANUP', 'WASTE DUMP PREPARATION', 'TOILET',
    'STUCK/AMBLAS', 'WAIT EXCAVATOR', 'WAIT LOCATION', 'WAIT LIGHTING', 'PRESTART CHECK UNIT', 'DUSTY', 'WASHING EQUIPMENT', 'DELAY TRANSPORT',
    'COFFE TIME', 'TEST FATIGUE', 'NO JOBS', 'NO OPERATOR', 'PRAYING', 'MEAL', 'SHIFT CHANGE', 'FRIDAY PRAYING AND MEAL', 'SAFETY MEETING', 'NO MATERIAL',
    'NO LOCATION', 'BUKA PUASA', 'WAIT FOR MATERIAL/TUNGGU MATERIAL', 'RAIN', 'SLIPPERY', 'FOG' 
]

def delay_site(request):
    driver = Driver.objects.get(id=request.session['driver_id'])

    # Ambil aktivitas terakhir
    last = HaulerActivity.objects.filter(driver=driver).order_by('-start_time').first()
    current_activity = last.activity if last else "Belum Mulai"

    # Tentukan aktivitas berikutnya
    if last:
        try:
            next_index = (activity_sequence.index(last.activity) + 1) % len(activity_sequence)
        except:
            next_index = 0
    else:
        next_index = 0

    next_activity = activity_sequence[next_index]

    return render(request, 'tracking/delay.html', {
        'driver': driver,
        'current_activity': current_activity,
        'activity_button_label': next_activity,
        'delay_list' : list_delay,

    })

    # return render(request, 'tracking/delay.html', {
    # })

# def logout_driver(request):
#     request.session.flush()
#     return redirect('login_driver')

def logout_driver(request):
    login_log_id = request.session.get('login_log_id')

    if login_log_id:
        try:
            log = LoginLog.objects.get(id=login_log_id)
            log.logout_time = datetime.now(ZoneInfo("Asia/Makassar"))
            log.save()
        except LoginLog.DoesNotExist:
            pass

    request.session.flush()
    return redirect('login_driver')