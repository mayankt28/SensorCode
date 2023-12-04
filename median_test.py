from statistics import median

def median_filter(data, window_size):
    filtered_data = []
    half_window = window_size // 2

    for i in range(len(data)):
        window = data[max(0, i - half_window): min(len(data), i + half_window + 1)]
        filtered_data.append(median(window))

    return filtered_data


data = [23,43,456,67,88,853,45,23]
result =median_filter(data, 3)
print(result)