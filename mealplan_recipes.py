""" Function for diversifying recipe results."""

from model import connect_to_db, db, FoodType, Recipe, Ingredient
import requests
import json
import os
from random import choice
from mealplan_db import (create_recipe, get_recipe_ingredient, get_ingredient,
                         create_recipe_ingredient, add_ingredient, standardize_ingredient_name,
                         get_recipe_by_url)


def create_type_to_ingredient_dict(ingredients, food_types):
    """ Create dictionary of ingredients for each food type."""

    type_to_ing = {}

    for i in range(len(food_types)):
        type_to_ing.setdefault(food_types[i], []).append(ingredients[i])

    return type_to_ing


def combine_ingredients(ingredients_dict):
    """ Create combination of different types of ingredients."""

    ingredients = []

    for protein in ingredients_dict['Proteins']:
        ingredients_inner = [protein]
        for key in ingredients_dict:
            if key != 'Proteins':
                ingredients_inner.extend(ingredients_dict[key])
        ingredients.append(ingredients_inner)

    return ingredients


def get_recipes(payload):
    """Get meal results from spoonacular."""

    # pass into EDAMAM api
    r = requests.get("https://api.edamam.com/search",
                     params=payload)
    data = r.json()
    return data['hits']


def get_EDAMAM_recipes_from_ingredients(ingredients):
    """Pass ingredients into EDAMAM API and get response."""

    params = {"app_id": os.environ['EDAMAM_SECRET_ID'],
              "app_key": os.environ['EDAMAM_SECRET_KEY'],
              "q": ingredients}
    results = get_recipes(params)
    return results


def save_recipes_from_response(results):
    """Pass JSON response to recipes db."""

    recipes = set()

    for recipe in results:
        # If recipe url currently not in Recipes
        create_recipe(recipe['recipe']['label'],
                      recipe['recipe']['url'], recipe['recipe']['image'])
        recipes.add(get_recipe_by_url(recipe['recipe']['url']))

    return list(recipes)


def save_recipes_and_ingredients_from_response(recipes, ingredients):
    """Add recipe response for each ingredient."""

    for recipe in recipes:
        recipe_ingredient = get_recipe_ingredient(recipe.recipe_id)
        if recipe_ingredient is None:
            # Add to recipe_ingredients and commit
            for ingredient in ingredients:
                ingredient = get_ingredient(ingredient)
                create_recipe_ingredient(recipe.recipe_id,
                                         ingredient.ingredient_id)


def get_diverse_recipes(ingredients_combos):
    """ Get diverse recipes from creating combination of ingredients."""

    results = []

    if type(ingredients_combos[0]) == list:
        for combo in ingredients_combos:
            ingredients = ','.join(combo)

            results.append(get_EDAMAM_recipes_from_ingredients(ingredients))

    else:
        ingredients = ','.join(ingredients_combos)

        get_EDAMAM_recipes_from_ingredients(ingredients)

    return results


def pass_ingredients_to_db(ingredients_dict):
    """Pass ingredients into db."""

    for food_type in ingredients_dict:
        for ingredient in ingredients_dict[food_type]:
            add_ingredient(ingredient, food_type)


def get_random_sampling_of_diverse_recipes(ingredients, types):
    """Combine mealplan_recipes fns to get random sampling of diverse recipes.
    """

    for i in range(len(ingredients)):
        ingredients[i] = standardize_ingredient_name(ingredients[i])
    # Create dictionary mapping each ingredient to their food type
    ingredients_to_food_types_dict = create_type_to_ingredient_dict(ingredients,
                                                                    types)
    # create ingredient
    pass_ingredients_to_db(ingredients_to_food_types_dict)
    # Get list of all possible ingredient combinations based on protein
    ingredient_combos_by_protein = combine_ingredients(
        ingredients_to_food_types_dict)
    # Pass combinations into EDAMAM API
    diverse_EDAMAM_recipes = get_diverse_recipes(ingredient_combos_by_protein)
    # Save each recipe into database
    recipes = []
    for recipes_list in diverse_EDAMAM_recipes:
        recipes.append(save_recipes_from_response(recipes_list))
    # Save result into UserIngredients association table
    # for index in results,
    for i in range(len(recipes)):
        # iterate through list of recipes results at index
        # map to RecipeIngredients based off same index
        save_recipes_and_ingredients_from_response(recipes[i],
                                                   ingredient_combos_by_protein[i])

    # Randomly select through recipes until 12 recipes selected (unless total
    # number of responses is less than 12)
    meal_plan_recipes_all = set()
    for lst in recipes:
        for recipe in lst:
            meal_plan_recipes_all.add(recipe)
    meal_plan_recipes_all = tuple(meal_plan_recipes_all)

    meal_plan_recipes_sample = set()
    if len(meal_plan_recipes_all) > 12:
        while len(meal_plan_recipes_sample) < 13:
            meal_plan_recipes_sample.add(choice(meal_plan_recipes_all))
    else:
        meal_plan_recipes_sample = meal_plan_recipes_all
    return meal_plan_recipes_sample
