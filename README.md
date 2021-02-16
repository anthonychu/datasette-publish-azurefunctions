# Datasette plugin for publishing to Azure Functions

## Usage

1. Create a function app in Azure
    - Python 3.8
    - Linux Consumption (Serverless) plan

1. Install this plugin
    ```bash
    python -m pip install git+https://github.com/anthonychu/datasette-publish-azurefunctions
    ```

1. Publish
    ```bash
    datasette publish azurefunctions sf-trees.db --functionapp-name target-function-app-name
    ```