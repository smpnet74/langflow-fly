#!/bin/bash

echo "Monitoring application scaling status..."

while true; do
    # Get the status and parse it
    status=$(fly status --json)
    
    # Check if there are any running instances
    instance_count=$(echo "$status" | jq '.Machines | map(select(.state == "started")) | length')
    
    # Get current timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    if [ "$instance_count" -eq 0 ]; then
        echo "[$timestamp] Application has scaled to zero - No running instances"
    else
        echo "[$timestamp] Application is running with $instance_count instance(s)"
        
        # Show details of running instances
        echo "$status" | jq -r '.Machines[] | select(.state == "started") | "  - Instance \(.id) in region \(.region) - State: \(.state)"'
    fi
    
    # Wait before next check
    sleep 10
done
