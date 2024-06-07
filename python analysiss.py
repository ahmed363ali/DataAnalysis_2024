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
survey_all = pd.read_csv(file_path + 'survey_all.txt', delimiter='\t', encoding='latin1', on_bad_lines='skip')

# Standardize DBN column names
datasets = [sat_results, demographics, graduation, ap_2010]
for dataset in datasets:
    dataset.rename(columns={'DBN': 'dbn'}, inplace=True)

# Correct the dbn values in class_size
class_size['dbn'] = class_size['CSD'].astype(str).str.zfill(2) + class_size['SCHOOL CODE']

# Merge all datasets
combined = sat_results
for dataset in [demographics, graduation, hs_directory, class_size, ap_2010]:
    combined = combined.merge(dataset, on='dbn', how='inner')

# Select only relevant columns from survey_all
survey_fields = ['dbn', 'rr_s', 'rr_t', 'rr_p', 'N_s', 'N_t', 'N_p', 'saf_p_11', 'com_p_11', 'eng_p_11', 'aca_p_11',
                 'saf_t_11', 'com_t_11', 'eng_t_11', 'aca_t_11']
survey_all = survey_all[survey_fields]

# Merge the survey data
combined = combined.merge(survey_all, on='dbn', how='inner')

# Remove duplicate rows
combined.drop_duplicates(subset=['dbn'], keep='first', inplace=True)

# Convert SAT score columns to numeric and calculate the sat_score
sat_results['SAT Math Avg. Score'] = pd.to_numeric(sat_results['SAT Math Avg. Score'], errors='coerce')
sat_results['SAT Critical Reading Avg. Score'] = pd.to_numeric(sat_results['SAT Critical Reading Avg. Score'], errors='coerce')
sat_results['SAT Writing Avg. Score'] = pd.to_numeric(sat_results['SAT Writing Avg. Score'], errors='coerce')
sat_results['sat_score'] = sat_results[['SAT Math Avg. Score', 'SAT Critical Reading Avg. Score', 'SAT Writing Avg. Score']].mean(axis=1)

# Merge SAT scores with combined data
combined = combined.merge(sat_results[['dbn', 'sat_score']], on='dbn', how='inner')

# Perform correlation analysis on numeric columns
numeric_columns = combined.select_dtypes(include=['number']).columns
correlations = combined[numeric_columns].corr()['sat_score'].drop('sat_score')
print("\nCorrelation between survey fields and SAT scores:")
print(correlations)
