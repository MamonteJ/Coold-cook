from django.urls import path

from . import views

urlpatterns = [
    path("", views.recipe_list, name="recipe_list"),
    path("assistant/", views.assistant, name="assistant"),
    path("random/", views.random_recipe, name="random_recipe"),
    path("recipes/create/", views.recipe_create, name="recipe_create"),
    path("recipes/<slug:slug>/", views.recipe_detail, name="recipe_detail"),
    path(
        "recipes/<slug:slug>/favorite/",
        views.toggle_favorite,
        name="toggle_favorite",
    ),
    path("recipes/<slug:slug>/report/", views.report_recipe, name="report_recipe"),
    path("profile/", views.profile, name="profile"),
    path("moderation/", views.moderation_queue, name="moderation_queue"),
    path(
        "moderation/<int:pk>/<str:decision>/",
        views.moderate_recipe,
        name="moderate_recipe",
    ),
    path(
        "moderation/recipes/<int:pk>/delete/",
        views.delete_recipe,
        name="delete_recipe",
    ),
    path(
        "moderation/comments/<int:pk>/delete/",
        views.delete_comment,
        name="delete_comment",
    ),
]
