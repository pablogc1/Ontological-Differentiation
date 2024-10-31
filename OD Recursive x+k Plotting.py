# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 12:32:01 2024

@author: pablo
"""

import os
import matplotlib.pyplot as plt

# Path to your folder with results
folder_path = "Recursive x+k"

def load_data(k_value, differentiation_type):
    """Load x and y values from the file based on the chosen k value and differentiation type."""
    filename = f"recursive_k{k_value}_{differentiation_type}_data.txt"
    file_path = os.path.join(folder_path, filename)
    
    x_vals, y_vals = [], []
    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith("Set 1 vs Set"):
                parts = line.strip().split(":")
                x_val = float(parts[0].split()[-1])  # Extract Set number after "Set"
                y_val = float(parts[1].strip())  # Extract the Total Points value
                x_vals.append(x_val)
                y_vals.append(y_val)
    return x_vals, y_vals

def plot_multiple_k(k_values, differentiation_type):
    """Plot data for multiple k values for the specified differentiation type."""
    plt.figure(figsize=(10, 6))
    
    for k in k_values:
        x_vals, y_vals = load_data(k, differentiation_type)
        plt.plot(x_vals, y_vals, marker='o', linestyle='-', label=f"k={k}")
    
    plt.xlabel("Set Number")
    plt.ylabel("Total Distance")
    plt.title(f"Results for {differentiation_type.capitalize()} Ontological Differentiation")
    plt.legend(title="k Values")
    plt.grid()
    plt.show()

# Example usage
k_values = [1, 2, 3, 4, 5]  # Replace with desired k values
differentiation_type = 'weak'  # Choose 'weak' or 'strong'

# Plot results for multiple k values
plot_multiple_k(k_values, differentiation_type)




