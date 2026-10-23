# Meteotemplate uploader for WeeWX

Send weather observations to the `api.php` upload endpoint of a Meteotemplate
website. The API mapping covers temperature, humidity, pressure, wind, rain,
solar radiation, UV and additional sensors when those observations are present.

This is the weewx-packages continuation of
[matthewwall/weewx-meteotemplate](https://github.com/matthewwall/weewx-meteotemplate).
[Origin](ORIGIN.md) records the upstream revision; [repair notes](REPAIR_NOTES.md)
describe the maintenance changes.

## Requirements

* A Meteotemplate website, version 12 or later, with its upload API `api.php`.
* The update password from the Meteotemplate settings. It differs from the
  website's administrator login.

No additional Python package is required.

## Installation

Install `meteotemplate` from the [WeeWX packages catalog](https://github.com/weewx-packages/catalog/blob/main/packages/meteotemplate.md).
The catalog page lists the current release, its WeeWX and Python
requirements, and the install, update and removal commands.

The installer registers `user.meteotemplate.Meteotemplate` as a RESTful service
and adds a `[[Meteotemplate]]` section with placeholder values. Replace them as
shown below, restart WeeWX, then check its log after the next archive record.

## Configuration

```ini
[StdRESTful]
    [[Meteotemplate]]
        server_url = https://weather.example.com/template/api.php
        password = YOUR_UPDATE_PASSWORD
```

`server_url` is the full URL of the `api.php` script. The API must reply
`Success`; surrounding whitespace is allowed. Any other reply counts as a
failed upload.

| Option | Default | Meaning |
|---|---|---|
| `password` | required | Meteotemplate update password. |
| `server_url` | `http://localhost/template/api.php` | Full URL of `api.php`. |
| `enable` | `true` | Set to `false` to turn the uploader off. |
| `binding` | `archive` | `archive`, `loop`, or both, comma separated. |
| `skip_upload` | `false` | Build each upload but do not send it. |
| `post_interval` | none | Minimum seconds between uploads. |
| `max_backlog` | unlimited | Queued records kept when uploads fall behind. |
| `stale` | none | Skip records older than this many seconds. |
| `log_success` | top-level `log_success`, else `true` | Log each successful upload. |
| `log_failure` | top-level `log_failure`, else `true` | Log each failed upload. |
| `timeout` | `60` | Seconds to wait for the server. |
| `max_tries` | `3` | Attempts per record. |
| `retry_wait` | `5` | Seconds between attempts. |

### Sending LOOP packets

Set `binding = loop` to send every LOOP packet instead of every archive record.
The Meteotemplate server aggregates and stores the data on its own schedule.

### Sending additional observations

The subsection `[[[field_map]]]` maps Meteotemplate API field names to WeeWX
observation names. Its entries add to the default map or replace entries in it:

```ini
[StdRESTful]
    [[Meteotemplate]]
        [[[field_map]]]
            PP1 = pm2_5
            PP2 = pm10
            L = lightning_strike_count
```

Values from `field_map` are sent with three decimals, `L` without decimals.
Only observations with a value are sent. The default map is
`create_default_field_map()` in
[bin/user/meteotemplate.py](bin/user/meteotemplate.py).

### Units

Before upload, records are converted to the WeeWX `METRIC` unit system.
Temperature is sent in Celsius, pressure in mbar, wind in km/h, and rain
and rain rate in mm and mm/h. `R` is the rain since midnight. When a record has
no `dayRain`, WeeWX sums it from the archive of `wx_binding`.

## Limitations

* Snow depth (`SD`) is sent in centimetres, the `METRIC` unit for
  `snowDepth`. Daily snow (`SN`) is sent unconverted, in the unit system of
  the record.
* Battery status fields of the default map are sent. Battery voltages have no
  field in the Meteotemplate API.
* Check additional field names against the `api.php` of your Meteotemplate
  installation. A WH41 sensor measures PM2.5 only, so a `pm10` mapping
  sends nothing for it.
* An option not named on this page stops WeeWX at startup.
* The tests use a local receiver. They do not check the path, the password or
  the replies of your Meteotemplate server.

## Development

```sh
python -m pytest -q tests
```

Run it in a Python environment with WeeWX and pytest installed.

## License

Copyright 2016-2020 Matthew Wall. [GNU GPLv3](license).
