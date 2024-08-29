import json
import time
import threading
import random
from datetime import datetime, timedelta


# Load the process steps from the JSON file
def load_process_steps(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


# Load configuration from a config file
def load_config(file_path):
    with open(file_path, 'r') as f:
        return json.load(f)


# Simulate the processing of a single trade
def process_trade(trade_id, steps):
    start_time = datetime.now()
    print(f"\nStarting trade {trade_id} at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    for step in steps:
        # Simulate the processing time
        process_time = int(step["processing_time"].split()[0]) / 1000 if "ms" in step["processing_time"] else 0
        if process_time > 0:
            time.sleep(process_time)

        # Simulate scheduled time processing
        scheduled_time = step.get("scheduled_time")
        if scheduled_time:
            # Calculate the actual scheduled datetime
            current_time = datetime.now()
            delta = timedelta(days=int(scheduled_time.split()[0].replace("T+", "")))
            scheduled_datetime = start_time + delta + timedelta(hours=int(scheduled_time.split()[1].split(':')[0]),
                                                                minutes=int(scheduled_time.split()[1].split(':')[1]),
                                                                seconds=int(scheduled_time.split()[1].split(':')[2]))
            if scheduled_datetime > current_time:
                time_to_wait = (scheduled_datetime - current_time).total_seconds()
                print(f"Waiting for scheduled time: {scheduled_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
                time.sleep(time_to_wait)

        # Output step result
        print(f"Trade {trade_id} - {step['process_id']} completed by {step['application']}")

    print(f"Trade {trade_id} completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# Generate and process trades based on trades per second from config
def generate_trades(steps, trades_per_second):
    trade_id = 1
    while True:
        threads = []
        for _ in range(trades_per_second):
            thread = threading.Thread(target=process_trade, args=(trade_id, steps))
            threads.append(thread)
            thread.start()
            trade_id += 1

        for thread in threads:
            thread.join()

        time.sleep(1)


# Main function to load config, steps, and start trade processing
def main():
    steps = load_process_steps("./configs/trading.json")
    config = load_config("config.json")

    trades_per_second = config.get("trades_per_second", 1)
    print(f"Simulating {trades_per_second} trades per second.")

    generate_trades(steps, trades_per_second)


if __name__ == "__main__":
    main()
