"""
6.101 Lab 5:
Recipes
"""

import pickle
import sys

sys.setrecursionlimit(20_000)
# NO ADDITIONAL IMPORTS!


def atomic_ingredient_costs(recipes):
    """
    Given a recipes list, make and return a dictionary mapping each atomic food item
    name to its cost.
    """
    if not recipes:
        return None

    atomic_dict = {}
    for recipe in recipes:
        if recipe[0] == "atomic":
            # recipe[1] is food name, recipe[2] is food cost
            atomic_dict.update({recipe[1]: recipe[2]})
    return atomic_dict


def compound_ingredient_possibilities(recipes):
    """
    Given recipes, a list containing compound and atomic food items, make and
    return a dictionary that maps each compound food item name to a list
    of all the ingredient lists associated with that name.
    """
    if not recipes:
        return None

    compound_dict = {}
    for recipe in recipes:

        if recipe[0] == "compound":

            if recipe[1] not in compound_dict:
                #make a key/val pair if it doesn't already exist
                compound_dict[recipe[1]] = []
            #if it does exist already, add the ingredient list tuple by tuple
            temp_ingredients = compound_dict[recipe[1]] + [
                [(ingredient[0], ingredient[1]) for ingredient in recipe[2]]
            ]
            compound_dict.update({recipe[1]: temp_ingredients})
    return compound_dict


def lowest_cost(recipes, food_item, allergy=()):
    """
    Given a recipes list and the name of a food item, return the lowest cost of
    a full recipe for the given food item.
    """
    atomic_dict = atomic_ingredient_costs(recipes)
    compound_dict = compound_ingredient_possibilities(recipes)

    #checks for if the original food is the allergy
    if allergy:
        if food_item in allergy:
            return None

    # if food is just one ingredient
    if food_item in atomic_dict:
        return atomic_dict[food_item]

    # if food requires multiple ingredients
    elif food_item in compound_dict:
        # create my recursion function
        recur_find_cost = create_recur_find_cost()
        possible_recipe_costs = []

        for recipe in compound_dict[food_item]:
            possible_recipe_costs.append(
                recur_find_cost(recipe.copy(), compound_dict, atomic_dict, 0, allergy)
            )

        #if the minimum cost is infinity (ingredients are unavaliable)
        if min(possible_recipe_costs) != float("inf"):
            return min(possible_recipe_costs)
        return None

    else:
        return None


def create_recur_find_cost():
    """
    Create recur_find_cost creates the recursive function that finds the lowest possible
    price for a certain recipe
    """

    def recur_find_cost(overall_items, compound_dict, atomic_dict, price, allergy=()):
        """
        Recur find cost takes in a list of tuples with names as index 0 and quantities
        needed for the recipe as index 2. It returns an integer representing the
        lowest cost.

        If no cost is avaliable, or if the ingredients are unavaliable/allergies, it
        will return None.
        """
        for ix, item in enumerate(overall_items):

            if isinstance(item, (int,float)):
                continue

            if allergy:
                if item[0] in allergy:
                    if item[0] in compound_dict.keys():
                        compound_dict.pop(item[0])
                    if item[0] in atomic_dict.keys():
                        atomic_dict.pop(item[0])

            if item[0] in compound_dict:
                for iy, method_of_cooking in enumerate(compound_dict[item[0]]):
                    if iy == 0:
                        possible_prices = []
                    possible_prices.append(
                        recur_find_cost(
                            method_of_cooking,
                            compound_dict,
                            atomic_dict,
                            price,
                            allergy,
                        )
                    )

                # the final price is the smallest price times the quantity needed
                final_price = min(possible_prices) * item[1]

                # input the item in the necessary index
                overall_items = (
                    overall_items[:ix] + [final_price] + overall_items[ix + 1 :]
                )

            if item[0] in atomic_dict:
                item = atomic_dict[item[0]] * item[1]
                overall_items = overall_items[:ix] + [item] + overall_items[ix + 1 :]

            elif item[0] not in atomic_dict and item[0] not in compound_dict:
                overall_items = (
                    overall_items[:ix] + [float("inf")] + overall_items[ix + 1 :]
                )

        count = 0
        for price_for_item in overall_items:
            if not isinstance(price_for_item, (int, float)):
                break
            count += 1
            if not price_for_item:
                return None

        if count == len(overall_items):
            for price_for_item in overall_items:
                price += price_for_item

        return price

    return recur_find_cost


