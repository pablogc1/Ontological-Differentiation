# -*- coding: utf-8 -*-
"""
Created on Sat Oct 26 18:50:17 2024

@author: pablo
"""

import os

# Function to load data from the data file
def load_data(filename):
    data = []
    current_entry = None

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()

            if "Set vs Rest:" in line or "All vs All:" in line:
                if current_entry is None:  # Ensure there is a current_entry initialized
                    continue  # Skip until a valid entry initialization
                if "Set vs Rest:" in line:
                    current_entry['type'] = 'one_vs_all'
                elif "All vs All:" in line:
                    current_entry['type'] = 'all_vs_all'
                continue

            if line.startswith("Iteration"):
                parts = line.split(",")
                if len(parts) >= 3:  # Check if we have enough information to process
                    iteration_info = parts[0].strip()
                    num_sets_info = parts[1].strip()
                    num_elements_info = parts[2].strip()

                    # Extract all constant tags, assuming they start from the 4th part
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


# Function to group data based on constant tag combinations
def filter_data_by_constant_tags(data):
    tag_combinations = {}

    # Group entries by constant tag combinations
    for entry in data:
        constant_tags = entry['constant_tags']
        if constant_tags not in tag_combinations:
            tag_combinations[constant_tags] = []
        tag_combinations[constant_tags].append(entry)

    return tag_combinations


# Function to save filtered data to separate files for each tag combination
def save_filtered_data_by_tags(tag_combinations, output_dir="filtered_data"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)  # Create the folder if it doesn't exist

    for constant_tags, entries in tag_combinations.items():
        # Create a filename based on the constant tags
        sanitized_tags = constant_tags.replace(", ", "_").replace(" ", "-")
        output_filename = f"{output_dir}/{sanitized_tags}.txt"

        with open(output_filename, 'w') as output_file:
            for entry in entries:
                output_file.write(f"{entry['description']}\n")
                if entry['type'] == 'one_vs_all':
                    output_file.write("Set vs Rest:\n")
                elif entry['type'] == 'all_vs_all':
                    output_file.write("All vs All:\n")

                for x, y in zip(entry['x_vals'], entry['y_vals']):
                    if entry['type'] == 'one_vs_all':
                        output_file.write(f"Set 1 vs Set {x}: {y}\n")
                    elif entry['type'] == 'all_vs_all':
                        output_file.write(f"Comparison {x[0]}-{x[1]}: {y}\n")
                output_file.write("="*80 + "\n")
        print(f"Saved filtered data to {output_filename}")


def main():
    data_filename = "random_set_points_data.txt"
    output_folder = "filtered_tag_combinations1"  # You can customize the output folder name here

    # Load data from file
    data = load_data(data_filename)
    print(f"Loaded {len(data)} entries.")

    # Group data by constant tag combinations
    tag_combinations = filter_data_by_constant_tags(data)

    # Save each group of filtered data into separate files inside the created folder
    save_filtered_data_by_tags(tag_combinations, output_dir=output_folder)
    print(f"Filtered data saved into separate files in the '{output_folder}' folder.")

if __name__ == "__main__":
    main()