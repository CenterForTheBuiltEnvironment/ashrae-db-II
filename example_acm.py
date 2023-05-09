# Import required libraries
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import statsmodels.api as sm
import statsmodels.formula.api as smf

# Read metadata from Github
url_meta = "https://github.com/CenterForTheBuiltEnvironment/ashrae-db-II/raw/master/v2.1.0/db_metadata.csv"
df_meta = pd.read_csv(url_meta)

# Read database from Github
url_measurements = "https://github.com/CenterForTheBuiltEnvironment/ashrae-db-II/raw/master/v2.1.0/db_measurements_v2.1.0.csv.gz"
df_measurements = pd.read_csv(url_measurements)

# remove nan values in Ta, thermal_sensation, and t_out_isd or t_out
df_acm = df_measurements.loc[(~df_measurements['ta'].isna()) &
                              (~df_measurements['thermal_sensation'].isna()) &
                              (~df_measurements['rh'].isna()) &
                              (~(df_measurements['t_out_isd'].isna()) | ~(df_measurements['t_out'].isna()))].copy()
print('number of rows that have required data for acm:', len(df_acm))
print('number of buildings that have required data for acm:', len(df_acm.building_id.unique()))

# Fill the missing values in the outdoor temperature column
df_acm.loc[:, 't_out_combined'] = df_acm.loc[:, 't_out_isd'].fillna(df_acm.loc[:, 't_out'])

# Remove original temperature columns
df_acm = df_acm.drop(columns=['t_out_isd', 't_out'])

# Merge metadata and databased by office buildings
df_acm = df_acm.merge(df_meta[['building_id', 'region', 'building_type', 'cooling_type', 'records']], on='building_id', how='left')
df_acm = df_acm[df_acm['building_type'] == 'office']
df_acm = df_acm.drop(columns=['building_type'])
print('number of office buildings that have required data for acm:', len(df_acm.building_id.unique()))
print('number of rows (office) that have required data for acm:', len(df_acm))

# Calculate the neutral temperature for each building
def run_lm(bldg):
    try:
        lm_result = smf.ols(formula='ta ~ thermal_sensation', data=bldg).fit()
        # check whether the slope is significant
        if lm_result.pvalues['Intercept'] < 0.05:
            return lm_result.params['Intercept']
        else:
            return np.nan
    except (ValueError, TypeError):
        return np.nan

df_models = df_acm.groupby('building_id').apply(run_lm).reset_index()
df_models.columns = ['building_id', 'neutral_temp']
df_models = df_models.merge(df_meta[['building_id', 'records', 'cooling_type', 'region']], on='building_id', how='left')
df_models['t_out_mean'] = df_acm.groupby('building_id')['t_out_combined'].mean().values
# get rid of all nan values in the neutral_temp column
df_models = df_models[~df_models['neutral_temp'].isna()]

# visualization (weighted regression)
def weighted_regression(x, y, weights, **kwargs):
    X = sm.add_constant(x)
    model = sm.WLS(y, X, weights=weights).fit()
    intercept, slope = model.params
    plt.plot(x, intercept + slope * x, **kwargs)

filtered_df = df_models[(df_models['t_out_mean'] >= 10) & (df_models['t_out_mean'] <= 33) &
                        (df_models['neutral_temp'] > 17) & (df_models['neutral_temp'] < 32)].copy()

filtered_df['cooling_type'] = filtered_df['cooling_type'].str.title()
filtered_df['point_size'] = filtered_df['records']

colors = {"Air Conditioned": "#000000", "Mixed Mode": "#E69F00", "Naturally Ventilated": "#56B4E9"}

lm = sns.lmplot(data=filtered_df, x='t_out_mean', y='neutral_temp', hue='cooling_type', 
                palette=colors, scatter_kws={'alpha': 0.25}, 
                height=5, aspect=1.6, fit_reg=False)

for cooling_type, color in colors.items():
    data_subset = filtered_df[filtered_df['cooling_type'] == cooling_type]
    weighted_regression(data_subset['t_out_mean'], data_subset['neutral_temp'], data_subset['records'], color=color)

sns.scatterplot(data=filtered_df, x='t_out_mean', y='neutral_temp', hue='cooling_type', 
                size='point_size', sizes=(10, 200), legend=False, 
                palette=colors, alpha=0.25, ax=lm.ax)

lm.ax.set_xlim(8, 32)
lm.ax.set_ylim(17, 33)
lm.ax.set_xlabel('\nOutdoor Temperature')
lm.ax.set_ylabel('Neutral Temperature\n')
lm.ax.xaxis.set_major_formatter(FormatStrFormatter('%d°C'))
lm.ax.yaxis.set_major_formatter(FormatStrFormatter('%d°C'))

lm.ax.annotate("Lower 80%", xy=(33.7, 24.5), xycoords='data', fontsize=10, color='grey', fontstyle='italic')
lm.ax.annotate("Lower 90%", xy=(33.7, 25.5), xycoords='data', fontsize=10, color='grey', fontstyle='italic')
lm.ax.annotate("Upper 90%", xy=(33.7, 28.0), xycoords='data', fontsize=10, color='grey', fontstyle='italic')
lm.ax.annotate("Upper 80%", xy=(33.7, 30.5), xycoords='data', fontsize=10, color='grey', fontstyle='italic')

plt.title('Adaptive Comfort Model', fontsize=16)
plt.suptitle('Example analysis of adaptive thermal comfort using the ASHRAE Global Thermal Comfort Database II', fontsize=12, fontstyle='italic', y=0.95)
plt.savefig('ACM_db2.png', dpi=300, bbox_inches='tight')
