from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Comment, Rating, Recipe, Report


class SignUpForm(UserCreationForm):
    email = forms.EmailField(label="Электронная почта", required=False)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")


class RecipeForm(forms.ModelForm):
    ingredients_text = forms.CharField(
        label="Ингредиенты",
        widget=forms.Textarea(
            attrs={
                "rows": 7,
                "placeholder": "картофель 500\nкурица 300\nсоль",
            }
        ),
        help_text="Каждый ингредиент с новой строки. Граммовка необязательна.",
    )

    class Meta:
        model = Recipe
        fields = [
            "title",
            "slug",
            "description",
            "category",
            "instructions",
            "cooking_time",
            "portions",
            "difficulty",
            "image",
        ]


class ProductSearchForm(forms.Form):
    products = forms.CharField(
        label="Какие продукты есть?",
        widget=forms.Textarea(
            attrs={
                "rows": 5,
                "placeholder": "курица 300\nкартофель\nсыр 100",
            }
        ),
    )


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["text"]
        widgets = {"text": forms.Textarea(attrs={"rows": 3})}


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ["score"]


class ReportForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ["reason"]
        widgets = {"reason": forms.Textarea(attrs={"rows": 3})}
