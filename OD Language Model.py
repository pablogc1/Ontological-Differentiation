# -*- coding: utf-8 -*-
"""
Created on Sun Oct 27 19:43:17 2024

@author: pablo
"""

import pandas as pd
from collections import Counter
import sys
import traceback
import random
import time
import multiprocessing as mp

# Function to process levels and apply Great Differentiation (GD)
def process_great_differentiation(set_word_a, set_word_b, sets_dict, max_level=10000):
    repeated_sets = set()      # Track repeated sets
    uncanceled_sets = set()    # Track uncanceled sets
    opened_sets = set()        # Track opened sets
    level = 0

    steps_output = []  # Collect steps outputs

    # Initial level (Level 0)
    initial_sets = [set_word_a, set_word_b]
    new_elements_in_iteration = set(initial_sets)

    # Determine repeated and uncanceled sets for Level 0
    for element in initial_sets:
        if element in repeated_sets or element in uncanceled_sets:
            repeated_sets.add(element)
            uncanceled_sets.discard(element)
        else:
            uncanceled_sets.add(element)

    # Log Level 0
    steps_output.append(f"Level {level}:")
    steps_output.append(f"Uncanceled sets: {uncanceled_sets}")
    steps_output.append(f"Repeated sets: {repeated_sets}")
    steps_output.append('')

    # Track elements to be opened in the next level
    elements_to_open_next = new_elements_in_iteration.copy()
    level += 1

    # Process subsequent levels
    while level <= max_level:
        current_level_uncanceled = set()  # Track uncanceled sets at the current level
        new_elements_in_iteration = set()  # Track new elements in the current iteration

        # Process each set in the elements to be opened in this level
        for set_word in elements_to_open_next:
            opened_sets.add(set_word)
            related_words = sets_dict.get(set_word, [])

            # Check for repetitions and add to appropriate sets
            for word in related_words:
                if word in repeated_sets or word in uncanceled_sets:
                    repeated_sets.add(word)
                    uncanceled_sets.discard(word)
                elif word in new_elements_in_iteration:
                    # If the word is repeated within the iteration, mark as repeated
                    repeated_sets.add(word)
                    current_level_uncanceled.discard(word)
                else:
                    # Otherwise, mark as a new uncanceled set
                    new_elements_in_iteration.add(word)
                    current_level_uncanceled.add(word)

        # Update uncanceled sets with the current level's uncanceled sets
        uncanceled_sets.update(current_level_uncanceled)

        # Log current level
        steps_output.append(f"Level {level}:")
        steps_output.append(f"New elements in iteration: {new_elements_in_iteration}")
        steps_output.append(f"Current level uncanceled: {current_level_uncanceled}")
        steps_output.append(f"Uncanceled sets: {uncanceled_sets}")
        steps_output.append(f"Repeated sets: {repeated_sets}")
        steps_output.append('')

        # Determine elements to open in the next level
        elements_to_open_next = new_elements_in_iteration.copy()

        # Termination condition: if no new elements are found, stop the process
        if not new_elements_in_iteration:
            steps_output.append(f"Termination condition met at Level {level} because no new elements were found.")
            steps_output.append('')
            break

        level += 1

    # Return the maximum level reached and steps_output
    output_text = '\n'.join(steps_output)
    return level, output_text

