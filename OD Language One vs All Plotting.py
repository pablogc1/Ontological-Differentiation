# -*- coding: utf-8 -*-
"""
Created on Sun Oct 27 19:01:02 2024

@author: pablo
"""

import matplotlib.pyplot as plt
import re
import os

# Function to load data from the one_vs_all_results file
def load_one_vs_all_data(file_path):
    data = []
    with open(file_path, 'r') as f:
        current_entry = None
        for line in f:
            line = line.strip()
            if line.startswith("Comparison between"):
                # Start of a new comparison
                if current_entry is not None:
                    data.append(current_entry)
                current_entry = {}
                match = re.match(r"Comparison between '(.+)' and '(.+)':", line)
                if match:
                    current_entry['word_a'] = match.group(1)
                    current_entry['word_b'] = match.group(2)
                else:
                    print(f"Error parsing line: {line}")
            elif line.startswith("GD max level:"):
                if current_entry is not None:
                    current_entry['gd_max_level'] = int(line.split(": ")[1])
            elif line.startswith("WD total points:"):
                if current_entry is not None:
                    current_entry['wd_total_points'] = int(line.split(": ")[1])
            elif line.startswith("SD total points:"):
                if current_entry is not None:
                    current_entry['sd_total_points'] = int(line.split(": ")[1])
        if current_entry is not None:
            data.append(current_entry)
    return data

# Function to plot the one-vs-all data
def plot_one_vs_all_data(data):
    # Prepare data for plotting
    wd_points = [entry['wd_total_points'] for entry in data]
    sd_points = [entry['sd_total_points'] for entry in data]
    indices = list(range(1, len(data) + 1))

    # Plot WD total points
    plt.figure()
    plt.scatter(indices, wd_points, s=10, color='blue', label='WOD')
    plt.xlabel('Comparison Index')
    plt.ylabel('Total Distance')
    plt.title('WOD for One-vs-All Comparisons')
    plt.grid(True)
    plt.legend()
    plt.show()

    # Plot SD total points
    plt.figure()
    plt.scatter(indices, sd_points, s=10, color='orange', label='SOD')
    plt.xlabel('Comparison Index')
    plt.ylabel('Total Distance')
    plt.title('SOD for One-vs-All Comparisons')
    plt.grid(True)
    plt.legend()
    plt.show()

def main():
    # Set the file path directly
    file_path = 'one_vs_all_results_word.txt'  # Update this path if your file is located elsewhere

    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    # Load the data
    data = load_one_vs_all_data(file_path)
    print(f"Loaded data for {len(data)} comparisons.")

    # Plot the data
    plot_one_vs_all_data(data)

if __name__ == "__main__":
    main()