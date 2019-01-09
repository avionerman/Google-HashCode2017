from __future__ import print_function
import os
from ortools.algorithms import pywrapknapsack_solver

file_name = "kittens.in"
output_file_name = "kittens.txt"



# changing working directory to script directory
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

print(dname)


def read_input_file(file_name):

    with open(file_name, "r") as input_file:

        # first line
        line = input_file.readline()
        videos, endpoints, req_desc, cache_servers, cache_capacity = [ int(x) for x in line.split() ]

        # second line
        video_sizes = [ int(x) for x in  input_file.readline().split()]

        endpoints_datacenters_latency = [0 for x in range(endpoints)]
        endpoints_caches = [0 for x in range(endpoints)]
        endpoints_caches_latency = [[0 for x in range(cache_servers)] for y in range(endpoints)]
        request_matrix = [[0 for x in range(videos)] for y in range(endpoints)]

        # endpoints
        for x in range(endpoints):
            line_0 = [int(y) for y in input_file.readline().split()]
            endpoints_datacenters_latency[x] = line_0[0]
            endpoints_caches[x] = line_0[1]
            for w in range( endpoints_caches[x] ):
                line_1 =  [int(z) for z in input_file.readline().split()]
                endpoints_caches_latency[x][line_1[0]] = line_1[1]

        # videos
        for x in range(req_desc):
            line_0 = [int(y) for y in input_file.readline().split()]
            request_matrix[ line_0[1] ][ line_0[0] ] = line_0[2]
        return cache_capacity, cache_servers, endpoints, videos, video_sizes, request_matrix, endpoints_datacenters_latency, endpoints_caches, endpoints_caches_latency


def write_output_file(output_file_name, cache_server_videos):

    with open(output_file_name, 'w') as output_file:
        output_file.write("%d\n" % cache_servers)

        for x in range(cache_servers):
            output_file.write("%d " % x)
            for y in cache_server_videos[x]:
                output_file.write("%d " % y)
            output_file.write("\n")



# reading the input file
print("I am attempting to read the input file")
cache_capacity, cache_servers, endpoints, videos, video_sizes, request_matrix, endpoints_datacenters_latency, endpoints_caches, endpoints_caches_latency = read_input_file(file_name)
print("I have finished reading the input file")



# ==========================================================================================================================
# calculating solution
# ==========================================================================================================================


# calculating weights
print("I am starting to calculate the video weights")
video_weights_per_endpoint = [[0 for x in range(videos)] for y in range(endpoints)]
for i in range(endpoints):
    for j in range(videos):
        video_weights_per_endpoint[i][j] = request_matrix[i][j] * video_sizes[j] * endpoints_datacenters_latency[i]
print("I have finished calculating the video weights")

# cache server videos is the solution to submit
cache_server_videos = [[0 for x in range(videos)] for y in range(cache_servers)]

clients = []
clients_videos = []
clients_videos_size = []
clients_videos_weight = []
videos_served_to_endpoints = [[0 for x in range(videos)] for y in range(endpoints)]
knapsack_solver = pywrapknapsack_solver.KnapsackSolver( pywrapknapsack_solver.KnapsackSolver.KNAPSACK_MULTIDIMENSION_BRANCH_AND_BOUND_SOLVER, 'cache_server_knapsack')
for j in range(cache_servers):

    print("I will now examine cache server #%d" % j)

    summ = 0
    del clients[:]
    del clients_videos[:]
    del clients_videos_size[:]
    del clients_videos_weight[:]

    for i in range(endpoints):
        if( endpoints_caches_latency[i][j] != 0 ):
            clients.append(i)

    for x in range(endpoints):
        for y in range(videos):
            if( request_matrix[x][y] != 0 ):
                clients_videos.append(y)
    clients_videos = sorted(list(set(clients_videos)))

    for w in clients_videos:
        clients_videos_size.append( video_sizes[w] )
        summ = 0
        for z in range(endpoints):
            if(z in clients and (videos_served_to_endpoints[z][w] == 0)):
                summ += video_weights_per_endpoint[z][w]
        clients_videos_weight.append(summ)

    print("I will now run knapsack for cache server #%d" % j)
    knapsack_solver.Init(clients_videos_weight, [clients_videos_size], [cache_capacity])
    knapsack_solver.Solve()

    print("I am now saving the results for cache server #%d" % j)
    cache_server_videos[j] = [clients_videos[video] for video in range(len(clients_videos)) if knapsack_solver.BestSolutionContains(video)]

    for video in cache_server_videos[j]:
        for endpoint in len(endpoints):
            if(request_matrix[endpoint][video] != 0 ):
                videos_served_to_endpoints[endpoint][video] = 1

write_output_file(output_file_name, cache_server_videos)