# Function to process levels and apply optimized Weak Differentiation (WD)
def process_optimized_weak_differentiation(set_word_a, set_word_b, sets_dict, max_level=10000):
    # Initialize data structures
    U = {}  # Uncanceled elements
    R = {}  # Repeated elements
    element_locations = {}  # Mapping from element to set of (level, side)

    steps_output = {}  # Store all steps for output per level
    sides = [1, 2]     # Two sides

    # Initialize Level 0
    level = 0
    U[(level, 1)] = Counter([set_word_a])
    U[(level, 2)] = Counter([set_word_b])
    R[(level, 1)] = Counter()
    R[(level, 2)] = Counter()

    # Update element_locations
    element_locations.setdefault(set_word_a, set()).add((level, 1))
    element_locations.setdefault(set_word_b, set()).add((level, 2))

    # Handle repeats at Level 0
    check_and_move_repeats_weak(U, R, element_locations, steps_output)

    # Log Level 0
    log_current_state(steps_output, U, R, level, sides)

    # Termination check after Level 0
    empty_U_sides_levels = check_any_U_empty(U)
    if empty_U_sides_levels:
        empty_U_info = ', '.join([f"U_{lvl}_{s}" for lvl, s in empty_U_sides_levels])
        steps_output['Termination'] = f"Termination condition met at Level {level} because {empty_U_info} became empty."
        total_points = calculate_total_points(R)
        steps_output['Total Points'] = f"Total points: {total_points}"
        output_text = save_outputs(steps_output)
        return total_points, output_text

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
        check_and_move_repeats_weak(U, R, element_locations, steps_output)

        # Log current level
        log_current_state(steps_output, U, R, level, sides)

        # Termination check after each level
        empty_U_sides_levels = check_any_U_empty(U)
        if empty_U_sides_levels:
            empty_U_info = ', '.join([f"U_{lvl}_{s}" for lvl, s in empty_U_sides_levels])
            steps_output['Termination'] = f"Termination condition met at Level {level} because {empty_U_info} became empty."
            total_points = calculate_total_points(R)
            steps_output['Total Points'] = f"Total points: {total_points}"
            output_text = save_outputs(steps_output)
            return total_points, output_text

    # If max level reached without termination
    steps_output['Termination'] = f"Reached max level {max_level} without termination."
    total_points = calculate_total_points(R)
    steps_output['Total Points'] = f"Total points: {total_points}"
    output_text = save_outputs(steps_output)
    return total_points, output_text

# Function to check and move repeats for Weak Differentiation (WD)
def check_and_move_repeats_weak(U, R, element_locations, steps_output):
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
            # Update steps_output
            log_current_state(steps_output, U, R, level, [side])
        if not element_locations[elem]:
            del element_locations[elem]

# Function to process levels and apply optimized Strong Differentiation (SD)
def process_optimized_strong_differentiation(set_word_a, set_word_b, sets_dict, max_level=10000):
    # Initialize data structures
    U = {}  # Uncanceled elements
    R = {}  # Repeated elements
    element_locations = {}  # Mapping from element to set of (level, side)

    steps_output = {}  # Store all steps for output per level
    sides = [1, 2]     # Two sides

    # Initialize Level 0
    level = 0
    U[(level, 1)] = Counter([set_word_a])
    U[(level, 2)] = Counter([set_word_b])
    R[(level, 1)] = Counter()
    R[(level, 2)] = Counter()

    # Update element_locations
    element_locations.setdefault(set_word_a, set()).add((level, 1))
    element_locations.setdefault(set_word_b, set()).add((level, 2))

    # Handle repeats at Level 0
    check_and_move_repeats_strong(U, R, element_locations, steps_output)

    # Log Level 0
    log_current_state(steps_output, U, R, level, sides)

    # Termination check after Level 0
    empty_U_sides_levels = check_any_U_empty(U)
    if empty_U_sides_levels:
        empty_U_info = ', '.join([f"U_{lvl}_{s}" for lvl, s in empty_U_sides_levels])
        steps_output['Termination'] = f"Termination condition met at Level {level} because {empty_U_info} became empty."
        total_points = calculate_total_points(R)
        steps_output['Total Points'] = f"Total points: {total_points}"
        output_text = save_outputs(steps_output)
        return total_points, output_text

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
        check_and_move_repeats_strong(U, R, element_locations, steps_output)

        # Log current level
        log_current_state(steps_output, U, R, level, sides)

        # Termination check after each level
        empty_U_sides_levels = check_any_U_empty(U)
        if empty_U_sides_levels:
            empty_U_info = ', '.join([f"U_{lvl}_{s}" for lvl, s in empty_U_sides_levels])
            steps_output['Termination'] = f"Termination condition met at Level {level} because {empty_U_info} became empty."
            total_points = calculate_total_points(R)
            steps_output['Total Points'] = f"Total points: {total_points}"
            output_text = save_outputs(steps_output)
            return total_points, output_text

    # If max level reached without termination
    steps_output['Termination'] = f"Reached max level {max_level} without termination."
    total_points = calculate_total_points(R)
    steps_output['Total Points'] = f"Total points: {total_points}"
    output_text = save_outputs(steps_output)
    return total_points, output_text

