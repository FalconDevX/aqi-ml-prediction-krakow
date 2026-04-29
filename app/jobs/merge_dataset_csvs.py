import pandas as pd
import os

# Parametry
base_dir = 'data'      # Twój główny folder z danymi
years = range(2017, 2024) # Lata od 2017 do 2023 włącznie

# Lista wszystkich wskaźników z Twojego zrzutu ekranu
pollutants = ['CO', 'NO2', 'O3', 'PM10', 'PM25', 'SO2']

# Pętla zewnętrzna - przechodzi przez każdy wskaźnik
for pollutant in pollutants:
    dataframes = []
    print(f"--- Przetwarzanie wskaźnika: {pollutant} ---")
    
    # Pętla wewnętrzna - przechodzi przez kolejne lata dla danego wskaźnika
    for year in years:
        file_path = os.path.join(base_dir, str(year), f"{year}_{pollutant}.csv")
        
        if os.path.exists(file_path):
            df = pd.read_csv(file_path)
            dataframes.append(df)
            print(f"  Wczytano: {file_path}")
        else:
            print(f"  Nie znaleziono pliku: {file_path}")
    
    # Łączenie i zapisywanie danych dla obecnego wskaźnika
    if dataframes:
        merged_df = pd.concat(dataframes, ignore_index=True)
        output_filename = f"merged_{pollutant}_2017_2023.csv"
        merged_df.to_csv(output_filename, index=False)
        print(f"-> Zapisano połączony plik: {output_filename}\n")
    else:
        print(f"-> Brak danych dla {pollutant}\n")

print("Zakończono łączenie wszystkich wskaźników! :)")