# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 17:30:42 2024

@author: pablo
"""

import os
import matplotlib.pyplot as plt

# Path to the folder with results
folder_path = "Recursive Function"

# Helper function to load data based on filename pattern
def load_data(func_type, differentiation_type, iterations):
    """Load x and y values from the file based on chosen function, differentiation type, and iterations."""
    # Define filename based on the function type, differentiation, and iterations
    filename = f"recursive_{func_type}{'' if differentiation_type == 'weak' else differentiation_type}_data.txt"
    file_path = os.path.join(folder_path, filename)
    
    # Initialize lists for x and y values
    x_vals, y_vals = [], []
    inside_target_iteration = False
    
    # Open and read the file
    with open(file_path, 'r') as file:
        for line in file:
            # Detect the target iteration section
            if line.strip() == f"Iterations={iterations}":
                inside_target_iteration = True
            elif line.startswith("==="):  # End of the target iteration section
                inside_target_iteration = False
            
            # Extract data if within the target iteration
            if inside_target_iteration and line.startswith("Set 1 vs Set"):
                parts = line.strip().split(":")
                x_val = float(parts[0].split()[-1])  # Extract Set number
                y_val = float(parts[1].strip())  # Extract the Total Points value
                x_vals.append(x_val)
                y_vals.append(y_val)
    
    return x_vals, y_vals

# Function to plot data based on user-defined parameters
def plot_recursive_data(func_type, differentiation_type, iterations):
    """Plot data for a given function type, differentiation type, and iteration."""
    x_vals, y_vals = load_data(func_type, differentiation_type, iterations)
    
    # Map function names for display in titles
    func_name_map = {'cos': 'cos(x)', 'sin': 'sin(x)', 'x-1': '1/x'}
    
    # Plotting
    plt.figure(figsize=(10, 6))
    plt.plot(x_vals, y_vals, marker='o', linestyle='-', label=f"Iterations={iterations}")
    
    # Titles and labels
    plt.xlabel("Set Number")
    plt.ylabel("Total Distance")
    plt.title(f"Results for {differentiation_type.capitalize()} Ontological Differentiation for {func_name_map.get(func_type, func_type)}")
    plt.legend(title="Iteration Count")
    plt.grid()
    plt.show()

# Function to plot multiple iterations for comparison
def plot_multiple_iterations(func_type, differentiation_type, iteration_list):
    """Plot data for multiple iterations to compare results."""
    func_name_map = {'cos': 'cos(x)', 'sin': 'sin(x)', 'x-1': '1/x'}
    
    plt.figure(figsize=(12, 8))
    
    for iterations in iteration_list:
        x_vals, y_vals = load_data(func_type, differentiation_type, iterations)
        plt.plot(x_vals, y_vals, marker='o', linestyle='-', label=f"Iterations={iterations}")
    
    # Titles and labels
    plt.xlabel("Set Number")
    plt.ylabel("Total Distance")
    plt.title(f"Results for {differentiation_type.capitalize()} Ontological Differentiation for {func_name_map.get(func_type, func_type)}")
    plt.legend(title="Iterations")
    plt.grid()
    plt.show()

# Example usage
# Choose parameters for plotting
func_type = 'sin'  # Options: 'cos', 'sin', 'x-1'
differentiation_type = 'strong'  # Options: 'strong', 'weak'
iterations = 50  # Specify a single iteration count

# Plot for a single iteration
plot_recursive_data(func_type, differentiation_type, iterations)

# Plot for multiple iterations
iteration_list = [10, 20, 50]  # Adjust as needed
plot_multiple_iterations(func_type, differentiation_type, iteration_list)
