# Getting Started with 4tellr 

Once 4tellr is installed, you can begin running information into the application. This is similar to capturing events in a system. To simulate this, run the **BankingSimulator**. Running the simulator for several days allows the system to collect data, which will later be analyzed to understand event patterns and expectations.

When viewed through the 4tellr interface, these events will initially appear **blue**. This is because they are new events, and 4tellr has no prior knowledge of them.

The next step is to "register" these new events with 4tellr, effectively creating placeholders for them in the system. This can be done daily or weekly, giving you time to understand why these events are new—such as a new software release or a business process change. To register the events, you should call the following endpoint with the relevant business date:

### Endpoint:

```
/api/job/create_event_metadata_from_events
```

Example request body:

```
{
  "businessDate": "2024-10-13"
}
```

This process creates metadata entries for each new event that 4tellr has not previously seen. By registering these events, the system can start tracking statistics for each event, allowing for better analysis and understanding in the future.

The best way to handle this is by creating a **Job** using the appropriate endpoint.

**TODO**: Add standard jobs to **Job Control**.

### 

### 

### Data Analysis

Next, you will need to analyze the data. This process can be run regularly if you want to gather the latest statistics, such as processing times, associated with the events. To generate these statistics, you can call the following endpoint:

### Endpoint:

```
/api/events/expected-times/update
```

Currently, this action is available as a button on the **Admin Tasks Screen**. It does not require any parameters.

### Example of Generated Statistics:

```
{
  "statistics": [
    {
      "sequence": 1,
      "no_events_in_sequence": 5,
      "average_time_elapsed": "38:30:54",
      "standard_deviation": 3595.58,
      "monthly_growth": -75
    }
  ]
}
```

### Creating Daily Occurrences for Future Events

Once we have the analysis and statistics, we can begin structuring future events. To do this, we run the `/api/event/create_daily_occurrence` endpoint.

### Endpoint:

```
/api/event/create_daily_occurrence
```

### Example Output:

```
{
  "daily_occurrences": [
    {
      "sequence": 1,
      "expectation": {
        "origin": "initial",
        "status": "active",
        "time": "T+1 14:30:54",
        "updated_at": "2024-10-12T10:37:31.534470"
      },
      "slo": {
        "origin": "auto",
        "status": "active",
        "time": "T+1 15:00:54",
        "updated_at": "2024-10-12T17:31:18.225894"
      },
      "sla": {
        "origin": "auto",
        "status": "active",
        "time": "T+1 15:30:54",
        "updated_at": "2024-10-12T17:31:18.225896"
      }
    }
  ]
}
```

### 

This structure contains the future events, showing when the event is expected to occur, along with the corresponding Service Level Objectives (SLOs) and Service Level Agreements (SLAs), if applicable.


### Generating Event Expectations

Once daily occurrences are defined, we can generate expectations for a specific business date. The expectation generation process uses the structure and times from the daily occurrences to create expectations for the events on the specified business date.

### Endpoint:

```
/api/events/generate-expectations
```

### Example Request:

```
{
  "businessDate": "2024-10-13"
}
```

This request creates the event expectations for the provided business date.

### Example Output:

```
{
  "type": "expectation",
  "eventId": "EXP#Prepare_Variance_Analysis_Report#SUCCESS#3663120d-74d4-4f96-941d-c...",
  "eventName": "Prepare_Variance_Analysis_Report",
  "eventStatus": "SUCCESS",
  "sequence": 1,
  "businessDate": "2024-10-07",
  "expectedArrival": "2024-10-08T06:47:46+00:00",
  "timestamp": "2024-10-12T17:33:17.174127+00:00"
}
```

This output shows the generated expectation for the event, including the event type, name, status, sequence, business date, expected arrival time, and the timestamp when the expectation was generated.

