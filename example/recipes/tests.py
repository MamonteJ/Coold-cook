from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, Ingredient, Recipe, RecipeIngredient
from .services import find_recipe_matches, parse_products


class RecipeTestMixin:
    def setUp(self):
        self.user = User.objects.create_user("cook", password="secret12345")
        self.category = Category.objects.create(title="Горячее", slug="hot-test")
        self.recipe = Recipe.objects.create(
            title="Курица с картофелем",
            slug="chicken-potato-test",
            description="Простое блюдо на ужин",
            instructions="Нарезать, запечь и подать.",
            category=self.category,
            author=self.user,
            cooking_time=45,
            portions=2,
            status=Recipe.Status.PUBLISHED,
        )
        chicken = Ingredient.objects.create(name="курица")
        potato = Ingredient.objects.create(name="картофель")
        RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=chicken, amount_grams=300
        )
        RecipeIngredient.objects.create(
            recipe=self.recipe, ingredient=potato, amount_grams=500
        )


class ProductParserTests(TestCase):
    def test_parse_products_with_amounts(self):
        result = parse_products("курица 300\nкартофель")

        self.assertEqual(len(result.products), 2)
        self.assertIn("курица", result.raw_names)
        self.assertEqual(result.products[0].amount_grams, 300)


class RecipeMatchTests(RecipeTestMixin, TestCase):
    def test_find_recipe_matches_by_ingredients(self):
        matches = find_recipe_matches("курица\nкартофель")

        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].percent, 100)
        self.assertEqual(matches[0].recipe, self.recipe)

    def test_find_recipe_matches_show_missing_ingredients(self):
        matches = find_recipe_matches("курица")

        self.assertEqual(matches[0].percent, 50)
        self.assertEqual(matches[0].missing[0].ingredient.name, "картофель")


class RecipeViewTests(RecipeTestMixin, TestCase):
    def test_recipe_list_page_contains_recipe(self):
        response = self.client.get(reverse("recipe_list"))

        self.assertContains(response, "Курица с картофелем")

    def test_authenticated_user_can_comment_recipe(self):
        self.client.login(username="cook", password="secret12345")
        response = self.client.post(
            reverse("recipe_detail", kwargs={"slug": self.recipe.slug}),
            {"comment": "1", "text": "Очень вкусно"},
            follow=True,
        )

        self.assertContains(response, "Очень вкусно")
        self.assertEqual(self.recipe.comments.count(), 1)

    def test_recipe_creation_requires_login(self):
        response = self.client.get(reverse("recipe_create"))

        self.assertEqual(response.status_code, 302)
        self.assertIn("login", response.url)
