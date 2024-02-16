# reproject

Fill in this README with details for this task

## Description

It is often best to tell people what this task
does. And perhaps why they might choose to use it.

## Configuration Parameters

It's not uncommon to list out the parameters so people can better
understand how to use this task once they have chosen to do so.
Don't just say what they are, but where they go.

Configuration parameters are passed in `payload['process']['tasks']['copy-metadata']`:

- Name: `mappings`
  Type: `dict`
  Required: True
  Default: None
  An array of mapping dicts that define source item,
  destination item, and metadata fields to copy


Providing an example is often best.

Example:
```
"copy-metadata": {
  "mappings":[
    {
      "source": "GEO",
      "destination": "SLC",
      "metadata": {
        "assets": ["preview", "thumbnail"]
      }
    }
  ]
}
```

## Detail any other options

It's possible your task uses more fields to define options.

Maybe your task also REQUIRES the following parameters
supplied in `payload['process']['item-queries']`:

```
"item-queries": {
  "GEO": {
    "sar:product_type": "GEO"
    },
  "SLC": {
    "sar:product_type": "SLC"
    },
  "SICD": {
    "sar:product_type": "SICD"
  }
}
```
