from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model


User = get_user_model()


class RegisterForm(forms.ModelForm):

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter your password"
            }
        )
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm your password"
            }
        )
    )


    class Meta:

        model = User

        fields = [
            "first_name",
            "last_name",
            "email",
            "mobile",
            "password"
        ]

        widgets = {

            "first_name": forms.TextInput(
                attrs={
                    "placeholder": "First name"
                }
            ),

            "last_name": forms.TextInput(
                attrs={
                    "placeholder": "Last name"
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Enter your email"
                }
            ),

            "mobile": forms.TextInput(
                attrs={
                    "placeholder": "01XXXXXXXXX"
                }
            ),
        }


    def clean_email(self):

        email = self.cleaned_data["email"]

        if User.objects.filter(email=email).exists():

            raise forms.ValidationError(
                "This email is already registered."
            )

        return email


    def clean_mobile(self):

        mobile = self.cleaned_data["mobile"]

        if len(mobile) != 11 or not mobile.isdigit():

            raise forms.ValidationError(
                "Enter a valid Egyptian mobile number."
            )

        if not mobile.startswith(
            ("010", "011", "012", "015")
        ):

            raise forms.ValidationError(
                "Enter a valid Egyptian mobile number."
            )

        return mobile


    def clean(self):

        cleaned_data = super().clean()

        password = cleaned_data.get("password")

        confirm_password = cleaned_data.get(
            "confirm_password"
        )

        if password and confirm_password:

            if password != confirm_password:

                raise forms.ValidationError(
                    "Passwords do not match."
                )

        return cleaned_data


    def save(self, commit=True):

        user = super().save(commit=False)

        user.set_password(
            self.cleaned_data["password"]
        )

        if commit:

            user.save()

        return user


class LoginForm(AuthenticationForm):

    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Enter your email"
            }
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter your password"
            }
        )
    )