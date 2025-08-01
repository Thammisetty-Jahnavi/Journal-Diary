from django.shortcuts import render, redirect, get_object_or_404
from .forms import JournalEntryForm, UserRegisterForm
from .models import JournalEntry
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import Q
from django.core.paginator import Paginator

from datetime import datetime

@login_required
def home(request):
    query = request.GET.get('q', '').strip()
    entries = JournalEntry.objects.filter(user=request.user).order_by('date_created')

    result_message = None

    if query:
        # Check if query is a valid page number
        try:
            page_num = int(query)
            if page_num > 0 and page_num <= entries.count():
                # Get that single entry
                selected_entry = entries[page_num - 1]  # 0-based index
                entries = [selected_entry]
                result_message = f'Showing page {page_num} of your journal'
            else:
                result_message = f'No entry found at page {page_num}.'
                entries = []
        except ValueError:
            # Not a page number, try as text or date
            try:
                parsed_date = datetime.strptime(query, "%Y-%m-%d").date()
                entries = entries.filter(
                    Q(title__icontains=query) |
                    Q(content__icontains=query) |
                    Q(date_created__date=parsed_date)
                )
            except ValueError:
                # Not a date either — fallback to text search
                entries = entries.filter(
                    Q(title__icontains=query) |
                    Q(content__icontains=query)
                )
            result_message = f'Showing results for “{query}”'

    paginator = Paginator(entries, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'journal/home.html', {
        'page_obj': page_obj,
        'query': query,
        'result_message': result_message,
    })

# --------------------
# Home view (with search + pagination + ordering)
# --------------------

'''
#HI
@login_required
def home(request):
    query = request.GET.get('q', '')
    entries = JournalEntry.objects.filter(user=request.user)

    if query:
        entries = entries.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(date_created__icontains=query)
        )

    entries = entries.order_by('date_created')  # oldest first

    paginator = Paginator(entries, 10)  # 10 entries per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'journal/home.html', {
        'page_obj': page_obj,
        'query': query,
    })'''


# --------------------
# Add Entry view
# --------------------
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


# --------------------
# Register view
# --------------------
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


# --------------------
# Entry Detail view (with accurate page number)
# --------------------

@login_required
def entry_detail(request, entry_id):
    # Order by date_created ASC to match home page
    entries = list(JournalEntry.objects.filter(user=request.user).order_by('date_created'))
    entry = get_object_or_404(JournalEntry, pk=entry_id, user=request.user)

    try:
        current_index = entries.index(entry)
    except ValueError:
        current_index = 0

    # 👇 Page number is entry's position in list (1-based)
    page_number = current_index + 1

    previous_entry = entries[current_index - 1] if current_index > 0 else None
    next_entry = entries[current_index + 1] if current_index < len(entries) - 1 else None

    return render(request, 'journal/entry_detail.html', {
        'entry': entry,
        'page_number': page_number,
        'previous_entry': previous_entry,
        'next_entry': next_entry
    })

