from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import *

# Create your views here.

def home(request):
    return render(request, 'index.html')

# Question 1: Display results for individual polling unit
def polling_unit_result(request):
    polling_unit_id = request.GET.get('polling_unit_id')
    results = None
    polling_unit = None
    
    if polling_unit_id:
        try:
            # Note we're using uniqueid which matches announced_pu_results.polling_unit_uniqueid
            polling_unit = PollingUnit.objects.get(uniqueid=polling_unit_id)
            results = AnnouncedPuResults.objects.filter(polling_unit_uniqueid=polling_unit.uniqueid)
        except PollingUnit.DoesNotExist:
            pass
    
    context = {
        'polling_unit': polling_unit,
        'results': results,
    }
    return render(request, 'polling_unit_result.html', context)

# Question 2: Summed total result for all polling units in an LGA
def lga_results(request):
    lgas = Lga.objects.all()
    selected_lga = None
    summed_results = None
    
    if request.method == 'POST':
        lga_id = request.POST.get('lga_id')
        if lga_id:
            selected_lga = Lga.objects.get(lga_id=lga_id)
            # Get all polling units in this LGA
            polling_units = PollingUnit.objects.filter(lga=selected_lga)
            
            # Sum results for each party across all polling units
            summed_results = {}
            for pu in polling_units:
                results = AnnouncedPuResults.objects.filter(polling_unit_uniqueid=pu.polling_unit_uniqueid)
                for result in results:
                    if result.party_abbreviation in summed_results:
                        summed_results[result.party_abbreviation] += result.party_score
                    else:
                        summed_results[result.party_abbreviation] = result.party_score
    
    context = {
        'lgas': lgas,
        'selected_lga': selected_lga,
        'summed_results': summed_results,
    }
    return render(request, 'lga_results.html', context)

# Question 3: Store results for a new polling unit
def new_polling_unit(request):
    lgas = Lga.objects.all()
    wards = Ward.objects.none()  # Empty queryset by default
    parties = Party.objects.all()
    
    if request.method == 'GET' and 'lga_id' in request.GET:
        lga_id = request.GET.get('lga_id')
        wards = Ward.objects.filter(lga_id=lga_id)
        return render(request, 'ward_dropdown.html', {'wards': wards})
    
    if request.method == 'POST':
        # Create new polling unit
        polling_unit_name = request.POST.get('polling_unit_name')
        ward_id = request.POST.get('ward_id')
        lga_id = request.POST.get('lga_id')
        
        ward = Ward.objects.get(ward_id=ward_id)
        lga = Lga.objects.get(lga_id=lga_id)
        state = lga.state
        
        # Get the next available polling_unit_id
        max_id = PollingUnit.objects.all().order_by('-polling_unit_id').first()
        new_id = max_id.polling_unit_id + 1 if max_id else 1
        
        # Create the polling unit
        polling_unit = PollingUnit.objects.create(
            polling_unit_id=new_id,
            polling_unit_uniqueid=new_id,  # For simplicity, using same as ID
            polling_unit_name=polling_unit_name,
            ward=ward,
            lga=lga,
            state=state
        )
        
        # Save results for each party
        for party in parties:
            score = request.POST.get(f'party_{party.partyid}')
            if score and score.isdigit():
                AnnouncedPuResults.objects.create(
                    polling_unit_uniqueid=polling_unit.polling_unit_uniqueid,
                    party_abbreviation=party.partyid,
                    party_score=int(score),
                    entered_by_user=request.user.username if request.user.is_authenticated else 'anonymous',
                    user_ip_address=request.META.get('REMOTE_ADDR', '')
                )
        
        return redirect('polling_unit_result') + f'?polling_unit_id={new_id}'
    
    context = {
        'lgas': lgas,
        'parties': parties,
    }
    return render(request, 'new_polling_unit.html', context)