def scaled_flat_recipe(flat_recipe, n):
    """
    Given a dictionary of ingredients mapped to quantities needed, returns a
    new dictionary with the quantities scaled by n.
    """
    new_recipe = {}
    for ingred in flat_recipe:
        new_recipe.update({ingred: (n * flat_recipe[ingred])})
    return new_recipe


def add_flat_recipes(flat_recipes):
    """
    Given a list of flat_recipe dictionaries that map food items to quantities,
    return a new overall 'grocery list' dictionary that maps each ingredient name
    to the sum of its quantities across the given flat recipes.

    For example,
        add_flat_recipes([{'milk':1, 'chocolate':1}, {'sugar':1, 'milk':2}])
    should return:
        {'milk':3, 'chocolate': 1, 'sugar': 1}
    """
    combo_recipe = {}
    for recipe in flat_recipes:
        for ingred in recipe:
            try:
                combo_recipe.update({ingred: combo_recipe[ingred] + recipe[ingred]})
            except KeyError:
                combo_recipe[ingred] = recipe[ingred]
    return combo_recipe


def cheapest_flat_recipe(recipes, food_item, allergy=()):
    """
    Given a recipes list and the name of a food item, return a dictionary
    (mapping atomic food items to quantities) representing the cheapest full
    recipe for the given food item.

    Returns None if there is no possible recipe.
    """

    atomic_dict = atomic_ingredient_costs(recipes)
    compound_dict = compound_ingredient_possibilities(recipes)


    if not food_item:
        return None

    if allergy:
        if food_item in allergy:
            return None

        for one_allergy in allergy:
            if one_allergy in atomic_dict:
                atomic_dict.pop(one_allergy)
            if one_allergy in compound_dict:
                compound_dict.pop(one_allergy)

    if food_item in atomic_dict:
        # if the food item is itself it needs to return 1 of itself.
        return {
            food_item: 1,
        }

    all_recipes = all_flat_recipes(recipes, food_item, allergy)

    #create recursion function
    recur_find_cost = create_recur_find_cost()
    prices = []

    for one_recipe in all_recipes:
        converted_recipe = convert_to_find_cost(one_recipe)
        #adds each cost to a list of prices
        prices.append(recur_find_cost(converted_recipe, compound_dict, atomic_dict, 0))

    #zips recipe with tuple so I can check for minimum
    total_list = list(zip(all_recipes, prices))

    #returns recipe with minimum price
    for one_recipe, one_price in total_list:
        if min(prices) == one_price:
            return one_recipe


def convert_to_find_cost(given_dict):
    """
    Converts a given dictionary from its current form to a list of
    tuples with quantities.
    """
    ingreds = []
    for key in given_dict.keys():
        ingreds.append((key, given_dict[key]))
    return ingreds


def combined_flat_recipes(flat_recipes):
    """
    Given a list of lists of dictionaries, where each inner list represents all
    the flat recipes for a certain ingredient, compute and return a list of flat
    recipe dictionaries that represent all the possible combinations of
    ingredient recipes.
    """

    final_list = []
    check_list = []

    if len(flat_recipes) == 1:
        return flat_recipes[0]

    for ix, ingred_list in enumerate(flat_recipes):
        # if ix is 0
        if not ix:
            check_list = ingred_list.copy()  ##
        if ix:
            new_check_list = []
            #a new result for every item in next list
            for combo_dict in check_list:
                new_combo = []
                #check through every item in the next list
                for second_ingred_list in ingred_list:
                    dicts = [combo_dict, second_ingred_list]
                    final_dict = add_flat_recipes(dicts)
                    new_combo.append(final_dict)

                #add the dicts into a list
                final_list += new_combo
                new_check_list.extend(new_combo)
            check_list = new_check_list

    return check_list


