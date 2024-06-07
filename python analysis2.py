import pandas as pd

# Define the file path
file_path = 'C:/Users/AHMED2/Desktop/files/pythone 实验/实验二/data/schools/'

# Load datasets
sat_results = pd.read_csv(file_path + 'sat_results.csv')
demographics = pd.read_csv(file_path + 'demographics.csv')
graduation = pd.read_csv(file_path + 'graduation.csv')
hs_directory = pd.read_csv(file_path + 'hs_directory.csv')
class_size = pd.read_csv(file_path + 'class_size.csv')
ap_2010 = pd.read_csv(file_path + 'ap_2010.csv')
survey_d75 = pd.read_csv(file_path + 'survey_d75.txt', delimiter='\t')
survey_all = pd.read_csv(file_path + 'survey_all.txt', delimiter='\t', encoding='latin1', on_bad_lines='skip')

# Standardize DBN column names
sat_results.rename(columns={'DBN': 'dbn'}, inplace=True)
demographics.rename(columns={'DBN': 'dbn'}, inplace=True)
graduation.rename(columns={'DBN': 'dbn'}, inplace=True)
ap_2010.rename(columns={'DBN': 'dbn'}, inplace=True)

# Correct the dbn values in class_size
class_size['dbn'] = class_size['CSD'].astype(str).str.zfill(2) + class_size['SCHOOL CODE']

# Ensure all dbn values are strings and properly formatted
datasets = {
    'sat_results': sat_results,
    'demographics': demographics,
    'graduation': graduation,
    'hs_directory': hs_directory,
    'class_size': class_size,
    'ap_2010': ap_2010,
    'survey_d75': survey_d75,
    'survey_all': survey_all
}

for df in datasets.values():
    df['dbn'] = df['dbn'].astype(str).str.strip()

# Print unique dbn values for each dataset
def print_unique_dbn(df, name):
    unique_dbn = df['dbn'].unique()
    print(f"Unique dbn values in {name}: {unique_dbn[:10]}")
    return set(unique_dbn)

print("Unique dbn values in each dataset:")
dbn_sets = {}
for name, df in datasets.items():
    dbn_sets[name] = print_unique_dbn(df, name)

# Find common dbn values before merging
def find_common_dbn(*dbn_sets):
    common_dbn = set.intersection(*dbn_sets)
    return common_dbn

# Determine the common dbn values
common_dbn = find_common_dbn(dbn_sets['sat_results'], dbn_sets['demographics'], dbn_sets['graduation'], dbn_sets['hs_directory'], dbn_sets['class_size'], dbn_sets['ap_2010'], dbn_sets['survey_all'])
print(f"Common dbn values before merging: {list(common_dbn)[:10]}")

# Subset datasets to only include common dbn values
for key in datasets:
    datasets[key] = datasets[key][datasets[key]['dbn'].isin(common_dbn)]

# Inspect the columns of survey_all
print("Columns in survey_all dataset:")
print(survey_all.columns.tolist())

# Define survey_fields based on available columns in survey_all
survey_fields = [
    'dbn', 'rr_s', 'rr_t', 'rr_p', 'N_s', 'N_t', 'N_p',
    'saf_p_11', 'com_p_11', 'eng_p_11', 'aca_p_11',
    'saf_t_11', 'com_t_11', 'eng_t_11', 'aca_t_11'
]

# Select only the necessary columns from survey_all
survey_all = survey_all[survey_fields]

# Merge datasets step-by-step and inspect shape
combined = sat_results.copy()
print("Initial combined shape:", combined.shape)

combined = combined.merge(demographics, on='dbn', how='inner')
print("After merging demographics:", combined.shape)

combined = combined.merge(graduation, on='dbn', how='inner')
print("After merging graduation:", combined.shape)

combined = combined.merge(hs_directory, on='dbn', how='inner')
print("After merging hs_directory:", combined.shape)

combined = combined.merge(class_size, on='dbn', how='inner')
print("After merging class_size:", combined.shape)

combined = combined.merge(ap_2010, on='dbn', how='inner')
print("After merging ap_2010:", combined.shape)

combined = combined.merge(survey_all, on='dbn', how='inner')
print("After merging survey_all:", combined.shape)

# Remove duplicate rows
combined.drop_duplicates(subset=['dbn'], keep='first', inplace=True)
print("After removing duplicates:", combined.shape)

# Convert SAT score columns to numeric
sat_results['SAT Math Avg. Score'] = pd.to_numeric(sat_results['SAT Math Avg. Score'], errors='coerce')
sat_results['SAT Critical Reading Avg. Score'] = pd.to_numeric(sat_results['SAT Critical Reading Avg. Score'], errors='coerce')
sat_results['SAT Writing Avg. Score'] = pd.to_numeric(sat_results['SAT Writing Avg. Score'], errors='coerce')

# Calculate the sat_score as the mean of the three scores
sat_results['sat_score'] = sat_results[['SAT Math Avg. Score', 'SAT Critical Reading Avg. Score', 'SAT Writing Avg. Score']].mean(axis=1)

# Merge SAT scores with combined data
combined = combined.merge(sat_results[['dbn', 'sat_score']], on='dbn', how='inner')
print("After merging SAT scores:", combined.shape)

# Keep only numeric columns
numeric_columns = combined.select_dtypes(include=['number']).columns
print(f"Numeric columns: {numeric_columns.tolist()}")

# Perform correlation analysis on numeric columns
correlations = combined[numeric_columns].corr()['sat_score'].drop('sat_score')
print("\nCorrelation between survey fields and SAT scores:")
print(correlations)
