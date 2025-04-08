from django import forms
from .models import CustomUser

class TransactionForm(forms.Form):
    recipient_email = forms.EmailField(label="Recipient Email", max_length=255)
    amount = forms.DecimalField(label="Amount", max_digits=10, decimal_places=2)
    description = forms.CharField(label="Description (Optional)", required=False, widget=forms.Textarea)


    
    # The sender and currency will be managed by the backend (view)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Get the logged-in user passed to the form

        super().__init__(*args, **kwargs)

        if user:
            # Set the sender as the logged-in user and pre-fill the currency field with the user's registered currency
            self.fields['currency'] = forms.ChoiceField(
                choices=[(user.currency, user.currency)],  # Only show the user's currency
                initial=user.currency,
                widget=forms.HiddenInput()  # Hide the field as it is not editable
            )


class AdminUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'email', 'first_name', 'last_name']
        widgets = {
            'password': forms.PasswordInput(),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_staff = True  # Assign as admin
        if commit:
            user.save()
        return user
    




