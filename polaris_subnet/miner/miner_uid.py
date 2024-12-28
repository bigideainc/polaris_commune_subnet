import logging
from communex.client import CommuneClient
from communex.compat.key import classic_load_key

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("MinerUIDPrinter")

def print_miner_uid(miner_name, netuid):
    """
    Retrieve and print the miner's UID on the subnet.
    """
    try:
        # Load the miner's key
        key = classic_load_key(miner_name)
        # commune_node_url="wss://api.communeai.net"
        # Specify the Commune node WebSocket endpoint
        commune_node_url = "wss://testnet-commune-api-node-0.communeai.net/"

        # Create a CommuneClient instance using the endpoint
        client = CommuneClient(commune_node_url)
        modules_keys = client.query_map_key(netuid)
        # Find the miner's UID by matching the SS58 address
        val_ss58 = key.ss58_address
        miner_uid = next(uid for uid, address in modules_keys.items() if address == val_ss58)

        logger.info(f"Miner SS58 Address: {val_ss58}")
        logger.info(f"Miner UID on the subnet: {miner_uid}")

    except StopIteration:
        logger.error("Miner's SS58 address not found in the network.")
    except Exception as e:
        logger.error(f"Error retrieving miner UID: {e}")

if __name__ == "__main__":
    print_miner_uid("yominer", 13)
