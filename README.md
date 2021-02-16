# Datasette plugin for publishing to Azure Functions

## Usage

1. Create a function app in Azure
    - Python 3.8
    - Linux Consumption (Serverless) plan

1. Install tools needed for deployment
    - [Azure CLI](https://docs.microsoft.com/cli/azure/install-azure-cli)
    - [Azure Functions Core Tools](https://github.com/Azure/azure-functions-core-tools/blob/dev/README.md)

1. Login to Azure CLI and select the subscription to use
    ```bash
    az login
    az account set -s <subscription_to_use>
    ```

1. Install this plugin
    ```bash
    python -m pip install git+https://github.com/anthonychu/datasette-publish-azurefunctions
    ```

1. Publish
    ```bash
    datasette publish azurefunctions sf-trees.db --functionapp-name target-function-app-name
    ```