# Function to check and move repeats for Strong Differentiation (SD)
def check_and_move_repeats_strong(U, R, element_locations, steps_output):
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
            # Update steps_output
            log_current_state(steps_output, U, R, level, [side])
        if not element_locations[elem]:
            del element_locations[elem]

# Function to calculate total points
def calculate_total_points(R):
    total_points = 0
    for (level, side), elements in R.items():
        for elem, count in elements.items():
            total_points += count * level
    return total_points

# Function to log the current state
def log_current_state(steps_output, U, R, level, sides):
    if level not in steps_output:
        steps_output[level] = {}
    for side in sides:
        U_elements = list(U[(level, side)].keys())
        R_elements = dict(R[(level, side)])
        steps_output[level][(level, side)] = (U_elements, R_elements)

# Function to save outputs
def save_outputs(steps_output):
    output_lines = []
    levels = sorted([key for key in steps_output.keys() if isinstance(key, int)])
    for level in levels:
        output_lines.append(f"Level {level}:")
        for side in [1, 2]:
            U_elements, R_elements = steps_output[level][(level, side)]
            output_lines.append(f"Side {side} - U_{level}_{side}: {U_elements}, R_{level}_{side}: {R_elements}")
        output_lines.append('')
    if 'Termination' in steps_output:
        output_lines.append(steps_output['Termination'])
    if 'Total Points' in steps_output:
        output_lines.append(steps_output['Total Points'])
    output_text = '\n'.join(output_lines)
    return output_text

# Function to check if any U is empty
def check_any_U_empty(U):
    empty_U_sides_levels = [(lvl, s) for (lvl, s) in U if not U[(lvl, s)]]
    return empty_U_sides_levels

# Helper function to process one vs all pair
def process_one_vs_all_pair(args):
    try:
        word_of_choice, other_word, sets_dict, save_steps = args

        # Run GD to find the maximum level
        gd_max_level, gd_output_text = process_great_differentiation(
            word_of_choice,
            other_word,
            sets_dict
        )

        # Initialize a dictionary to collect total points for WD and SD
        total_points_dict = {}

        steps_output = []
        if save_steps:
            steps_output.append(f"GD between '{word_of_choice}' and '{other_word}':\n")
            steps_output.append(gd_output_text + '\n')
            steps_output.append(f"GD process determined the maximum level to be {gd_max_level}.\n\n")

        # Run both WD and SD
        for differentiation_type in ['WD', 'SD']:
            if differentiation_type == 'WD':
                # Run WD with max_level from GD
                total_points, output_text = process_optimized_weak_differentiation(
                    word_of_choice,
                    other_word,
                    sets_dict,
                    max_level=gd_max_level
                )
            elif differentiation_type == 'SD':
                # Run SD with max_level from GD
                total_points, output_text = process_optimized_strong_differentiation(
                    word_of_choice,
                    other_word,
                    sets_dict,
                    max_level=gd_max_level
                )

            if save_steps:
                steps_output.append(f"{differentiation_type} between '{word_of_choice}' and '{other_word}':\n")
                steps_output.append(output_text + '\n')
                steps_output.append(f"Differentiation completed with total points: {total_points}\n\n")

            # Collect the total points
            total_points_dict[differentiation_type] = total_points

        return (other_word, gd_max_level, total_points_dict, steps_output)
    except Exception as e:
        # Return error information
        return ("Error", str(e), args)

