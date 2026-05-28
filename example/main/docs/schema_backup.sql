BEGIN;
--
-- Create model Category
--
CREATE TABLE "recipes_category" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "title" varchar(80) NOT NULL UNIQUE, "slug" varchar(90) NOT NULL UNIQUE);
--
-- Create model Ingredient
--
CREATE TABLE "recipes_ingredient" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "name" varchar(80) NOT NULL UNIQUE);
--
-- Create model Recipe
--
CREATE TABLE "recipes_recipe" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "title" varchar(160) NOT NULL, "slug" varchar(180) NOT NULL UNIQUE, "description" text NOT NULL, "instructions" text NOT NULL, "image" varchar(100) NULL, "cooking_time" smallint unsigned NOT NULL CHECK ("cooking_time" >= 0), "portions" smallint unsigned NOT NULL CHECK ("portions" >= 0), "difficulty" varchar(20) NOT NULL, "status" varchar(20) NOT NULL, "rejection_reason" text NOT NULL, "author_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "category_id" bigint NOT NULL REFERENCES "recipes_category" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model Comment
--
CREATE TABLE "recipes_comment" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "text" text NOT NULL, "is_visible" bool NOT NULL, "author_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "recipe_id" bigint NOT NULL REFERENCES "recipes_recipe" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model RecipeIngredient
--
CREATE TABLE "recipes_recipeingredient" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "amount_grams" integer unsigned NULL CHECK ("amount_grams" >= 0), "note" varchar(120) NOT NULL, "ingredient_id" bigint NOT NULL REFERENCES "recipes_ingredient" ("id") DEFERRABLE INITIALLY DEFERRED, "recipe_id" bigint NOT NULL REFERENCES "recipes_recipe" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Add field ingredients to recipe
--
CREATE TABLE "new__recipes_recipe" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "title" varchar(160) NOT NULL, "slug" varchar(180) NOT NULL UNIQUE, "description" text NOT NULL, "instructions" text NOT NULL, "image" varchar(100) NULL, "cooking_time" smallint unsigned NOT NULL CHECK ("cooking_time" >= 0), "portions" smallint unsigned NOT NULL CHECK ("portions" >= 0), "difficulty" varchar(20) NOT NULL, "status" varchar(20) NOT NULL, "rejection_reason" text NOT NULL, "author_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "category_id" bigint NOT NULL REFERENCES "recipes_category" ("id") DEFERRABLE INITIALLY DEFERRED);
INSERT INTO "new__recipes_recipe" ("id", "created_at", "updated_at", "title", "slug", "description", "instructions", "image", "cooking_time", "portions", "difficulty", "status", "rejection_reason", "author_id", "category_id") SELECT "id", "created_at", "updated_at", "title", "slug", "description", "instructions", "image", "cooking_time", "portions", "difficulty", "status", "rejection_reason", "author_id", "category_id" FROM "recipes_recipe";
DROP TABLE "recipes_recipe";
ALTER TABLE "new__recipes_recipe" RENAME TO "recipes_recipe";
CREATE INDEX "recipes_comment_author_id_2394f8a2" ON "recipes_comment" ("author_id");
CREATE INDEX "recipes_comment_recipe_id_251ae78a" ON "recipes_comment" ("recipe_id");
CREATE UNIQUE INDEX "recipes_recipeingredient_recipe_id_ingredient_id_b6da77a8_uniq" ON "recipes_recipeingredient" ("recipe_id", "ingredient_id");
CREATE INDEX "recipes_recipeingredient_ingredient_id_0efc0df1" ON "recipes_recipeingredient" ("ingredient_id");
CREATE INDEX "recipes_recipeingredient_recipe_id_76423229" ON "recipes_recipeingredient" ("recipe_id");
CREATE INDEX "recipes_recipe_author_id_7274f74b" ON "recipes_recipe" ("author_id");
CREATE INDEX "recipes_recipe_category_id_6d665355" ON "recipes_recipe" ("category_id");
--
-- Create model Report
--
CREATE TABLE "recipes_report" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "reason" text NOT NULL, "is_resolved" bool NOT NULL, "author_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "recipe_id" bigint NOT NULL REFERENCES "recipes_recipe" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model ShoppingListItem
--
CREATE TABLE "recipes_shoppinglistitem" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "amount_grams" integer unsigned NULL CHECK ("amount_grams" >= 0), "is_done" bool NOT NULL, "ingredient_id" bigint NOT NULL REFERENCES "recipes_ingredient" ("id") DEFERRABLE INITIALLY DEFERRED, "recipe_id" bigint NULL REFERENCES "recipes_recipe" ("id") DEFERRABLE INITIALLY DEFERRED, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model Rating
--
CREATE TABLE "recipes_rating" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "score" smallint unsigned NOT NULL CHECK ("score" >= 0), "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "recipe_id" bigint NOT NULL REFERENCES "recipes_recipe" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model Favorite
--
CREATE TABLE "recipes_favorite" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "created_at" datetime NOT NULL, "updated_at" datetime NOT NULL, "user_id" integer NOT NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED, "recipe_id" bigint NOT NULL REFERENCES "recipes_recipe" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE INDEX "recipes_report_author_id_7e5a3f65" ON "recipes_report" ("author_id");
CREATE INDEX "recipes_report_recipe_id_10423daa" ON "recipes_report" ("recipe_id");
CREATE INDEX "recipes_shoppinglistitem_ingredient_id_043d0d23" ON "recipes_shoppinglistitem" ("ingredient_id");
CREATE INDEX "recipes_shoppinglistitem_recipe_id_1d09faa8" ON "recipes_shoppinglistitem" ("recipe_id");
CREATE INDEX "recipes_shoppinglistitem_user_id_8c2abcac" ON "recipes_shoppinglistitem" ("user_id");
CREATE UNIQUE INDEX "recipes_rating_recipe_id_user_id_528566fe_uniq" ON "recipes_rating" ("recipe_id", "user_id");
CREATE INDEX "recipes_rating_user_id_508a5e61" ON "recipes_rating" ("user_id");
CREATE INDEX "recipes_rating_recipe_id_f4d760b9" ON "recipes_rating" ("recipe_id");
CREATE UNIQUE INDEX "recipes_favorite_recipe_id_user_id_1259e216_uniq" ON "recipes_favorite" ("recipe_id", "user_id");
CREATE INDEX "recipes_favorite_user_id_dd4f6854" ON "recipes_favorite" ("user_id");
CREATE INDEX "recipes_favorite_recipe_id_288529df" ON "recipes_favorite" ("recipe_id");
COMMIT;
