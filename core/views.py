from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import *
from django.db.models import Sum
from .forms import NewResultForm

# Create your views here.

def home(request):
    return render(request, 'index.html')

# Question 1: Display results for individual polling unit
def polling_unit_result(request, polling_unit_id):
    # Get the polling unit
    try:
        polling_unit = PollingUnit.objects.get(polling_unit_id=polling_unit_id)
    except PollingUnit.DoesNotExist:
        return render(request, 'error.html', {'message': 'Polling unit not found'})
    
    # Get results for this polling unit
    results = AnnouncedPuResults.objects.filter(polling_unit_uniqueid=polling_unit.uniqueid)
    
    context = {
        'polling_unit': polling_unit,
        'results': results,
    }
    return render(request, 'polling_unit_result.html', context)

# Question 2: Summed total result for all polling units in an LGA

def lga_results(request):
    lgas = Lga.objects.filter(state_id=25)  # Only Delta State LGAs
    
    selected_lga = None
    results = None
    
    if request.method == 'POST':
        lga_id = request.POST.get('lga_id')
        selected_lga = Lga.objects.get(lga_id=lga_id)
        
        # Get all polling units in this LGA
        polling_units = PollingUnit.objects.filter(lga_id=lga_id)
        
        # Get results for all polling units in this LGA
        results = AnnouncedPuResults.objects.filter(
            polling_unit_uniqueid__in=polling_units.values_list('uniqueid', flat=True)
        ).values('party_abbreviation').annotate(total_score=Sum('party_score')).order_by('party_abbreviation')
    
    context = {
        'lgas': lgas,
        'selected_lga': selected_lga,
        'results': results,
    }
    return render(request, 'lga_results.html', context)

# Question 3: Store results for a new polling unit
def new_polling_unit(request):
    if request.method == 'POST':
        form = NewResultForm(request.POST)
        if form.is_valid():
            polling_unit = form.cleaned_data['polling_unit']
            
            # Save results for each party
            parties = Party.objects.all()
            for party in parties:
                score = form.cleaned_data[f'party_{party.partyid}']
                
                AnnouncedPuResults.objects.create(
                    polling_unit_uniqueid=polling_unit.uniqueid,
                    party_abbreviation=party.partyid,
                    party_score=score,
                    entered_by_user=request.user.username if request.user.is_authenticated else 'Anonymous',
                    user_ip_address=request.META.get('REMOTE_ADDR')
                )
            
            return redirect('success_page')
    else:
        form = NewResultForm()
    
    return render(request, 'new_polling_unit.html', {'form': form})