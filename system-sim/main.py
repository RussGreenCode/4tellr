import json
from api_helper.event_helper import APIHelper
from api_helper.validators import CommonFieldValidator, FileEventValidator, MessageEventValidator, \
    DatabaseEventValidator
from event_simulator import EventSimulator, load_config

API_URL = "http://127.0.0.1:5000/api/events"


def main():
    config = load_config('config.txt')
    delta = config['DELTA']
    business_days = config['BUSINESS_DAYS']

    api_helper = APIHelper(API_URL)

    # Add validators
    api_helper.add_validator(CommonFieldValidator())
    api_helper.add_validator(FileEventValidator())
    api_helper.add_validator(MessageEventValidator())
    api_helper.add_validator(DatabaseEventValidator())

    # Load systems flow from JSON
    with open('system_definition.json', 'r') as file:
        systems_flow = json.load(file)

    event_simulator = EventSimulator(api_helper, systems_flow, delta, business_days)

    # Run simulation
    event_simulator.run_simulation()


if __name__ == "__main__":
    main()
