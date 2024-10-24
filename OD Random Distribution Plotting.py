# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 23:01:37 2024

@author: pablo
"""

import os
import matplotlib.pyplot as plt

# Function to load data from the file
def load_filtered_data(filepath):
    data = []
    current_entry = None

    with open(filepath, 'r') as file:
        for line in file:
            line = line.strip()

            # If we encounter a new "Set vs Rest" or "All vs All" entry
            if "Set vs Rest:" in line or "All vs All:" in line:
                if current_entry is None:  # Ensure there is a current_entry initialized
                    continue  # Skip until a valid entry initialization
                if "Set vs Rest:" in line:
                    current_entry['type'] = 'one_vs_all'
                elif "All vs All:" in line:
                    current_entry['type'] = 'all_vs_all'
                continue

            # When encountering an Iteration line, start a new entry
            if line.startswith("Iteration"):
                parts = line.split(",")
                if len(parts) >= 3:  # Check if we have enough information to process
                    iteration_info = parts[0].strip()
                    num_sets_info = parts[1].strip()
                    num_elements_info = parts[2].strip()

                    # Extract the constant tag information
                    constant_tags_info = ', '.join(parts[3:]).strip()

                    # Initialize the new entry here
                    current_entry = {
                        'description': f"{iteration_info}, {num_sets_info}, {num_elements_info}, {constant_tags_info}",
                        'iteration': int(iteration_info.split("Iteration ")[1]),
                        'num_sets': int(num_sets_info.split("num_sets=")[1]),
                        'num_elements': int(num_elements_info.split("num_elements=")[1]),
                        'constant_tags': constant_tags_info,
                        'x_vals': [],
                        'y_vals': [],
                        'type': ''  # This will be updated later
                    }
                    data.append(current_entry)
                else:
                    print(f"Skipping line due to unexpected format: {line}")
                continue

            # If current_entry is initialized, process the data
            if current_entry:
                parts = line.split(": ")
                if len(parts) == 2:
                    try:
                        if current_entry['type'] == 'one_vs_all':
                            current_entry['x_vals'].append(int(parts[0].split(" ")[-1]))
                            current_entry['y_vals'].append(int(parts[1]))
                        elif current_entry['type'] == 'all_vs_all':
                            comparison = parts[0].split("Comparison ")[1]
                            set_a, set_b = map(int, comparison.split("-"))
                            current_entry['x_vals'].append((set_a, set_b))
                            current_entry['y_vals'].append(int(parts[1]))
                    except ValueError:
                        print(f"Skipping line due to unexpected format: {line}")

    return data

# Function to plot the filtered data
def plot_filtered_data(data, max_iteration=None, num_sets=None, num_elements=None):
    plots_made = False
    filtered_entries = []

    # Filter data based on max_iteration, num_sets, and num_elements
    for entry in data:
        if (max_iteration is None or entry['iteration'] <= max_iteration) and \
           (num_sets is None or entry['num_sets'] == num_sets) and \
           (num_elements is None or entry['num_elements'] == num_elements):
            filtered_entries.append(entry)

    # Plot filtered data
    for entry in filtered_entries:
        print(f"Plotting for description: {entry['description']}")
        if entry['type'] == 'one_vs_all':
            plt.scatter(entry['x_vals'], entry['y_vals'], marker='o')
        elif entry['type'] == 'all_vs_all':
            max_set = max(max(pair) for pair in entry['x_vals'])
            set_points = {i: [] for i in range(1, max_set + 1)}

            for (set_a, set_b), points in zip(entry['x_vals'], entry['y_vals']):
                set_points[set_a].append(points)
                set_points[set_b].append(points)

            for set_num, points in set_points.items():
                plt.scatter(range(1, len(points) + 1), points, marker='o')

        plots_made = True

    # Adjust plot title with constant taggings
    if plots_made:
        title = f"Filtered Data for num_sets={num_sets}, num_elements={num_elements}"
        if max_iteration:
            title += f", up to iteration {max_iteration}"
        title += f"\n{entry['constant_tags']}"  # Add constant tags to the title
        plt.title(title)
        plt.xlabel('Set Number' if entry['type'] == 'one_vs_all' else 'Comparison')
        plt.ylabel('Total Points')
        plt.grid(True)
        plt.show()

def main():
    # Folder where the data is stored
    folder_path = r"C:\Users\pablo\OneDrive\Escritorio\Programar\filtered_tag_combinations1"  # Updated with your full path

    # Set your constant tagging options here
    constraint = "unconstrained"  # Options: 'unconstrained', 'regular_uniqueness', 'strict_uniqueness', 'weighted'
    differentiation = "strong-differentiation"  # Options: 'weak-differentiation', 'strong-differentiation'
    size = "fixed-size"  # Options: 'fixed-size', 'irregular-size'
    comparison_strategy = "all_vs_all"  # Options: 'one_vs_all', 'all_vs_all'
    continuous = "continuous=False"  # Options: 'continuous=True', 'continuous=False'

    # Construct the filename based on selected taggings with correct hyphen and underscore format
    filename = f"Running-with-{constraint}_-{differentiation}_-{size}_-{comparison_strategy}_-{continuous}.txt"
    filepath = os.path.join(folder_path, filename)

    # Check if the file exists
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        return

    # Load data from the file
    data = load_filtered_data(filepath)
    print(f"Loaded {len(data)} entries from {filename}.")

    # Set your variable filtering options
    max_iteration = 100  # Choose up to what iteration you want to plot (None to include all iterations)
    num_sets = 100  # Choose a specific num_sets value (None to include all)
    num_elements = 2  # Choose a specific num_elements value (None to include all)

    # Plot the filtered data based on the user's filtering choices
    plot_filtered_data(data, max_iteration=max_iteration, num_sets=num_sets, num_elements=num_elements)

if __name__ == "__main__":
    main()
