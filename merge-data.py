import pandas as pd

# Load original dataset
data_original = pd.read_csv('data/winequality-red.csv', sep=';')

# Load additional dataset
data_additional = pd.read_csv('data/winequality-red-additional.csv', sep=';')

# Merge both datasets
data_combined = pd.concat([data_original, data_additional])

# Save combined dataset
data_combined.to_csv('data/winequality-red-combined.csv', sep=';', index=False)

print("Dataset has been successfully combined and saved.")
