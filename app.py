import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
# Asegúrate de tener estos archivos en la misma carpeta o ajusta las rutas
# from truck_simulator import TruckSimulator
# from monte_carlo import MonteCarloSimulation

# Page configuration
st.set_page_config(
    page_title="Mavis Road - Monte Carlo Simulator",
    page_icon="🚚",
    layout="wide"
)

# Initialize session state
if 'fleet' not in st.session_state:
    st.session_state.fleet = []
if 'simulation_results' not in st.session_state:
    st.session_state.simulation_results = None
if 'use_repair_tool' not in st.session_state:
    st.session_state.use_repair_tool = False
if 'referral_tier' not in st.session_state:
    st.session_state.referral_tier = 0

def main():
    # Referral code header
    st.markdown("""
    # 🚚 Mavis Road - Profit Simulator
    ### 💎 Support the Creator!
    Use my referral code in the game:
    """, unsafe_allow_html=True)
    
    # Copy referral code section
    import streamlit.components.v1 as components

    st.markdown("### 📋 Copy Referral Code")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.text_input("Referral Code", value="7FB951B1", disabled=False, key="referral_code", label_visibility="collapsed")

    with col2:
        components.html("""
        <div style="padding: 5px 0;">
            <button onclick="copyToClipboard()" style="
                background: #ff4b4b;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                cursor: pointer;
                width: 100%;
                font-size: 14px;
            ">📋 Copy Code</button>
            <div id="status" style="margin-top: 5px; font-size: 12px; text-align: center;"></div>
        </div>
        <script>
        function copyToClipboard() {
            navigator.clipboard.writeText('7FB951B1').then(function() {
                document.getElementById('status').innerHTML = '✅ Copied!';
                document.getElementById('status').style.color = 'green';
                setTimeout(() => {
                    document.getElementById('status').innerHTML = '';
                }, 2000);
            }).catch(function(err) {
                document.getElementById('status').innerHTML = '❌ Copy failed';
                document.getElementById('status').style.color = 'red';
                console.error('Could not copy text: ', err);
            });
        }
        </script>
        """, height=60)

    # Program description
    st.markdown("""
    ### 🎯 Simulator Objective
    This application helps you **calculate real profits** you can earn in Mavis Road
    based on your truck fleet. The simulator considers all important expenses:

    ● **Trip earnings** according to each truck's rarity
    ● **Fixed costs**: fuel (every 2 trips) and tires (every 4 trips)
    ● **Repairs**: each truck has its specific breakdown probability
    ● **Referral tier**: reduces breakdowns for your entire fleet

    Use Monte Carlo simulation (10,000 iterations) to get **realistic results**
    and make better decisions about your truck investments.
    """)

    # Sidebar for truck management
    with st.sidebar:
        st.header("🔧 Fleet Management")

        # Truck rarity selection
        rarity_options = {
            1: "Rarity 1 - Comfort (4 RON/trip)",
            2: "Rarity 2 - Highline (5 RON/trip)",
            3: "Rarity 3 - Shift (7 RON/trip)",
            4: "Rarity 4 - Electric (9 RON/trip)",
            5: "Rarity 5 - Autonomous (11 RON/trip)"
        }

        selected_rarity = st.selectbox(
            "Select truck type:",
            options=list(rarity_options.keys()),
            format_func=lambda x: rarity_options[x]
        )

        quantity = st.number_input(
            "Quantity to add:",
            min_value=1,
            max_value=100,
            value=1
        )

        # Referral tier
        referral_options = {
            0: "No referral tier",
            1: "Tier 1 (-2% breakdowns)",
            2: "Tier 2 (-3% breakdowns)",
            3: "Tier 3 (-5% breakdowns)"
        }

        st.session_state.referral_tier = st.selectbox(
            "💼 Referral Tier:",
            options=list(referral_options.keys()),
            format_func=lambda x: referral_options[x],
            index=st.session_state.referral_tier,
            help="Referral tiers reduce breakdown probability for ALL trucks in your fleet."
        )

        # Anti-breakdown tool
        st.session_state.use_repair_tool = st.checkbox(
            "🔧 Use anti-breakdown tool",
            value=st.session_state.use_repair_tool,
            help="Reduces breakdown probability by 5% for the first 2 trips. Costs 1 RON per truck."
        )

        if st.button("➕ Add Trucks"):
            for _ in range(quantity):
                st.session_state.fleet.append(selected_rarity)
            st.success(f"{quantity} truck(s) of rarity {selected_rarity} added!")
            st.rerun()

        # Fleet summary
        if st.session_state.fleet:
            st.subheader("📊 Fleet Summary")
            fleet_summary = pd.Series(st.session_state.fleet).value_counts().sort_index()

            for rarity, count in fleet_summary.items():
                st.write(f"**Rarity {rarity}:** {count} truck(s)")

            st.write(f"**Total:** {len(st.session_state.fleet)} trucks")

            # Show active benefits
            benefits = []
            if st.session_state.referral_tier > 0:
                tier_reductions = {1: "-2%", 2: "-3%", 3: "-5%"}
                benefits.append(f"Tier {st.session_state.referral_tier}: {tier_reductions[st.session_state.referral_tier]} breakdowns")

            if st.session_state.use_repair_tool:
                benefits.append("Tool: -5% breakdowns x 2 trips")

            if benefits:
                st.success("**Active benefits:**\n\n" + "\n".join(f"✓ {b}" for b in benefits))

            if st.button("🗑 Clear Fleet"):
                st.session_state.fleet = []
                st.session_state.simulation_results = None
                st.rerun()

    # Main content area
    if not st.session_state.fleet:
        st.info("👆 Add trucks to your fleet using the sidebar to start the simulation.")
        
        # ==============================================================================
        # ========= SECCIÓN DE CÓDIGO CORREGIDA PARA LAS TARJETAS RESPONSIVE ===========
        # ==============================================================================
        
        st.subheader("🚚 Truck Gallery")

        # 1. Definimos el CSS para las tarjetas y el contenedor con scroll
        st.markdown("""
        <style>
        .scroll-container {
            display: flex;
            overflow-x: auto;
            padding-bottom: 20px; /* Espacio para la barra de scroll */
            scrollbar-width: thin; /* Estilo opcional para la barra */
        }
        .card {
            flex: 0 0 220px; /* No se encoge, ancho base de 220px */
            margin-right: 15px;
            border: 2px solid #ddd;
            border-radius: 10px;
            display: flex;
            flex-direction: column;
            background-color: #f8f9fa;
            height: 100%; /* Asegura que todas las tarjetas tengan la misma altura */
        }
        .card-header {
            padding: 15px;
            text-align: center;
            border-bottom: 2px solid #ddd;
        }
        .card-header h4 {
            margin: 0 0 10px 0;
            font-size: 1.1em;
        }
        .card img {
            width: 100%;
            height: auto;
            object-fit: cover;
        }
        .card-body {
            padding: 15px;
            font-size: 0.9em;
            text-align: left;
            flex-grow: 1; /* Permite que esta sección crezca para igualar alturas */
        }
        </style>
        """, unsafe_allow_html=True)

        truck_data = [
            {"name": "Comfort", "rarity": 1, "image": "20250913_124714_1757782671363.jpg", "ron_per_trip": 4, "breakdown_chance": "30%", "fuel_price": "2 $Ron", "engine": "Advanced Diesel"},
            {"name": "Highline", "rarity": 2, "image": "20250913_124802_1757782671385.jpg", "ron_per_trip": 5, "breakdown_chance": "26%", "fuel_price": "2 $Ron", "engine": "Advanced Diesel"},
            {"name": "Shift", "rarity": 3, "image": "20250913_124821_1757782671402.jpg", "ron_per_trip": 7, "breakdown_chance": "20%", "fuel_price": "2 $Ron", "engine": "Advanced Diesel"},
            {"name": "Electric", "rarity": 4, "image": "20250913_124838_1757782671418.jpg", "ron_per_trip": 9, "breakdown_chance": "17%", "fuel_price": "1 $Ron", "engine": "Electric Engine"},
            {"name": "Autonomous", "rarity": 5, "image": "20250913_124853_1757782671434.jpg", "ron_per_trip": 11, "breakdown_chance": "14%", "fuel_price": "1 $Ron", "engine": "Electric Engine"}
        ]

        # 2. Creamos el HTML para las tarjetas dentro del contenedor de scroll
        html_cards = '<div class="scroll-container">'
        for truck in truck_data:
            stars = '⭐' * truck['rarity'] + '⚫' * (5 - truck['rarity'])
            html_cards += """
            <div class="card">
                <div class="card-header">
                    <h4>{truck['name']} (Rarity {truck['rarity']})</h4>
                    <div>{stars}</div>
                </div>
                <img src="{truck['image']}" alt="{truck['name']} Truck">
                <div class="card-body">
                    <strong>RON per trip:</strong> {truck['ron_per_trip']}<br>
                    <strong>Breakdown chance:</strong> {truck['breakdown_chance']}<br>
                    <strong>Fuel Price:</strong> {truck['fuel_price']}<br>
                    <strong>Engine Type:</strong> {truck['engine']}
                </div>
            </div>
            """
        html_cards += '</div>'

        # 3. Mostramos el HTML en Streamlit
        st.markdown(html_cards, unsafe_allow_html=True)
        
        # ==============================================================================
        # ======================= FIN DE LA SECCIÓN CORREGIDA ==========================
        # ==============================================================================

        # Display truck specifications table
        st.subheader("📋 Truck Specifications")
        
        specs_data = {
            'Rarity': [1, 2, 3, 4, 5],
            'RON per trip': [4, 5, 7, 9, 11],
            'Fuel (every 2 trips)': [2, 2, 2, 1, 1],
            'Tires (every 4 trips)': [4, 4, 4, 4, 4],
            'Repair cost': [6, 6, 6, 10, 10],
            'Breakdown probability (%)': [30, 26, 20, 17, 14]
        }
        
        st.info("💡 **Available benefits:**\n\n"
                "• **Referral tier**: Permanently reduces breakdowns for entire fleet\n"
                "• **Anti-breakdown tool**: Reduces breakdown 5% for 2 trips (costs 1 RON/truck)")
        
        specs_df = pd.DataFrame(specs_data)
        st.dataframe(specs_df, use_container_width=True)

    else:
        # Simulation parameters
        col1, col2 = st.columns([1, 2])

        with col1:
            st.subheader("⚙ Simulation Parameters")
            
            time_period = st.selectbox(
                "Simulation period:",
                options=['1_week', '30_days', '1_year'],
                format_func=lambda x: {
                    '1_week': '1 Week (7 days)',
                    '30_days': '30 Days (1 month)',
                    '1_year': '1 Year (365 days)'
                }[x]
            )

            st.write("**Iterations:** 10,000")
            st.write("**Trips every:** 12 hours")

            if st.button("🎲 Run Monte Carlo Simulation", type="primary"):
                with st.spinner("Running simulation..."):
                    # NOTE: The simulation classes need to be defined or imported for this to run
                    # For now, this part will error out unless you have the files.
                    try:
                        simulator = MonteCarloSimulation(st.session_state.fleet, st.session_state.use_repair_tool, st.session_state.referral_tier)
                        results = simulator.run_simulation(time_period, iterations=10000)
                        st.session_state.simulation_results = results

                        if st.session_state.use_repair_tool or st.session_state.referral_tier > 0:
                            st.text("Running comparative simulation without benefits...")
                            simulator_baseline = MonteCarloSimulation(st.session_state.fleet, use_repair_tool=False, referral_tier=0)
                            results_baseline = simulator_baseline.run_simulation(time_period, iterations=10000)
                            st.session_state.simulation_results['comparison_baseline'] = results_baseline
                        st.success("Simulation completed!")
                    except NameError:
                        st.error("Simulation classes (e.g., MonteCarloSimulation) are not defined. Please ensure they are imported correctly.")
                    except Exception as e:
                        st.error(f"An error occurred during simulation: {e}")
                
                if st.session_state.simulation_results:
                    st.rerun()

        with col2:
            st.subheader("🚚 Your Current Fleet")
            fleet_df = pd.DataFrame({
                'Truck': [f"Truck {i+1}" for i in range(len(st.session_state.fleet))],
                'Rarity': st.session_state.fleet
            })
            st.dataframe(fleet_df, use_container_width=True)

    # Display results
    if st.session_state.simulation_results:
        results = st.session_state.simulation_results
        
        st.header("📈 Simulation Results")

        # Summary statistics
        if 'comparison_baseline' in results and (st.session_state.use_repair_tool or st.session_state.referral_tier > 0):
            st.subheader("🆚️ Comparison: With vs Without Benefits")
            comparison = results['comparison_baseline']
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                diff_profit = results['mean_profit'] - comparison['mean_profit']
                st.metric("💰 Average Profit", f"{results['mean_profit']:.2f} RON", delta=f"{diff_profit:+.2f} RON")
            with col2:
                diff_max = results['max_profit'] - comparison['max_profit']
                st.metric("📈 Maximum Profit", f"{results['max_profit']:.2f} RON", delta=f"{diff_max:+.2f} RON")
            with col3:
                diff_min = results['min_profit'] - comparison['min_profit']
                st.metric("📉 Minimum Profit", f"{results['min_profit']:.2f} RON", delta=f"{diff_min:+.2f} RON")
            with col4:
                diff_prob = results['positive_probability'] - comparison['positive_probability']
                st.metric("🎯 Positive Profit Probability", f"{results['positive_probability']:.1f}%", delta=f"{diff_prob:+.1f}%")
        else:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("💰 Average Profit", f"{results['mean_profit']:.2f} RON", delta=f"±{results['std_profit']:.2f}")
            with col2:
                st.metric("📈 Maximum Profit", f"{results['max_profit']:.2f} RON")
            with col3:
                st.metric("📉 Minimum Profit", f"{results['min_profit']:.2f} RON")
            with col4:
                st.metric("🎲 Positive Profit Probability", f"{results['positive_probability']:.1f}%")

        # Charts and further analysis would go here...
        # (El resto del código de visualización de resultados permanece igual)


