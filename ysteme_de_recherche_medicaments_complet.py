"""
SYSTÈME COMPLET D'OPTIMISATION DES MÉDICAMENTS - MAURITANIE
Avec analyses et recommandations avancées
"""

import math
import json
from datetime import datetime

class SystemeMedicamentsMauritanie:
    def __init__(self):
        self.pharmacies = {
            "Pharmacie Tevragh": {
                "coords": (0, 0),
                "stock": {"Paracétamol": 50, "Amoxicilline": 30, "Aspirine": 100},
                "prix": {"Paracétamol": 200, "Amoxicilline": 500, "Aspirine": 150},
                "tel": "45 25 10 10",
                "horaire": "8h-20h"
            },
            "Pharmacie Ksar": {
                "coords": (2, 3),
                "stock": {"Paracétamol": 0, "Amoxicilline": 50, "Insuline": 20},
                "prix": {"Paracétamol": 250, "Amoxicilline": 480, "Insuline": 5000},
                "tel": "45 25 11 11",
                "horaire": "8h-22h"
            },
            "Pharmacie Sebkha": {
                "coords": (4, 1),
                "stock": {"Paracétamol": 30, "Amoxicilline": 0, "Aspirine": 50},
                "prix": {"Paracétamol": 180, "Amoxicilline": 520, "Aspirine": 160},
                "tel": "45 25 12 12",
                "horaire": "24h/24"
            },
            "Pharmacie Toujounine": {
                "coords": (6, 4),
                "stock": {"Insuline": 10, "Metformine": 40, "Amoxicilline": 20},
                "prix": {"Insuline": 4800, "Metformine": 300, "Amoxicilline": 490},
                "tel": "45 25 13 13",
                "horaire": "9h-21h"
            },
            "Pharmacie Dar Naim": {
                "coords": (8, 2),
                "stock": {"Paracétamol": 20, "Metformine": 30, "Aspirine": 80},
                "prix": {"Paracétamol": 220, "Metformine": 320, "Aspirine": 140},
                "tel": "45 25 14 14",
                "horaire": "8h-19h"
            },
            "Pharmacie Arafat": {
                "coords": (7, 6),
                "stock": {"Insuline": 5, "Paracétamol": 40, "Amoxicilline": 15},
                "prix": {"Insuline": 5200, "Paracétamol": 190, "Amoxicilline": 510},
                "tel": "45 25 15 15",
                "horaire": "8h-21h"
            }
        }
        self.patient_pos = (1, 2)
        self.historique_recherches = []
    
    def distance(self, pos1, pos2):
        return math.hypot(pos1[0]-pos2[0], pos1[1]-pos2[1])
    
    def temps_trajet(self, distance):
        """Estimation du temps de trajet (minutes)"""
        return distance * 15  # 15 min par km en ville
    
    def trouver_medicament(self, medicament, quantite=1, critere="prix", position_patient=None):
        """Recherche optimisée"""
        if position_patient is None:
            position_patient = self.patient_pos
        
        pharmacies_dispo = []
        
        for nom, infos in self.pharmacies.items():
            stock = infos["stock"].get(medicament, 0)
            if stock >= quantite:
                dist = self.distance(position_patient, infos["coords"])
                prix_unitaire = infos["prix"].get(medicament, float('inf'))
                prix_total = prix_unitaire * quantite
                temps = self.temps_trajet(dist)
                
                # Score selon critère
                if critere == "prix":
                    score = prix_total
                elif critere == "distance":
                    score = dist
                elif critere == "temps":
                    score = temps
                else:  # mixte
                    score = 0.4 * (dist/10) + 0.4 * (prix_total/5000) + 0.2 * (temps/60)
                
                pharmacies_dispo.append({
                    "nom": nom,
                    "distance": dist,
                    "temps_minutes": temps,
                    "prix_unitaire": prix_unitaire,
                    "prix_total": prix_total,
                    "stock": stock,
                    "telephone": infos["tel"],
                    "horaire": infos["horaire"],
                    "score": score
                })
        
        if pharmacies_dispo:
            pharmacies_dispo.sort(key=lambda x: x["score"])
            # Sauvegarder dans l'historique
            self.historique_recherches.append({
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "medicament": medicament,
                "quantite": quantite,
                "critere": critere,
                "resultats": len(pharmacies_dispo)
            })
            return pharmacies_dispo
        return None
    
    def comparer_options(self, medicament, quantite):
        """Compare toutes les options pour un médicament"""
        print(f"\n📊 ANALYSE COMPLÈTE POUR {medicament.upper()} ({quantite} unités)")
        print("=" * 70)
        
        resultats = self.trouver_medicament(medicament, quantite, "prix")
        if not resultats:
            print(f"❌ {medicament} non disponible")
            return
        
        print(f"\n{'Pharmacie':<20} {'Distance':<12} {'Temps':<10} {'Prix total':<15} {'Stock':<8}")
        print("-" * 70)
        
        for ph in resultats:
            print(f"{ph['nom']:<20} {ph['distance']:.1f} km     {ph['temps_minutes']:.0f} min   {ph['prix_total']:>8} MRU   {ph['stock']:>3} u")
        
        # Recommandation par critère
        print("\n" + "=" * 70)
        print("🎯 RECOMMANDATIONS PAR CRITÈRE :")
        print("-" * 70)
        
        for critere in ["prix", "distance", "temps", "mixte"]:
            resultats_critere = self.trouver_medicament(medicament, quantite, critere)
            if resultats_critere:
                meilleur = resultats_critere[0]
                print(f"  • {critere.upper():8} : {meilleur['nom']:<18} "
                      f"(Prix: {meilleur['prix_total']} MRU | "
                      f"Distance: {meilleur['distance']:.1f} km | "
                      f"Temps: {meilleur['temps_minutes']:.0f} min)")
    
    def alerte_rupture(self):
        """Détecte les médicaments en rupture"""
        print("\n⚠️ ALERTES RUPTURE DE STOCK")
        print("=" * 70)
        
        rupture = []
        for nom, infos in self.pharmacies.items():
            for med, stock in infos["stock"].items():
                if stock == 0:
                    rupture.append((nom, med))
                elif stock < 10:
                    print(f"  ⚠️ {nom} : {med} (stock critique : {stock} unités)")
        
        if not rupture:
            print("  ✅ Aucune rupture détectée")
    
    def statistiques(self):
        """Statistiques du réseau pharmaceutique"""
        print("\n📈 STATISTIQUES DU RÉSEAU")
        print("=" * 70)
        
        # Médicaments les plus chers
        prix_max = {}
        for infos in self.pharmacies.values():
            for med, prix in infos["prix"].items():
                if med not in prix_max or prix > prix_max[med]:
                    prix_max[med] = prix
        
        print("\n💰 Médicaments les plus chers :")
        for med, prix in sorted(prix_max.items(), key=lambda x: x[1], reverse=True)[:3]:
            print(f"  • {med} : {prix} MRU/unité")
        
        # Pharmacies 24h/24
        print("\n🏪 Pharmacies ouvertes 24h/24 :")
        for nom, infos in self.pharmacies.items():
            if infos["horaire"] == "24h/24":
                print(f"  • {nom} : {infos['tel']}")
        
        # Couverture géographique
        print("\n🗺️ Couverture par zone :")
        zones = {
            "Nord (Arafat/Teyarett)": ["Pharmacie Arafat", "Pharmacie Toujounine"],
            "Sud (Sebkha/Ksar)": ["Pharmacie Sebkha", "Pharmacie Ksar"],
            "Est (Dar Naim/Toujounine)": ["Pharmacie Dar Naim", "Pharmacie Toujounine"],
            "Ouest (Tevragh)": ["Pharmacie Tevragh"]
        }
        
        for zone, pharmacies in zones.items():
            print(f"  • {zone} : {', '.join(pharmacies)}")

