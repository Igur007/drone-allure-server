# **drone-allure-server-plugin**
- Drone plugin to generate allure reports in allure server 

## Inputs

**ENV**                      | **TYPE**                 | **DEFAULT** | **DESCRIPTION**
-----------------------------|--------------------------|-------------|----------------------------------------------------------------------------------------------------------------------------------------------------------
ALLURE_SERVER_URL            | string                   | -           | **Required** Full url of your deployed allure-server
ALLURE_SERVER_USERNAME       | string                   | ""          | If your allure-server has basic auth enabled, specify username here.
ALLURE_SERVER_PASSWORD       | string                   | ""          | If your allure-server has basic auth enabled, specify password here.
REPORT_PATH                  | string                   | "main"      | Use this option to group test reports. All reports with same `path` will have common allure history. Also it used as url path to access latest report. You can specify branch name here, or project name.
REPORT_NAME                  | string                   | "Allure"    | Report name
REPORT_URL                   | string                   | ""          | Report URL
EXECUTOR_INFO_NAME           | string                   | "Drone"     | Executor name
EXECUTOR_INFO_TYPE           | string                   | "exectype"  | Executor type
EXECUTOR_INFO_URL            | string                   | ""          | Executor url
DELETE_RESULTS               | boolean                  | true        | Delete results after report generation.


## Example usage:
```yml
steps:
  - name: allure-report
    image: igur007/drone-allure-server-plugin:latest
    environment:
      ALLURE_SERVER_URL: http://10.110.213.220:8080
    secrets: [DRONE_BUILD_NUMBER, DRONE_BUILD_LINK]