from numpy import inf


def calculate_rmse(predictions, targets):
    return ((predictions - targets) ** 2).mean() ** 0.5


def calculate_mae(predictions, targets):
    return (abs(predictions - targets)).mean()


def calculate_mre(predictions, targets):
    result = (abs(predictions - targets) / targets).mean()
    if result != inf:
        return result
    return -1


def generate_sentence(key_indicators):
    humidity_mean = key_indicators['relative_humidity_2m']['mean']
    wind_mean = key_indicators['wind_speed_10m']['mean']
    wind_std = key_indicators['wind_speed_10m']['std']

    sentence = f"The humidity has been around {humidity_mean:.2f}%. " \
               f"The wind speed has been averaging {wind_mean:.2f} m/s with a {wind_std:.2f} m/s variation."

    return sentence
