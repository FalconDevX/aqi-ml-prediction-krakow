import pandas as pd
import numpy as np
import joblib

def predict_future(model_path, current_data_csv, index_name, steps=8):
    """
    Recursive future prediction using trained model.
    index_name must be EXACTLY the same as used in training (e.g. 'PM10', 'O3', 'CO')
    """

    #load model
    try:
        model = joblib.load(model_path)
        print(f"Loaded model: {model_path}")
    except FileNotFoundError:
        raise Exception(f"Model file not found: {model_path}")

    #load data
    df = pd.read_csv(current_data_csv)

    df = df[['Time', df.columns[1]]].copy()
    df.rename(columns={df.columns[1]: index_name}, inplace=True)

    df['Time'] = pd.to_datetime(df['Time'])
    df = df.sort_values('Time').dropna()

    #validation
    if len(df) < 48:
        raise Exception(f"Not enough data! Need at least 48 rows, got {len(df)}")

    #take last 48h
    df = df.tail(48)

    history = df[index_name].tolist()
    last_time = df['Time'].iloc[-1]

    predictions = []

    print(f"Starting recursive prediction for {steps} steps...")

    #recursive prediction
    for step in range(1, steps + 1):
        prediction_time = last_time + pd.Timedelta(hours=step)

        hour = prediction_time.hour
        month = prediction_time.month

        input_data = pd.DataFrame([{
            'hour': hour,
            'dayofweek': prediction_time.dayofweek,
            'month': month,
            'dayofyear': prediction_time.dayofyear,
            'hour_sin': np.sin(2 * np.pi * hour / 24),
            'hour_cos': np.cos(2 * np.pi * hour / 24),
            'month_sin': np.sin(2 * np.pi * month / 12),
            'month_cos': np.cos(2 * np.pi * month / 12),

            f'{index_name}_lag_1': history[-1],
            f'{index_name}_lag_2': history[-2],
            f'{index_name}_lag_3': history[-3],
            f'{index_name}_lag_24': history[-24],
            f'{index_name}_lag_48': history[-48]
        }])

        pred = model.predict(input_data)[0]

        history.append(pred)

        predictions.append({
            'Time': prediction_time,
            index_name: round(pred, 2)
        })

    result_df = pd.DataFrame(predictions)

    print("Prediction finished.")
    return result_df

wyniki = predict_future(
    model_path='models/CO_model.joblib',
    current_data_csv='data/test_CO.csv',
    index_name='CO', 
    steps=8
)
