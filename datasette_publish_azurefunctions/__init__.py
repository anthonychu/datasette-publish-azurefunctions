from datasette import hookimpl
from datasette.publish.common import (
    add_common_publish_arguments_and_options,
    fail_if_publish_binary_not_installed,
)
from datasette.utils import (
    temporary_docker_directory,
)
from subprocess import run
import click
from click.types import CompositeParamType
import os
import pathlib
import shutil
from termcolor import colored, cprint

HOST_JSON = """
{
  "version": "2.0",
  "logging": {
    "applicationInsights": {
      "samplingSettings": {
        "isEnabled": true,
        "excludedTypes": "Request"
      }
    }
  },
  "extensions": {
    "http": {
      "routePrefix": ""
    }
  },
  "customHandler": {
    "description": {
       "defaultExecutablePath": "python",
       "arguments": [
         "-m", "datasette", "-p", "%FUNCTIONS_CUSTOMHANDLER_PORT%", "%DB_FILES%"
       ]
    },
    "enableForwardingHttpRequest": true
  }
}
""".strip()

FUNCTION_JSON = """
{
  "bindings": [
    {
      "authLevel": "anonymous",
      "type": "httpTrigger",
      "direction": "in",
      "name": "req",
      "route": "{*path}"
    },
    {
      "type": "http",
      "direction": "out",
      "name": "$return"
    }
  ]
}
""".strip()

LOCAL_SETTINGS_JSON = """
{
  "IsEncrypted": false,
  "Values": {
    "PYTHONPATH": "/home/site/wwwroot/.python_packages/lib/site-packages",
    "FUNCTIONS_WORKER_RUNTIME": "python"
  }
}
""".strip()

FUNCIGNORE = """
.git*
.vscode
local.settings.json
test
.venv
""".strip()

REQUIREMENTS_TXT = "datasette"

LOGO = (colored("                  %%%%%%\n", "yellow") +
        colored("                 %%%%%%\n", "yellow") +
        colored("            @", "cyan") + colored("   %%%%%%", "yellow") + colored("    @\n", "cyan") +
        colored("          @@", "cyan") + colored("   %%%%%%", "yellow") + colored("      @@\n", "cyan") +
        colored("       @@@", "cyan") + colored("    %%%%%%%%%%%", "yellow") + colored("    @@@\n", "cyan") +
        colored("     @@", "cyan") + colored("      %%%%%%%%%%", "yellow") + colored("        @@\n", "cyan") +
        colored("       @@", "cyan") + colored("         %%%%", "yellow") + colored("       @@\n", "cyan") +
        colored("         @@", "cyan") + colored("      %%%", "yellow") + colored("       @@\n", "cyan") +
        colored("           @@", "cyan") + colored("    %%", "yellow") + colored("      @@\n", "cyan") +
        colored("                %%\n", "yellow") +
        colored("                %\n", "yellow"))


def add_azure_functions_options(cmd):
    for decorator in reversed(
        (
            click.option(
                "--generate-dir",
                type=click.Path(dir_okay=True, file_okay=False),
                help="Output generated application files here",
            ),
            click.option(
                "--functionapp-name",
                help="Name of function app to deploy to",
                required=True
            ),
        )
    ):
        cmd = decorator(cmd)
    return cmd


def _publish_azure_functions(
    files,
    metadata,
    extra_options,
    branch,
    template_dir,
    plugins_dir,
    static,
    install,
    plugin_secret,
    version_note,
    secret,
    title,
    license,
    license_url,
    source,
    source_url,
    about,
    about_url,
    generate_dir,
    functionapp_name,
):
    fail_if_publish_binary_not_installed(
        "func", "Azure Functions", "https://github.com/Azure/azure-functions-core-tools/blob/dev/README.md"
    )
    fail_if_publish_binary_not_installed(
        "az", "Azure Functions", "https://docs.microsoft.com/cli/azure/install-azure-cli"
    )
    extra_metadata = {
        "title": title,
        "license": license,
        "license_url": license_url,
        "source": source,
        "source_url": source_url,
        "about": about,
        "about_url": about_url,
    }

    if generate_dir:
        generate_dir = str(pathlib.Path(generate_dir).resolve())

    with temporary_docker_directory(
        files,
        "datasette-azure-functions",
        metadata,
        extra_options,
        branch,
        template_dir,
        plugins_dir,
        static,
        install,
        False,
        version_note,
        secret,
        extra_metadata,
        port=8080,
    ):
        # We don't actually want the Dockerfile
        os.remove("Dockerfile")
        open("host.json", "w").write(HOST_JSON.replace("%DB_FILES%", " ".join(files)))
        open("local.settings.json", "w").write(LOCAL_SETTINGS_JSON)
        open(".funcignore", "w").write(FUNCIGNORE)
        open("requirements.txt", "w").write(REQUIREMENTS_TXT)
        os.mkdir("serve")
        open("serve/function.json", "w").write(FUNCTION_JSON)

        extras = []
        if template_dir:
            extras.append('template_dir="{}"'.format(template_dir))
        if plugins_dir:
            extras.append('plugins_dir="{}"'.format(plugins_dir))

        statics = [item[0] for item in static]


        if generate_dir:
            if os.path.exists(generate_dir) and os.path.isdir(generate_dir):
                shutil.rmtree(generate_dir)
            # Copy these to the specified directory
            shutil.copytree(".", generate_dir)
            click.echo(
                "Your generated application files have been written to:", err=True
            )
            click.echo("    {}\n".format(generate_dir), err=True)
            cprint(f"\n{LOGO}\n")
            click.echo("To deploy to Azure, run the following...")
            click.echo("    cd {}".format(generate_dir), err=True)
            click.echo("    func azure functionapp publish <function_app_name> -b remote -i -y\n", err=True)
        else:
            # Deploy to Azure
            cmd = ["func", "azure", "functionapp", "publish", functionapp_name, "-b", "remote", "-i", "-y"]
            print(" ".join(cmd))
            run(cmd)
            cprint(f"\n{LOGO}\n\nhttps://{functionapp_name}.azurewebsites.net/\n")


@hookimpl
def publish_subcommand(publish):
    @publish.command()
    @add_common_publish_arguments_and_options
    @add_azure_functions_options
    def azurefunctions(*args, **kwargs):
        _publish_azure_functions(*args, **kwargs)