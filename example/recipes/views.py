import random

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Avg, Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import (
    CommentForm,
    ProductSearchForm,
    RatingForm,
    RecipeForm,
    ReportForm,
    SignUpForm,
)
from .models import Category, Comment, Favorite, Rating, Recipe
from .services import find_recipe_matches, sync_recipe_ingredients


def is_moderator(user):
    return user.is_staff or user.is_superuser


def published_recipes():
    return Recipe.objects.filter(status=Recipe.Status.PUBLISHED)


def recipe_list(request):
    recipes = published_recipes().select_related("category", "author")
    recipes = recipes.annotate(avg_rating=Avg("ratings__score"))
    query = request.GET.get("q", "").strip()
    category_id = request.GET.get("category")
    difficulty = request.GET.get("difficulty")
    sort = request.GET.get("sort", "new")

    if query:
        recipes = recipes.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(ingredient_links__ingredient__name__icontains=query)
        ).distinct()
    if category_id:
        recipes = recipes.filter(category_id=category_id)
    if difficulty:
        recipes = recipes.filter(difficulty=difficulty)
    if sort == "rating":
        recipes = recipes.order_by("-avg_rating", "title")
    elif sort == "time":
        recipes = recipes.order_by("cooking_time", "title")

    context = {
        "recipes": recipes,
        "categories": Category.objects.all(),
        "difficulties": Recipe.Difficulty.choices,
    }
    return render(request, "recipes/recipe_list.html", context)


def assistant(request):
    form = ProductSearchForm(request.POST or None)
    matches = []
    if request.method == "POST" and form.is_valid():
        matches = find_recipe_matches(form.cleaned_data["products"])
        if not matches:
            messages.info(request, "Подходящие рецепты пока не найдены.")
    return render(
        request,
        "recipes/assistant.html",
        {"form": form, "matches": matches},
    )


def random_recipe(request):
    form = ProductSearchForm(request.POST or None)
    recipe = None
    if request.method == "POST" and form.is_valid():
        matches = find_recipe_matches(form.cleaned_data["products"], limit=50)
        recipe = random.choice(matches).recipe if matches else None
    else:
        ids = list(published_recipes().values_list("id", flat=True))
        recipe = Recipe.objects.get(id=random.choice(ids)) if ids else None
    return render(
        request,
        "recipes/random_recipe.html",
        {"form": form, "recipe": recipe},
    )


def recipe_detail(request, slug):
    recipe = get_object_or_404(
        published_recipes().select_related("category", "author"), slug=slug
    )
    comment_form = CommentForm()
    rating_form = RatingForm()
    if request.method == "POST" and request.user.is_authenticated:
        if "comment" in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.recipe = recipe
                comment.author = request.user
                comment.save()
                messages.success(request, "Комментарий добавлен.")
                return redirect(recipe)
        if "rating" in request.POST:
            rating_form = RatingForm(request.POST)
            if rating_form.is_valid():
                Rating.objects.update_or_create(
                    recipe=recipe,
                    user=request.user,
                    defaults={"score": rating_form.cleaned_data["score"]},
                )
                messages.success(request, "Оценка сохранена.")
                return redirect(recipe)
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = Favorite.objects.filter(user=request.user, recipe=recipe).exists()
    context = {
        "recipe": recipe,
        "comment_form": comment_form,
        "rating_form": rating_form,
        "is_favorite": is_favorite,
    }
    return render(request, "recipes/recipe_detail.html", context)


@login_required
def recipe_create(request):
    form = RecipeForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        recipe = form.save(commit=False)
        recipe.author = request.user
        recipe.status = Recipe.Status.PENDING
        recipe.save()
        sync_recipe_ingredients(recipe, form.cleaned_data["ingredients_text"])
        messages.success(request, "Рецепт отправлен на модерацию.")
        return redirect("profile")
    return render(request, "recipes/recipe_form.html", {"form": form})


@login_required
def toggle_favorite(request, slug):
    recipe = get_object_or_404(published_recipes(), slug=slug)
    favorite, created = Favorite.objects.get_or_create(user=request.user, recipe=recipe)
    if created:
        messages.success(request, "Рецепт добавлен в избранное.")
    else:
        favorite.delete()
        messages.info(request, "Рецепт удален из избранного.")
    return redirect(recipe)


@login_required
def report_recipe(request, slug):
    recipe = get_object_or_404(published_recipes(), slug=slug)
    form = ReportForm(request.POST or None)
    if form.is_valid():
        report = form.save(commit=False)
        report.recipe = recipe
        report.author = request.user
        report.save()
        messages.success(request, "Жалоба отправлена модератору.")
        return redirect(recipe)
    return render(request, "recipes/report_form.html", {"form": form, "recipe": recipe})


@login_required
def profile(request):
    context = {
        "my_recipes": request.user.recipes.select_related("category"),
        "favorites": request.user.favorites.select_related(
            "recipe", "recipe__category"
        ),
    }
    return render(request, "recipes/profile.html", context)


@user_passes_test(is_moderator)
def moderation_queue(request):
    recipes = Recipe.objects.filter(status=Recipe.Status.PENDING).select_related(
        "author", "category"
    )
    all_recipes = Recipe.objects.select_related("author", "category").order_by(
        "-created_at"
    )
    comments = Comment.objects.select_related("author", "recipe").order_by(
        "-created_at"
    )[:30]
    stats = Recipe.objects.values("status").annotate(total=Count("id"))
    return render(
        request,
        "recipes/moderation_queue.html",
        {
            "recipes": recipes,
            "all_recipes": all_recipes,
            "comments": comments,
            "stats": stats,
        },
    )


@user_passes_test(is_moderator)
def moderate_recipe(request, pk, decision):
    recipe = get_object_or_404(Recipe, pk=pk)
    if decision == "approve":
        recipe.status = Recipe.Status.PUBLISHED
        recipe.rejection_reason = ""
        messages.success(request, "Рецепт опубликован.")
    elif decision == "reject":
        recipe.status = Recipe.Status.REJECTED
        recipe.rejection_reason = request.POST.get("reason", "Требуется доработка")
        messages.info(request, "Рецепт отклонен.")
    recipe.save(update_fields=["status", "rejection_reason", "updated_at"])
    return redirect("moderation_queue")


@user_passes_test(is_moderator)
def delete_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    title = recipe.title
    recipe.delete()
    messages.success(request, f"Рецепт «{title}» удален.")
    return redirect("moderation_queue")


@user_passes_test(is_moderator)
def delete_comment(request, pk):
    comment = get_object_or_404(Comment.objects.select_related("recipe"), pk=pk)
    recipe = comment.recipe
    comment.delete()
    messages.success(request, "Комментарий удален.")
    if recipe.status == Recipe.Status.PUBLISHED:
        return redirect(recipe)
    return redirect("moderation_queue")


def signup(request):
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Аккаунт создан.")
        return redirect("recipe_list")
    return render(request, "registration/signup.html", {"form": form})
