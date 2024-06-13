#!/bin/bash

set -e

FILE="./model.json"
ACTION=$1
TABLE_NAME=$2

function log_info() {
    echo "[INFO] $1"
}

function read_json_file() {
    cat "$FILE"
}

function create_table() {
    local table=$1

    local table_name=$(echo "$table" | jq -r '.TableName')
    log_info "Generating command to create table: $table_name"

    local key_attributes=$(echo "$table" | jq -r '.KeyAttributes')
    local provisioned_capacity=$(echo "$table" | jq -r '.ProvisionedCapacitySettings.ProvisionedThroughput')
    local gsi=$(echo "$table" | jq -r '.GlobalSecondaryIndexes')

    local partition_key=$(echo "$key_attributes" | jq -r '.PartitionKey')
    local sort_key=$(echo "$key_attributes" | jq -r '.SortKey')

    local attribute_definitions=""
    attribute_definitions+="AttributeName=$(echo "$partition_key" | jq -r '.AttributeName'),AttributeType=$(echo "$partition_key" | jq -r '.AttributeType')"

    if [ "$(echo "$sort_key" | jq -r '.AttributeName')" != "null" ]; then
        attribute_definitions+=" AttributeName=$(echo "$sort_key" | jq -r '.AttributeName'),AttributeType=$(echo "$sort_key" | jq -r '.AttributeType')"
    fi

    local key_schema="AttributeName=$(echo "$partition_key" | jq -r '.AttributeName'),KeyType=HASH"
    
    if [ "$(echo "$sort_key" | jq -r '.AttributeName')" != "null" ]; then
        key_schema+=" AttributeName=$(echo "$sort_key" | jq -r '.AttributeName'),KeyType=RANGE"
    fi

    local throughput="ReadCapacityUnits=$(echo "$provisioned_capacity" | jq -r '.ReadCapacityUnits'),WriteCapacityUnits=$(echo "$provisioned_capacity" | jq -r '.WriteCapacityUnits')"

    local gsi_definitions=""
    if [ "$(echo "$gsi" | jq '. | length')" -gt 0 ]; then
        gsi_definitions+=" --global-secondary-indexes"
        for index in $(echo "$gsi" | jq -r '.[] | @base64'); do
            _jq() {
                echo "${index}" | base64 --decode | jq -r "${1}"
            }
            attribute_definitions+=" AttributeName=$(_jq '.KeyAttributes.PartitionKey.AttributeName'),AttributeType=$(_jq '.KeyAttributes.PartitionKey.AttributeType')"
            attribute_definitions+=" AttributeName=$(_jq '.KeyAttributes.SortKey.AttributeName'),AttributeType=$(_jq '.KeyAttributes.SortKey.AttributeType')"
            gsi_definitions+=" IndexName=$(_jq '.IndexName'),KeySchema=[{AttributeName=$(_jq '.KeyAttributes.PartitionKey.AttributeName'),KeyType=HASH},{AttributeName=$(_jq '.KeyAttributes.SortKey.AttributeName'),KeyType=RANGE}],Projection={ProjectionType=$(_jq '.Projection.ProjectionType')}"
        done
    fi

    local create_table_command="aws dynamodb create-table \
        --table-name \"$table_name\" \
        --attribute-definitions $attribute_definitions \
        --key-schema $key_schema \
        --provisioned-throughput $throughput \
        $gsi_definitions \
	--endpoint-url http://localhost:8000"

    echo $create_table_command
    log_info "Command to create table $table_name generated successfully."
}

function delete_table() {
    local table_name=$1
    log_info "Generating command to delete table: $table_name"
    local delete_table_command="aws dynamodb delete-table --table-name \"$table_name\""
    echo $delete_table_command
    log_info "Command to delete table $table_name generated successfully."
}

json=$(read_json_file)
tables=$(echo "$json" | jq -r '.DataModel')

if [ "$ACTION" == "create" ]; then
    if [ -n "$TABLE_NAME" ]; then
        table=$(echo "$tables" | jq -r --arg TABLE_NAME "$TABLE_NAME" '.[] | select(.TableName == $TABLE_NAME)')
        create_table "$table"
    else
        for table in $(echo "$tables" | jq -r '.[] | @base64'); do
            _jq() {
                echo "${table}" | base64 --decode
            }
            create_table "$(_jq)"
        done
    fi
elif [ "$ACTION" == "delete" ]; then
    if [ -n "$TABLE_NAME" ]; then
        delete_table "$TABLE_NAME"
    else
        for table in $(echo "$tables" | jq -r '.[] | @base64'); do
            _jq() {
                echo "${table}" | base64 --decode
            }
            delete_table "$(_jq | jq -r '.TableName')"
        done
    fi
else
    echo "Invalid action. Use 'create' or 'delete'."
fi
