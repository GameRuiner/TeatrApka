from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q, Avg
from datetime import datetime, date
from .models import Performance

def home(request):
    """Main page with performances list and filters"""
    performances = Performance.objects.all()
    print(len(performances))
    # theatres = Theatre.objects.all()
    # performances = Performance.objects.select_related('theatre').all()
    # print(performances)
    
    # # Filter by theatre
    # theatre_id = request.GET.get('theatre')
    # if theatre_id:
    #     performances = performances.filter(theatre_id=theatre_id)
    
    # # Filter by date range
    # start_date = request.GET.get('start_date')
    # end_date = request.GET.get('end_date')
    
    # if start_date:
    #     try:
    #         start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    #         performances = performances.filter(date__gte=start_date)
    #     except ValueError:
    #         pass
    
    # if end_date:
    #     try:
    #         end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    #         performances = performances.filter(date__lte=end_date)
    #     except ValueError:
    #         pass
    
    # # Filter by status
    # status = request.GET.get('status')
    # if status:
    #     performances = performances.filter(status=status)
    
    # # Search by title
    # search = request.GET.get('search')
    # if search:
    #     performances = performances.filter(title__icontains=search)
    
    # # # Add average rating to each performance
    # # for performance in performances:
    # #     performance.avg_rating = performance.reviews.aggregate(Avg('rating'))['rating__avg']
    
    context = {
    #     # 'theatres': theatres,
        'performances': performances,
    #     'status_choices': Performance.STATUS_CHOICES,
    #     'selected_theatre': theatre_id,
    #     'selected_status': status,
    #     'start_date': start_date,
    #     'end_date': end_date,
    #     'search_query': search,
    }
    
    return render(request, 'theatre_app/home.html', context)

def performance_detail(request, performance_id):
    """Detailed view of a single performance"""
    performance = get_object_or_404(Performance, id=performance_id)
    reviews = performance.reviews.all()
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg']
    
    context = {
        'performance': performance,
        'reviews': reviews,
        'avg_rating': avg_rating,
    }
    
    return render(request, 'theatre_app/performance_detail.html', context)

def api_performances(request):
    """API endpoint for AJAX requests"""
    performances = Performance.objects.select_related('theatre').all()
    
    # Apply filters similar to home view
    theatre_id = request.GET.get('theatre')
    if theatre_id:
        performances = performances.filter(theatre_id=theatre_id)
    
    start_date = request.GET.get('start_date')
    if start_date:
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            performances = performances.filter(date__gte=start_date)
        except ValueError:
            pass
    
    end_date = request.GET.get('end_date')
    if end_date:
        try:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            performances = performances.filter(date__lte=end_date)
        except ValueError:
            pass
    
    data = []
    for perf in performances:
        data.append({
            'id': perf.id,
            'title': perf.title,
            'theatre': perf.theatre.name,
            'date': perf.date.strftime('%Y-%m-%d'),
            'time': perf.time.strftime('%H:%M'),
            'status': perf.status,
            'is_available': perf.is_available,
        })
    
    return JsonResponse({'performances': data})