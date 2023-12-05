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

def disable_ssh(project_id):
    # Run the gcloud command to get the default network
    default_network_cmd = f"gcloud compute networks list --project={project_id} --format=json"
    default_network_output = subprocess.check_output(default_network_cmd, shell=True)
    default_networks = json.loads(default_network_output.decode("utf-8"))

    if not default_networks:
        print(f"No default network found for project {project_id}. Skipping.")
        return

    default_network = default_networks[0]["name"]

    # Disable SSH by updating the default-allow-ssh firewall rule
    disable_ssh_cmd = f"gcloud compute firewall-rules update default-allow-ssh --project={project_id} --deny=INGRESS"
    subprocess.run(disable_ssh_cmd, shell=True)
    print(f"SSH access disabled for project {project_id}.")

def get_projects_with_public_ips():
    # Run the gcloud command to list all projects in the organization
    org_projects_cmd = "gcloud projects list --format=json"
    org_projects_output = subprocess.check_output(org_projects_cmd, shell=True)
    org_projects = json.loads(org_projects_output.decode("utf-8"))

    # Iterate through each project and check if it has public IPs
    projects_with_public_ips = []
    for project in org_projects:
        project_id = project["projectId"]

        # Check if the Compute Engine API is enabled for the project
        if not is_compute_api_enabled(project_id):
            print(f"Compute Engine API not enabled for project {project_id}. Skipping.")
            continue

        # Check if the project has instances with public IPs
        list_instances_cmd = f"gcloud compute instances list --project={project_id} --format=json"
        list_instances_output = subprocess.check_output(list_instances_cmd, shell=True)
        instances = json.loads(list_instances_output.decode("utf-8"))

        for instance in instances:
            network_interfaces = instance.get("networkInterfaces", [])
            for network_interface in network_interfaces:
                access_configs = network_interface.get("accessConfigs", [])
                for access_config in access_configs:
                    public_ip = access_config.get("natIP")
                    if public_ip:
                        projects_with_public_ips.append(project_id)
                        break

    return projects_with_public_ips

if __name__ == "__main__":
    projects_with_public_ips = get_projects_with_public_ips()

    for project_id in projects_with_public_ips:
        disable_ssh(project_id)
