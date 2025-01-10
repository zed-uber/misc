from azure.identity import DefaultAzureCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.subscription import SubscriptionClient
import json
import os

class AzureD2DiagramGenerator:
    def __init__(self):
        # Initialize Azure credentials
        self.credential = DefaultAzureCredential()
        self.subscription_client = SubscriptionClient(self.credential)
        
        # Get subscription ID (using first available subscription)
        self.subscription_id = next(self.subscription_client.subscriptions.list()).subscription_id
        self.resource_client = ResourceManagementClient(self.credential, self.subscription_id)

    def get_azure_resources(self):
        """Collect all Azure resources and organize by resource group"""
        resources_by_rg = {}
        
        # Get all resource groups
        resource_groups = self.resource_client.resource_groups.list()
        
        for rg in resource_groups:
            rg_name = rg.name
            resources_by_rg[rg_name] = []
            
            # Get resources in this resource group
            resources = self.resource_client.resources.list_by_resource_group(rg_name)
            for resource in resources:
                resources_by_rg[rg_name].append({
                    'name': resource.name,
                    'type': resource.type,
                    'location': resource.location,
                    'id': resource.id
                })
        
        return resources_by_rg

    def generate_d2_files(self, resources_by_rg):
        """Generate D2 files for each resource group and main file"""
        
        # Create output directory if it doesn't exist
        os.makedirs('d2_output', exist_ok=True)
        
        # Generate individual RG files
        for rg_name, resources in resources_by_rg.items():
            self._generate_rg_file(rg_name, resources)
        
        # Generate main file
        self._generate_main_file(resources_by_rg.keys())

    def _generate_rg_file(self, rg_name, resources):
        """Generate D2 file for a single resource group"""
        filename = f"d2_output/{rg_name}.d2"
        
        with open(filename, 'w') as f:
            f.write(f"{rg_name}: {{\n")
            
            # Add resources
            for resource in resources:
                resource_type = resource['type'].split('/')[-1]
                f.write(f"  {resource['name']}: {{\n")
                f.write(f"    shape: {self._get_shape_for_type(resource_type)}\n")
                f.write(f"    label: {resource['name']}\n")
                f.write(f"    type: {resource_type}\n")
                f.write("  }\n")
            
            f.write("}\n")

    def _generate_main_file(self, rg_names):
        """Generate main D2 file that imports all RG files"""
        with open('d2_output/main.d2', 'w') as f:
            # Import all RG files
            for rg_name in rg_names:
                f.write(f'import "./{rg_name}.d2"\n')
            
            f.write("\n# Resource Group Connections\n")
            # Add any connections between resource groups here
            # This would need to be customized based on your needs

    def _get_shape_for_type(self, resource_type):
        """Map Azure resource types to D2 shapes"""
        shape_mapping = {
            'virtualMachines': 'rectangle',
            'storageAccounts': 'cylinder',
            'virtualNetworks': 'cloud',
            # Add more mappings as needed
            'default': 'rectangle'
        }
        return shape_mapping.get(resource_type, shape_mapping['default'])

def main():
    generator = AzureD2DiagramGenerator()
    
    # Get resources from Azure
    print("Collecting Azure resources...")
    resources = generator.get_azure_resources()
    
    # Generate D2 files
    print("Generating D2 files...")
    generator.generate_d2_files(resources)
    
    print("D2 files generated in 'd2_output' directory")

if __name__ == "__main__":
    main()