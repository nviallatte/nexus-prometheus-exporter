#!/usr/bin/python

import json
import time
import urllib2
from prometheus_client import start_http_server
from prometheus_client.core import GaugeMetricFamily, SummaryMetricFamily, REGISTRY
import argparse
import yaml
from objectpath import Tree
import logging
import base64

DEFAULT_PORT=9158
DEFAULT_LOG_LEVEL='info'

class JsonPathCollector(object):
  def __init__(self, config):
    self._config = config

  def collect(self):
    config = self._config
    info_request = urllib2.Request(config['json_data_url'])
    if config['basic_auth_user'] != "":
      info_request.add_header("Authorization", "Basic %s" % base64.standard_b64encode('%s:%s' % (config['basic_auth_user'], config['basic_auth_password'])))
    if config['host'] != "":
      info_request.add_header("Host", config['host'])
    result = json.loads(urllib2.urlopen(info_request).read())
    result_tree = Tree(result)
    for metric_config in config['metrics']:
      metric_path = metric_config['path']
      metric_type = metric_config['type']
      values = result_tree.execute(metric_path)

      if metric_type == "gauge":
        for current_gauge_metric_attribute in tuple(values):
          current_gauge_metric_attribute_value = result_tree.execute(metric_path + ".*['" + current_gauge_metric_attribute + "'].value")
          if isinstance(current_gauge_metric_attribute_value, float):
            metric_name = "{}_{}".format(config['metric_name_prefix'], current_gauge_metric_attribute.replace('.', '_').replace('-','_').lower())
            metric = GaugeMetricFamily(metric_name, '', value=current_gauge_metric_attribute_value)
            yield metric

      if metric_type == "meters":
        exception_count_map = {}
        for current_meters_metric_attribute in tuple(values):         
          count_value=result_tree.execute(metric_path + ".*['" + current_meters_metric_attribute + "'].count")
          exception_count_map[current_meters_metric_attribute] = count_value

        for key in exception_count_map.keys():
          suffix = key.replace('.', '_').replace('-','_').lower()
          label = "type"
          formatted_key = key
          if ".exception" in key:
            suffix = "exceptions"
            label = "exceptionType"
            formatted_key = key.replace(".exception", "")
          elif "metrics." in key:
            suffix = "log"
            label = "level"
            formatted_key = key.replace("metrics.", "")
          elif "-responses" in key:
            suffix = "response"
            label = "status"
            formatted_key = key.replace("-responses", "").replace("org.eclipse.jetty.webapp.WebAppContext.", "")
          metric_name = "{}_{}".format(config['metric_name_prefix'], suffix)
          metric = SummaryMetricFamily(metric_name, '', labels=[label])
          metric.add_metric([formatted_key], count_value=exception_count_map.get(key), sum_value=exception_count_map.get(key))
          yield metric

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Expose metrics bu jsonpath for configured url')
  parser.add_argument('config_file_path', help='Path of the config file')
  args = parser.parse_args()
  with open(args.config_file_path) as config_file:
    config = yaml.load(config_file)
    log_level = config.get('log_level', DEFAULT_LOG_LEVEL)
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.getLevelName(log_level.upper()))
    exporter_port = config.get('exporter_port', DEFAULT_PORT)
    logging.debug("Config %s", config)
    logging.info('Starting server on port %s', exporter_port)
    start_http_server(exporter_port)
    REGISTRY.register(JsonPathCollector(config))
  while True: time.sleep(1)