def all_flat_recipes(recipes, food_item, allergy=()):
    """
    Given a list of recipes and the name of a food item, produce a list (in any
    order) of all possible flat recipes for that category.

    Returns an empty list if there are no possible recipes
    """
    atomic_dict = atomic_ingredient_costs(recipes)
    compound_dict = compound_ingredient_possibilities(recipes)

    if food_item in allergy:
        return []

    if allergy:
        for one_allergy in allergy:
            if one_allergy in atomic_dict:
                atomic_dict.pop(one_allergy)
            if one_allergy in compound_dict:
                compound_dict.pop(one_allergy)

    all_recipes_recur = all_recipes_recur_helper()
    return all_recipes_recur(recipes, food_item, compound_dict, atomic_dict, allergy)


def all_recipes_recur_helper():
    """
    Creates a recursive helper for the all recipes function.
    """

    def all_recipes_recur(recipes, food_item, compound_dict, atomic_dict, allergy):
        """
        Creates a recursive function that takes in recipes in their raw form and a food
        item and returns a list of dictionaries of all of that food item's possible
        recipes.
        """
        flat_recipes = []
        food_recipes = []

        if food_item in atomic_dict:
            return [{food_item: 1}]

        try:
            food_recipes = compound_dict[food_item]
        except KeyError:
            flat_recipes = []

        for recipe in food_recipes:
            final_list = []

            for ingredient_tuple in recipe:
                ingredient = ingredient_tuple[0]

                if ingredient in compound_dict:
                    something_new = all_flat_recipes(recipes, ingredient, allergy)
                    scaled_recipes = []

                    for one_recipe in something_new:
                        scaled_recipes.append(
                            scaled_flat_recipe(one_recipe, ingredient_tuple[1])
                        )

                    final_list.append(scaled_recipes)

                elif ingredient in atomic_dict:
                    final_list.append([{ingredient: ingredient_tuple[1]}])


                elif ingredient not in compound_dict and ingredient not in atomic_dict:
                    final_list.append(None)

            for val in final_list:
                if val is None:
                    final_list = 0

            #checks to make sure the returning value is in the right nesting level
            try:
                if isinstance(final_list[0][0], list):
                    flat_recipe = combined_flat_recipes(final_list[0])
                elif isinstance(final_list[0][0], dict):
                    flat_recipe = combined_flat_recipes(final_list)
                flat_recipes.extend(flat_recipe)
            except TypeError:
                flat_recipe = None
            except IndexError:
                flat_recipe = None

        return flat_recipes

    return all_recipes_recur


