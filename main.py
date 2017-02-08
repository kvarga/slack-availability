#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""Host Availability Slack Notification Tool
Pings a list of hosts and notifies Slack channel when the host goes down/up
"""

from slacker import Slacker
import logging
import os
import subprocess
import time

hosts = os.environ['HOSTS_TO_MONITOR'].split(" ")
slack_api_token = os.environ['SLACK_API_TOKEN']
slack_channel = os.environ['SLACK_CHANNEL']
sleep_time = float(os.environ['SLEEP_TIME'])

slack = Slacker(slack_api_token)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
  slack.chat.post_message(slack_channel, 'Slack Ping Notifier Running!')
  slack.chat.post_message(slack_channel, 'Retry Time: %s seconds' % sleep_time)

  error_count = {}
  first_run = True

  while True:
    for host in hosts:
      ping_success = ping_host(host)

      # Send notification when the script first runs
      if first_run:
        if ping_success:
          post_message('%s - Ping Success!' % host)
        else:
          post_message('%s - Ping Failure!' % host)

      if not ping_success:
        '''Handle failures:'''
        if host not in error_count:
          error_count[host] = 1
        else:
          error_count[host] += 1
        if error_count[host] % 4 == 0:
          post_message('%s - %s ping failures! (Downtime: %s seconds)' % (host, error_count[host], error_count[host] * sleep_time))
      else:
        '''Handle successful pings
        If a host comes back up, send a notification'''
        if host in error_count:
          post_message('%s - available after %s failures! (Downtime: %s seconds)' % (host, error_count[host], error_count[host] * sleep_time))
          del error_count[host]
    first_run = False
    time.sleep(sleep_time)


def ping_host(host):
  '''ping_host: Pings a host and returns True or False'''
  ping = subprocess.Popen(
    ["ping", "-c", "1", "-t", "1", host],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
  )
  out, error = ping.communicate()

  # If error return is an empty string, ping was successful
  return error == ''


def post_message(message):
  '''post_message: Send message to both logger/stdout and Slack'''
  logger.info(message)
  slack.chat.post_message(slack_channel, message)


if __name__ == '__main__':
  main()
