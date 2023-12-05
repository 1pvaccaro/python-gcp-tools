import subprocess
import json

def is_compute_api_enabled(project_id):
    # Run the gcloud command to check if the Compute Engine API is enabled
    check_api_cmd = f"gcloud services list --project={project_id} --format=json"
    check_api_output = subprocess.check_output(check_api_cmd, shell=True)
    services = json.loads(check_api_output.decode("utf-8"))

    for service in services:
        if service.get("config", {}).get("name") == "compute.googleapis.com" and service.get("state") == "ENABLED":
            return True
    return False

def get_public_ips():
    # Run the gcloud command to list all projects in the organization
    org_projects_cmd = "gcloud projects list --format=json"
    org_projects_output = subprocess.check_output(org_projects_cmd, shell=True)
    org_projects = json.loads(org_projects_output.decode("utf-8"))

    # Iterate through each project and retrieve the public IPs
    for project in org_projects:
        project_id = project["projectId"]
        
        # Check if the Compute Engine API is enabled for the project
        if not is_compute_api_enabled(project_id):
            print(f"Compute Engine API not enabled for project {project_id}. Skipping.")
            continue

        print(f"Project: {project_id}")

        # Run the gcloud command to list all instances and their public IPs
        list_instances_cmd = f"gcloud compute instances list --project={project_id} --format=json"
        list_instances_output = subprocess.check_output(list_instances_cmd, shell=True)
        instances = json.loads(list_instances_output.decode("utf-8"))

        # Extract and print public IPs for each instance
        for instance in instances:
            network_interfaces = instance.get("networkInterfaces", [])
            for network_interface in network_interfaces:
                access_configs = network_interface.get("accessConfigs", [])
                for access_config in access_configs:
                    public_ip = access_config.get("natIP")
                    if public_ip:
                        print(f"  Instance: {instance['name']}, Public IP: {public_ip}")

if __name__ == "__main__":
    get_public_ips()
