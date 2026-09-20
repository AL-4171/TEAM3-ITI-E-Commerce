from django import forms
from django.contrib.auth import get_user_model

from .models import Category, Product

User = get_user_model()


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ["name", "description"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Category name",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Optional category description",
                }
            ),
        }


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            "name",
            "description",
            "price",
            "stock",
            "image",
            "category",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={"placeholder": "Product name"}
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 5,
                    "placeholder": "Product description",
                }
            ),
            "price": forms.NumberInput(
                attrs={
                    "step": "0.01",
                    "min": "0",
                }
            ),
            "stock": forms.NumberInput(
                attrs={
                    "min": "0",
                }
            ),
        }


class UserManageForm(forms.ModelForm):
    new_password = forms.CharField(
        required=False,
        label="Password",
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Enter password",
                "autocomplete": "new-password",
            }
        ),
    )

    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "mobile",
            "is_active",
            "is_staff",
            "is_superuser",
        ]
        widgets = {
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "Enter email address",
                    "autocomplete": "email",
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "placeholder": "First name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "placeholder": "Last name",
                }
            ),
            "mobile": forms.TextInput(
                attrs={
                    "placeholder": "01XXXXXXXXX",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        request_user = kwargs.pop("request_user", None)
        super().__init__(*args, **kwargs)

        # Only superusers can manage staff/superuser permissions.
        if not request_user or not request_user.is_superuser:
            self.fields.pop("is_staff", None)
            self.fields.pop("is_superuser", None)

        # ADD USER
        if not self.instance or not self.instance.pk:
            self.fields["new_password"].required = True
            self.fields["new_password"].label = "Password"
            self.fields["new_password"].widget.attrs[
                "placeholder"
            ] = "Enter password"

        # EDIT USER
        else:
            self.fields["new_password"].required = False
            self.fields["new_password"].label = "New Password"
            self.fields["new_password"].widget.attrs[
                "placeholder"
            ] = "Leave blank to keep the current password"

    def save(self, commit=True):
        user = super().save(commit=False)

        new_password = self.cleaned_data.get("new_password")

        if new_password:
            user.set_password(new_password)

        if commit:
            user.save()

        return user