# Helper function to process a pair for all vs all differentiation
def process_all_vs_all_pair(args):
    try:
        word_a, word_b, sets_dict, save_steps = args

        # Run GD to find the maximum level
        gd_max_level, gd_output_text = process_great_differentiation(
            word_a,
            word_b,
            sets_dict
        )

        # Initialize a dictionary to collect total points for WD and SD
        total_points_dict = {}

        steps_output = []
        if save_steps:
            steps_output.append(f"GD between '{word_a}' and '{word_b}':\n")
            steps_output.append(gd_output_text + '\n')
            steps_output.append(f"GD process determined the maximum level to be {gd_max_level}.\n\n")

        # Run both WD and SD
        for differentiation_type in ['WD', 'SD']:
            if differentiation_type == 'WD':
                # Run WD with max_level from GD
                total_points, output_text = process_optimized_weak_differentiation(
                    word_a,
                    word_b,
                    sets_dict,
                    max_level=gd_max_level
                )
            elif differentiation_type == 'SD':
                # Run SD with max_level from GD
                total_points, output_text = process_optimized_strong_differentiation(
                    word_a,
                    word_b,
                    sets_dict,
                    max_level=gd_max_level
                )

            if save_steps:
                steps_output.append(f"{differentiation_type} between '{word_a}' and '{word_b}':\n")
                steps_output.append(output_text + '\n')
                steps_output.append(f"Differentiation completed with total points: {total_points}\n\n")

            # Collect the total points
            total_points_dict[differentiation_type] = total_points

        return (word_a, word_b, gd_max_level, total_points_dict, steps_output)
    except Exception as e:
        # Return error information
        return ("Error", str(e), args)

# Function to run "one vs all" differentiation with multiprocessing
def run_one_vs_all_differentiation(word_of_choice, document, sets_dict, save_steps):
    # Prepare a list of other words excluding the word of choice
    other_words = [row['word'] for idx, row in document.iterrows() if row['word'] != word_of_choice]

    # Open the results file
    results_file = open(f"one_vs_all_results_{word_of_choice}.txt", 'w')

    # Open the steps file if saving steps is enabled
    if save_steps:
        steps_file = open(f"one_vs_all_steps_{word_of_choice}.txt", 'w')
    else:
        steps_file = None

    # Prepare arguments for multiprocessing
    pool_args = [(word_of_choice, other_word, sets_dict, save_steps) for other_word in other_words]

    # Determine the number of processes (e.g., 32 cores)
    num_processes = 32  # Adjust based on your system

    # Use multiprocessing Pool
    with mp.Pool(processes=num_processes) as pool:
        # Use tqdm to display a progress bar
        try:
            from tqdm import tqdm
            iterator = pool.imap_unordered(process_one_vs_all_pair, pool_args)
            for result in tqdm(iterator, total=len(pool_args), desc=f"Processing '{word_of_choice}'", file=sys.stdout):
                if result[0] == "Error":
                    print(f"An error occurred while processing {result[2][0]} and {result[2][1]}: {result[1]}")
                    continue
                other_word, gd_max_level, total_points_dict, steps_output = result

                # Write steps outputs if save_steps is True
                if save_steps:
                    steps_file.write(''.join(steps_output))

                # Write results to results file
                results_file.write(f"Comparison between '{word_of_choice}' and '{other_word}':\n")
                results_file.write(f"GD max level: {gd_max_level}\n")
                for differentiation_type in ['WD', 'SD']:
                    total_points = total_points_dict[differentiation_type]
                    results_file.write(f"{differentiation_type} total points: {total_points}\n")
                results_file.write('\n')
        except ImportError:
            # If tqdm is not available, proceed without progress bar
            iterator = pool.imap_unordered(process_one_vs_all_pair, pool_args)
            for result in iterator:
                if result[0] == "Error":
                    print(f"An error occurred while processing {result[2][0]} and {result[2][1]}: {result[1]}")
                    continue
                other_word, gd_max_level, total_points_dict, steps_output = result

                # Write steps outputs if save_steps is True
                if save_steps:
                    steps_file.write(''.join(steps_output))

                # Write results to results file
                results_file.write(f"Comparison between '{word_of_choice}' and '{other_word}':\n")
                results_file.write(f"GD max level: {gd_max_level}\n")
                for differentiation_type in ['WD', 'SD']:
                    total_points = total_points_dict[differentiation_type]
                    results_file.write(f"{differentiation_type} total points: {total_points}\n")
                results_file.write('\n')

    # Close the results file
    results_file.close()

    # Close the steps file if it was opened
    if save_steps:
        steps_file.close()

