import os
import json
import click
import requests

def expand_r_package_definition(package_definition):
    if package_definition.startswith("github://"):
        full_package_name = package_definition[len("github://"):]
        package_name = full_package_name.split("/")[-1]
        output = "R -e \"if (!require('%s')) devtools::install_github('%s')\"" % (package_name, full_package_name)
    elif "@" in package_definition:
        package_name, version = package_definition.split("@")
        output = "R -e \"if (!require('%s')) devtools::install_version('%s', version='%s', repos = 'http://cran.rstudio.com/')\"" % (package_name, package_name, version)
    else:
        package_name = package_definition
        output = "R -e \"if (!require('%s')) install.packages('%s', repos = 'http://cran.rstudio.com/')\"" % (package_name, package_name)

    return output

def build_provision_code(r_packages_section):
    return "\n".join([expand_r_package_definition(pd) for pd in r_packages_section])

def read_config(config_file):
    config = json.loads(config_file.read())

    # Rudimentary support for pulling config from env vars
    for key, value in config.items():
        if type(value) is str and value.startswith("${"):
            var_name = value[2:-1]
            config[key] = os.environ.get(var_name, None)
    return config

@click.command()
@click.argument('code_file', type=click.File('rb'))
@click.argument('inputs_file', type=click.File('rb'))
@click.argument('config_file', type=click.File('rb'))
def cli(code_file, inputs_file, config_file):
    config = read_config(config_file)

    submit_url = os.path.join(config['base_url'], "submit_job_token/")

    provision_code = None
    if 'r_packages' in config:
        provision_code = build_provision_code(config['r_packages'])
        print(provision_code)

    payload = {
        'ghap_credentials': {
            'username': config['ghap_username'],
            'password': config['ghap_password'],
            'ip': config['ghap_ip']
        },
        'inputs': json.loads(inputs_file.read()),
        'backend': 'ghap',
        'code': code_file.read().decode('utf-8'),
        'provision': provision_code
    }

    print("Submitting job to %s" % submit_url)

    response = requests.post(submit_url, json=payload, headers={
        'Content-Type': 'application/json',
        'Authorization': config['token'],
    })

    if response.status_code == 200:
        print("Submission success. View results at:")
        print("")
        print(response.json()['results_url'])
        print("")
    else:
        print("Error submitting to server!")
        print(response)
