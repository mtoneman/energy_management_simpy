import csv
from datetime import datetime

def process(schedule_file):

    with open(schedule_file, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        schedule = []
        for row in csv_reader:
            if line_count == 0:
                #print(f'Column names are {", ".join(row)}')
                line_count += 1
            if line_count == 1:
                start_time = datetime.fromisoformat(row["datetime"]);
                #print(f'\tstart time {start_time}')
            #print(f'\tRow {line_count} at date {row["datetime"]}: {row["activity"]} at/to {row["destination_city"]},{row["destination_country"]}.')
            row_time = datetime.fromisoformat(row["datetime"])
            schedule_row = {"minutes":(row_time - start_time).total_seconds()/60,"compliment":row["compliment"],"activity":row["activity"],"destination_city":row["destination_city"],"destination_country":row["destination_country"]}
            #print(schedule_row)
            schedule.append(schedule_row)
            line_count += 1
        #print(f'Processed {line_count} lines.')
        return start_time, schedule
