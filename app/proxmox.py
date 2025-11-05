# Spin up a Target Box with unique IP Address utilizing Proxmox Python API

from proxmoxer import ProxmoxAPI
from proxmoxer.tools import Tasks
import time
import json
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PROXMOX_NODE = 'pve'
STORAGE_NAME = 'BARRACUDA'
SOURCE_CT_ID = 201              # DEFCON Target Template
NEW_CT_NAME = 'target'          # New Template Hostname
NEW_CT_ID = 0                   # New Template CT ID Placeholder
container_ids = []

proxmox = ProxmoxAPI(
    '192.168.1.100', 
    user='root@pam',
    token_name='DefaultTokenID', 
    token_value='72e45e51-45de-4058-877c-e50c01a1cd75',
    verify_ssl=False 
)

def powerUp(NEW_CT_ID):
    try:
        start_task = proxmox.nodes(PROXMOX_NODE).lxc(NEW_CT_ID).status.start.post()
    except Exception as e:
        logger.error(f"An error occurred while attempting to start CT {NEW_CT_ID}: {e}")
        return -1

    logger.info(f"{NEW_CT_ID} starting up")
    return 0

def getContainers():
    global container_ids
    active_count = 0

    # Check if the Node is correct by attempting the API call
    containers = proxmox.nodes(PROXMOX_NODE).lxc.get()

    # Analyze and print the running containers
    # print("\n--- Containers Found Results ---")
    # print(f"{'CT ID':<6} | {'Status':<10} | {'Name':<8} | {'Tags'}")
    # print("-" * 50)

    data = []

    for container in containers:
        vmid = container.get('vmid')
        status = container.get('status')
        name = container.get('name')
        tags = container.get('tags')
        
        # We are specifically checking if the value is 'running'
        # print(f"{vmid:<6} | {status:<10} | {name:<8} | {tags}")
        active_count += 1
        container_ids.append(vmid)

        data.append({"vmid": vmid, "status": status, "name": name, "tags": tags})
            
    if active_count == 0:
        return "No active containers found"

    sorted_data = sorted(data, key=lambda d: d['vmid'])

    return sorted_data

def createTarget():
    container_ids = []

    for container in getContainers():
        container_ids.append(container['vmid'])

    NEW_CT_ID = 101

    for id in sorted(container_ids):
        if id == NEW_CT_ID:
            NEW_CT_ID += 1
        else:
            break

    print(f"\n--- Cloning CT {SOURCE_CT_ID} to new CT {NEW_CT_ID} ---")

    clone_task = proxmox.nodes(PROXMOX_NODE).lxc(SOURCE_CT_ID).clone.post(
        newid=NEW_CT_ID,
        full=0                # Use 0 for linked clone (fast)
    )

    print(f"Clone task started successfully.")
    print(f"Proxmox Task ID: {clone_task}")

    # Wait for the clone task to complete before continuing
    exitstatus = ''
    while 'OK' not in exitstatus:
        exitstatus = Tasks.blocking_status(proxmox, clone_task)['exitstatus']
        time.sleep(1)

    print(f'Clone Task Completed with exitstatus: {exitstatus}\n')

    NEW_IP_ADDRESS = f"192.168.1.{NEW_CT_ID}/24"
    GATEWAY_IP = "192.168.1.100"

    FULL_NET_CONFIG = (
            f"name=eth0,"
            f"bridge=vmbr0,"
            f"ip={NEW_IP_ADDRESS},"
            f"gw={GATEWAY_IP}"
        )

    # Update network configuration - this may or may not return a task ID
    config_result = proxmox.nodes(PROXMOX_NODE).lxc(NEW_CT_ID).config.put(
            net0=FULL_NET_CONFIG
        )
    
    print(f"Network configuration update result: {config_result}")
    
    # Check if config.put returned a task ID (some operations do, some don't)
    if config_result and isinstance(config_result, str) and config_result.startswith('UPID:'):
        print(f"Config update task started: {config_result}")
        # Wait for the config task to complete
        config_exitstatus = ''
        while 'OK' not in config_exitstatus:
            config_exitstatus = Tasks.blocking_status(proxmox, config_result)['exitstatus']
            time.sleep(1)
        print(f'Config update completed with exitstatus: {config_exitstatus}')
    else:
        print("Network configuration updated synchronously")
    
    power_result = powerUp(NEW_CT_ID)

    if power_result == -1:
        return f"An error occurred while attempting to start CT {NEW_CT_ID}: {e}"

    return f"Node {NEW_CT_ID} has been created at {NEW_IP_ADDRESS[:-3]}"
