# Repair validation

Version 0.11.0. Original repository and revision are in ORIGIN.md.

* https://github.com/matthewwall/weewx-meteotemplate/issues/12: Configurable API field_map sends PM2.5/PM10/lightning values when available; fixture confirms absent PM10 omitted. WH41 cannot supply unmeasured PM10; installed api.php must accept configured field names.
* https://github.com/matthewwall/weewx-meteotemplate/issues/11: Success with trailing newline accepted; Unauthorized remains FailedPost. Local receiver passes. Reporter password/path/dashboard state requires its exact response and server log.
* https://github.com/matthewwall/weewx-meteotemplate/issues/6: Real SQLite archive augmentation sums daily rain and converts METRICWX millimetres correctly; existing behavior validated.

Tests run under WeeWX 4.10.2/5.1.0 on Python 3.10 and WeeWX 5.5.2 on Python 3.14. Local receivers and isolated install directories avoid live station changes. The tests do not establish individual external account permissions.
