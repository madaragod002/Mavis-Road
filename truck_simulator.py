import random
import numpy as np

class TruckSimulator:
    """
    Simulador para un camión individual en Mavis Road
    """
    
    # Configuración de camiones por rareza
    TRUCK_CONFIG = {
        1: {
            'earnings_per_trip': 4,
            'fuel_cost': 2,  # cada 2 viajes
            'fuel_frequency': 2,
            'tire_cost': 4,  # cada 4 viajes
            'tire_frequency': 4,
            'repair_cost': 6,
            'breakdown_probability': 0.30
        },
        2: {
            'earnings_per_trip': 5,
            'fuel_cost': 2,  # cada 2 viajes
            'fuel_frequency': 2,
            'tire_cost': 4,  # cada 4 viajes
            'tire_frequency': 4,
            'repair_cost': 6,
            'breakdown_probability': 0.26
        },
        3: {
            'earnings_per_trip': 7,
            'fuel_cost': 2,  # cada 2 viajes
            'fuel_frequency': 2,
            'tire_cost': 4,  # cada 4 viajes
            'tire_frequency': 4,
            'repair_cost': 6,
            'breakdown_probability': 0.20
        },
        4: {
            'earnings_per_trip': 9,
            'fuel_cost': 1,  # cada 2 viajes
            'fuel_frequency': 2,
            'tire_cost': 4,  # cada 4 viajes
            'tire_frequency': 4,
            'repair_cost': 10,
            'breakdown_probability': 0.17
        },
        5: {
            'earnings_per_trip': 11,
            'fuel_cost': 1,  # cada 2 viajes
            'fuel_frequency': 2,
            'tire_cost': 4,  # cada 4 viajes
            'tire_frequency': 4,
            'repair_cost': 10,
            'breakdown_probability': 0.14
        }
    }
    
    def __init__(self, rarity, use_repair_tool=False, referral_tier=0):
        """
        Inicializar camión con rareza específica
        
        Args:
            rarity (int): Rareza del camión (1-5)
            use_repair_tool (bool): Si usar la herramienta de reducción de averías
            referral_tier (int): Tier de referido (0: ninguno, 1: -2%, 2: -3%, 3: -5%)
        """
        if rarity not in self.TRUCK_CONFIG:
            raise ValueError(f"Rareza {rarity} no válida. Debe estar entre 1-5")
        
        self.rarity = rarity
        self.config = self.TRUCK_CONFIG[rarity]
        self.trip_count = 0
        self.total_earnings = 0
        self.total_costs = 0
        self.repairs_count = 0
        
        # Herramienta de reducción de averías
        self.use_repair_tool = use_repair_tool
        self.repair_tool_trips_remaining = 2 if use_repair_tool else 0
        self.repair_tool_cost = 1 if use_repair_tool else 0
        
        # Tier de referido
        self.referral_tier = referral_tier
        self.referral_reduction = {
            0: 0.0,
            1: 0.02,  # 2%
            2: 0.03,  # 3%
            3: 0.05   # 5%
        }.get(referral_tier, 0.0)
        
        # Añadir costo de herramienta al inicio
        if use_repair_tool:
            self.total_costs += self.repair_tool_cost
        
    def simulate_trip(self):
        """
        Simular un viaje individual
        
        Returns:
            dict: Resultados del viaje
        """
        trip_result = {
            'earnings': 0,
            'costs': 0,
            'breakdown': False,
            'fuel_cost': 0,
            'tire_cost': 0,
            'repair_cost': 0
        }
        
        # Calcular probabilidad de avería (reducida por tier de referido y herramienta)
        current_breakdown_prob = self.config['breakdown_probability']
        
        # Aplicar reducción por tier de referido
        current_breakdown_prob = max(0, current_breakdown_prob - self.referral_reduction)
        
        # Aplicar reducción por herramienta si está activa
        if self.repair_tool_trips_remaining > 0:
            current_breakdown_prob = max(0, current_breakdown_prob - 0.05)  # Reducir 5%
            self.repair_tool_trips_remaining -= 1
        
        # Verificar si el camión se rompe antes del viaje
        if random.random() < current_breakdown_prob:
            trip_result['breakdown'] = True
            trip_result['repair_cost'] = self.config['repair_cost']
            trip_result['costs'] += self.config['repair_cost']
            self.repairs_count += 1
        
        # El camión puede hacer el viaje después de reparación
        self.trip_count += 1
        trip_result['earnings'] = self.config['earnings_per_trip']
        
        # Calcular costos de combustible
        if self.trip_count % self.config['fuel_frequency'] == 0:
            trip_result['fuel_cost'] = self.config['fuel_cost']
            trip_result['costs'] += self.config['fuel_cost']
        
        # Calcular costos de gomas
        if self.trip_count % self.config['tire_frequency'] == 0:
            trip_result['tire_cost'] = self.config['tire_cost']
            trip_result['costs'] += self.config['tire_cost']
        
        # Actualizar totales
        self.total_earnings += trip_result['earnings']
        self.total_costs += trip_result['costs']
        
        return trip_result
    
    def simulate_period(self, hours):
        """
        Simular un período de tiempo específico
        
        Args:
            hours (int): Número de horas a simular
            
        Returns:
            dict: Resumen del período
        """
        # Cada viaje toma 12 horas
        trips_possible = hours // 12
        
        trip_results = []
        for _ in range(trips_possible):
            trip_results.append(self.simulate_trip())
        
        return {
            'total_trips': trips_possible,
            'total_earnings': self.total_earnings,
            'total_costs': self.total_costs,
            'net_profit': self.total_earnings - self.total_costs,
            'repairs_count': self.repairs_count,
            'trip_details': trip_results
        }
    
    def reset(self):
        """Resetear el estado del camión"""
        self.trip_count = 0
        self.total_earnings = 0
        self.total_costs = 0
        self.repairs_count = 0
        
        # Resetear herramienta
        self.repair_tool_trips_remaining = 2 if self.use_repair_tool else 0
        if self.use_repair_tool:
            self.total_costs = self.repair_tool_cost
        else:
            self.total_costs = 0
    
    def get_stats(self):
        """
        Obtener estadísticas del camión
        
        Returns:
            dict: Estadísticas actuales
        """
        return {
            'rarity': self.rarity,
            'trip_count': self.trip_count,
            'total_earnings': self.total_earnings,
            'total_costs': self.total_costs,
            'net_profit': self.total_earnings - self.total_costs,
            'repairs_count': self.repairs_count,
            'config': self.config,
            'use_repair_tool': self.use_repair_tool,
            'repair_tool_trips_remaining': self.repair_tool_trips_remaining,
            'repair_tool_cost': self.repair_tool_cost,
            'referral_tier': self.referral_tier,
            'referral_reduction': self.referral_reduction
        }
