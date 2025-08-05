from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import Q
from django.core.paginator import Paginator
from datetime import datetime

from .forms import (
    JournalEntryForm, UserRegisterForm, UserUpdateForm,
    ProfileUpdateForm, ReminderForm
)
from .models import JournalEntry, Profile, Reminder


@login_required
def home(request):
    query = request.GET.get('q', '').strip()
    entries = JournalEntry.objects.filter(user=request.user).order_by('date_created')
    total_entries = entries.count()

    reminders = Reminder.objects.filter(user=request.user).order_by('date')
    result_message = None

    if query:
        try:
            page_num = int(query)
            if page_num > 0 and page_num <= entries.count():
                selected_entry = entries[page_num - 1]
                entries = [selected_entry]
                result_message = f'Showing page {page_num} of your journal'
            else:
                result_message = f'No entry found at page {page_num}.'
                entries = []
        except ValueError:
            try:
                parsed_date = datetime.strptime(query, "%Y-%m-%d").date()
                entries = entries.filter(
                    Q(title__icontains=query) |
                    Q(content__icontains=query) |
                    Q(date_created__startswith=parsed_date.isoformat())

                )
            except ValueError:
                entries = entries.filter(
                    Q(title__icontains=query) |
                    Q(content__icontains=query)
                )
            result_message = f'Showing results for “{query}”'

    paginator = Paginator(entries, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    start_index = page_obj.start_index()
    for idx, entry in enumerate(page_obj.object_list, start=start_index):
        entry.page_number = idx
    # ✅ NEW: Get reminder dates as strings like '2025-08-05'
    reminder_dates = [r.date.strftime('%Y-%m-%d') for r in reminders]

    return render(request, 'journal/home.html', {
        'page_obj': page_obj,
        'query': query,
        'result_message': result_message,
        'reminders': reminders,
        'reminder_dates': reminder_dates,
        'total_entries': total_entries,# ✅ Pass to template
    })


@login_required
def add_entry(request):
    if request.method == 'POST':
        form = JournalEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            return redirect('home')
    else:
        form = JournalEntryForm()
    return render(request, 'journal/add_entry.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'journal/register.html', {'form': form})


@login_required
def entry_detail(request, entry_id):
    entries = list(JournalEntry.objects.filter(user=request.user).order_by('date_created'))
    entry = get_object_or_404(JournalEntry, pk=entry_id, user=request.user)

    try:
        current_index = entries.index(entry)
    except ValueError:
        current_index = 0

    page_number = current_index + 1
    previous_entry = entries[current_index - 1] if current_index > 0 else None
    next_entry = entries[current_index + 1] if current_index < len(entries) - 1 else None

    return render(request, 'journal/entry_detail.html', {
        'entry': entry,
        'page_number': page_number,
        'previous_entry': previous_entry,
        'next_entry': next_entry
    })


@login_required
def profile_view(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'journal/profile.html', {
        'u_form': u_form,
        'p_form': p_form
    })


@login_required
def calendar_view(request):
    return render(request, 'journal/calendar.html')



@login_required
def add_reminder(request):
    if request.method == 'POST':
        form = ReminderForm(request.POST)
        if form.is_valid():
            reminder = form.save(commit=False)
            reminder.user = request.user
            reminder.save()
    return redirect('home')



@login_required
def delete_reminder(request, reminder_id):
    reminder = get_object_or_404(Reminder, id=reminder_id, user=request.user)
    if request.method == 'POST':
        reminder.delete()
        return redirect('home')
    return render(request, 'journal/delete_reminder.html', {'reminder': reminder})
