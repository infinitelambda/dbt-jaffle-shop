import os
for key, item in os.environ.items():
    if 'dbt' in key.lower():
        print(f'{key}: {item}, {" ".join(list(item))}')