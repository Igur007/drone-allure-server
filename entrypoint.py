import os
import sys
import zipfile
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List

import requests
from requests.auth import HTTPBasicAuth

output_zip = "allure-results.zip"


@dataclass
class ExecutorInfo:
    name: str
    type: str
    url: str
    buildOrder: str
    buildName: str
    buildUrl: str
    reportName: str
    reportUrl: str


@dataclass
class ReportSpec:
    path: List[str]
    executorInfo: ExecutorInfo


@dataclass
class CreateReportPayload:
    reportSpec: ReportSpec
    results: List[str]
    deleteResults: bool


def zip_folder(folder_path):
    '''
    Function to zip the allure-results folder

    :param folder_path: Path to folder that has to be zipped
    '''
    folder_path = Path(folder_path)
    if not folder_path.is_dir():
        print(f"Error: Allure results folder not found at {folder_path}")
        sys.exit(1)

    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in folder_path.rglob('*'):  # Recursively find all files in the folder
            if file.is_file():
                zipf.write(file, file.relative_to(folder_path))  # Store path relative to the base folder
    print(f"Zipped {folder_path} to {output_zip}")


def upload_results(allure_server_url, auth: HTTPBasicAuth):
    '''
    Function to upload the zip file and get the UUID

    :param allure_server_url: allure server url
    :return: uuid v4 of allure result file on server
    '''
    url = f"{allure_server_url}/api/result"
    with open(output_zip, 'rb') as f:
        try:
            response = requests.post(
                url=url,
                files={'allureResults': (output_zip, f, 'application/zip')},
                auth=auth
            )
            print(response.status_code, url, response.text)
            if response.status_code != 201:
                sys.exit(1)
            return response.json().get('uuid')
        except requests.exceptions.ConnectionError as e:
            print(e)
            sys.exit(1)


# Function to generate the report
def generate_report(allure_server_url, payload: CreateReportPayload, auth: HTTPBasicAuth):
    url = f"{allure_server_url}/api/report"
    try:
        response = requests.post(
            url=url,
            headers={'Content-Type': 'application/json', 'accept': '*/*'},
            json=asdict(payload),
            auth=auth
        )
        print(response.status_code, url, response.text)
        if response.status_code != 201:
            sys.exit(1)
        print("Report generated successfully")
    except requests.exceptions.ConnectionError as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    ENV_ALLURE_SERVER_URL = "ALLURE_SERVER_URL"
    required_env_vars = (ENV_ALLURE_SERVER_URL,)
    missing_vars = [var_name for var_name in required_env_vars if os.getenv(var_name) is None]
    if missing_vars:
        print(f"Error: Missing required parameters {', '.join(missing_vars)}")
        sys.exit(1)

    allure_server_url = os.getenv(ENV_ALLURE_SERVER_URL)
    username = os.getenv("ALLURE_SERVER_USERNAME", "")
    password = os.getenv("ALLURE_SERVER_PASSWORD", "")
    path_to_results = os.getenv("ALLURE_RESULTS", "allure-results")
    report_path = os.getenv("REPORT_PATH", "main")
    report_name = os.getenv("REPORT_NAME", "Allure")
    report_url = os.getenv("REPORT_URL", "")
    executor_info_name = os.getenv("EXECUTOR_INFO_NAME", "Drone")
    executor_info_type = os.getenv("EXECUTOR_INFO_TYPE", "exectype")
    executor_info_url = os.getenv("EXECUTOR_INFO_URL", "")
    delete_results = os.getenv("DELETE_RESULTS", "true").lower() == "true"
    build_name = os.getenv("DRONE_BUILD_NUMBER", "")
    build_url = os.getenv("DRONE_BUILD_LINK", "")

    basic_auth = HTTPBasicAuth('username', 'password')

    # Perform zipping, uploading, and report generation
    zip_folder(path_to_results)
    uuid = upload_results(allure_server_url, auth=basic_auth)
    generate_report(
        allure_server_url=allure_server_url,
        payload=CreateReportPayload(
            reportSpec=ReportSpec(
                path=[report_path],
                executorInfo=ExecutorInfo(
                    name=executor_info_name,
                    type=executor_info_type,
                    url=executor_info_url,
                    buildOrder=build_name,
                    buildName=build_name,
                    buildUrl=build_url,
                    reportName=report_name,
                    reportUrl=report_url
                )
            ),
            results=[uuid],
            deleteResults=delete_results
        ),
        auth=basic_auth
    )
