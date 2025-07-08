"""
To enable user interaction with the server to retrieve DNS information of the five domain
names
"""
import socket
import struct
import random
SERVER_HOST = '127.0.0.1' 
SERVER_PORT = 10005
def create_qname(domain_name):
    # Convert domain name to QNAME format (length-prefixed labels)
    labels = domain_name.split('.')
    qname_parts = []
    for label in labels:
        length = len(label)
        # Add the length byte followed by the label's bytes
        qname_parts.append(struct.pack('B', length) + label.encode())
    # Join all parts and add the terminating zero byte
    qname = b''.join(qname_parts) + b'\x00'
    return qname

def generate_DNS_query(domain_name):
    #For DNS Header
    ID = random.randint(0, 65535)           # 16-bit => 0 - 65535
    QR = 0                                  # 1 bit: Set 0 for query
    OPCODE = 0                              # 4 bits: Set 0 for standard query
    AA = 1                                  # 1 bit: authoritative answer
    TC = 0                                  # 1 bit: not truncated
    RD = 0                                  # 1 bit: recursion desired
    RA = 0                                  # 1 bit: recursion not available
    Z = 0                                   # 3 bits: reserved
    RCODE = 0                               # 4 bits: no error
    FLAGS = (QR << 15) | (OPCODE << 11) | (AA << 10) | (TC << 9) | (RD << 8) | (RA << 7) | (Z << 4) | RCODE
    QDCOUNT = 1                             # 16-bit question count
    ANCOUNT = 0                             # 16-bit answer count
    NSCOUNT = 0                             # 16-bit authority record count
    ARCOUNT = 0                             # 16-bit additional record count
    # Header packed into 12 bytes
    header = struct.pack('!HHHHHH', ID, FLAGS, QDCOUNT, ANCOUNT, NSCOUNT, ARCOUNT)
    # For DNS Question
    qname = create_qname(domain_name)
    QTYPE = 1                               # 16-bit type (A record)
    QCLASS = 1                              # 16-bit class (IN)
    question = struct.pack('!HH', QTYPE, QCLASS)
    # Combine header and question for the complete DNS query message
    dns_query = header + qname + question
    # formatted_hex = ' '.join(f'{byte:02x}' for byte in dns_query)
    # print(formatted_hex)
    return dns_query

def parse_DNS_response(response):
    # get domain name
    qname = []
    index = 12  # Skip the first 12 bytes that is the header
    
    while response[index] != 0:  # QNAME ends with a null byte (0)
        length = response[index]  # First byte is the length of the label
        label = response[index + 1:index + 1 + length].decode('utf-8')  # Extract the label
        qname.append(label)
        index += length + 1  # Move to the next label
    domain_name = '.'.join(qname)
    num_records = int.from_bytes(response[6:8], byteorder='big')
    # hardcode TYPE A for the lab
    TYPE = "type A"
    # hardcode CLASS IN for the lab
    CLASS = "class IN"
    # get total length for header + question 
    # print(index)
    answer_offset = index + 4 # get to the end of header section
    for i in range(num_records):
        # print(hex(response[answer_offset]))
        ttl = struct.unpack("!I", response[answer_offset+7:answer_offset+11])[0]
        answer_offset = answer_offset + 11 #adjust offset
        #get ip address
        ip_address = socket.inet_ntoa(response[answer_offset+2:answer_offset+6])
        print(f"{domain_name}: {TYPE}, {CLASS}, TTL {ttl}, addr (4) {ip_address}")
        answer_offset = answer_offset + 5

def establish_connection():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #this creates a UDP socket
    client_socket.settimeout(2)
    
    while True:
        # take user input 
        # get rid of leading or trailing white space and conver to lower case
        domain = input("Enter Domain Name: ").strip().lower()
        if domain == 'end':
            print("Session ended")
            break
        dns_query = generate_DNS_query(domain)
        client_socket.sendto(dns_query, (SERVER_HOST,SERVER_PORT))
        
        try:
            response, _ = client_socket.recvfrom(512)  # Receive up to 512 bytes 
            # Parse the DNS response
            parse_DNS_response(response)
            
        except socket.timeout:
            print("Request timed out.")
if __name__ == "__main__":
    establish_connection()