if __name__ == "__main__":
    # load example recipes from section 3 of the write-up
    with open("test_recipes/example_recipes.pickle", "rb") as f:
        example_recipes = pickle.load(f)
    # you are free to add additional testing code here!

    with open(("test_recipes/examples_filter.pickle"), "rb") as g:
        test_data = pickle.load(g)

    # print(test_data, 'tomato', 'tomato')

    # print(lowest_cost(test_data, 'tomato, ('tomato')))
    # for target, filt in test_data:
    #     print("reset")
    #     print(target, filt)
    #     result = lowest_cost(example_recipes, target, filt)
    #     print(target, result)
    #     assert result == test_data[(target, filt)][1]

    # ATOMIC INGREDIENT COSTS
    # print(example_recipes)
    # atomic = (atomic_ingredient_costs(example_recipes))
    # print(atomic)
    # CALCULATING TOTAL PRICES
    # tally_prices = 0
    # for ingredient in atomic:
    #     tally_prices += atomic[ingredient]
    # print(tally_prices)

    # COMPOUND INGREDIENT RECIPES
    # compound = (compound_ingredient_possibilities(example_recipes))
    # tally = 0
    # for key in compound:
    #     print(compound[key])
    #     if len(compound[key]) != 1:
    #         tally += 1
    # print(tally)

    # LOWEST COST
    dairy_recipes = [
        ("compound", "milk", [("cow", 2), ("milking stool", 1)]),
        ("compound", "cheese", [("milk", 1), ("time", 1)]),
        ("compound", "cheese", [("cutting-edge laboratory", 11)]),
        ("atomic", "milking stool", 5),
        ("atomic", "cutting-edge laboratory", 1000),
        ("atomic", "time", 10000),
        ("atomic", "cow", 100),
    ]

    # print(f'FINAL ANSWER: {lowest_cost(dairy_recipes, "milk")}')
    # assert lowest_cost(dairy_recipes, "cheese") == 10205

    # print(f'FINAL ANSWER: {lowest_cost(example_recipes, "burger")}')
    # print(f'ACTUAL ANSWER: {10685}')

    # print(f'FINAL ANSWER: {lowest_cost(example_recipes, "time")}')
    # print(f'ACTUAL ANSWER: {10000}')
    # assert lowest_cost(dairy_recipes, "milk") == 205
    dairy_recipes_2 = [
        ("compound", "milk", [("cow", 2), ("milking stool", 1)]),
        ("compound", "cheese", [("milk", 1), ("time", 1)]),
        ("compound", "cheese", [("cutting-edge laboratory", 11)]),
        ("atomic", "milking stool", 5),
        ("atomic", "cutting-edge laboratory", 1000),
        ("atomic", "time", 10000),
    ]

    print(
        all_flat_recipes(
            example_recipes,
            "cheese",
        )
    )
    # print(lowest_cost(example_recipes, "milk", ("cow",)))
    # print(lowest_cost(example_recipes, "burger", ("cow",)))
    # print(lowest_cost(example_recipes, "chili", ("cow",)))

    # print("all should be None")

    # CHEAPEST FLAT RECIPES!!!
    soup = {
        "carrots": 5,
        "celery": 3,
        "broth": 2,
        "noodles": 1,
        "chicken": 3,
        "salt": 10,
    }
    # print(scaled_flat_recipe(soup, 3))
    carrot_cake = {
        "carrots": 5,
        "flour": 8,
        "sugar": 10,
        "oil": 5,
        "eggs": 4,
        "salt": 3,
    }
    bread = {"flour": 10, "sugar": 3, "oil": 3, "yeast": 15, "salt": 5}
    new_list = [carrot_cake, bread, soup]
    # print(add_flat_recipes(new_list))
    raw_flat_recipes = [
        [("time", 1), ("cow", 2), ("milking stool", 1)],
        ("cutting-edge laboratory", 11),
    ]
    # print(convert_flat_recipe(raw_flat_recipes, "cheese"))

    # print(example_recipes)
    # print(cheapest_flat_recipe(example_recipes, "burger"))

    # print(combined_flat_recipes(
    #     [[{'peanut butter': 1}, {'almond butter': 1}],
    #     [{'jelly': 2}]]
    # ))

    # HERER!!!!!!
    cakes = [
        [{"cake": 1}, {"gluten free cake": 1}],
        [{"cream cheese icing": 1}],
        [{"cake": 20}, {"cream cheese icing": 1}],
    ]
    inp = [[{"a": 1, "b": 2}]]

    # print(all_flat_recipes(example_recipes, "cheese"))
    # print(cheapest_flat_recipe(dairy_recipes, "cheese"))
    # print({"cow": 2, "milking stool": 1, "time": 1})

    # # cheese
    # # print([{"cow": 1, "milking stool": 1, "time": 1},
    # {"cutting-edge laboratory": 11}])
    # # print([{'cake': 1, 'vanilla icing': 1}, {'cake': 1,
    # 'cream cheese icing': 1}, {'gluten free cake': 1, 'vanilla icing': 1},
    # {'gluten free cake': 1, 'cream cheese icing': 1}]
# )
# print(all_flat_recipes(example_recipes, "burger"))
# print({
# "yeast": 2,
# "salt": 3,
# "flour": 4,
# "cow": 2,
# "milking stool": 1,
# "time": 1,
# "lettuce": 1,
# "tomato": 30,
# "vinegar": 3,
# "sugar": 2,
# "cinnamon": 1,
# })
# print(cheapest_flat_recipe(dairy_recipes, "cheese",))

