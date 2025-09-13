import random
import numpy as np
from truck_simulator import TruckSimulator
from concurrent.futures import ThreadPoolExecutor
import threading

class MonteCarloSimulation:
    """
    Simulador Monte Carlo para flota de camiones en Mavis Road
    """
    
    # Configuración de períodos de tiempo
    TIME_PERIODS = {
        '1_week': 7 * 24,  # 168 horas
        '30_days': 30 * 24,  # 720 horas
        '1_year': 365 * 24  # 8760 horas
    }
    
    def __init__(self, fleet, use_repair_tool=False, referral_tier=0):
        """
        Inicializar simulación con flota de camiones
        
        Args:
            fleet (list): Lista de rarezas de camiones
            use_repair_tool (bool): Si usar herramienta de reducción de averías
            referral_tier (int): Tier de referido (0: ninguno, 1: -2%, 2: -3%, 3: -5%)
        """
        self.fleet = fleet
        self.use_repair_tool = use_repair_tool
        self.referral_tier = referral_tier
        self.lock = threading.Lock()
        
    def simulate_single_run(self, time_period_hours):
        """
        Ejecutar una simulación individual de la flota
        
        Args:
            time_period_hours (int): Horas del período a simular
            
        Returns:
            dict: Resultados de la simulación individual
        """
        total_profit = 0
        fleet_results = {}
        rarity_stats = {}
        
        for truck_rarity in self.fleet:
            # Crear nuevo camión para cada simulación
            truck = TruckSimulator(truck_rarity, self.use_repair_tool, self.referral_tier)
            
            # Simular el período
            period_result = truck.simulate_period(time_period_hours)
            
            total_profit += period_result['net_profit']
            
            # Acumular estadísticas por rareza
            if truck_rarity not in rarity_stats:
                rarity_stats[truck_rarity] = {
                    'count': 0,
                    'total_profit': 0,
                    'total_trips': 0,
                    'total_repairs': 0
                }
            
            rarity_stats[truck_rarity]['count'] += 1
            rarity_stats[truck_rarity]['total_profit'] += period_result['net_profit']
            rarity_stats[truck_rarity]['total_trips'] += period_result['total_trips']
            rarity_stats[truck_rarity]['total_repairs'] += period_result['repairs_count']
        
        return {
            'total_profit': total_profit,
            'rarity_stats': rarity_stats
        }
    
    def run_simulation(self, time_period, iterations=10000):
        """
        Ejecutar simulación Monte Carlo completa
        
        Args:
            time_period (str): Período de tiempo ('1_week', '30_days', '1_year')
            iterations (int): Número de iteraciones a ejecutar
            
        Returns:
            dict: Resultados completos de la simulación
        """
        if time_period not in self.TIME_PERIODS:
            raise ValueError(f"Período {time_period} no válido")
        
        if not self.fleet:
            raise ValueError("La flota no puede estar vacía")
        
        time_period_hours = self.TIME_PERIODS[time_period]
        all_profits = []
        combined_rarity_stats = {}
        
        # Ejecutar simulaciones
        print(f"Ejecutando {iterations} simulaciones para período de {time_period}...")
        
        for i in range(iterations):
            if i % 1000 == 0:
                print(f"Progreso: {i}/{iterations} simulaciones completadas")
            
            run_result = self.simulate_single_run(time_period_hours)
            all_profits.append(run_result['total_profit'])
            
            # Combinar estadísticas por rareza
            for rarity, stats in run_result['rarity_stats'].items():
                if rarity not in combined_rarity_stats:
                    combined_rarity_stats[rarity] = {
                        'profits': [],
                        'trips': [],
                        'repairs': [],
                        'count': stats['count']
                    }
                
                combined_rarity_stats[rarity]['profits'].append(stats['total_profit'])
                combined_rarity_stats[rarity]['trips'].append(stats['total_trips'])
                combined_rarity_stats[rarity]['repairs'].append(stats['total_repairs'])
        
        # Calcular estadísticas finales
        all_profits = np.array(all_profits)
        
        results = {
            'iterations': iterations,
            'time_period': time_period,
            'fleet_size': len(self.fleet),
            'all_profits': all_profits.tolist(),
            'mean_profit': float(np.mean(all_profits)),
            'std_profit': float(np.std(all_profits)),
            'min_profit': float(np.min(all_profits)),
            'max_profit': float(np.max(all_profits)),
            'median_profit': float(np.median(all_profits)),
            'positive_probability': float(np.sum(all_profits > 0) / len(all_profits) * 100),
            'percentile_25': float(np.percentile(all_profits, 25)),
            'percentile_75': float(np.percentile(all_profits, 75)),
            'rarity_breakdown': {}
        }
        
        # Calcular estadísticas por rareza
        for rarity, stats in combined_rarity_stats.items():
            profits = np.array(stats['profits'])
            trips = np.array(stats['trips'])
            repairs = np.array(stats['repairs'])
            
            results['rarity_breakdown'][rarity] = {
                'count': stats['count'],
                'avg_profit': float(np.mean(profits)) / stats['count'],  # Profit per truck
                'total_profit': float(np.mean(profits)),  # Total profit for all trucks of this rarity
                'std_profit': float(np.std(profits)),
                'avg_trips': float(np.mean(trips)) / stats['count'],  # Trips per truck
                'avg_repairs': float(np.mean(repairs)) / stats['count'],  # Repairs per truck
                'profit_per_truck': profits.tolist()
            }
        
        print(f"Simulación completada: {iterations} iteraciones")
        return results
    
    def get_fleet_summary(self):
        """
        Obtener resumen de la flota actual
        
        Returns:
            dict: Resumen de la flota
        """
        from collections import Counter
        fleet_count = Counter(self.fleet)
        
        return {
            'total_trucks': len(self.fleet),
            'by_rarity': dict(fleet_count),
            'fleet_composition': self.fleet
        }
    
    def estimate_expected_profit(self, time_period):
        """
        Estimar ganancia esperada sin Monte Carlo (cálculo teórico)
        
        Args:
            time_period (str): Período de tiempo
            
        Returns:
            dict: Estimación teórica
        """
        if time_period not in self.TIME_PERIODS:
            raise ValueError(f"Período {time_period} no válido")
        
        time_period_hours = self.TIME_PERIODS[time_period]
        trips_per_truck = time_period_hours // 12
        
        total_expected_profit = 0
        
        for truck_rarity in self.fleet:
            config = TruckSimulator.TRUCK_CONFIG[truck_rarity]
            
            # Ganancias esperadas
            expected_earnings = trips_per_truck * config['earnings_per_trip']
            
            # Costos esperados
            fuel_costs = (trips_per_truck // config['fuel_frequency']) * config['fuel_cost']
            tire_costs = (trips_per_truck // config['tire_frequency']) * config['tire_cost']
            
            # Calcular probabilidad de avería considerando tier de referido y herramienta
            breakdown_prob = config['breakdown_probability']
            
            # Aplicar reducción por tier de referido
            referral_reduction = {
                0: 0.0, 1: 0.02, 2: 0.03, 3: 0.05
            }.get(self.referral_tier, 0.0)
            breakdown_prob = max(0, breakdown_prob - referral_reduction)
            
            if self.use_repair_tool and trips_per_truck > 0:
                # Reducir probabilidad en 5% para los primeros 2 viajes
                trips_with_tool = min(2, trips_per_truck)
                reduced_prob = max(0, breakdown_prob - 0.05)
                repair_costs = (trips_with_tool * reduced_prob + 
                               (trips_per_truck - trips_with_tool) * breakdown_prob) * config['repair_cost']
            else:
                repair_costs = trips_per_truck * breakdown_prob * config['repair_cost']
            
            expected_costs = fuel_costs + tire_costs + repair_costs
            
            # Añadir costo de herramienta si está activa
            if self.use_repair_tool:
                expected_costs += 1  # Costo de la herramienta
            
            expected_profit = expected_earnings - expected_costs
            total_expected_profit += expected_profit
        
        return {
            'expected_profit': total_expected_profit,
            'trips_per_truck': trips_per_truck,
            'time_period_hours': time_period_hours
        }
