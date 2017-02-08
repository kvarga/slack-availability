from pprint import pprint
import subprocess
import logging
import time
from slacker import Slacker
import os

hosts = os.environ['HOSTS_TO_MONITOR'].split()
slack_api_token = os.environ['SLACK_API_TOKEN']
slack_channel = os.environ['SLACK_CHANNEL']
sleep_time = 15

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
  slack = Slacker(slack_api_token)
  slack.chat.post_message(slack_channel, 'Slack Ping Notifier Running!')
  slack.chat.post_message(slack_channel, 'Retry Time: %s seconds' % sleep_time)

  error_count = {}
  first_run = True
  while True:
    for host in hosts:
      ping = subprocess.Popen(
          ["ping", "-c", "1", host],
          stdout=subprocess.PIPE,
          stderr=subprocess.PIPE
      )

      out, error = ping.communicate()
      if error != '':
        if first_run:
          slack.chat.post_message(slack_channel, '%s - Not Available!' % host)
        if host not in error_count:
          error_count[host] = 1
        else:
          error_count[host] += 1
        if error_count[host] % 4 == 0:
          logger.error('%s - %s ping failures!' % (host, error_count[host]))
          slack.chat.post_message(slack_channel, '%s - %s ping failures! (Downtime: %s seconds)' % (host, error_count[host], error_count[host] * sleep_time))
      else:
        if first_run:
          slack.chat.post_message(slack_channel, '%s - Available!' % host)
        if host in error_count:
          logger.info('%s - available after %s failures!' % (host, error_count[host]))
          slack.chat.post_message(slack_channel, '%s - available after %s failures! (Downtime: %s seconds)' % (host, error_count[host], error_count[host] * sleep_time))
          del error_count[host]
    pprint(error_count)
    time.sleep(sleep_time)
    first_run = False

if __name__ == '__main__':
  main()