# def create_recur_find_cost():
#     def recur_find_cost(overall_items, compound_dict, atomic_dict, price,
# allergy = ()):
#         if overall_items[0][0] == [allergy]:
#             return None

#         #print(f'Loop is being restarted. Current status of items:
# {overall_items}')
#         for ix, item in enumerate(overall_items):

#             if allergy:
#                 #print("YES. Allergy")
#                 #print(item[0])
#                 if item[0] in allergy:
#                     #print('item 0 is in allergy')
#                     if item[0] in compound_dict.keys():
#                         #print(compound_dict)
#                         compound_dict.pop(item[0])
#                         #print(compound_dict)
#                     if item[0] in atomic_dict.keys():
#                         atomic_dict.pop(item[0])
#             #print(f'After allegry, current status of items:
# {overall_items}')
#             #print(f"Moved to the next item in the list: {item}")
#             #print(f'Current status of items: {overall_items}')
#             if type(item) == int or type(item) == float:
#                 #print("Found an int")
#                 continue

#             #if the first item is COMPOUND
#             if item[0] in compound_dict:
#                 #print(f"Made it into the compound loop for {item}")
#                 for iy, method_of_cooking in enumerate(compound_dict[item[0]]):
#                     if iy == 0:
#                         possible_prices = []
#                     #print("Made it to recursion in compound; restarting")
#                     possible_prices.append(recur_find_cost(method_of_cooking,
# compound_dict, atomic_dict, price, allergy = allergy))
#                 final_price = min(possible_prices) * item[1]
#                 #print(f'status of possible prices: {possible_prices}')
#                 #print("Possible prices min put in item")
#                 #print(item)
#                 #print(f"Final price put into the list: {final_price}")
#                 overall_items = overall_items[:ix] + [final_price] +
# overall_items[ix+1:]


#             #If the first item is ATOMIC
#             #print(f'here is atomic dict: {atomic_dict}')
#             if allergy:
#                 if item[0] in allergy:
#                     #print(atomic_dict.keys())
#                     if item[0] in atomic_dict.keys():
#                         atomic_dict.pop(item[0])
#             #print(f'here is atomic dict after I supposedly removed stuff:
# {atomic_dict}')

#             if item[0] in atomic_dict:
#                 #print("Made it into the atomic loop")
#                 #print(atomic_dict[item[0]])
#                 item = atomic_dict[item[0]] * item[1]
#                 overall_items = overall_items[:ix] + [item] +
# overall_items[ix+1:]

#             elif item[0] not in atomic_dict and item[0] not in compound_dict:
#                 #print("made it to goal")
#                 overall_items = overall_items[:ix] + [float('inf')] +
# overall_items[ix+1:]


#         #print(f"Out of the for loop, the full list of items
# I'm considering is : {overall_items}")
#         count = 0
#         for price_for_item in overall_items:
#                 if not isinstance(price_for_item, (int, float)):
#                    break
#                 count += 1
#                 if price_for_item == None:
#                     return None
#         if count == len(overall_items):
#             #print(f"hi I basically printed this: {overall_items}")
#             for price_for_item in overall_items:
#                 price += price_for_item

#         #print(f'Returning the price... {price}')
#         return price

#     return recur_find_cost

# CHEAPEST FLAT RECIPE
# if food_item[0] in atomic_dict:
#         return food_item

#     possible_recipes = compound_dict[food_item]
#     final_recipe = []

#     print(food_item)
#     while possible_recipes:
#         current = possible_recipes.pop(0)
#         print(current)
#         for ingredient in current:

#             if ingredient[0] in atomic_dict:
#                 print("made it to atomic loop")
#                 final_recipe.append(atomic_dict[ingredient[0]])

#             if ingredient[0] in compound_dict:
#                 print("made it to compound loop")
#                 for ix, recipe in enumerate(compound_dict[ingredient[0]]):
#                     if ix == 0:
#                         possible_recipes = []
#                     possible_recipes.append(find_recipes(recipe,
# compound_dict, atomic_dict, allergy))

#                 for one_recipe in possible_recipes:
#                     final_recipe.append(ingredient[0] + one_recipe)

#     print(final_recipe)

#     return final_recipe
