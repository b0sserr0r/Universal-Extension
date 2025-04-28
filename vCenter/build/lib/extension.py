from __future__ import (print_function)
from universal_extension import UniversalExtension
from universal_extension import ExtensionResult
from universal_extension import logger
from universal_extension.deco import dynamic_choice_command

from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
from pyVim.task import WaitForTask
import ssl


class Extension(UniversalExtension):
    """Required class that serves as the entry point for the extension
    """
    

    @dynamic_choice_command("data_center")
    def list_datacenter(self, fields):
        host =str(fields.get('host'))
        user = str(fields.get("credential")["user"])
        password = str(fields.get("credential")["password"])
        ins = util.connect_vcenter(host,user,password)
        content = ins.RetrieveContent()
        root_folder = content.rootFolder
        datacenter_list = []
        for child in root_folder.childEntity:
            if isinstance(child, vim.Datacenter):
                datacenter_list.append(child.name)
        
        logger.info(str(datacenter_list))
        Disconnect(ins)
        return ExtensionResult(
            rc=0,
            message="Values for choice field: 'data_center'",
            values=datacenter_list
        )

    @dynamic_choice_command("esx_host")
    def list_esx(self, fields):
        dc_name = str(fields.get('data_center')[0])
        logger.info("Data Center : " + dc_name)
        host =str(fields.get('host'))
        user = str(fields.get("credential")["user"])
        password = str(fields.get("credential")["password"])
        ins = util.connect_vcenter(host,user,password)
        content = ins.RetrieveContent()
        datacenters = [dc for dc in content.rootFolder.childEntity if isinstance(dc, vim.Datacenter)]
        target_dc = next((dc for dc in datacenters if dc.name == dc_name), None)
        
        host_folder = target_dc.hostFolder
        logger.info(str(host_folder))
        container_view = content.viewManager.CreateContainerView(
            host_folder, [vim.HostSystem], True
        )

        hosts = list(container_view.view)
        esx_list = []
        for host in hosts:
            esx_list.append(host.name)
        container_view.Destroy()
        logger.info("Esx List : " + str(esx_list))
        Disconnect(ins)
        return ExtensionResult(
            rc=0,
            message="Values for choice field: 'Esx Host'",
            values=esx_list
        )
    
    @dynamic_choice_command("vm_list")
    def list_vm(self, fields):
        host_name = str(fields.get('esx_host')[0])
        logger.info("Host Name : " + host_name)
        host =str(fields.get('host'))
        user = str(fields.get("credential")["user"])
        password = str(fields.get("credential")["password"])
        ins = util.connect_vcenter(host,user,password)
        content = ins.RetrieveContent()
        container_view = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.HostSystem], True
        )      
        

        hosts = list(container_view.view)
        target_host = None
        for host in hosts:
            logger.info("Host : " + host.name)
            if host.name == host_name:
                target_host = host
                break
          

        container_view.Destroy()

        vm_list = []
        for vm in target_host.vm:
            vm_list.append(vm.name)

        logger.info("VM List : " + str(vm_list))

        Disconnect(ins)

        return ExtensionResult(
            rc=0,
            message="Values for choice field: 'data_center'",
            values=vm_list
        )

    def __init__(self):
        """Initializes an instance of the 'Extension' class
        """
        # Call the base class initializer
        super(Extension, self).__init__()

    def extension_start(self, fields):
        function = str(fields.get('function')[0])
        function_str = str("".join(function))
        vm_name = str(fields.get('vm_list')[0])
        host =str(fields.get('host'))
        user = str(fields.get("credential")["user"])
        password = str(fields.get("credential")["password"])
        ins = util.connect_vcenter(host,user,password)
        content = ins.RetrieveContent()
        #print("Function : " + str("".join(function)))
        #print("VN Name : " + vm_name)
        if function_str == "Start VM":
            #print("Start VM ....")
            util.start_vm(content,vm_name)
        elif function_str == "Stop VM":
            util.stop_vm(content,vm_name)
        Disconnect(ins)

        return ExtensionResult(
            unv_output=''
        )
class util:
    def connect_vcenter(hostname,username,password):
        try:
            #logger.info("Connect to vCenter......")
            context = ssl._create_unverified_context()
            si = SmartConnect(
                host=hostname,
                user=username,
                pwd=password,
                sslContext=context
            )
            #logger.info("Connected to vCenter!")
            return si
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")

    def get_vm_by_name(content, vm_name):
        container = content.viewManager.CreateContainerView(
            content.rootFolder, [vim.VirtualMachine], True
        )
        for vm in container.view:
            if vm.name == vm_name:
                container.Destroy()
                return vm
        container.Destroy()
        return None

    def start_vm(content, vm_name):
        vm = util.get_vm_by_name(content, vm_name)
        if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
            print(f"✅ VM '{vm_name}' is already powered on.")
        else:
            print(f"🔄 Powering on VM '{vm_name}'...")
            task = vm.PowerOn()
            WaitForTask(task)
            print(f"✅ VM '{vm_name}' has been powered on successfully.")

    def stop_vm(content, vm_name):
        vm = util.get_vm_by_name(content, vm_name)
        if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff:
            print(f"✅ VM '{vm_name}' is already powered off.")
        else:
            print(f"🔄 Powering off VM '{vm_name}'...")
            task = vm.PowerOff()
            WaitForTask(task)
            print(f"✅ VM '{vm_name}' has been powered off successfully.")