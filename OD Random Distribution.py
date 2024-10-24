# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 23:00:38 2024

@author: pablo
"""

import random
from collections import Counter

# Function to generate fixed-size sets with constraints
def generate_fixed_size_sets(num_sets, num_elements, constraint='unconstrained', weighted_numbers=None, weight_factor=1):
    available_numbers = list(range(num_sets))
    list_of_sets = []

    # Adjust the pool of numbers for weighted generation
    if constraint == 'weighted' and weighted_numbers:
        weighted_pool = []
        for number in available_numbers:
            if number in weighted_numbers:
                weighted_pool.extend([number] * weight_factor)
            else:
                weighted_pool.append(number)
    else:
        weighted_pool = available_numbers

    for i in range(num_sets):
        while True:
            random_numbers = random.sample(weighted_pool, num_elements)
            if i in random_numbers:
                random_numbers = [num if num != i else random.choice([n for n in weighted_pool if n != i]) for num in random_numbers]

            if constraint == 'regular_uniqueness' and random_numbers in list_of_sets:
                continue
            if constraint == 'strict_uniqueness' and any(set(random_numbers) == set(existing_set) for existing_set in list_of_sets):
                continue

            list_of_sets.append(random_numbers)
            break

    return list_of_sets

# Function to generate irregular-size sets with constraints
def generate_irregular_size_sets(num_sets, min_elements, max_elements, constraint='unconstrained', weighted_numbers=None, weight_factor=1):
    available_numbers = list(range(num_sets))
    list_of_sets = []

    if constraint == 'weighted' and weighted_numbers:
        weighted_pool = []
        for number in available_numbers:
            if number in weighted_numbers:
                weighted_pool.extend([number] * weight_factor)
            else:
                weighted_pool.append(number)
    else:
        weighted_pool = available_numbers

    for i in range(num_sets):
        while True:
            num_elements = random.randint(min_elements, max_elements)
            random_numbers = random.sample(weighted_pool, num_elements)
            if i in random_numbers:
                random_numbers = [num if num != i else random.choice([n for n in weighted_pool if n != i]) for num in random_numbers]

            if constraint == 'regular_uniqueness' and random_numbers in list_of_sets:
                continue
            if constraint == 'strict_uniqueness' and any(set(random_numbers) == set(existing_set) for existing_set in list_of_sets):
                continue

            list_of_sets.append(random_numbers)
            break

    return list_of_sets

# Function to generate additional sets in continuous generation
def continuous_generation(existing_sets, num_new_sets, num_elements=None, min_elements=None, max_elements=None, constraint='unconstrained', weighted_numbers=None, weight_factor=1):
    num_sets = len(existing_sets)
    new_sets = []

    # Combine existing numbers with new indices for continuous generation
    available_numbers = list(range(num_sets + num_new_sets))

    # Adjust the pool of numbers for weighted generation
    if constraint == 'weighted' and weighted_numbers:
        weighted_pool = []
        for number in available_numbers:
            if number in weighted_numbers:
                weighted_pool.extend([number] * weight_factor)
            else:
                weighted_pool.append(number)
    else:
        weighted_pool = available_numbers

    # Determine element range based on fixed or irregular size
    if num_elements:
        for i in range(num_sets, num_sets + num_new_sets):
            while True:
                random_numbers = random.sample(weighted_pool, num_elements)
                if i in random_numbers:
                    random_numbers = [num if num != i else random.choice([n for n in weighted_pool if n != i]) for num in random_numbers]

                if constraint == 'regular_uniqueness' and random_numbers in existing_sets + new_sets:
                    continue
                if constraint == 'strict_uniqueness' and any(set(random_numbers) == set(existing_set) for existing_set in existing_sets + new_sets):
                    continue

                new_sets.append(random_numbers)
                break

    else:
        for i in range(num_sets, num_sets + num_new_sets):
            while True:
                num_elements = random.randint(min_elements, max_elements)
                random_numbers = random.sample(weighted_pool, num_elements)
                if i in random_numbers:
                    random_numbers = [num if num != i else random.choice([n for n in weighted_pool if n != i]) for num in random_numbers]

                if constraint == 'regular_uniqueness' and random_numbers in existing_sets + new_sets:
                    continue
                if constraint == 'strict_uniqueness' and any(set(random_numbers) == set(existing_set) for existing_set in existing_sets + new_sets):
                    continue

                new_sets.append(random_numbers)
                break

    return existing_sets + new_sets

# Function to process levels and apply Great Differentiation (GD)
def process_great_differentiation(set_num_a, set_num_b, sets_dict, max_level=10000):
    repeated_elements = set()      # Track repeated elements
    uncanceled_elements = set()    # Track uncanceled elements
    opened_elements = set()        # Track opened elements
    level = 0

    # Initial level (Level 0)
    initial_elements = [set_num_a, set_num_b]
    new_elements_in_iteration = set(initial_elements)

    # Determine repeated and uncanceled elements for Level 0
    for element in initial_elements:
        if element in repeated_elements or element in uncanceled_elements:
            repeated_elements.add(element)
            uncanceled_elements.discard(element)
        else:
            uncanceled_elements.add(element)

    # Track elements to be opened in the next level
    elements_to_open_next = new_elements_in_iteration.copy()
    level += 1

    # Process subsequent levels
    while level <= max_level:
        current_level_uncanceled = set()  # Track uncanceled elements at the current level
        new_elements_in_iteration = set()  # Track new elements in the current iteration

        # Process each element in the elements to be opened in this level
        for element in elements_to_open_next:
            opened_elements.add(element)
            related_elements = sets_dict.get(element, [element])

            # Check for repetitions and add to appropriate sets
            for el in related_elements:
                if el in repeated_elements or el in uncanceled_elements:
                    repeated_elements.add(el)
                    uncanceled_elements.discard(el)
                elif el in new_elements_in_iteration:
                    # If the element is repeated within the iteration, mark as repeated
                    repeated_elements.add(el)
                    current_level_uncanceled.discard(el)
                else:
                    # Otherwise, mark as a new uncanceled element
                    new_elements_in_iteration.add(el)
                    current_level_uncanceled.add(el)

        # Update uncanceled elements with the current level's uncanceled elements
        uncanceled_elements.update(current_level_uncanceled)

        # Determine elements to open in the next level
        elements_to_open_next = new_elements_in_iteration.copy()

        # Termination condition: if no new elements are found, stop the process
        if not new_elements_in_iteration:
            break

        level += 1

    # Return the maximum level reached
    return level

# Function to check and move repeats for Weak Differentiation (WD)
def check_and_move_repeats_weak(U, R, element_locations):
    # Identify elements to move to R
    elements_to_move = set()

    # First, check for repeats within the same U (elements with count > 1)
    for (level, side), u_counter in U.items():
        for elem, count in u_counter.items():
            if count > 1:
                elements_to_move.add(elem)

    # Second, check for elements that appear in multiple locations
    for elem, locations in element_locations.items():
        if len(locations) > 1:
            elements_to_move.add(elem)

    # Move repeats to R
    for elem in elements_to_move:
        locations = element_locations[elem].copy()
        for (level, side) in locations:
            count = U[(level, side)].pop(elem, 0)
            if count > 0:
                R[(level, side)][elem] += count
            # Remove from element_locations
            element_locations[elem].remove((level, side))
        if not element_locations[elem]:
            del element_locations[elem]

# Function to calculate total points
def calculate_total_points(R):
    total_points = 0
    for (level, side), elements in R.items():
        for elem, count in elements.items():
            total_points += count * level
    return total_points

# Function to check if any U is empty
def check_any_U_empty(U):
    empty_U_sides_levels = [(lvl, s) for (lvl, s) in U if not U[(lvl, s)]]
    return empty_U_sides_levels

# Function to process levels and apply optimized Weak Differentiation (WD)
def process_optimized_weak_differentiation(set_num_a, set_num_b, sets_dict, max_level=10000):
    # Initialize data structures
    U = {}  # Uncanceled elements
    R = {}  # Repeated elements
    element_locations = {}  # Mapping from element to set of (level, side)

    sides = [1, 2]     # Two sides

    # Initialize Level 0
    level = 0
    U[(level, 1)] = Counter([set_num_a])
    U[(level, 2)] = Counter([set_num_b])
    R[(level, 1)] = Counter()
    R[(level, 2)] = Counter()

    # Update element_locations
    element_locations.setdefault(set_num_a, set()).add((level, 1))
    element_locations.setdefault(set_num_b, set()).add((level, 2))

    # Handle repeats at Level 0
    check_and_move_repeats_weak(U, R, element_locations)

    # Termination check after Level 0
    empty_U_sides_levels = check_any_U_empty(U)
    if empty_U_sides_levels:
        # Termination condition met
        total_points = calculate_total_points(R)
        return total_points

    # Start iterations from Level 1
    for level in range(1, max_level + 1):
        # Initialize U and R for this level
        for side in sides:
            U[(level, side)] = Counter()
            R[(level, side)] = Counter()

        # Expand elements and fill U
        for side in sides:
            prev_U = U[(level - 1, side)]
            prev_R = R[(level - 1, side)]
            elements_to_expand = prev_U + prev_R
            expanded_elements = Counter()
            for elem, count in elements_to_expand.items():
                expansions = sets_dict.get(elem, [elem])
                for e in expansions:
                    expanded_elements[e] += count
            # Place elements in U
            U[(level, side)] = expanded_elements
            # Update element_locations
            for elem in expanded_elements:
                element_locations.setdefault(elem, set()).add((level, side))

        # Handle repeats
        check_and_move_repeats_weak(U, R, element_locations)

        # Termination check after each level
        empty_U_sides_levels = check_any_U_empty(U)
        if empty_U_sides_levels:
            # Termination condition met
            total_points = calculate_total_points(R)
            return total_points

    # If max level reached without termination
    total_points = calculate_total_points(R)
    return total_points

# Function to check and move repeats for Strong Differentiation (SD)
def check_and_move_repeats_strong(U, R, element_locations):
    # Identify elements that appear on both sides
    elements_to_move = set()

    # Build a mapping from elements to sides where they appear
    for elem, locations in element_locations.items():
        sides_present = set(side for level, side in locations)
        if len(sides_present) > 1:
            elements_to_move.add(elem)

    # Move repeats to R
    for elem in elements_to_move:
        locations = element_locations[elem].copy()
        for (level, side) in locations:
            count = U[(level, side)].pop(elem, 0)
            if count > 0:
                R[(level, side)][elem] += count
            # Remove from element_locations
            element_locations[elem].remove((level, side))
        if not element_locations[elem]:
            del element_locations[elem]

# Function to process levels and apply optimized Strong Differentiation (SD)
def process_optimized_strong_differentiation(set_num_a, set_num_b, sets_dict, max_level=10000):
    # Initialize data structures
    U = {}  # Uncanceled elements
    R = {}  # Repeated elements
    element_locations = {}  # Mapping from element to set of (level, side)

    sides = [1, 2]     # Two sides

    # Initialize Level 0
    level = 0
    U[(level, 1)] = Counter([set_num_a])
    U[(level, 2)] = Counter([set_num_b])
    R[(level, 1)] = Counter()
    R[(level, 2)] = Counter()

    # Update element_locations
    element_locations.setdefault(set_num_a, set()).add((level, 1))
    element_locations.setdefault(set_num_b, set()).add((level, 2))

    # Handle repeats at Level 0
    check_and_move_repeats_strong(U, R, element_locations)

    # Termination check after Level 0
    empty_U_sides_levels = check_any_U_empty(U)
    if empty_U_sides_levels:
        # Termination condition met
        total_points = calculate_total_points(R)
        return total_points

    # Start iterations from Level 1
    for level in range(1, max_level + 1):
        # Initialize U and R for this level
        for side in sides:
            U[(level, side)] = Counter()
            R[(level, side)] = Counter()

        # Expand elements and fill U
        for side in sides:
            prev_U = U[(level - 1, side)]
            prev_R = R[(level - 1, side)]
            elements_to_expand = prev_U + prev_R
            expanded_elements = Counter()
            for elem, count in elements_to_expand.items():
                expansions = sets_dict.get(elem, [elem])
                for e in expansions:
                    expanded_elements[e] += count
            # Place elements in U
            U[(level, side)] = expanded_elements
            # Update element_locations
            for elem in expanded_elements:
                element_locations.setdefault(elem, set()).add((level, side))

        # Handle repeats (only across opposite sides in SD)
        check_and_move_repeats_strong(U, R, element_locations)

        # Termination check after each level
        empty_U_sides_levels = check_any_U_empty(U)
        if empty_U_sides_levels:
            # Termination condition met
            total_points = calculate_total_points(R)
            return total_points

    # If max level reached without termination
    total_points = calculate_total_points(R)
    return total_points

# Function to compare sets based on given parameters
def compare_sets(num_sets, num_elements, differentiation='weak', irregular=False, min_elements=None, max_elements=None,
                 constraint='unconstrained', weighted_numbers=None, weight_factor=1, continuous=False,
                 num_new_sets=0, comparison_strategy='one_vs_all', max_level=10000):
    if irregular:
        sets_list = generate_irregular_size_sets(num_sets, min_elements, max_elements, constraint=constraint, weighted_numbers=weighted_numbers, weight_factor=weight_factor)
    else:
        sets_list = generate_fixed_size_sets(num_sets, num_elements, constraint=constraint, weighted_numbers=weighted_numbers, weight_factor=weight_factor)

    if continuous:
        sets_list = continuous_generation(sets_list, num_new_sets, num_elements=num_elements, min_elements=min_elements, max_elements=max_elements, constraint=constraint, weighted_numbers=weighted_numbers, weight_factor=weight_factor)

    # Build sets_dict: mapping from element to its expansions
    sets_dict = {}
    for idx, numbers_set in enumerate(sets_list):
        sets_dict[idx] = numbers_set
    # Also, map elements in the sets to themselves if not already in sets_dict
    for numbers_set in sets_list:
        for elem in numbers_set:
            if elem not in sets_dict:
                sets_dict[elem] = [elem]

    output = []

    output.append("Generated Sets:")
    for idx, numbers_set in enumerate(sets_list):
        output.append(f"Set {idx}: {numbers_set}")

    results = []
    data_output = []

    if comparison_strategy == 'one_vs_all':
        # Compare Set 1 with all other sets
        for i in range(2, len(sets_list)):
            output.append(f"\nComparing Set 1 with Set {i}:")
            # Determine the maximum level using GD
            max_level_gd = process_great_differentiation(1, i, sets_dict, max_level=max_level)
            # Run the differentiation process
            if differentiation == 'weak':
                points = process_optimized_weak_differentiation(1, i, sets_dict, max_level=max_level_gd)
            else:
                points = process_optimized_strong_differentiation(1, i, sets_dict, max_level=max_level_gd)
            results.append(points)
            data_output.append(f"Set 1 vs Set {i}: Total Points = {points}")
            output.append(f"Total Points = {points}")
    elif comparison_strategy == 'all_vs_all':
        # Compare all sets with each other
        for i in range(1, len(sets_list)):
            for j in range(i + 1, len(sets_list)):
                output.append(f"\nComparing Set {i} with Set {j}:")
                # Determine the maximum level using GD
                max_level_gd = process_great_differentiation(i, j, sets_dict, max_level=max_level)
                # Run the differentiation process
                if differentiation == 'weak':
                    points = process_optimized_weak_differentiation(i, j, sets_dict, max_level=max_level_gd)
                else:
                    points = process_optimized_strong_differentiation(i, j, sets_dict, max_level=max_level_gd)
                results.append((i, j, points))
                data_output.append(f"Set {i} vs Set {j}: Total Points = {points}")
                output.append(f"Total Points = {points}")

    if comparison_strategy == 'one_vs_all':
        x_vals = list(range(2, len(sets_list)))
        y_vals = results
        title = f'Set 1 vs Other Sets ({differentiation.capitalize()} Differentiation)'
    else:
        x_vals = [f"{x[0]}-{x[1]}" for x in results]
        y_vals = [x[2] for x in results]
        title = f'All Sets vs All Sets ({differentiation.capitalize()} Differentiation)'

    return '\n'.join(output), '\n'.join(data_output), x_vals, y_vals, title

# Function to save the results to a text file
def save_results_to_file(filename, content):
    with open(filename, 'a') as file:
        file.write(content)
        file.write("\n" + "="*80 + "\n")

# Function to save data output for further analysis in a structured format
def save_data_output_to_file(filename, params_description, comparison_strategy, x_vals, y_vals):
    with open(filename, 'a') as file:
        file.write(params_description)
        if comparison_strategy == 'one_vs_all':
            file.write("Set vs Rest:\n")
            for x, y in zip(x_vals, y_vals):
                file.write(f"Set 1 vs Set {x}: {y}\n")
        else:
            file.write("All vs All:\n")
            for x, y in zip(x_vals, y_vals):
                file.write(f"Comparison {x}: {y}\n")
        file.write("\n" + "="*80 + "\n")

# Function to run all comparisons for a specified number of iterations and a range of num_sets and num_elements
def run_comparisons(iterations=1, num_sets_range=[10, 20], num_elements_range=[2, 3]):
    constraints = ['weighted', 'unconstrained', 'regular_uniqueness', 'strict_uniqueness']
    differentiations = ['weak', 'strong']
    sizes = ['fixed', 'irregular']
    comparison_strategies = ['one_vs_all', 'all_vs_all']
    continuous_options = [True, False]

    min_elements = 2
    max_elements = 5
    weighted_values = [2, 5]  # Values to weight more heavily
    weight_factor = 10  # Weight factor for weighted constraint
    num_new_sets = 10  # Number of new sets to add in continuous generation

    log_filename = "random_set_comparison_results.txt"
    data_filename = "random_set_points_data.txt"

    for num_sets in num_sets_range:
        for num_elements in num_elements_range:
            for iteration in range(iterations):
                print(f"\n--- Iteration {iteration + 1}/{iterations} for num_sets={num_sets}, num_elements={num_elements} ---\n")
                for constraint in constraints:
                    for differentiation in differentiations:
                        for size in sizes:
                            for comparison_strategy in comparison_strategies:
                                for continuous in continuous_options:
                                    params_description = (f"Iteration {iteration + 1}, num_sets={num_sets}, num_elements={num_elements}, Running with {constraint}, "
                                                          f"{differentiation} differentiation, {size} size, {comparison_strategy}, continuous={continuous}\n")
                                    print(params_description)
                                    if size == 'fixed':
                                        result, data_output, x_vals, y_vals, title = compare_sets(
                                            num_sets, num_elements, differentiation=differentiation, irregular=False,
                                            constraint=constraint, weighted_numbers=weighted_values, weight_factor=weight_factor,
                                            continuous=continuous, num_new_sets=num_new_sets, comparison_strategy=comparison_strategy)
                                    else:
                                        result, data_output, x_vals, y_vals, title = compare_sets(
                                            num_sets, num_elements, differentiation=differentiation, irregular=True,
                                            min_elements=min_elements, max_elements=max_elements, constraint=constraint,
                                            weighted_numbers=weighted_values, weight_factor=weight_factor, continuous=continuous,
                                            num_new_sets=num_new_sets, comparison_strategy=comparison_strategy)

                                    save_results_to_file(log_filename, params_description + result)
                                    save_data_output_to_file(data_filename, params_description, comparison_strategy, x_vals, y_vals)

# Example of running the comparisons
run_comparisons(iterations=100, num_sets_range=[10, 25, 50, 75, 100], num_elements_range=[2, 3, 4, 5])