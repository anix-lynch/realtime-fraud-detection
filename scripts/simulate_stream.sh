#!/bin/bash

# Simulate streaming events to the fraud detection API
cd "$(dirname "$0")/.."

API_URL="http://localhost:8001"
EVENTS_FILE="data/synthetic_events.jsonl"

if [ ! -f "$EVENTS_FILE" ]; then
    echo "Error: Events file not found: $EVENTS_FILE"
    exit 1
fi

echo "Starting stream simulation..."
echo "Sending events to: $API_URL/fraud_score"
echo "Events file: $EVENTS_FILE"

# Count total events
TOTAL_EVENTS=$(wc -l < "$EVENTS_FILE")
echo "Total events to process: $TOTAL_EVENTS"

# Process events sequentially with small delays
COUNT=0
while IFS= read -r event; do
    COUNT=$((COUNT + 1))

    # Send POST request
    response=$(curl -s -w "%{http_code}" -X POST \
        -H "Content-Type: application/json" \
        -d "$event" \
        "$API_URL/fraud_score")

    http_code=${response: -3}
    response_body=${response:0:-3}

    if [ "$http_code" -eq 200 ]; then
        # Extract score from response (simple JSON parsing)
        score=$(echo "$response_body" | grep -o '"score":[0-9.]*' | cut -d':' -f2)
        echo "[$COUNT/$TOTAL_EVENTS] Event processed - Score: $score"
    else
        echo "[$COUNT/$TOTAL_EVENTS] Error: HTTP $http_code - $response_body"
    fi

    # Small delay between requests (simulate real-time streaming)
    sleep 0.1

done < "$EVENTS_FILE"

echo "Stream simulation completed!"
