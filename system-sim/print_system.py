import json

# Load the JSON structure from a file or directly from the string
with open('./system_definition.json', 'r') as file:
    systems_flow = json.load(file)

flow_diagram = []

# Example function to print the flow of data with event types
def print_system_flow(system_name, systems_flow, level=0):
    global flow_diagram
    system = next((s for s in systems_flow['systems'] if s['name'] == system_name), None)
    if system:
        indent = "  " * level
        flow_diagram.append(f"{indent}{system['name']}")

        print(f"{indent}System: {system['name']}")
        print(f"{indent}Type: {system['type']}")
        print(f"{indent}Data Types:")
        for data_type in system['dataTypes']:
            print(f"{indent}  - {data_type['name']}: {data_type['description']} ({', '.join(data_type['formats'])})")
        print(f"{indent}Next Systems:")
        for next_system in system['nextSystems']:
            print(f"{indent}  - {next_system['system']} (Event Type: {next_system['eventType']})")
            print(f"{indent}    Events:")
            for event in next_system['events']:
                print(f"{indent}      - {event['name']} (Status: {event['status']}, Expected Time: {event['expectedTime']})")
            flow_diagram.append(f"{indent}  -> {next_system['system']} (Event Type: {next_system['eventType']})")
        print()
        for next_system in system['nextSystems']:
            print_system_flow(next_system['system'], systems_flow, level + 1)
    else:
        print(f"System '{system_name}' not found in the flow.")

# Start printing from the first system (e.g., "Market Data Providers")
print_system_flow("Market Data Providers", systems_flow)

# Print the conceptual flow diagram
print("\nConceptual Flow Diagram:")
print("\n".join(flow_diagram))
