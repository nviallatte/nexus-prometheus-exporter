# prometheus-nexus-exporter

Converts json data from a Nexus 3 from endpoint `http://<nexus>/service/metrics/data`. 

This project is forked from https://github.com/project-sunbird/prometheus-jsonpath-exporter

### Run

#### Using code (local)

```
# Ensure python 2.x and pip installed
pip install -r app/requirements.txt
python app/exporter.py example/config.yml
```

#### Using docker

```
docker run -p 9158:9158 -v $(pwd)/example/config.yml:/etc/prometheus-nexus-exporter/config.yml nviallatte/prometheus-nexus-exporter /etc/prometheus-nexus-exporter/config.yml
```

### Config

```yml
exporter_port: 9158 # Port on which prometheu can call this exporter to get metrics
namespace: nexus
log_level: debug|info|warn|error
json_data_url: <url_with_scheme> # Url to get json data used for fetching metric values, and with the /service/metrics/data
basic_auth_user: <username> # User to connect to Nexus. Optional, leave empty for empty Basic auth
basic_auth_password: <password>
metric_name_prefix: nexus # All metric names will be prefixed with this value
metrics: # Default JSON metrics from /service/metrics/data
- type: gauge
  path: $.gauges # Object Path format to scrape gauges in the Nexus Json
- type: meters
  path: $.meters # Object Path format to scrape meters in the Nexus Json

```

### Datas from Nexus

This is a Json example retrieved from the Nexus 3 data endpoint. The `config.yml` file present in the Config part above allows you to parse the following Json in the Prometheus format.

```json
{
  "version": "3.0.0",
  "gauges": {
    "jvm.buffers.direct.capacity": {
	  "value": 135636938
	},
	"jvm.buffers.direct.count": {
      "value": 68
    },
    "..."
    "meters": {
	  "com.sonatype.nexus.analytics.internal.ui.EventsComponent.clear.exceptions": {
	    "count": 0,
		"m15_rate": 0.0,
		"m1_rate": 0.0,
		"m5_rate": 0.0,
		"mean_rate": 0.0,
		"units": "events/second"
	  },
	  "metrics.error": {
	    "count": 111,
	    "m15_rate": 8.904204078708139E-22,
	    "m1_rate": 4.5840990483670495E-274,
	    "m5_rate": 1.6245846951657174E-57,
	    "mean_rate": 9.885520410623464E-5,
        "units": "events/second"
      },
      "..."
	}
  }
}
```

### Usage

Metrics will available in http://localhost:9158
```
$ curl -s localhost:9158 | grep ^nexus
nexus_log_count{level="info"} 6387.0
nexus_log_count{level="all"} 8297.0
nexus_log_count{level="error"} 111.0
nexus_response_count{status="3xx"} 1.0
nexus_response_count{status="5xx"} 0.0
nexus_response_count{status="2xx"} 78215.0
[...]
```

