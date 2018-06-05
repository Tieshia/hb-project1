""" Function for diversifying recipe results."""

from model import connect_to_db, db, FoodType, Recipe, Ingredient
import requests
import json
import os
from mealplan_db import *


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

    recipes=set()

    for recipe in results:
        # If recipe url currently not in Recipes
        add_json_response_to_recipes(recipe['recipe']['label'], 
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
        else:
            pass



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

    for key in ingredients_dict:
        for ingredient in ingredients_dict[key]:
            food_type = get_ingredient_type(key)
            create_ingredient(ingredient, food_type.type_id)
