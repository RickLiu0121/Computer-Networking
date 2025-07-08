# Computer-Networking
M/M/1/K and Socket Programming in Python

**M/M/1/K:**

The M/M/1/K queue is implemented in Python. M/M/1/K has the buffer limited to a size of K packets. As a result, if a packet arrives in an M/M/1/K
queue and this queue has already K packets in it, the packet is dropped, i.e., the packet will be lost. Performance metrics such as packet loss ratio and utilization are assessed

Here's the implementation logic:
For the M/M/1/K, all the arrival events over a T of 1000s are generated first. Then, by iterating through all the arrival events in a chronological order, I determine whether the
packets should be dropped by using a queue for storing arriving packets. The logic inside the loop is as follows:
1. Determine if there’s any packets already in queue and if the arriving time of the current packet is after the departure of the first packet in the FIFO queue. Since the arrival time could happen after several packets’ departures in the queue, make sure to pop all those packets in queue to empty the correct amount of space in the queue. The departure time for the next-to-be-departed packet in the queue will be adjusted every time a packet leaves the queue.
2. If the queue is full, drop the packet and update all relevant parameters as needed. For example, delete these arrival events from the data structure that houses all the initially generated arrival
events.
3. If the queue is empty, adjust departure time simply to be equal to the arrival time of the current
packet plus its service time
4. Add the packet to the queue

Since P_Loss is the packet loss probability, which is the ratio of the total number of packets lost due to
the buffer full condition to the total number of generated packets. In my program, the total number of
generated packets is all the arrival packets generated. The number of packets lost is constantly updated
when all the true departure events are being generated.

**Socket Programming:**

The client program sends a request containing domain-name to the server, and the server replies with IP Address/es that
corresponds to the domain name. A DNS query will be sent from the client to the server, and the server will send a DNS
response to the client.
