from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg
from django.urls import reverse


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("создано", auto_now_add=True)
    updated_at = models.DateTimeField("обновлено", auto_now=True)

    class Meta:
        abstract = True


class Category(models.Model):
    title = models.CharField("название", max_length=80, unique=True)
    slug = models.SlugField("slug", max_length=90, unique=True)

    class Meta:
        ordering = ["title"]
        verbose_name = "категория"
        verbose_name_plural = "категории"

    def __str__(self):
        return self.title


class Ingredient(models.Model):
    name = models.CharField("название", max_length=80, unique=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "ингредиент"
        verbose_name_plural = "ингредиенты"

    def __str__(self):
        return self.name


class Recipe(TimeStampedModel):
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        PENDING = "pending", "На проверке"
        PUBLISHED = "published", "Опубликован"
        REJECTED = "rejected", "Отклонен"

    class Difficulty(models.TextChoices):
        EASY = "easy", "Легко"
        MEDIUM = "medium", "Средне"
        HARD = "hard", "Сложно"

    title = models.CharField("название", max_length=160)
    slug = models.SlugField("slug", max_length=180, unique=True)
    description = models.TextField("описание")
    instructions = models.TextField("шаги приготовления")
    category = models.ForeignKey(
        Category,
        verbose_name="категория",
        on_delete=models.PROTECT,
        related_name="recipes",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name="автор",
        on_delete=models.CASCADE,
        related_name="recipes",
    )
    image = models.ImageField(
        "изображение", upload_to="recipes/", blank=True, null=True
    )
    cooking_time = models.PositiveSmallIntegerField("время, мин")
    portions = models.PositiveSmallIntegerField("порции", default=1)
    difficulty = models.CharField(
        "сложность", max_length=20, choices=Difficulty.choices, default=Difficulty.EASY
    )
    status = models.CharField(
        "статус", max_length=20, choices=Status.choices, default=Status.PENDING
    )
    rejection_reason = models.TextField("причина отклонения", blank=True)
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        related_name="recipes",
        verbose_name="ингредиенты",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "рецепт"
        verbose_name_plural = "рецепты"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("recipe_detail", kwargs={"slug": self.slug})

    @property
    def average_rating(self):
        value = self.ratings.aggregate(avg=Avg("score"))["avg"]
        return round(value or 0, 1)


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="ingredient_links"
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="recipe_links"
    )
    amount_grams = models.PositiveIntegerField(
        "граммы", blank=True, null=True, help_text="Можно оставить пустым"
    )
    note = models.CharField("примечание", max_length=120, blank=True)

    class Meta:
        unique_together = ("recipe", "ingredient")
        ordering = ["ingredient__name"]
        verbose_name = "ингредиент рецепта"
        verbose_name_plural = "ингредиенты рецепта"

    def __str__(self):
        amount = f" - {self.amount_grams} г" if self.amount_grams else ""
        return f"{self.ingredient.name}{amount}"


class Comment(TimeStampedModel):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    text = models.TextField("текст")
    is_visible = models.BooleanField("виден", default=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "комментарий"
        verbose_name_plural = "комментарии"

    def __str__(self):
        return f"Комментарий {self.author} к {self.recipe}"


class Rating(TimeStampedModel):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="ratings"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ratings",
    )
    score = models.PositiveSmallIntegerField(
        "оценка", validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        unique_together = ("recipe", "user")
        verbose_name = "оценка"
        verbose_name_plural = "оценки"

    def __str__(self):
        return f"{self.score}/5 для {self.recipe}"


class Favorite(TimeStampedModel):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="favorites"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="favorites",
    )

    class Meta:
        unique_together = ("recipe", "user")
        verbose_name = "избранное"
        verbose_name_plural = "избранное"

    def __str__(self):
        return f"{self.user} -> {self.recipe}"


class ShoppingListItem(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="shopping_items",
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, related_name="shopping_items"
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="shopping_items",
        blank=True,
        null=True,
    )
    amount_grams = models.PositiveIntegerField("граммы", blank=True, null=True)
    is_done = models.BooleanField("куплено", default=False)

    class Meta:
        ordering = ["is_done", "ingredient__name"]
        verbose_name = "пункт списка покупок"
        verbose_name_plural = "список покупок"

    def __str__(self):
        return self.ingredient.name


class Report(TimeStampedModel):
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="reports"
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reports",
    )
    reason = models.TextField("причина")
    is_resolved = models.BooleanField("обработана", default=False)

    class Meta:
        ordering = ["is_resolved", "-created_at"]
        verbose_name = "жалоба"
        verbose_name_plural = "жалобы"

    def __str__(self):
        return f"Жалоба на {self.recipe}"

