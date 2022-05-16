# Power BI Utils
This action provides support for CI/CD of Power BI Reports and Datasets. It deploys a PBIX File or a RDL File to the Power BI Service.

How to Deploy:
1) Create a config file under **.github/config/** in your repository with the name **deploy_config.yaml**.

```yaml
spn_credentials:
    tenant_id: ########-####-####-####-############           #The tenant id

deploy_options:
    max_file_size_supported_in_mb: 110                        #Maximum File Size Supported. Action only supports files upto 1000 MB.
    
pbix_deploy_options:
    pbix_name_conflict: CreateOrOverwrite                     #Determines what to do if a dataset with the same name already exists. Abort, CreateOrOverwrite, GenerateUniqueName, Ignore, Overwrite (https://docs.microsoft.com/en-us/rest/api/power-bi/imports/post-import-in-group#post-import-example)
    override_model_name: True                                 #Determines whether to override existing label on model during republish of PBIX file, service default value is true.
    override_report_label: True                               #Determines whether to override existing label on report during republish of PBIX file, service default value is true.

rdl_deploy_options:
    max_file_size_supported_in_mb: 110                        #Maximum File Size Supported. Action only supports files upto 1000 MB.
    rdl_name_conflict: Overwrite                              #Determines what to do if a dataset with the same name already exists. Only Abort and Overwrite are supported with Rdl files. (https://docs.microsoft.com/en-us/rest/api/power-bi/imports/post-import-in-group#post-import-example)

deploy_location:
    workspace_id:########-####-####-####-############         #The workspace ID
```


2) Create a workflow under **.github/workflows/** in your repository.
```yaml
name: Workflow Name
on: pull_request
jobs:
  Deploy-Asset:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
        with:
          fetch-depth: 0
      - name: Get changed files
        id: changed-files
        uses: tj-actions/changed-files@v19
        with:
          separator: ","
          quotepath: "false"
      - name: Upload files
        uses: mohitnayar123/power-bi-utils@v1.0.3 # Replace this with the latest version
        with:
          files: ${{ steps.changed-files.outputs.all_modified_files }}
        env:
          CLIENT_ID: ${{ secrets.client_id }}
          CLIENT_SECRET: ${{ secrets.client_secret }}
```
