from django.contrib import admin

from .models import (
    Category,
    Comment,
    Favorite,
    Ingredient,
    Rating,
    Recipe,
    RecipeIngredient,
    Report,
    ShoppingListItem,
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    autocomplete_fields = ["ingredient"]


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "author",
        "status",
        "cooking_time",
        "created_at",
    )
    list_filter = ("status", "category", "difficulty")
    search_fields = ("title", "description", "author__username")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [RecipeIngredientInline]


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title",)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    search_fields = ("name",)


admin.site.register(Comment)
admin.site.register(Rating)
admin.site.register(Favorite)
admin.site.register(ShoppingListItem)
admin.site.register(Report)
