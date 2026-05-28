import re
from dataclasses import dataclass

from django.db.models import Count, Q

from .models import Ingredient, Recipe, RecipeIngredient


@dataclass(frozen=True)
class ProductInput:
    name: str
    amount_grams: int | None = None


@dataclass(frozen=True)
class MatchResult:
    recipe: Recipe
    matched_count: int
    total_count: int
    percent: int
    missing: list[RecipeIngredient]


@dataclass(frozen=True)
class ParseResult:
    products: list[ProductInput]
    raw_names: set[str]


def normalize_name(value):
    return " ".join(value.lower().strip().split())


def parse_products(raw_text):
    products = []
    names = set()
    for raw_line in re.split(r"[\n,;]+", raw_text):
        line = raw_line.strip().lower()
        if not line:
            continue
        parts = re.findall(r"[^\W_]+", line, flags=re.UNICODE)
        amount = next((int(part) for part in parts if part.isdigit()), None)
        name_parts = [part for part in parts if not part.isdigit()]
        if not name_parts:
            continue
        name = normalize_name(" ".join(name_parts))
        products.append(ProductInput(name=name, amount_grams=amount))
        names.add(name)
    return ParseResult(products=products, raw_names=names)


def find_recipe_matches(raw_text, limit=20):
    parsed = parse_products(raw_text)
    if not parsed.raw_names:
        return []
    recipes = (
        Recipe.objects.filter(status=Recipe.Status.PUBLISHED)
        .prefetch_related("ingredient_links__ingredient", "category")
        .annotate(total_ingredients=Count("ingredient_links", distinct=True))
        .annotate(
            matched_ingredients=Count(
                "ingredient_links",
                filter=Q(ingredient_links__ingredient__name__in=parsed.raw_names),
                distinct=True,
            )
        )
        .filter(matched_ingredients__gt=0)
        .order_by("-matched_ingredients", "total_ingredients", "cooking_time")[:limit]
    )
    results = []
    for recipe in recipes:
        links = list(recipe.ingredient_links.all())
        missing = [
            link for link in links
            if link.ingredient.name not in parsed.raw_names
        ]
        total = len(links)
        matched = total - len(missing)
        percent = round((matched / total) * 100) if total else 0
        results.append(
            MatchResult(
                recipe=recipe,
                matched_count=matched,
                total_count=total,
                percent=percent,
                missing=missing,
            )
        )
    return results


def sync_recipe_ingredients(recipe, ingredients_text):
    RecipeIngredient.objects.filter(recipe=recipe).delete()
    for line in ingredients_text.splitlines():
        parts = re.findall(r"[^\W_]+", line.lower(), flags=re.UNICODE)
        if not parts:
            continue
        amount = next((int(part) for part in parts if part.isdigit()), None)
        name_parts = [part for part in parts if not part.isdigit()]
        if not name_parts:
            continue
        ingredient, _ = Ingredient.objects.get_or_create(
            name=normalize_name(" ".join(name_parts))
        )
        RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=ingredient,
            amount_grams=amount,
        )
