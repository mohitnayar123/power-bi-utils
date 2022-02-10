import requests
import os
import yaml
import argparse

deploy_config_location = ".github/config/deploy_config.yaml"
with open(deploy_config_location, 'r') as file:
    config = yaml.safe_load(file)


def get_access_token():
    """
    This function takes in client id, client secrets and tenant id stored in the config file and returns an authentication token that can be used to call the Power BI Rest API.

    Returns
    -------
    access_token : str
        Authentication token to use when calling the Power BI Rest API.

    """
    tenant_id = config["spn_credentials"]["tenant_id"]

    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/token"

    payload = {
        'grant_type': 'client_credentials',
        'scope': 'oauth',
        'resource': 'https://analysis.windows.net/powerbi/api',
        'client_id': os.environ['CLIENT_ID'],
        'client_secret': os.environ['CLIENT_SECRET'],
        'response_mode': 'query'}

    response = requests.request("POST", url, data=payload)
    access_token = f"Bearer  {response.json().get('access_token')}"
    return access_token


def get_pbix_deploy_options():
    """
    This function takes in deploy options: pbix_name_conflict, override_model_name, override_report_label stored in the config file and returns a string that can appended to the rest api end point.
    Returns
    -------
    deploy_options : str
        Deploy options to use when calling the Power BI Rest API.

    """
    pbix_name_conflict = config["pbix_deploy_options"]["pbix_name_conflict"]
    override_model_name = config["pbix_deploy_options"]["override_model_name"]
    override_report_label = config["pbix_deploy_options"]["override_report_label"]

    if pbix_name_conflict in ["Overwrite", "Ignore", "Abort", "CreateOrOverwrite", "GenerateUniqueName"]:
        name_conflict_str = f"nameConflict={pbix_name_conflict}"
    else:
        name_conflict_str = "nameConflict=Ignore"

    if override_model_name in [True, False]:
        override_model_name_str = f"overrideModelLabel={override_model_name}"
    else:
        override_model_name_str = "overrideModelLabel=True"

    if override_report_label in [True, False]:
        override_report_label_str = f"overrideReportLabel={override_report_label}"
    else:
        override_report_label_str = "overrideReportLabel=True"

    deploy_options = "&" + name_conflict_str + "&" + \
        override_model_name_str + "&" + override_report_label_str
    return deploy_options


def get_rdl_deploy_options():
    """
    This function takes in deploy options: rdl_name_conflict stored in the config file and returns a string that can appended to the rest api end point.
    Returns
    -------
    deploy_options : str
        Deploy options to use when calling the Power BI Rest API.

    """
    rdl_name_conflict = config["rdl_deploy_options"]["rdl_name_conflict"]

    if rdl_name_conflict in ["Overwrite", "Abort"]:
        name_conflict_str = f"nameConflict={rdl_name_conflict}"
    else:
        name_conflict_str = "nameConflict=Abort"

    deploy_options = "&" + name_conflict_str
    return deploy_options


def main():
    access_token = get_access_token()

    if config["deploy_options"]["max_file_size_supported_in_mb"] < 1024:
        max_file_size_supported_in_mb = config["deploy_options"]["max_file_size_supported_in_mb"]
    else:
        max_file_size_supported_in_mb = 1024

    parser = argparse.ArgumentParser(description='Personal information')
    parser.add_argument('--files', dest='files', type=str,
                        help='List of all file names that need to be uploaded to the Power BI Service')
    args = parser.parse_args()

    # Deploy files passed in the files argument
    file_name_array = args.files.split(",")

    for file_name in file_name_array:
        file_extension = os.path.splitext(file_name)[1].lower()
        file_name_without_extension = os.path.splitext(file_name)[0]
        file_location = os.getcwd() + "/" + file_name

        if os.path.getsize(file_location) / (1024 * 1024) < max_file_size_supported_in_mb and file_extension in [".pbix", ".rdl"]:
            open_file = open(file_location, "rb")
            workspace_id = config["deploy_location"]["workspace_id"]

            headers = {'Authorization': access_token}
            file = {'file': open_file}

            if file_extension == ".pbix":
                url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/imports?datasetDisplayName={file_name_without_extension}" + \
                    get_pbix_deploy_options()
            elif file_extension == ".rdl":
                url = f"https://api.powerbi.com/v1.0/myorg/groups/{workspace_id}/imports?datasetDisplayName={file_name_without_extension}" + \
                    get_rdl_deploy_options()

            response = requests.request("POST", url, headers=headers, files=file)
            if response.status_code in [200, 202]:
                import_id = response.json().get("id")
                print("Load Succeeded, Import Id:" + import_id)
            else:
                print(f"ERROR: {response.status_code}: {response.content}\nURL: {response.url}")

        elif not file_extension in [".pbix", ".rdl"]:
                print("File type not supported")
        else:
                print("File Size over 1024 MB")


if __name__ == '__main__':

    main()
