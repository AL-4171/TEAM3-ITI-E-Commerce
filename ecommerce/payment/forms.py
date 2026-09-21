from django import forms

class PaymentForm(forms.Form):
    PAYMENT_METHOD_CHOICES = [
        ('credit_card', 'Credit Card'),
        ('wallet', 'Mobile Wallet'),
        ('cash_on_delivery', 'Cash on Delivery'),
    ]

    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={'class': 'admin-input', 'id': 'id_payment_method'})
    )

    card_number = forms.CharField(
        max_length=16,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'admin-input',
            'id': 'id_card_number',
            'placeholder': '16-digit Card Number',
            'maxlength': '16',
            'inputmode': 'numeric',
            'autocomplete': 'off'
        })
    )
    expiry_date = forms.CharField(
        max_length=5,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'admin-input',
            'id': 'id_card_expiry',
            'placeholder': 'MM/YY',
            'maxlength': '5',
            'inputmode': 'numeric',
            'autocomplete': 'off'
        })
    )
    cvv = forms.CharField(
        max_length=3,
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'admin-input',
            'id': 'id_cvv',
            'placeholder': '123',
            'maxlength': '3',
            'autocomplete': 'off'
        })
    )

    wallet_number = forms.CharField(
        max_length=11,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'admin-input',
            'id': 'id_wallet_number',
            'placeholder': '01XXXXXXXXX',
            'maxlength': '11',
            'inputmode': 'numeric'
        })
    )
    wallet_password = forms.CharField(
       max_length=8,
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'admin-input',
            'id': 'id_wallet_password',
            'placeholder': ' ',
            'maxlength': '8',
            'inputmode': 'numeric'
        })
    )

    def clean(self):
        cleaned_data = super().clean()
        method = cleaned_data.get('payment_method')

        if method == 'credit_card':
            card_number = cleaned_data.get('card_number')
            expiry_date = cleaned_data.get('expiry_date')
            cvv = cleaned_data.get('cvv')

            if not card_number or len(card_number) != 16 or not card_number.isdigit():
                self.add_error('card_number', 'Card number must be exactly 16 digits.')

            if not expiry_date or len(expiry_date) != 5 or '/' not in expiry_date:
                self.add_error('expiry_date', 'Enter a valid date in MM/YY format.')

            if not cvv or len(cvv) != 3 or not cvv.isdigit():
                self.add_error('cvv', 'CVV must be 3 digits.')

        elif method == 'wallet':
            wallet_number = cleaned_data.get('wallet_number')
            wallet_password = cleaned_data.get('wallet_password')

            if not wallet_number or len(wallet_number) != 11 or not wallet_number.isdigit():
                self.add_error('wallet_number', 'Wallet number must be exactly 11 digits.')

            if not wallet_password or len(wallet_password) != 8 or not wallet_password.isdigit():
                self.add_error('wallet_password', ' ')

        return cleaned_data