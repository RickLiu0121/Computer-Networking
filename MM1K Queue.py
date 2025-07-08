import numpy as np
from q1 import gen_exponential_random_variable as gen_exp
import matplotlib.pyplot as plt
import csv
import queue
L = 2000 #average length of a packet in bits
C = 1000000 #tranmission rate of the output link in bits per second
rho_values = np.arange(0.5, 1.5, 0.1)
T = 1000 #simulation time in seconds
all_P_idle = []
all_P_loss = []

def generate_all_arrival_events(incoming_packet_rate, T):
    global events, num_of_generated_packets
    current_time = 0
    while current_time < T:
        inter_arrival_time = gen_exp(incoming_packet_rate)
        current_time += inter_arrival_time
        if current_time > T:
            break
        packet_length = -L*np.log(1-np.random.uniform(low=0,high=1))
        service_time = packet_length/C
        num_of_generated_packets += 1
        events[current_time]= ["arrival", current_time, service_time, packet_length]


def generate_all_departure_events():
    global num_packets_in_queue, events, num_packets_dropped
    last_departure_time = 0
    departure_events = {}
    arrival_events_to_delete = []
    # real_arrival_events = {}
    packets_queue = queue.Queue(maxsize=queue_max_size)
    for arrival_packet in events.values():
        arrival_time = arrival_packet[1]
        service_time = arrival_packet[2]
        # if not packets_queue.empty() and arrival_time >= last_departure_time:
            #first queue is not empty, and the arriving packet is later than departure time than the processing time 
            #remove the processing packet
            #do this iteratively to make sure all the previous packets in queue that needs processing are removed 
        while arrival_time >= last_departure_time and not packets_queue.empty():
            packets_queue.get()
            departure_events[last_departure_time] = ["departure"]
            if not packets_queue.empty():
                last_departure_time = last_departure_time + packets_queue.queue[0]

        if packets_queue.full():
            #after the above if, the queue is full, then drop this arrival packet
            num_packets_dropped += 1
            arrival_events_to_delete.append(arrival_time)
            continue
        
        if packets_queue.empty():
            last_departure_time = arrival_time + service_time
        packets_queue.put(service_time)
        

    for arrival_time in arrival_events_to_delete:
        del events[arrival_time]

    while not packets_queue.empty():
        packets_queue.get()
        departure_events[last_departure_time] = ["departure"]
        if not packets_queue.empty():
            last_departure_time = last_departure_time + packets_queue.queue[0]

    events.update(departure_events)
    events = {key: events[key] for key in sorted(events)}
           

def generate_all_observation_events(observation_rate, T):
    global events
    current_time = 0
    while current_time < T:
        inter_arrival_time = gen_exp(observation_rate)
        current_time += inter_arrival_time
        if current_time > T:
            break
        events[current_time] = ["observation"]
    events = {key: events[key] for key in sorted(events)}


def generate_DES_events():
    generate_all_arrival_events(incoming_packet_rate, T)
    generate_all_departure_events()
    generate_all_observation_events(observation_rate, T)
    # write_to_csv()


def process_DES_events(events):
    N_a = 0
    N_d = 0
    N_o = 0
    P_idle = 0
    for key, value in events.items(): 
        if value[0] == "arrival":
            N_a += 1
        if value[0] == "departure":
            N_d += 1
        if value[0] == "observation":
            N_o += 1
            P_idle = process_observation_event(N_a, N_d)
    P_loss = num_packets_dropped/num_of_generated_packets
    print("p = ",rho)
    print("Number of Successful Arrival: ", N_a)
    print("Number of Departure: ", N_d)
    print("Number of Observations: ", N_o)
    print("P_idle: ",P_idle)
    print("P_loss: ",P_loss)
    print("Number of Packets dropped: ",num_packets_dropped)
    return P_idle, P_loss


def process_observation_event(N_a, N_d):
    """Need to return the following
    1. E[N] time-average of the number of packets in the queue - number of packets/
    2. P_idle the proportion of time the server is idle
    3. P_loss the probability that a packet will be dropped for a finite queue
    4. N_a, N_d, N_o
    """
    P_idle = 0
    if N_d > 0:
        P_idle = 1 -(N_a*L/C)/T
    else:
        P_idle = 0
    return P_idle

def graph_p_idle_vs_rho_for_all_K(all_p_idle_values,x,K):
    for i, y_values in enumerate(all_p_idle_values):
        # print(y_values)
        plt.plot(x,y_values, marker='o', linestyle='-', label=f"K={K[i]}")  # Plot with points marked with circles
    plt.xlabel('Utilitzation of Queue')  # Label for the x-axis
    plt.ylabel('P_idle')  # Label for the x-axis
    plt.title('P_idle vs. Utilization of Queue for varying K')  # Title of the plot
    plt.grid(True)  # Add grid for better readability
    plt.legend()
    plt.show()


def graph_p_loss_vs_rho_for_all_K(all_p_loss_values, x, K):
    for i, y_values in enumerate(all_p_loss_values):
        plt.plot(x,list(y_values), marker='o', linestyle='-', label=f"K={K[i]}")  # Plot with points marked with circles
    plt.xlabel('Utilitzation of Queue')  # Label for the x-axis
    plt.ylabel('P_loss')  # Label for the x-axis
    plt.title('P_loss vs. Utilization of Queue for varying K')  # Title of the plot
    plt.grid(True)  # Add grid for better readability
    plt.legend()
    plt.show()

def write_to_csv():
    for key, value in events.items():
        print(key, value)
    # Open the CSV file in write mode
    with open("Tabulate_data.csv", mode='w', newline='') as file:
        writer = csv.writer(file)
        # Optionally, write a header row
        writer.writerow(['Time', 'Type'])
        # Write the key-value pairs
        for key, value in events.items():
            writer.writerow([key, value[0]])


if __name__ == "__main__":
    K = [10,25,50]
    for i, queue_max_size in enumerate(K):
        #for each K. iteration through different rho values
        P_idle_per_K = []
        P_loss_per_K = []
        for rho in rho_values:
            incoming_packet_rate = rho*C/L
            observation_rate =5*incoming_packet_rate
            events = {}
            num_of_generated_packets = 0
            num_packets_dropped = 0
            num_packets_in_queue = 0   
            P_idle = 0
            P_loss = 0     
            generate_DES_events()
            # write_to_csv()
            P_idle, P_loss = process_DES_events(events)
            P_idle_per_K.append(P_idle)
            P_loss_per_K.append(P_loss)
        all_P_idle.append(P_idle_per_K)
        all_P_loss.append(P_loss_per_K)
        # print(all_P_idle)
        # print(all_P_loss)
        # break
    graph_p_idle_vs_rho_for_all_K(all_P_idle,rho_values,K)
    graph_p_loss_vs_rho_for_all_K(all_P_loss,rho_values,K)  
