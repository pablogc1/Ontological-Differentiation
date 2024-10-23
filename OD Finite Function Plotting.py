# -*- coding: utf-8 -*-
"""
Created on Wed Oct 23 18:12:34 2024

@author: pablo
"""

import matplotlib.pyplot as plt

# Function to load data from the file
def load_data(filename):
    data = []
    current_entry = None

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()

            if "Set vs Rest:" in line or "All vs All:" in line:
                if "Set vs Rest:" in line:
                    current_entry['type'] = 'one_vs_all'
                elif "All vs All:" in line:
                    current_entry['type'] = 'all_vs_all'
                continue

            if line.startswith("Running with"):
                num_sets_info = line.split(",")[0].strip()
                num_elements_info = line.split(",")[1].strip()
                k_info = line.split(",")[2].strip()
                current_entry = {
                    'description': f"{num_sets_info}, {num_elements_info}, {k_info}, {line.split('Running with')[1].strip()}",
                    'num_sets': int(num_sets_info.split("num_sets=")[1]),
                    'num_elements': int(num_elements_info.split("num_elements=")[1]),
                    'k_value': int(k_info.split("k=")[1]),
                    'x_vals': [],
                    'y_vals': [],
                    'type': ''
                }
                data.append(current_entry)
                continue

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

def tags_match(tags, description):
    """Checks if all the selected tags are present in the description."""
    for tag in tags:
        if tag not in description:
            return False
    return True

def plot_all_vs_all(entry, include_in_legend=True):
    """Scatter plot data for the 'All vs All' type by extracting and organizing data for each set."""
    set_a_vals = [pair[0] for pair in entry['x_vals']]
    set_b_vals = [pair[1] for pair in entry['x_vals']]

    label = "All vs All" if include_in_legend else None
    plt.scatter(set_a_vals, entry['y_vals'], marker='o', label=label)
    plt.scatter(set_b_vals, entry['y_vals'], marker='o')  # Scatter both set_a and set_b

def plot_data_based_on_tags(data, selected_tags, num_sets=None, num_elements=None, k_value=None, 
                            plot_all_num_sets=False, plot_all_num_elements=False, plot_all_k_values=False,
                            include_num_sets_in_legend=False, include_num_elements_in_legend=False,
                            include_k_in_legend=True, include_all_vs_all_in_legend=True):
    plots_made = False
    for entry in data:
        if tags_match(selected_tags, entry['description']):
            if plot_all_num_sets and num_sets and entry['num_sets'] != num_sets:
                continue

            if not plot_all_num_sets and num_sets and entry['num_sets'] != num_sets:
                continue

            if not plot_all_num_elements and num_elements and entry['num_elements'] != num_elements:
                continue

            if not plot_all_k_values and k_value and entry['k_value'] != k_value:
                continue

            print(f"Plotting for description: {entry['description']}")
            if entry['type'] == 'all_vs_all':
                plot_all_vs_all(entry, include_in_legend=include_all_vs_all_in_legend)  # Conditional legend inclusion
            else:
                # Scatter plot for 'one_vs_all' case
                label = ""
                if include_k_in_legend:  # Conditional inclusion of k in the legend
                    label += f"k={entry['k_value']}"
                if include_num_sets_in_legend:
                    label += f", num_sets={entry['num_sets']}"
                if include_num_elements_in_legend:
                    label += f", num_elements={entry['num_elements']}"

                # Ensure correct formatting for scatter plot
                if len(entry['x_vals']) == len(entry['y_vals']):
                    plt.scatter(entry['x_vals'], entry['y_vals'], marker='o', label=label)
                else:
                    print(f"Mismatch between x and y values for entry: {entry['description']}")

            plots_made = True
    
    if plots_made:
        plt.title(f"{'All' if plot_all_k_values else ''} k Values - {', '.join(selected_tags)}")
        plt.xlabel('Set Number' if entry['type'] == 'one_vs_all' else 'Set Number')
        plt.ylabel('Total Distance')
        plt.grid(True)
        plt.legend()
        plt.show()
    else:
        print("No matching data found for the selected tags.")

def main():
    data_filename = "special_function_data.txt"

    data = load_data(data_filename)
    print(f"Loaded {len(data)} entries.")
    
    selected_tags = ['strong', 'all_vs_all']  # Example tags
    
    # Example configurations
    num_sets = 50
    num_elements = 10
    k_value = 5
    plot_all_num_sets = False
    plot_all_num_elements = True  # Set this to True to plot all num_elements together
    plot_all_k_values = True  # Set this to True to plot all k values together
    include_num_sets_in_legend = False  # Set this to True to include num_sets in the legend
    include_num_elements_in_legend = False  # Set this to True to include num_elements in the legend
    include_k_in_legend = False  # Set this to False to exclude k values from the legend
    include_all_vs_all_in_legend = False  # Set this to False to exclude all vs all sets in the legend

    plot_data_based_on_tags(data, selected_tags, num_sets=num_sets, num_elements=num_elements, k_value=k_value, 
                            plot_all_num_sets=plot_all_num_sets, plot_all_num_elements=plot_all_num_elements, 
                            plot_all_k_values=plot_all_k_values, include_num_sets_in_legend=include_num_sets_in_legend, 
                            include_num_elements_in_legend=include_num_elements_in_legend,
                            include_k_in_legend=include_k_in_legend, include_all_vs_all_in_legend=include_all_vs_all_in_legend)

if __name__ == "__main__":
    main()

