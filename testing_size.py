import pandas as pd
df = pd.read_excel('crate_data.xlsx')
print(df['Size (cm)'].head(10))
print(df['Gross Weight (kg)'].head(10))
