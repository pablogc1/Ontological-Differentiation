# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 10:53:24 2024

@author: pablo
"""

import numpy as np
import time

# Function to generate sets using a custom recursive function
def generate_sets(start_num, iterations, f):
    sets_dict = {}
    to_process = [(start_num, start_num + 1, f(start_num + 1))]  # Initialize with the first set
    seen = set()

    for _ in range(iterations):
        if not to_process:
            break
        s, s_plus_1, f_s_plus_1 = to_process.pop(0)
        sets_dict[s] = [s_plus_1, f_s_plus_1]

        if s_plus_1 not in seen:
            to_process.append((s_plus_1, s_plus_1 + 1, f(s_plus_1 + 1)))
            seen.add(s_plus_1)

        if f_s_plus_1 not in seen:
            to_process.append((f_s_plus_1, f(f_s_plus_1 + 1), f(f(f_s_plus_1 + 1))))
            seen.add(f_s_plus_1)

    return sets_dict

# Function to mark repeated elements with "(c)"
def mark_repeats_with_c(elements, repeated_elements, tol=1e-8):
    return [f"{el}(c)" if any(np.isclose(el, x, atol=tol) for x in repeated_elements) else str(el) for el in elements]

# Function to explicitly expand each element in the current level as [x + 1, f(x + 1)]
def expand_elements(expansion_set, f):
    expanded = []
    for x in expansion_set:
        expanded.append(x + 1)           # x + 1
        expanded.append(f(x + 1))        # f(x + 1)
    return expanded

# Function to process levels and apply differentiation (weak or strong)
def process_levels_until_c(set_num_a, set_num_b, sets_dict, f, differentiation='weak'):
    general_list = []
    marked_levels = []

    def find_cross_repeats(current_a, current_b, all_previous_elements):
        """Find elements that are repeated across the left and right sides."""
        cross_repeats = set()
        for el in current_a:
            if any(np.isclose(el, x, atol=1e-8) for x in current_b):
                cross_repeats.add(el)
            for level in all_previous_elements:
                if differentiation == 'strong' and any(np.isclose(el, x, atol=1e-8) for x in level[len(level)//2:]):
                    cross_repeats.add(el)
        for el in current_b:
            for level in all_previous_elements:
                if differentiation == 'strong' and any(np.isclose(el, x, atol=1e-8) for x in level[:len(level)//2]):
                    cross_repeats.add(el)
        return cross_repeats

    level_0_elements = [set_num_a, set_num_b]
    general_list.append(level_0_elements)

    marked_level_0 = mark_repeats_with_c(level_0_elements, set())
    marked_levels.append(marked_level_0)

    output = []
    output.append(f"\nLevel 0: {marked_level_0[0]}; {marked_level_0[1]}")
    output.append(f"0th iteration repetitions: {marked_level_0[0]}; {marked_level_0[1]}")

    # Initial expansion for level 1
    current_a = expand_elements([set_num_a], f)
    current_b = expand_elements([set_num_b], f)

    level = 1
    while True:
        output.append(f"\nLevel {level}: {current_a}; {current_b}")
        level_elements = current_a + current_b
        general_list.append(level_elements)

        if differentiation == 'weak':
            cross_repeats = set()
            for element in level_elements:
                if sum(np.isclose(element, x, atol=1e-8) for x in level_elements) > 1:
                    cross_repeats.add(element)
                for element_prev in general_list[:-1]:
                    if any(np.isclose(element, x, atol=1e-8) for x in element_prev):
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

        # Check if one side is fully canceled
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

        # Expand each element by applying the strict rule x -> [x+1, f(x+1)]
        current_a = expand_elements(current_a, f)
        current_b = expand_elements(current_b, f)
        level += 1

# Function to select and compare a set with others
def select_and_compare(sets_dict, selected_set, f, iterations=5, differentiation='weak', save_results=True):
    output = []
    output.append(f"\nComparing Set {selected_set} with other sets:")
    results = []

    for set_num_b in list(sets_dict.keys()):  # Compare with all other sets
        if not np.isclose(selected_set, set_num_b):
            output.append(f"\nComparing Set {selected_set} with Set {set_num_b}:")
            points, output_details = process_levels_until_c(selected_set, set_num_b, sets_dict, f, differentiation)
            results.append((set_num_b, points))

            output.append(output_details)

    # Sort results by set number for plotting
    results.sort(key=lambda x: x[0])
    x_values = [set_num for set_num, _ in results]
    y_values = [points for _, points in results]

    # Return both results and detailed output
    if save_results:
        return results, x_values, y_values, '\n'.join(output)
    else:
        return results, x_values, y_values, None

# Function to save the results to a text file
def save_results_to_file(filename, content):
    with open(filename, 'a') as file:
        file.write(content)
        file.write("\n" + "="*80 + "\n")

# Function to save data output for further analysis in a structured format
def save_data_output_to_file(filename, params_description, x_vals, y_vals):
    with open(filename, 'a') as file:
        file.write(params_description)
        file.write("Set vs Rest:\n")
        for x, y in zip(x_vals, y_vals):
            file.write(f"Set 1 vs Set {x}: {y}\n")
        file.write("\n" + "="*80 + "\n")

# Function to run comparisons for multiple iterations and k values
def run_comparisons(iterations_range, k_range, selected_set=1, differentiation='weak', save_results=True):
    start_time = time.time()  # Start timing

    for k in k_range:
        # Define filenames based on k and differentiation type
        log_filename = f"recursive_k{k}_{differentiation}_function_results.txt"
        data_filename = f"recursive_k{k}_{differentiation}_data.txt"

        # Define the custom function with the current k
        def custom_function(x, k=k):  # Use default argument to bind current k
            return x + k

        for iterations in iterations_range:
            print(f"Running comparison for k={k}, iterations={iterations}, differentiation='{differentiation}'...")
            sets_dict = generate_sets(start_num=selected_set, iterations=iterations, f=custom_function)
            results, x_vals, y_vals, detailed_output = select_and_compare(
                sets_dict, selected_set=selected_set, f=custom_function, iterations=iterations,
                differentiation=differentiation, save_results=save_results)

            # Save detailed output to the log file if save_results is True
            if save_results and detailed_output:
                params_description = f"k={k}, Iterations={iterations}, {differentiation.capitalize()} Differentiation\n"
                save_results_to_file(log_filename, params_description + detailed_output)

            # Save x-y data output to files
            params_description = f"k={k}, Iterations={iterations}, {differentiation.capitalize()} Differentiation\n"
            save_data_output_to_file(data_filename, params_description, x_vals, y_vals)

    end_time = time.time()  # End timing
    elapsed_time = end_time - start_time
    print(f"Total time taken: {elapsed_time:.2f} seconds")

# Example usage with k_range
k_range = [5]

# Run comparisons with the custom function f(x) = x + k for each k in k_range
# Differentiation type is specified as either 'weak' or 'strong'
run_comparisons(iterations_range=[25], k_range=k_range, differentiation='strong', save_results=False)
