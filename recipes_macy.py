import pickle
import sys

sys.setrecursionlimit(20_000)

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
    def all_recipes_recur(recipes, food_item, compound_dict, atomic_dict, allergy):
        if food_item in atomic_dict:
            return [{food_item: 1}]
        
        flat_recipes = []
        food_recipes = compound_dict.get(food_item, [])

        for recipe in food_recipes:
            ingredient_lists = []

            for ingredient, qty in recipe:
                if ingredient in compound_dict:
                    sub_recipes = all_flat_recipes(recipes, ingredient, allergy)
                    ingredient_lists.append([scaled_flat_recipe(r, qty) for r in sub_recipes])
                elif ingredient in atomic_dict:
                    ingredient_lists.append([{ingredient: qty}])
                else:
                    ingredient_lists.append(None)

            if None in ingredient_lists:
                continue

            try:
                if isinstance(ingredient_lists[0][0], list):
                    flat_recipes.extend(combined_flat_recipes(ingredient_lists[0]))
                else:
                    flat_recipes.extend(combined_flat_recipes(ingredient_lists))
            except (TypeError, IndexError):
                pass

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
