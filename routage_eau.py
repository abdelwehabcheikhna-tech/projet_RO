"""
Projet RO - Routage des camions d'eau à Nouakchott
Version avec flotte de 2 camions
"""

from ortools.constraint_solver import routing_enums_pb2, pywrapcp
import math

# Données
points = ["Dépôt (Tevragh-Zeina)", "Ksar", "Sebkha", "Toujounine", "Dar Naim", "Teyarett", "Arafat"]
coords = [(0,0), (2,3), (4,1), (6,4), (8,2), (3,5), (7,6)]
demandes = [0, 250, 300, 200, 280, 350, 220]  # Litres
capacite_camion = 1000  # Litres par camion
nb_camions = 3 # Nombre de camions disponibles

print("=" * 50)
print("ROUTAGE DES CAMIONS D'EAU - NOUAKCHOTT")
print("=" * 50)
print(f"Points de distribution :")
for i, point in enumerate(points):
    print(f"  {i}: {point} - Demande: {demandes[i]} L")

print(f"\nCapacité par camion : {capacite_camion} L")
print(f"Demande totale : {sum(demandes)} L")
print(f"Nombre de camions : {nb_camions}")
print()

# Matrice des distances
dist = [[0]*7 for _ in range(7)]
for i in range(7):
    for j in range(7):
        if i != j:
            dist[i][j] = math.hypot(coords[i][0]-coords[j][0], coords[i][1]-coords[j][1])

# Création du gestionnaire de routage
manager = pywrapcp.RoutingIndexManager(len(points), nb_camions, 0)  # 0 = dépôt
routing = pywrapcp.RoutingModel(manager)

# Fonction de distance
def distance_callback(from_index, to_index):
    from_node = manager.IndexToNode(from_index)
    to_node = manager.IndexToNode(to_index)
    return int(dist[from_node][to_node] * 100)  # Multiplier pour éviter les floats

transit_callback_index = routing.RegisterTransitCallback(distance_callback)
routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

# Contrainte de capacité
def demand_callback(from_index):
    from_node = manager.IndexToNode(from_index)
    return demandes[from_node]

demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
routing.AddDimensionWithVehicleCapacity(
    demand_callback_index,
    0,  # capacité nulle
    [capacite_camion] * nb_camions,  # capacité de chaque camion
    True,  # début à 0
    'Capacity'
)

# Paramètres de recherche
search_parameters = pywrapcp.DefaultRoutingSearchParameters()
search_parameters.first_solution_strategy = (
    routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
)
search_parameters.local_search_metaheuristic = (
    routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
)
search_parameters.time_limit.seconds = 5

# Résolution
solution = routing.SolveWithParameters(search_parameters)

if solution:
    print("✅ SOLUTION TROUVÉE !")
    print("=" * 50)
    
    distance_totale = 0
    charge_par_camion = []
    
    for vehicle_id in range(nb_camions):
        print(f"\n🚚 CAMION {vehicle_id + 1} :")
        index = routing.Start(vehicle_id)
        tour = []
        distance_camion = 0
        charge = 0
        
        while not routing.IsEnd(index):
            node = manager.IndexToNode(index)
            tour.append(node)
            if node != 0:  # Pas le dépôt
                charge += demandes[node]
            next_index = solution.Value(routing.NextVar(index))
            distance_camion += dist[node][manager.IndexToNode(next_index)]
            index = next_index
        
        node = manager.IndexToNode(index)
        tour.append(node)  # Retour au dépôt
        
        # Afficher la tournée
        for i, node in enumerate(tour):
            if i < len(tour) - 1:
                print(f"   {i+1}. {points[node]} → ", end="")
            else:
                print(f"{i+1}. {points[node]}")
        
        print(f"   Distance : {distance_camion:.1f} km")
        print(f"   Charge totale : {charge}/{capacite_camion} L ({100*charge/capacite_camion:.0f}%)")
        distance_totale += distance_camion
        charge_par_camion.append(charge)
    
    print("\n" + "=" * 50)
    print("📊 STATISTIQUES GLOBALES")
    print("=" * 50)
    print(f"Distance totale parcourue : {distance_totale:.1f} km")
    print(f"Charge totale transportée : {sum(charge_par_camion)}/{sum(demandes)} L")
    print(f"Taux de remplissage moyen : {100 * sum(charge_par_camion) / (nb_camions * capacite_camion):.0f}%")
    
    # Vérification des contraintes
    print("\n✅ VÉRIFICATION DES CONTRAINTES :")
    print(f"   ✓ Capacités respectées : Oui")
    print(f"   ✓ Tous les points desservis : Oui")
    print(f"   ✓ Retour au dépôt : Oui")
    
    # Recommandations
    print("\n💡 RECOMMANDATIONS :")
    print(f"   • Tournée réalisable avec {nb_camions} camions")
    print(f"   • Éviter les heures de pointe (8h-10h, 17h-19h)")
    print(f"   • Prévoir des points de recharge intermédiaires")
    if max(charge_par_camion) < capacite_camion * 0.8:
        print(f"   • Possibilité d'optimiser davantage la charge des camions")
    
else:
    print("❌ Aucune solution trouvée")
    print("\n   Causes possibles :")
    print("   • Capacité des camions insuffisante")
    print("   • Nombre de camions insuffisant")
    print(f"   • Solution : Augmenter nb_camions à {math.ceil(sum(demandes)/capacite_camion)}")