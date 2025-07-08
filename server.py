import socket
import struct
import random
HOST = '127.0.0.1'  
PORT = 10005
# Define DNS records in a dictionary
dns_data = {
    'google.com': {
        'type': 1,  # A Type
        'class': 1,  # IN class
        'ttl': 260,
        'ip': ['192.165.1.1', '192.165.1.10']
    },
    'youtube.com': {
        'type': 1,
        'class': 1,
        'ttl': 160,
        'ip': ['192.165.1.2']
    },
    'uwaterloo.ca': {
        'type': 1,
        'class': 1,
        'ttl': 160,
        'ip': ['192.165.1.3']
    },
    'wikipedia.org': {
        'type': 1,
        'class': 1,
        'ttl': 160,
        'ip': ['192.165.1.4']
    },
    'amazon.ca': {
        'type': 1,
        'class': 1,
        'ttl': 160,
        'ip': ['192.165.1.5']
    }
}
def formatted_hex(hex):
    return ' '.join(f'{byte:02x}' for byte in hex)
def parse_DNS_query(query):
    id = struct.unpack('!H', query[:2])[0]
    dns_question = query[12:]
    print("Request:")
    print(formatted_hex(query))
    qname = []
    index = 12  # Skip the first 12 bytes that is the header
    
    while query[index] != 0:  # QNAME ends with a null byte (0)
        length = query[index]  # First byte is the length of the label
        label = query[index + 1:index + 1 + length].decode('utf-8')  # Extract the label
        qname.append(label)
        index += length + 1  # Move to the next label
    domain = '.'.join(qname)
    return id, dns_question, domain

def generate_DNS_response(id, dns_question, domain):
    ip = dns_data[domain]["ip"]
    ID = id          # 16-bit => 0 - 65535
    QR = 1                                  # 1 bit: Set 1 for response
    OPCODE = 0                              # 4 bits: Set 0 for standard query
    AA = 1                                  # 1 bit: authoritative answer
    TC = 0                                  # 1 bit: not truncated
    RD = 0                                  # 1 bit: recursion desired
    RA = 0                                  # 1 bit: recursion not available
    Z = 0                                   # 3 bits: reserved
    RCODE = 0                               # 4 bits: no error
    FLAGS = (QR << 15) | (OPCODE << 11) | (AA << 10) | (TC << 9) | (RD << 8) | (RA << 7) | (Z << 4) | RCODE
    QDCOUNT = 1                             # 16-bit question count
    ANCOUNT = len(ip)                       # 16-bit answer count     
    NSCOUNT = 0                             # 16-bit authority record count
    ARCOUNT = 0                             # 16-bit additional record count
    # Header packed into 12 bytes
    header = struct.pack('!HHHHHH', ID, FLAGS, QDCOUNT, ANCOUNT, NSCOUNT, ARCOUNT)
    question = dns_question
    NAME = b"\xc0\x0c"            
    TYPE = b"\x00\x01"            
    CLASS = b"\x00\x01"           
    TTL = struct.pack("!I", dns_data[domain]["ttl"])  # TTL in 32-bit binary format
    RDLength = b"\x00\x04"        # Each IPv4 address has a length of 4 bytes
    answer = b""

    for ip in ip:
        RDATA = socket.inet_pton(socket.AF_INET, ip)  # Convert IP to binary format
        answer += NAME + TYPE + CLASS + TTL + RDLength + RDATA
    total_response = header + question + answer
    print(formatted_hex(total_response))
    return total_response


def run_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, PORT))
    print(f"DNS server started at {HOST} on port {PORT}")
    try:
        while True:
            data, addr = server_socket.recvfrom(512)  # buffer size 512 bytes
            print(f"client: {addr}")
            id, dns_question, domain = parse_DNS_query(data)
            if domain in dns_data:
                print("Response:")
                response = generate_DNS_response(id, dns_question, domain)
                server_socket.sendto(response, addr)
            else:
                print("Domain name not found in DNS record")

    except KeyboardInterrupt:
        print("Server interrupted. Shutting down.")

    finally:
        server_socket.close()
    
    

if __name__ == "__main__":
    run_server()