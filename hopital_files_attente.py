"""
Projet RO - Optimisation des files d'attente en centre hospitalier
Catégorie 6 : Problèmes réels en Mauritanie
Modèle M/M/c pour les urgences
"""

import math
import numpy as np
import matplotlib.pyplot as plt
from ortools.linear_solver import pywraplp

class FileAttenteHospitalier:
    """Modélisation et optimisation des files d'attente"""
    
    def __init__(self, lambda_arrivees, mu_service):
        """
        lambda_arrivees: taux d'arrivée (patients/heure)
        mu_service: taux de service par serveur (patients/heure)
        """
        self.lambd = lambda_arrivees
        self.mu = mu_service
        self.rho = lambda_arrivees / mu_service  # Charge de trafic
    
    def probabilite_zero_mmc(self, c):
        """Probabilité qu'il n'y ait aucun patient dans le système M/M/c"""
        rho = self.rho
        if rho >= c:
            return 0  # Système instable
        
        # Calcul de la somme
        somme = 0
        for k in range(c):
            somme += (rho**k) / math.factorial(k)
        
        terme = (rho**c) / (math.factorial(c) * (1 - rho/c))
        p0 = 1 / (somme + terme)
        return p0
    
    def temps_attente_moyen_mmc(self, c):
        """Temps d'attente moyen dans la file (Wq) pour M/M/c"""
        if self.rho >= c:
            return float('inf')
        
        p0 = self.probabilite_zero_mmc(c)
        
        # Formule d'Erlang C
        erlang_c = ((self.rho**c) / math.factorial(c)) * p0 / (1 - self.rho/c)
        
        # Temps d'attente moyen dans la file
        Wq = erlang_c / (c * self.mu - self.lambd)
        return Wq
    
    def nombre_patients_file_mmc(self, c):
        """Nombre moyen de patients dans la file (Lq)"""
        if self.rho >= c:
            return float('inf')
        
        Wq = self.temps_attente_moyen_mmc(c)
        Lq = self.lambd * Wq
        return Lq
    
    def temps_reponse_moyen(self, c):
        """Temps de réponse moyen (W = Wq + 1/mu)"""
        Wq = self.temps_attente_moyen_mmc(c)
        return Wq + 1/self.mu
    
    def nombre_optimal_serveurs(self, temps_cible, min_serveurs=1, max_serveurs=20):
        """Détermine le nombre optimal de serveurs pour atteindre un temps cible"""
        for c in range(min_serveurs, max_serveurs + 1):
            Wq = self.temps_attente_moyen_mmc(c)
            if Wq <= temps_cible and Wq != float('inf'):
                return c
        return max_serveurs

def simulation_monte_carlo(lambda_arrivees, mu_service, c_serveurs, duree_simulation=1000):
    """
    Simulation Monte-Carlo pour validation
    """
    np.random.seed(42)
    
    # Génération des temps inter-arrivées (loi exponentielle)
    n_patients = int(lambda_arrivees * duree_simulation)
    temps_inter_arrivees = np.random.exponential(1/lambda_arrivees, n_patients)
    
    # Temps d'arrivée cumulés
    temps_arrivee = np.cumsum(temps_inter_arrivees)
    temps_arrivee = temps_arrivee[temps_arrivee <= duree_simulation]
    n_patients_reels = len(temps_arrivee)
    
    # Génération des temps de service
    temps_service = np.random.exponential(1/mu_service, n_patients_reels)
    
    # Simulation de la file
    temps_attente = np.zeros(n_patients_reels)
    disponibilite_serveurs = np.zeros(c_serveurs)
    
    for i in range(n_patients_reels):
        # Plus prochain serveur disponible
        prochain_serveur = np.argmin(disponibilite_serveurs)
        debut_service = max(temps_arrivee[i], disponibilite_serveurs[prochain_serveur])
        temps_attente[i] = max(0, debut_service - temps_arrivee[i])
        disponibilite_serveurs[prochain_serveur] = debut_service + temps_service[i]
    
    return temps_attente, temps_service

