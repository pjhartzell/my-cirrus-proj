# earthsearch-sentinel-2

Feeder for Sentinel-2 asset reprojection.

## Description

Pulls down the latest EarthSearch Sentinel-2 STAC Item and inserts it into a Cirrus
Process Payload along with the configuration values supplied in the feeder input.

## Configuration Parameters

Example input:

```json
{
    "assets": ["red", "green", "blue"],  # assets to reproject
    "crs": "EPSG:4326",                  # target reprojection CRS
    "dry_run": true,                    # whether to send the payload to the process queue
}
```
