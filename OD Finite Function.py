# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 20:13:09 2024

@author: pablo
"""


# Function to generate sets using a custom finite function
def generate_sets(num_sets, num_elements, f, k):
    list_of_sets = []

    for i in range(num_sets):
        start_num = (i + 1) % num_sets  # Start from the next number
        numbers_set = [start_num]  # Start with the first number

        for j in range(1, num_elements):
            next_num = f(numbers_set[-1], k) % num_sets  # Apply the custom function f(x, k)
            numbers_set.append(next_num)

        list_of_sets.append(numbers_set)

    return list_of_sets

# Function to mark repeated elements with "(c)"
def mark_repeats_with_c(elements, repeated_elements):
    return [f"{el}(c)" if el in repeated_elements else str(el) for el in elements]

# Function to process levels and apply differentiation (weak or strong)
def process_levels_until_c(set_num_a, set_num_b, sets_dict, differentiation='weak'):
    general_list = []
    marked_levels = []

    def find_cross_repeats(current_a, current_b, all_previous_elements):
        """Find elements that are repeated across the left and right sides."""
        cross_repeats = set()
        for el in current_a:
            if el in current_b:
                cross_repeats.add(el)
            for level in all_previous_elements:
                if differentiation == 'strong' and el in level[len(level)//2:]:
                    cross_repeats.add(el)

        for el in current_b:
            for level in all_previous_elements:
                if differentiation == 'strong' and el in level[:len(level)//2]:
                    cross_repeats.add(el)

        return cross_repeats

    level_0_elements = [set_num_a, set_num_b]
    general_list.append(level_0_elements)

    marked_level_0 = mark_repeats_with_c(level_0_elements, set())
    marked_levels.append(marked_level_0)

    output = []
    output.append(f"\nLevel 0: {marked_level_0[0]}; {marked_level_0[1]}")
    output.append(f"0th iteration repetitions: {marked_level_0[0]}; {marked_level_0[1]}")

    current_a = sets_dict[set_num_a]
    current_b = sets_dict[set_num_b]

    level = 1
    while True:
        output.append(f"\nLevel {level}: {current_a}; {current_b}")
        level_elements = current_a + current_b
        general_list.append(level_elements)

        if differentiation == 'weak':
            cross_repeats = set()
            for element in level_elements:
                if level_elements.count(element) > 1:
                    cross_repeats.add(element)
                for element_prev in general_list[:-1]:
                    if element in element_prev:
                        cross_repeats.add(element)
        else:
            cross_repeats = find_cross_repeats(current_a, current_b, general_list[:-1])

        marked_level_left = mark_repeats_with_c(current_a, cross_repeats)
        marked_level_right = mark_repeats_with_c(current_b, cross_repeats)

        for i in range(len(marked_levels)):
            left_size = len(general_list[i]) // 2
            marked_levels[i] = (
                mark_repeats_with_c(general_list[i][:left_size], cross_repeats) +
                mark_repeats_with_c(general_list[i][left_size:], cross_repeats)
            )

        marked_levels.append(marked_level_left + marked_level_right)

        output.append(f"{level}th iteration repetitions:")
        output.append(f"{', '.join(marked_level_left)} ; {', '.join(marked_level_right)}")

        for i in range(level + 1):
            left_size = len(marked_levels[i]) // 2
            if all("(c)" in el for el in marked_levels[i][:left_size]) or all("(c)" in el for el in marked_levels[i][left_size:]):
                output.append(f"\nStopping at Level {level} because one side is fully canceled.")
                total_points = 0
                for j in range(level + 1):
                    points = sum(el.count("(c)") for el in marked_levels[j])
                    total_points += points * j
                output.append(f"Total points: {total_points}")
                return total_points, '\n'.join(output)

        next_a = []
        next_b = []
        for num in current_a:
            next_a.extend(sets_dict.get(num, [num]))
        for num in current_b:
            next_b.extend(sets_dict.get(num, [num]))

        current_a = next_a
        current_b = next_b
        level += 1

# Function to compare sets based on given parameters
def compare_sets(num_sets, num_elements, f, k, differentiation='weak', comparison_strategy='one_vs_all'):
    sets_list = generate_sets(num_sets, num_elements, f, k)
    sets_dict = {i: sets_list[i] for i in range(len(sets_list))}

    output = []

    output.append("Generated Sets:")
    for idx, numbers_set in enumerate(sets_list):
        output.append(f"Set {idx}: {numbers_set}")

    results = []
    data_output = []

    if comparison_strategy == 'one_vs_all':
        for i in range(2, len(sets_list)):
            output.append(f"\nComparing Set 1 with Set {i}:")
            points, details = process_levels_until_c(1, i, sets_dict, differentiation=differentiation)
            results.append(points)
            data_output.append(f"Set 1 vs Set {i}: Total Points = {points}")
            output.append(details)
    elif comparison_strategy == 'all_vs_all':
        for i in range(1, len(sets_list)):
            for j in range(i + 1, len(sets_list)):
                output.append(f"\nComparing Set {i} with Set {j}:")
                points, details = process_levels_until_c(i, j, sets_dict, differentiation=differentiation)
                results.append((i, j, points))
                data_output.append(f"Set {i} vs Set {j}: Total Points = {points}")
                output.append(details)

    if comparison_strategy == 'one_vs_all':
        x_vals = list(range(2, len(sets_list)))
        y_vals = results
        title = f'Set 1 vs Other Sets ({differentiation.capitalize()} Differentiation, k={k})'
    else:
        x_vals = [f"{x[0]}-{x[1]}" for x in results]
        y_vals = [x[2] for x in results]
        title = f'All Sets vs All Sets ({differentiation.capitalize()} Differentiation, k={k})'

    return '\n'.join(output), '\n'.join(data_output), x_vals, y_vals, title

# # Function to save the results to a text file
# def save_results_to_file(filename, content):
#     with open(filename, 'a') as file:
#         file.write(content)
#         file.write("\n" + "="*80 + "\n")

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

# Function to run all comparisons for a specified number of num_sets, num_elements, and k values
def run_comparisons(num_sets_range=[10, 20], num_elements_range=[2, 3], k_range=[1, 10], f=None):
    differentiations = ['weak', 'strong']
    comparison_strategies = ['one_vs_all', 'all_vs_all']

    log_filename = "finite_function_results.txt"
    data_filename = "special_function_data.txt"

    for k in k_range:
        for num_sets in num_sets_range:
            for num_elements in num_elements_range:
                for differentiation in differentiations:
                    for comparison_strategy in comparison_strategies:
                        params_description = (f"Running with num_sets={num_sets}, num_elements={num_elements}, k={k}, "
                                              f"{differentiation} differentiation, {comparison_strategy}\n")
                        print(params_description)
                        result, data_output, x_vals, y_vals, title = compare_sets(
                            num_sets, num_elements, f, k, differentiation=differentiation,
                            comparison_strategy=comparison_strategy)

                        # Commented out to deactivate saving results to the log file
                        # save_results_to_file(log_filename, params_description + result)
                        save_data_output_to_file(data_filename, params_description, comparison_strategy, x_vals, y_vals)

# Example usage with a custom finite function
def custom_function(x, k):
    return (x + k)  # You can replace this with any function you like

# Run comparisons with the custom function, varying num_sets, num_elements, k values, and other parameters
run_comparisons(num_sets_range=[10, 20, 30, 40, 50], num_elements_range=[2, 3, 4, 5, 10], k_range=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], f=custom_function)