import csv
from datetime import datetime

def process(forecast_file, start_time):

    with open(forecast_file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        format_str = '%m/%d/%Y %H:%M:%S' # the Date Time format
        forecast = []

        for row in csv_reader:
            if line_count == 0:
                #print(f'Column names are {", ".join(row)}')
                line_count += 1
            row_time = datetime.strptime(row["Date time"], format_str)
            #print((row_time - start_time).total_seconds()/60)
            forecast_row = {"minutes":(row_time - start_time).total_seconds()/60,"location":row["Name"],"wind_direction":row["Wind Direction"],"solar_energy":row["Solar Energy"],"cloud_cover":row["Cloud Cover"],"wind_speed":row["Wind Speed"]}
            #print(forecast_row)
            forecast.append(forecast_row)
            line_count += 1
        print(f'Processed {line_count} lines.')
        return forecast
