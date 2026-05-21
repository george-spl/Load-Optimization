import pandas as pd
from faker import Faker
import random

random.seed(42)
fake = Faker('en_GB')

crate_types = ['Type A', 'Type B', 'Type C', 'Type D']
crate_sizes = ['141x107x234',
                '161x108x247',
                '142x115x259', 
                '161x111x234', 
                '151x131x257', 
                '155x115x234', 
                '147x132x231', 
                '147x131x257', 
                '154x131x257', 
                '145x131x231',
                '151x120x232'
                ]

data = []
for i in range(25):
    crate_id = i + 1
    crate_type = random.choice(crate_types)
    gross_weight = round(random.random() * 100 + 800, 2)  # Random weight between 800 and 900
    net_weight = round(gross_weight - (random.random() * 50 + 50), 2)  # Net weight is gross weight minus 50-100
    size = random.choice(crate_sizes)  # Size format: Length x Width x Height in cm
    asset_tag = fake.uuid4()
    location = "R" + str(random.randint(1, 10))  # Random location R1 to R10
    data.append({
        'Crate ID': crate_id,
        'Crate Type': crate_type,
        'Gross Weight (kg)': gross_weight,
        'Net Weight (kg)': net_weight,
        'Size (cm)': size,
        'Asset Tag': asset_tag,
        'Location': location
    })

df = pd.DataFrame(data)
df.to_excel('crate_data.xlsx', index=False)
print("Crate data has been generated and saved to 'crate_data.xlsx'.")
