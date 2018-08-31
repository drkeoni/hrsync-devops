import sys
import os
import json
import datetime as dt
import logging
import time

import boto3
from fabric import task

ROOT = os.path.abspath(os.path.dirname(__file__))
SERVER_DATA_FILE = os.path.join(ROOT, '.server.json')
TAG_NAME = 'hrsync-server'
DNS_NAME = 'nasonstudios.net.'
PUBLIC_NAME = '{}.{}'.format('hrsync', DNS_NAME.rstrip('.'))
AWS_REGION = 'us-east-1'
IP_TIMEOUT = 60

LOG_FORMAT = "%(asctime)s %(filename)s [%(levelname)s] %(message)s"
log = logging.getLogger(__file__)
log.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setFormatter(logging.Formatter(LOG_FORMAT))
log.addHandler(ch)


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (dt.datetime, dt.date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))


def server_data_is_stale():
    if not os.path.exists(SERVER_DATA_FILE):
        return True
    now = dt.datetime.now()
    then = dt.datetime.fromtimestamp(os.path.getmtime(SERVER_DATA_FILE))
    elapsed = now - then
    return elapsed > dt.timedelta(hours=6)


def get_aws_config(force_refresh=False):
    if server_data_is_stale() or force_refresh:
        data = {}
        ec2_client = boto3.client('ec2')
        instance_info = ec2_client.describe_instances(
            Filters=[{'Name': 'tag:Name', 'Values': [TAG_NAME]}]
        )
        instance_info = instance_info['Reservations'][0]['Instances'][0]
        data['instance_id'] = instance_info['InstanceId']
        data['public_ip'] = instance_info.get('PublicIpAddress', None)
        data['public_dns_name'] = instance_info.get('PublicDnsName', None)
        dns_client = boto3.client('route53')
        data['hosted_zone_id'] = dns_client.list_hosted_zones_by_name(DNSName=DNS_NAME)['HostedZones'][0]['Id']
        with open(SERVER_DATA_FILE, 'w') as outfile:
            outfile.write(json.dumps(data, indent=4, sort_keys=True) + os.linesep)
    with open(SERVER_DATA_FILE, 'r') as infile:
        data = json.load(infile)
    return data


def log_response(response):
    log.info(json.dumps(response, indent=4, default=json_serial))


@task
def launch_instance(c):
    aws_data = get_aws_config()
    ec2_client = boto3.client('ec2')
    response = ec2_client.start_instances(InstanceIds=[aws_data['instance_id']])
    log_response(response)


@task
def reroute_dns(c):
    aws_data = get_aws_config()
    if aws_data['public_ip'] is None:
        aws_data = get_aws_config(force_refresh=True)
        t = 0
        while aws_data['public_ip'] is None and t < IP_TIMEOUT:
            log.info('t={}, sleeping for 5 seconds to find public IP address'.format(t))
            time.sleep(5)
            aws_data = get_aws_config(force_refresh=True)
            t += 5
        if t >= IP_TIMEOUT:
            log.error('Waiting for public IP address timed out (>{} seconds)'.format(IP_TIMEOUT))
            return

    dns_client = boto3.client('route53')
    log.info('Changing A record for {} to point to {}'.format(PUBLIC_NAME, aws_data['public_ip']))
    change_request = {
        'Comment' : 'rerouting {}'.format(PUBLIC_NAME),
        'Changes': [
            {
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': PUBLIC_NAME,
                    'Type': 'A',
                    'TTL': 300,
                    'ResourceRecords': [
                        { 'Value': aws_data['public_ip'] }
                    ]
                }
            }]
    } 
    response = dns_client.change_resource_record_sets(
        HostedZoneId=aws_data['hosted_zone_id'],
        ChangeBatch=change_request
    )
    log_response(response)


@task
def hello(c):
    c.local('echo "hello"')
