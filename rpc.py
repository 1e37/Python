import hashlib
from bitcoinrpc.authproxy import AuthServiceProxy
import struct
import time

#pip3 install bitcoin-rpc

# Set Bitcoin Core node URL and credentials
rpc_user = 'minerclient1'
rpc_password = 'eb840e9430a62252099338262e06a7d5$6fb94860a3f405b779673ac52c3849c131b302d3f8035d156152c6a5829c96b4'
rpc_port = '8332'

# Connect to the Node Server 
rpc_connection = AuthServiceProxy("http://" + rpc_user + ":" + rpc_password + "@127.0.0.1:" + rpc_port)


# Get the latest block info to work with
latest_block_info = rpc_connection.getbestblockhash()
block_info = rpc_connection.getblock(latest_block_info)

# Create an empty list and add all keys, excluding transactions to it
block_info_directory = {}
for key, value in block_info.items():
    if key != 'tx':
        block_info_directory[key] = value

# Extract the necessary information from the block_info_directory
version = block_info_directory['version']
previous_block_hash = block_info_directory['previousblockhash']
merkleroot = block_info_directory['merkleroot']
block_time = block_info_directory['time']
bits = block_info_directory['bits']

# Define the target difficulty / zeros  as integer converted from hex provided by the Network
mining_difficulty = int(bits, 16)

# Initialize the nonce for n trys
nonce = 0
hash_counter = 0
start_time = time.time()


while True:
    # https://en.bitcoin.it/wiki/Block_hashing_algorithm
    # Create the block header required for the hashcat POW algorithm
    
    # using little-endian order:
    # Version | 4 Bytes
    # hashPrevBlock | 32 Bytes
    # hashMerkleRoot | 32 Bytes
    # Time | 4 Bytes
    # Bits | 4 Bytes target difficulty value
    # Nonce | 4 Bytes
    # < = little endian
    # L = 4 Bytes long int
    # 32s = 32 byte string or 256 bit key

    block_header = struct.pack('<L32s32sLLL', version, previous_block_hash.encode('utf-8').ljust(32), merkleroot.encode('utf-8').ljust(32), block_time, int(bits, 16), nonce)

    # Hash the block header twice
    block_hash = hashlib.sha256(hashlib.sha256(block_header).digest()).hexdigest()

    # Increment the try counter
    hash_counter += 1
    

    #Search for a valid block hash. if The difficulty amount of 0's is less then the current block hash, its a valid block!
    if int(block_hash, 16) < mining_difficulty:
        print("Found a valid block hash:", block_hash) 
        break

    # Increment and try next nonce
    nonce += 1

    # Calculate the hashrate while running
    elapsed_time = time.time() - start_time
    if elapsed_time > 0:
        hashrate = hash_counter / elapsed_time
        print("Hashrate: {:.2f} H/s".format(hashrate), end='\r')
    else:
        print("Hashrate: N/A", end='\r')