def menu_principal():
    """Interface principale"""
    systeme = SystemeMedicamentsMauritanie()
    
    print("\n" + "=" * 70)
    print("🏥 SYSTÈME D'OPTIMISATION DE RECHERCHE DE MÉDICAMENTS")
    print("   MAURITANIE - NOUAKCHOTT")
    print("=" * 70)
    
    while True:
        print("\n" + "-" * 70)
        print("📋 MENU PRINCIPAL")
        print("-" * 70)
        print("1. 🔍 Chercher un médicament")
        print("2. 📦 Voir tous les stocks")
        print("3. 📊 Comparer toutes les options")
        print("4. ⚠️ Alertes rupture de stock")
        print("5. 📈 Statistiques du réseau")
        print("6. 🚪 Quitter")
        print("-" * 70)
        
        choix = input("\n👉 Votre choix (1-6) : ").strip()
        
        if choix == "1":
            medicament = input("\n💊 Nom du médicament : ").strip().capitalize()
            
            # Liste des médicaments disponibles
            tous_meds = set()
            for p in systeme.pharmacies.values():
                tous_meds.update(p["stock"].keys())
            
            if medicament not in tous_meds:
                print(f"\n❌ '{medicament}' non disponible. Médicaments disponibles :")
                print(f"   {', '.join(sorted(tous_meds))}")
                continue
            
            quantite = input("🔢 Quantité : ").strip()
            try:
                quantite = int(quantite)
            except:
                print("❌ Quantité invalide")
                continue
            
            print("\n🎯 Critère de recherche :")
            print("   1. Prix le plus bas")
            print("   2. Distance la plus courte")
            print("   3. Temps de trajet minimum")
            print("   4. Mixte (équilibré)")
            
            critere_choix = input("\n👉 Choix (1-4) : ").strip()
            
            critere_map = {"1": "prix", "2": "distance", "3": "temps", "4": "mixte"}
            critere = critere_map.get(critere_choix, "prix")
            
            resultats = systeme.trouver_medicament(medicament, quantite, critere)
            
            if resultats:
                print(f"\n✅ {len(resultats)} pharmacie(s) trouvée(s) :")
                print("\n" + "-" * 70)
                for i, ph in enumerate(resultats[:3], 1):
                    print(f"\n📍 Option {i} : {ph['nom']}")
                    print(f"   📏 Distance : {ph['distance']:.1f} km")
                    print(f"   ⏱️  Temps trajet : {ph['temps_minutes']:.0f} min")
                    print(f"   💰 Prix unitaire : {ph['prix_unitaire']} MRU")
                    print(f"   💵 Prix total : {ph['prix_total']} MRU")
                    print(f"   📦 Stock : {ph['stock']} unités")
                    print(f"   📞 Téléphone : {ph['telephone']}")
                    print(f"   🕐 Horaires : {ph['horaire']}")
                    
                    if i == 1:
                        print(f"\n   🏆 RECOMMANDATION : Meilleure option selon votre critère !")
                print("\n" + "-" * 70)
            else:
                print(f"\n❌ Stock insuffisant pour {quantite} unités.")
        
        elif choix == "2":
            print("\n🏪 STOCKS DES PHARMACIES")
            print("=" * 70)
            for nom, infos in systeme.pharmacies.items():
                print(f"\n📍 {nom}")
                print(f"   📞 {infos['tel']} | 🕐 {infos['horaire']}")
                print("   💊 Stocks :")
                for med, stock in infos["stock"].items():
                    if stock > 0:
                        prix = infos["prix"][med]
                        print(f"      • {med:15} : {stock:3} unités  ({prix} MRU)")
        
        elif choix == "3":
            medicament = input("\n💊 Nom du médicament : ").strip().capitalize()
            quantite = int(input("🔢 Quantité : ").strip())
            systeme.comparer_options(medicament, quantite)
        
        elif choix == "4":
            systeme.alerte_rupture()
        
        elif choix == "5":
            systeme.statistiques()
            print(f"\n📊 Historique des recherches : {len(systeme.historique_recherches)} requêtes")
        
        elif choix == "6":
            print("\n" + "=" * 70)
            print("🙏 Merci d'avoir utilisé le système de recherche de médicaments !")
            print("   Prenez soin de votre santé. À bientôt !")
            print("=" * 70)
            break
        
        else:
            print("\n⚠️ Option invalide. Veuillez choisir 1-6.")

if __name__ == "__main__":
    menu_principal()