if __name__ == "__main__":
    # NOTE: You need to define or import TruckSimulator and MonteCarloSimulation classes
    # for the simulation logic to work. The following are placeholder classes to make the app runnable.
    
    class TruckSimulator:
        def __init__(self, fleet, use_repair_tool, referral_tier):
            self.fleet = fleet
            self.use_repair_tool = use_repair_tool
            self.referral_tier = referral_tier
        
        def simulate_period(self, period):
            # Dummy simulation logic
            import random
            base_profit = sum(rarity * 10 for rarity in self.fleet)
            random_factor = random.uniform(0.5, 1.5)
            return {"total_profit": base_profit * random_factor, "rarity_breakdown": {}}

    class MonteCarloSimulation:
        def __init__(self, fleet, use_repair_tool, referral_tier):
            self.fleet = fleet
            self.use_repair_tool = use_repair_tool
            self.referral_tier = referral_tier

        def run_simulation(self, time_period, iterations=10000):
            # Dummy simulation results
            import numpy as np
            profits = np.random.normal(loc=sum(self.fleet) * 20, scale=sum(self.fleet) * 5, size=iterations)
            if self.use_repair_tool: profits += 10
            if self.referral_tier > 0: profits += self.referral_tier * 5
            
            return {
                'mean_profit': np.mean(profits),
                'std_profit': np.std(profits),
                'min_profit': np.min(profits),
                'max_profit': np.max(profits),
                'positive_probability': (np.sum(profits > 0) / iterations) * 100,
                'all_profits': profits,
                'rarity_breakdown': {} # Populate with real data if needed
            }

    main()