# Function to run "all vs all" differentiation using multiprocessing
def run_all_vs_all_differentiation(document, sets_dict, chosen_word, save_steps):
    # Prepare a list of words excluding the chosen word
    words = [row['word'] for idx, row in document.iterrows() if row['word'] != chosen_word]

    # Open the results file
    results_file = open("all_vs_all_results.txt", 'w')

    # Open the steps file if saving steps is enabled
    if save_steps:
        steps_file = open("all_vs_all_steps.txt", 'w')
    else:
        steps_file = None

    # Generate all unique pairs without duplicates
    pool_args = []
    total_pairs = 0
    for i, word_a in enumerate(words):
        for word_b in words[i+1:]:
            pool_args.append((word_a, word_b, sets_dict, save_steps))
            total_pairs += 1

    # Determine the number of processes (e.g., 32 cores)
    num_processes = 32  # Adjust based on your system

    # Use multiprocessing Pool
    with mp.Pool(processes=num_processes) as pool:
        # Use tqdm to display a progress bar
        try:
            from tqdm import tqdm
            iterator = pool.imap_unordered(process_all_vs_all_pair, pool_args)
            for result in tqdm(iterator, total=total_pairs, desc="Processing all vs all", file=sys.stdout):
                if result[0] == "Error":
                    print(f"An error occurred while processing {result[2][0]} and {result[2][1]}: {result[1]}")
                    continue
                word_a, word_b, gd_max_level, total_points_dict, steps_output = result

                # Write steps outputs if save_steps is True
                if save_steps:
                    steps_file.write(''.join(steps_output))

                # Write results to results file
                results_file.write(f"Comparison between '{word_a}' and '{word_b}':\n")
                results_file.write(f"GD max level: {gd_max_level}\n")
                for differentiation_type in ['WD', 'SD']:
                    total_points = total_points_dict[differentiation_type]
                    results_file.write(f"{differentiation_type} total points: {total_points}\n")
                results_file.write('\n')
        except ImportError:
            # If tqdm is not available, proceed without progress bar
            iterator = pool.imap_unordered(process_all_vs_all_pair, pool_args)
            for result in iterator:
                if result[0] == "Error":
                    print(f"An error occurred while processing {result[2][0]} and {result[2][1]}: {result[1]}")
                    continue
                word_a, word_b, gd_max_level, total_points_dict, steps_output = result

                # Write steps outputs if save_steps is True
                if save_steps:
                    steps_file.write(''.join(steps_output))

                # Write results to results file
                results_file.write(f"Comparison between '{word_a}' and '{word_b}':\n")
                results_file.write(f"GD max level: {gd_max_level}\n")
                for differentiation_type in ['WD', 'SD']:
                    total_points = total_points_dict[differentiation_type]
                    results_file.write(f"{differentiation_type} total points: {total_points}\n")
                results_file.write('\n')

    # Close the results file
    results_file.close()

    # Close the steps file if it was opened
    if save_steps:
        steps_file.close()

# Main function to run the differentiation
def main():
    try:
        # Load the document (ensure you adjust the file path)
        file_path = 'final_definitions.txt'  # Update with your actual file path
        data = pd.read_csv(file_path, header=None, delimiter=':', names=['word', 'definition'])
        # Split the definition column into multiple columns using the comma as a delimiter
        data_split = data['definition'].str.split(',', expand=True)
        # Adjust column names based on the actual number of columns in data_split
        column_count = data_split.shape[1]
        column_names = ['synonym' + str(i + 1) for i in range(column_count)]
        data_split.columns = column_names
        # Combine the word column with the split data
        data_split.insert(0, 'word', data['word'])

        # Option to save steps or not
        save_steps = False  # Set to False to deactivate saving steps

        # Build the sets_dict once to use in both functions
        sets_dict = {
            str(row['word']).strip(): [str(syn).strip() for syn in row.dropna().tolist()[1:]]
            for _, row in data_split.iterrows()
        }

        # Run 'one vs all' differentiation for the chosen word
        chosen_word = 'word'  # Replace this with your chosen word

        start_time = time.time()
        run_one_vs_all_differentiation(chosen_word, data_split, sets_dict, save_steps)
        end_time = time.time()

        print(f"Time taken for one vs all differentiation for '{chosen_word}': {end_time - start_time} seconds")

        # Run 'all vs all' differentiation excluding the chosen word
        start_time_all = time.time()
        run_all_vs_all_differentiation(data_split, sets_dict, chosen_word, save_steps)
        end_time_all = time.time()

        print(f"Time taken for all vs all differentiation: {end_time_all - start_time_all} seconds")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()