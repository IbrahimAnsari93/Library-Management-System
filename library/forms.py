from django import forms
from .models import Student, Book


class StudentForm(forms.ModelForm):

    class Meta:
        model = Student

        fields = [
            "name",
            "roll_no",
            "email",
            "phone",
        ]

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter student full name",
                }
            ),

            "roll_no": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter roll number",
                }
            ),

            "email": forms.EmailInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "student@example.com",
                }
            ),

            "phone": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter 10 digit phone number",
                }
            ),
        }

    def clean_phone(self):
        phone = self.cleaned_data["phone"]

        if not phone.isdigit():
            raise forms.ValidationError(
                "Phone number must contain only digits."
            )

        if len(phone) != 10:
            raise forms.ValidationError(
                "Phone number must be exactly 10 digits."
            )

        return phone


class BookForm(forms.ModelForm):

    class Meta:
        model = Book

        fields = [
            "title",
            "author",
            "isbn",
            "category",
            "publisher",
            "publication_year",
            "language",
            "edition",
            "description",
            "shelf_number",
            "rack_number",
            "quantity",
            "cover_image",
        ]

        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter book title",
                }
            ),

            "author": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter author name",
                }
            ),

            "isbn": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter ISBN",
                }
            ),

            "category": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. Programming, AI, Database",
                }
            ),

            "publisher": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter publisher name",
                }
            ),

            "publication_year": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 2025",
                    "min": "1000",
                    "max": "2100",
                }
            ),

            "language": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. English",
                }
            ),

            "edition": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. 3rd Edition",
                }
            ),

            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter book description",
                    "rows": 5,
                }
            ),

            "shelf_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. S-01",
                }
            ),

            "rack_number": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "e.g. R-01",
                }
            ),

            "quantity": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter quantity",
                    "min": "1",
                }
            ),

            "cover_image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": "image/jpeg,image/png,image/webp",
                }
            ),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data["quantity"]

        if quantity < 1:
            raise forms.ValidationError(
                "Quantity must be at least 1."
            )

        return quantity

    def clean_publication_year(self):
        year = self.cleaned_data.get("publication_year")

        if year is not None:
            if year < 1000 or year > 2100:
                raise forms.ValidationError(
                    "Enter a valid publication year."
                )

        return year

    def clean_cover_image(self):
        image = self.cleaned_data.get("cover_image")

        if not image:
            return image

        if hasattr(image, "content_type"):
                                      
            max_size = 5 * 1024 * 1024

            if image.size > max_size:
                raise forms.ValidationError(
                    "Cover image must be less than 5 MB."
                )

                                   
            allowed_types = [
                "image/jpeg",
                "image/png",
                "image/webp",
            ]

            if image.content_type not in allowed_types:
                raise forms.ValidationError(
                    "Only JPG, PNG and WEBP images are allowed."
                )

        return image
