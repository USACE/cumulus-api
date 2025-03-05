# Dev Notes

```mermaid
flowchart LR
    subgraph main
    A[sqs message] --> B[handle message]
    B --> C[packager]
    C --> D{writer}
    end
    subgraph dss
    D --> E[DSS7]
    end
    subgraph cog
    D --> F[tar COG]
    end
```


## packager message body with download ID

```
{"id" : "a01fdb6e-c496-4ebf-a354-b11b0847523b"}
```

## packager_request endpoint with download ID

`"{CUMULUS_API_URL}/downloads/{download_id}/packager_request"`

```
{
    "download_id": "a01fdb6e-c496-4ebf-a354-b11b0847523b",
    "output_key": "cumulus/download/dss7/download_a01fdb6e-c496-4ebf-a354-b11b0847523b.dss",
    "contents": [
        {
            "bucket": "castle-data-develop",
            "key": "cumulus/products/cbrfc-mpe/xmrg0526202206z.tif",
            "dss_datatype": "PER-CUM",
            "dss_fpart": "CBRFC-MPE",
            "dss_cpart": "PRECIP",
            "dss_dpart": "26MAY2022:0500",
            "dss_epart": "26MAY2022:0600",
            "dss_unit": "MM"
        },
        {
            "bucket": "castle-data-develop",
            "key": "cumulus/products/cbrfc-mpe/xmrg0526202207z.tif",
            "dss_datatype": "PER-CUM",
            "dss_fpart": "CBRFC-MPE",
            "dss_cpart": "PRECIP",
            "dss_dpart": "26MAY2022:0600",
            "dss_epart": "26MAY2022:0700",
            "dss_unit": "MM"
        },
        {
            "bucket": "castle-data-develop",
            "key": "cumulus/products/cbrfc-mpe/xmrg0526202208z.tif",
            "dss_datatype": "PER-CUM",
            "dss_fpart": "CBRFC-MPE",
            "dss_cpart": "PRECIP",
            "dss_dpart": "26MAY2022:0700",
            "dss_epart": "26MAY2022:0800",
            "dss_unit": "MM"
        },
    "format": "dss7",
    "extent": {
        "name": "Ohio River",
        "bbox": [
            488000,
            1344000,
            1380000,
            2102000
        ]
    }
}
```
___

## Create documentation from the Python docstring

_Requires mkdocs_

The `mkdocs.yml` file and the repo's `docs/async_packager/docs` are the configurations for building documentation from Python docstrings.  Documenation pages can be built with the command `mkdocs build` at the same directory level as `mkdocs.yml`.

### Mkdocs

Generating documentation locally requires mkdocs to be installed.  Use `pip install mkdocs` to install and make available `mkdocs` at the command line.

`Example:`

```bash
[./cumulus-api/async_packager] > mkdocs build
```