def optimiser_cout_total(lambda_arrivees, mu_service, cout_serveur=50, cout_attente=10):
    """
    Optimisation du coût total (coût des serveurs + coût d'attente)
    """
    solver = pywraplp.Solver.CreateSolver('SCIP')
    
    if not solver:
        print("❌ Solveur non disponible")
        return None
    
    # Variable : nombre de serveurs (entier)
    c = solver.IntVar(1, 20, 'c')
    
    # Coût des serveurs
    cout_serveurs = cout_serveur * c
    
    # Estimation du coût d'attente (fonction non linéaire, optimisation discrète)
    # On va évaluer manuellement
    meilleur_cout = float('inf')
    meilleur_c = 1
    
    for nb_serveurs in range(1, 21):
        file = FileAttenteHospitalier(lambda_arrivees, mu_service)
        Lq = file.nombre_patients_file_mmc(nb_serveurs)
        
        if Lq == float('inf'):
            continue
        
        cout_total = cout_serveur * nb_serveurs + cout_attente * Lq
        
        if cout_total < meilleur_cout:
            meilleur_cout = cout_total
            meilleur_c = nb_serveurs
    
    return meilleur_c, meilleur_cout

def visualisation_resultats():
    """Visualisation complète des résultats"""
    
    # Paramètres de l'hôpital
    lambda_arrivees = 5  # 5 patients/heure
    mu_service = 4       # 4 patients/heure par médecin
    
    print("=" * 60)
    print("OPTIMISATION DES FILES D'ATTENTE - SERVICE DES URGENCES")
    print("=" * 60)
    print(f"Taux d'arrivée (λ) : {lambda_arrivees} patients/heure")
    print(f"Taux de service (μ) : {mu_service} patients/heure/médecin")
    print(f"Charge de trafic (ρ) : {lambda_arrivees/mu_service:.2f}")
    print()
    
    # Création de l'objet
    file = FileAttenteHospitalier(lambda_arrivees, mu_service)
    
    # Analyse pour différents nombres de serveurs
    print("📊 ANALYSE POUR DIFFÉRENTS NOMBRES DE MÉDECINS")
    print("-" * 60)
    print(f"{'Médecins':<10} {'Taux occupation':<15} {'Temps attente (h)':<18} {'Patients file':<15}")
    print("-" * 60)
    
    resultats = []
    for c in range(1, 8):
        rho_effectif = lambda_arrivees / (c * mu_service)
        
        if rho_effectif >= 1:
            print(f"{c:<10} {rho_effectif:<15.2f} {'Système instable':<18} {'∞':<15}")
            resultats.append((c, rho_effectif, float('inf'), float('inf')))
        else:
            Wq = file.temps_attente_moyen_mmc(c)
            Lq = file.nombre_patients_file_mmc(c)
            W = file.temps_reponse_moyen(c)
            
            print(f"{c:<10} {rho_effectif:<15.2f} {Wq:<18.2f} {Lq:<15.2f}")
            resultats.append((c, rho_effectif, Wq, Lq))
    
    print()
    
    # Détermination du nombre optimal selon objectif
    print("🎯 RECOMMANDATIONS SELON L'OBJECTIF")
    print("-" * 60)
    
    # Objectif 1: Temps d'attente < 15 minutes
    c_optimal_15min = file.nombre_optimal_serveurs(temps_cible=0.25)  # 0.25 heure = 15 min
    print(f"✓ Pour temps d'attente < 15 minutes : {c_optimal_15min} médecins")
    
    # Objectif 2: Temps d'attente < 30 minutes
    c_optimal_30min = file.nombre_optimal_serveurs(temps_cible=0.5)
    print(f"✓ Pour temps d'attente < 30 minutes : {c_optimal_30min} médecins")
    
    # Objectif 3: Optimisation économique
    c_optimal_cout, cout_min = optimiser_cout_total(lambda_arrivees, mu_service, 
                                                     cout_serveur=50, cout_attente=10)
    print(f"✓ Optimisation économique (coût serveur=50, coût attente=10/h) : {c_optimal_cout} médecins")
    print(f"  Coût total minimum : {cout_min:.0f} unités/h")
    
    print()
    
    # Simulation Monte-Carlo
    print("🔄 SIMULATION MONTE-CARLO (Validation)")
    print("-" * 60)
    
    c_test = c_optimal_30min  # Utilisons la recommandation
    temps_attente_sim, temps_service_sim = simulation_monte_carlo(
        lambda_arrivees, mu_service, c_test, duree_simulation=500
    )
    
    print(f"Avec {c_test} médecins (simulation sur 500h) :")
    print(f"  Temps d'attente moyen simulé : {np.mean(temps_attente_sim):.2f} h")
    print(f"  Temps d'attente médian : {np.median(temps_attente_sim):.2f} h")
    print(f"  Temps d'attente max : {np.max(temps_attente_sim):.2f} h")
    print(f"  Percentile 95% : {np.percentile(temps_attente_sim, 95):.2f} h")
    
    # Visualisation
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    
    # Graphique 1: Temps d'attente vs nombre de médecins
    ax1 = axes[0, 0]
    c_vals = [r[0] for r in resultats if r[2] != float('inf')]
    wq_vals = [r[2] for r in resultats if r[2] != float('inf')]
    ax1.plot(c_vals, wq_vals, 'bo-', linewidth=2, markersize=8)
    ax1.axhline(y=0.25, color='r', linestyle='--', label='Objectif 15 min')
    ax1.axhline(y=0.5, color='orange', linestyle='--', label='Objectif 30 min')
    ax1.set_xlabel('Nombre de médecins')
    ax1.set_ylabel("Temps d'attente moyen (heures)")
    ax1.set_title("Impact du nombre de médecins sur le temps d'attente")
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Graphique 2: Occupation vs nombre de médecins
    ax2 = axes[0, 1]
    c_vals_all = [r[0] for r in resultats]
    rho_vals = [r[1] for r in resultats]
    ax2.bar(c_vals_all, rho_vals, color='skyblue', edgecolor='black')
    ax2.axhline(y=0.7, color='g', linestyle='--', label='Charge optimale (70%)')
    ax2.axhline(y=0.85, color='orange', linestyle='--', label='Limite recommandée (85%)')
    ax2.set_xlabel('Nombre de médecins')
    ax2.set_ylabel("Taux d'occupation")
    ax2.set_title("Occupation des médecins")
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # Graphique 3: Distribution des temps d'attente (simulation)
    ax3 = axes[1, 0]
    ax3.hist(temps_attente_sim, bins=30, color='lightgreen', edgecolor='black', alpha=0.7)
    ax3.axvline(x=np.mean(temps_attente_sim), color='r', linestyle='--', 
                label=f'Moyenne: {np.mean(temps_attente_sim):.2f}h')
    ax3.set_xlabel("Temps d'attente (heures)")
    ax3.set_ylabel("Fréquence")
    ax3.set_title(f"Distribution des temps d'attente ({c_test} médecins)")
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Graphique 4: Comparaison théorie vs simulation
    ax4 = axes[1, 1]
    wq_theorique = [file.temps_attente_moyen_mmc(c) for c in range(1, 8) 
                    if file.temps_attente_moyen_mmc(c) != float('inf')]
    c_theorique = [c for c in range(1, len(wq_theorique)+1)]
    
    # Simulation pour chaque c
    wq_simule = []
    for c in c_theorique:
        temps_sim, _ = simulation_monte_carlo(lambda_arrivees, mu_service, c, duree_simulation=200)
        wq_simule.append(np.mean(temps_sim))
    
    ax4.plot(c_theorique, wq_theorique, 'bo-', label='Théorique (M/M/c)', linewidth=2)
    ax4.plot(c_theorique, wq_simule, 'rs--', label='Simulation Monte-Carlo', linewidth=2)
    ax4.set_xlabel('Nombre de médecins')
    ax4.set_ylabel("Temps d'attente moyen (heures)")
    ax4.set_title("Validation: Théorie vs Simulation")
    ax4.legend()
    ax4.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()
    
    # Recommandations finales
    print("\n" + "=" * 60)
    print("💡 RECOMMANDATIONS POUR LE CENTRE HOSPITALIER")
    print("=" * 60)
    print(f"1. Personnel optimal : {c_optimal_30min} médecins aux urgences")
    print(f"2. Temps d'attente estimé : {file.temps_attente_moyen_mmc(c_optimal_30min):.2f} h ({file.temps_attente_moyen_mmc(c_optimal_30min)*60:.0f} min)")
    print(f"3. Occupation des médecins : {lambda_arrivees/(c_optimal_30min*mu_service)*100:.1f}%")
    print(f"4. Nombre moyen de patients dans la file : {file.nombre_patients_file_mmc(c_optimal_30min):.1f}")
    
    print("\n📋 Actions concrètes :")
    print("   • Renforcer l'équipe médicale aux heures de pointe (8h-12h)")
    print("   • Mettre en place un système de triage prioritaire")
    print("   • Ajouter un médecin supplémentaire si λ > 6 patients/h")
    print("   • Former le personnel aux protocoles accélérés")

if __name__ == "__main__":
    visualisation_resultats()