from django import forms
from .models import Party, PollingUnit

class NewResultForm(forms.Form):
    polling_unit = forms.ModelChoiceField(queryset=PollingUnit.objects.all(), label="Polling Unit")
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Dynamically add fields for each party
        parties = Party.objects.all()
        for party in parties:
            self.fields[f'party_{party.partyid}'] = forms.IntegerField(
                label=party.partyname,
                min_value=0,
                required=True
            )