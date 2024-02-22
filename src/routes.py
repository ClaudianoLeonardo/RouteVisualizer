
from utils import calculate_distance_matrix, create_init_route, calculate_full_path, create_map
from SimulatedAnnealing import SARouteOptimizer, Model


def finding_routes(graph,
                   HILLS,
                   START_HILL,
                   END_HILL,
                   pontos,
                   max_iter=2000,
                   max_iter_without_improvement=300):
    
    

    # init variables
    hill_names, coordinates, duration = [], [], []
    colnames = ["optimal_order","plot_model",
                "optimal_path","create_map",
                "save_map","distance"]

   
    
    # get the coordinates                
    for name, coord in HILLS.items():
        hill_names.append(name)
        coordinates.append(coord)

    # distances between coordinates
    distances_matrix = None
    print("Calculating distances between points")
    distances_matrix = calculate_distance_matrix(graph, coordinates)


    # optimizer configuration
    optimizer = SARouteOptimizer(model=Model(cost_matrix=distances_matrix),
                                 max_iter=max_iter,
                                 max_iter_without_improvement=max_iter_without_improvement)

    # optimal order
    print("Calculating optimal order of hills")
    init_route = create_init_route(hill_names.index(START_HILL), 
                                   hill_names.index(END_HILL), 
                                   distances_matrix.shape[0])

 
    optimal_route, total_distance = optimizer.run(init_route)
   


  
    
    
    full_path, distances = calculate_full_path(graph, optimal_route, coordinates)

    
    
    map = create_map(graph, full_path, optimal_route, hill_names, coordinates, distances,pontos)
   
    
    
    map.save("optimal.html")
    

    return map, total_distance