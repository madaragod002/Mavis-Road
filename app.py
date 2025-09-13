import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from truck_simulator import TruckSimulator
from monte_carlo import MonteCarloSimulation

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
    🚚 Mavis Road - Profit Simulator
    💎 Support the Creator!
    Use my referral code in the game:
    """, unsafe_allow_html=True)
    
    # Copy referral code section
    import streamlit.components.v1 as components

    st.markdown("### 📋 Copy Referral Code")
    col1, col2 = st.columns([2, 1])

    with col1:
        st.text_input("Referral Code", value="7FB951B1", disabled=False, help="Select all text and copy (Ctrl+C)", label_visibility="collapsed")

    with col2:
        # JavaScript copy button that works reliably
        copy_button = components.html("""
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
                document.getElementById('status').innerHTML = '❌ Copy failed - use manual copy';
                document.getElementById('status').style.color = 'red';
                console.error('Could not copy text: ', err);
            });
        }
        </script>
        """, height=80)

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
                benefits.append(f"💼 Tier {st.session_state.referral_tier}: {tier_reductions[st.session_state.referral_tier]} breakdowns")

            if st.session_state.use_repair_tool:
                benefits.append("🔧 Tool: -5% breakdowns x 2 trips (+1 RON/truck)")

            if benefits:
                st.success("**Active benefits:**\n\n" + "\n".join(f" {b}" for b in benefits)) # Changed icon for clarity

            if st.button("🗑 Clear Fleet"):
                st.session_state.fleet = []
                st.session_state.simulation_results = None
                st.rerun()

    # Main content area
    if not st.session_state.fleet:
        st.info("👆 Add trucks to your fleet using the sidebar to start the simulation.")

        # ==============================================================================
        # ========= INICIO DE LA SECCIÓN DE CÓDIGO CORREGIDA Y REVISADA ==================
        # ==============================================================================
        
        st.subheader("🚚 Truck Gallery")

        # 1. Definir el CSS para las tarjetas y el contenedor con scroll
        css_style = """
        <style>
            .scroll-container {
                display: flex;
                overflow-x: auto;
                padding-bottom: 20px;
                scrollbar-width: thin;
            }
            .card {
                flex: 0 0 220px;
                margin-right: 15px;
                border: 2px solid #ddd;
                border-radius: 10px;
                display: flex;
                flex-direction: column;
                background-color: #f8f9fa;
            }
            .card-header {
                padding: 15px;
                text-align: center;
            }
            .card-header h4 {
                margin: 0 0 10px 0;
                font-size: 1.1em;
            }
            .card img {
                width: 100%;
                height: 150px; /* Altura fija para la imagen */
                object-fit: cover; /* Asegura que la imagen cubra el espacio sin deformarse */
            }
            .card-body {
                padding: 15px;
                font-size: 0.9em;
                text-align: left;
                flex-grow: 1;
            }
        </style>
        """
        st.markdown(css_style, unsafe_allow_html=True)

        truck_data = [
            {"name": "Comfort", "rarity": 1, "image": "20250913_124714_1757782671363.jpg", "ron_per_trip": 4, "breakdown_chance": "30%", "fuel_price": "2 $Ron", "engine": "Advanced Diesel"},
            {"name": "Highline", "rarity": 2, "image": "20250913_124802_1757782671385.jpg", "ron_per_trip": 5, "breakdown_chance": "26%", "fuel_price": "2 $Ron", "engine": "Advanced Diesel"},
            {"name": "Shift", "rarity": 3, "image": "20250913_124821_1757782671402.jpg", "ron_per_trip": 7, "breakdown_chance": "20%", "fuel_price": "2 $Ron", "engine": "Advanced Diesel"},
            {"name": "Electric", "rarity": 4, "image": "20250913_124838_1757782671418.jpg", "ron_per_trip": 9, "breakdown_chance": "17%", "fuel_price": "1 $Ron", "engine": "Electric Engine"},
            {"name": "Autonomous", "rarity": 5, "image": "20250913_124853_1757782671434.jpg", "ron_per_trip": 11, "breakdown_chance": "14%", "fuel_price": "1 $Ron", "engine": "Electric Engine"}
        ]

        # 2. Construir el HTML de las tarjetas usando concatenación de strings para evitar errores
        html_cards = '<div class="scroll-container">'
        for truck in truck_data:
            stars = '⭐' * truck['rarity'] + '⚫' * (5 - truck['rarity'])
            
            # Usamos el método .format() que es más seguro para este caso
            card_html = (
                '<div class="card">'
                '  <div class="card-header">'
                '    <h4>{name} (Rarity {rarity})</h4>'
                '    <div>{stars}</div>'
                '  </div>'
                '  <img src="{image}" alt="{name} Truck">'
                '  <div class="card-body">'
                '    <strong>RON per trip:</strong> {ron_per_trip}<br>'
                '    <strong>Breakdown chance:</strong> {breakdown_chance}<br>'
                '    <strong>Fuel Price:</strong> {fuel_price}<br>'
                '    <strong>Engine Type:</strong> {engine}'
                '  </div>'
                '</div>'
            ).format(
                name=truck['name'],
                rarity=truck['rarity'],
                stars=stars,
                image=truck['image'],
                ron_per_trip=truck['ron_per_trip'],
                breakdown_chance=truck['breakdown_chance'],
                fuel_price=truck['fuel_price'],
                engine=truck['engine']
            )
            html_cards += card_html
        
        html_cards += '</div>'

        # 3. Mostrar el HTML final en Streamlit
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
                    # Execute main simulation
                    simulator = MonteCarloSimulation(st.session_state.fleet, st.session_state.use_repair_tool, st.session_state.referral_tier)
                    results = simulator.run_simulation(time_period, iterations=10000)
                    st.session_state.simulation_results = results

                    # If benefits are active, run comparative simulation without benefits
                    if st.session_state.use_repair_tool or st.session_state.referral_tier > 0:
                        st.text("Running comparative simulation without benefits...")
                        simulator_baseline = MonteCarloSimulation(st.session_state.fleet, use_repair_tool=False, referral_tier=0)
                        results_baseline = simulator_baseline.run_simulation(time_period, iterations=10000)
                        st.session_state.simulation_results['comparison_baseline'] = results_baseline

                st.success("Simulation completed!")
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

        # El resto del código para mostrar los resultados no necesita cambios
        # y se mantiene tal como lo proporcionaste.
        # ... (Tu código de visualización de resultados) ...

# Este bloque final es para asegurar que el script se ejecute
if __name__ == "__main__":
    main()
