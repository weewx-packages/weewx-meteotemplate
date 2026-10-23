# Meteotemplate uploader for WeeWX

Send weather observations to the `api.php` upload endpoint of a Meteotemplate
website. The API mapping covers temperature, humidity, pressure, wind, rain,
solar radiation, UV and additional sensors when those observations are present.

This is the weewx-packages continuation, release **0.11.0**.
[Origin](ORIGIN.md) records the upstream revision; [repair notes](REPAIR_NOTES.md)
describe the maintenance changes.

The catalog archive targets WeeWX `>=5.5.2,<5.7` and Python `>=3.10,<3.15`.

## Install

Use `weectl` from the Python environment running WeeWX. With stock WeeWX 5,
install the published archive:

```sh
weectl extension install https://github.com/weewx-packages/weewx-meteotemplate/releases/download/v0.11.0/weewx-meteotemplate-0.11.0.tar.gz --config /path/to/weewx.conf
```

Replace `/path/to/weewx.conf` with your station configuration. You can also
download that URL and pass the local archive to the same command. Use elevated
permissions only when your station files require them.

## Connect your website

You need a Meteotemplate installation exposing the upload API introduced in
version 12, and its update password. No additional Python package is required.
Configure the full script URL and the update password, which differs from the
website's administrator login:

```ini
[StdRESTful]
    [[Meteotemplate]]
        server_url = https://weather.example.com/template/api.php
        password = YOUR_UPDATE_PASSWORD
```

The installer registers `user.meteotemplate.Meteotemplate`. Restart WeeWX
yourself and check its log after the next archive record. The API must return
`Success`, allowing surrounding whitespace; other replies count as failures.

## Send more frequent or additional observations

The default binding is `archive`. Set `binding = loop` to send LOOP packets.
The receiving API controls its own aggregation and storage schedule.

Map API field names to WeeWX observations to add sensors:

```ini
[StdRESTful]
    [[Meteotemplate]]
        [[[field_map]]]
            PP1 = pm2_5
            PP2 = pm10
            L = lightning_strike_count
```

Merge this into your configured section. Only present, non-null values are
sent. A WH41 PM2.5 observation cannot supply PM10. Confirm additional field
names against your installed `api.php` version. The [module](bin/user/meteotemplate.py)
contains the complete default map.

Temperature is sent in Celsius, pressure in mbar, wind in km/h and rain in mm.
`R` is daily cumulative rain; when `dayRain` is absent, the uploader obtains it
through `wx_binding`. It needs archive rain records for that sum. Battery status
fields are supported by the default map; battery voltages have no API mapping.
A local protocol check does not establish your server's path or credentials.

Copyright 2016-2020 Matthew Wall. [GNU GPLv3](license).
