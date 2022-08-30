"""
Module to provide an interaction with Kinesis data streams.
This could be expanded to accept command line arguments.
"""
import time

import boto3
from botocore.exceptions import ClientError

AWS_REGION = "us-east-2"
AWS_PROFILE = "localstack"
LOCALSTACK_ENDPOINT = "http://localhost:4566"


def main():
    boto3.setup_default_session(profile_name=AWS_PROFILE)
    client = boto3.client(
        "kinesis", region_name=AWS_REGION, endpoint_url=LOCALSTACK_ENDPOINT
    )
    stream_name = "my_stream"

    print(f"Creating Kinesis data stream: {stream_name}")
    client.create_stream(
        StreamName=stream_name,
        ShardCount=1,
        StreamModeDetails={"StreamMode": "PROVISIONED"},
    )
    streams = client.list_streams(ExclusiveStartStreamName=stream_name)
    print(f"{streams=}")

    print(f"Waiting for Kinesis data stream, {stream_name}, to be ACTIVE")
    i = 0
    while i < 10:
        response = client.describe_stream_summary(StreamName=stream_name)
        if response["StreamDescriptionSummary"]["StreamStatus"] != "ACTIVE":
            i += 1
            time.sleep(0.1)
            continue
        else:
            break

    print(f"Putting records on Kinesis data stream, {stream_name}")
    data = ["Test data", "more data"]
    partition_key = "1"
    response = client.put_records(
        Records=[
            {"Data": data[0], "PartitionKey": partition_key},
            {"Data": data[1], "PartitionKey": partition_key},
        ],
        StreamName=stream_name,
    )
    records = response.get("Records")
    if not records:
        raise RuntimeError(
            f"Failed to put records on Kinesis stream {stream_name}. Got {response}"
        )
    errors = [record for record in records if record.get("ErrorCode")]
    if errors:
        print(
            f"Errors when putting data on Kinesis data stream {stream_name}: {errors}"
        )
    shard_id = records[0]["ShardId"]
    sequence_number = records[0]["SequenceNumber"]

    response = client.get_shard_iterator(
        StreamName=stream_name,
        ShardId=shard_id,
        ShardIteratorType="AT_SEQUENCE_NUMBER",
        StartingSequenceNumber=sequence_number,
    )
    shard_iterator = response.get("ShardIterator")
    if not shard_iterator:
        raise RuntimeError(
            f"Shard Iterator for Kinesis data stream {stream_name} could not be "
            f"created. Got {response}"
        )

    print(f"Retrieving records on Kinesis data stream: {stream_name}")
    response = client.get_records(ShardIterator=shard_iterator)
    records = response.get("Records")
    if len(records) != len(data):
        raise RuntimeError(
            f"Put {len(data)} records on the Kinesis data stream, {stream_name}, "
            f"but got {len(records)}!"
        )
    print(f"Retrieved all records form Kinesis data stream, {stream_name}")

    print(f"Deleting Kinesis data stream: {stream_name}")
    client.delete_stream(
        StreamName=stream_name,
        EnforceConsumerDeletion=True,
    )
    print(f"Waiting for Kinesis data stream, {stream_name}, to be DELETED")
    i = 0
    while i < 10:
        try:
            response = client.describe_stream_summary(StreamName=stream_name)
        # ClientError used since the stream no longer exists.
        except ClientError:
            break
        if response["StreamDescriptionSummary"]["StreamStatus"] == "DELETING":
            i += 1
            time.sleep(0.1)
            continue
        else:
            break

    streams = client.list_streams()
    if streams.get("StreamNames"):
        raise RuntimeError(f"Created 1 data stream, but stream not deleted")
    else:
        print("All Kinesis data streams deleted. Have a nice day :)")


if __name__ == "__main__":
    main()
