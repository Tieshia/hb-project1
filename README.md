# Meal-of-Fortune

## Summary

**Meal-of-Fortune** is a meal planning application that allows users to minimize food waste and to determine quickly what meals to make for the week. It generates meal plans based on the list of ingredients the user plans on cooking.


## About the Developer

Meal-of-Fortune was created by Tieshia Francis, a software engineer in San Francisco, CA. Learn more about the developer on [LinkedIn](https://www.linkedin.com/in/francistie).


## Technologies

**Tech Stack:**

- Python
- Flask
- SQLAlchemy
- Jinja2
- HTML
- CSS
- Javascript
- JQuery
- AJAX
- JSON
- Bootstrap
- Python unittest module
- Edamam API

Meal-of-Fortune is an app built on a Flask server with a PostgreSQL database, with SQLAlchemy as the ORM. The front end templating uses Jinja2, the HTML was built using Bootstrap, and the Javascript uses JQuery and AJAX to interact with the backend. Server routes are tested using the Python unittest module.


## Features


![alt text](https://github.com/Tieshia/hb-project1/blob/master/static/images/recipe_diversification.gif "Meal-of-Fortune Recipe Diversification Algorithm")


- **Recipe diversification algorithm:** When the user enters ingredients to their meal plan, the application creates various combinations of these ingredients and passes them to the Edamam API using a recipe diversification algorithm, providing the user a greater variety of recipes from which to choose.
 



![alt text](https://github.com/Tieshia/hb-project1/blob/master/static/images/recipe_recommendations.gif "Meal-of-Fortune Recipe Recommendation Engine")




- **Recipe recommendation engine:** Meal-of-Fortune features a recipe recommendation engine that uses a series of SQLAlchemy queries to determine the best recipes based on user ratings, automatically suggesting meals to a user without their having to create a new meal plan.




![alt text](https://github.com/Tieshia/hb-project1/blob/master/static/images/recipe_ratings.gif "Meal-of-Fortune Recipe Ratings")




- **Interactive rating functionality:** Once a user makes a meal, they have the option of rating a recipe between 1-5 stars. These ratings are then used for the recipe recommendation engine.




![alt text](https://github.com/Tieshia/hb-project1/blob/master/static/images/recipe_deletion.gif "Meal-of-Fortune Recipe Deletion")


- **Deleting meal plan recipes:** Selected a recipe for your meal plan by accident? No worries! Just select the 'x' at the corner of the card to delete it from your meal plan.


## For Version 2.0

- **More input control:** Implementing the autocomplete ingredient functionality of the Spoonacular API to ensure users are querying actual edible ingredients.
- **Updated recipe recommendation engine:** Replacing current system with engine that uses collaborative filtering to recommend recipes based on user ratings as well as ingredients used.
- **Update recipe diversification algorithm:** Adding ability to query recipe based on various types of produce provided.
- **Charts of user activity:** Display users ingredients most typically used, general recipe ratings and frequency made.
