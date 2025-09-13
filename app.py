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
    page_icon="馃殯",
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
    <div style="background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 50%, #1e40af 100%); 
                padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
        <h1 style="color: white; font-size: 2.5em; margin: 0;">🚚 Mavis Road - Profit Simulator</h1>
        <h2 style="color: #fbbf24; font-size: 1.5em; margin: 10px 0;">💎 Support the Creator!</h2>
        <p style="color: white; font-size: 1.2em; margin: 10px 0;">Use my referral code in the game:</p>
        <div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 5px; margin: 10px auto; width: fit-content;">
            <span style="color: #fbbf24; font-size: 1.8em; font-weight: bold; font-family: monospace;">7FB951B1</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Copy referral code section
    import streamlit.components.v1 as components
    
    st.markdown("### 📋 Copy Referral Code")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.text_input("Referral Code", value="7FB951B1", disabled=False, help="Select all text and copy (Ctrl+C)")
    
    with col2:
        # JavaScript copy button that works reliably
        copy_button = components.html("""
        <div style="padding: 10px;">
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
                st.success("**Active benefits:**\n\n" + "\n".join(f"💼 {b}" for b in benefits))
            
            if st.button("🗑 Clear Fleet"):
                st.session_state.fleet = []
                st.session_state.simulation_results = None
                st.rerun()
    
    # Main content area
    if not st.session_state.fleet:
        st.info("👆 Add trucks to your fleet using the sidebar to start the simulation.")
        
        # Display truck cards with images
        st.subheader("🚚 Truck Gallery")
        
        # Create truck cards
        cols = st.columns(5)
        
        truck_data = [
            {
                "name": "Comfort",
                "rarity": 1,
                #"image": "20250913_124714_1757782671363.jpg",
                "ron_per_trip": 4,
                "breakdown_chance": "30%",
                "fuel_price": "2 $Ron",
                "engine": "Advanced Diesel"
            },
            {
                "name": "Highline", 
                "rarity": 2,
               # "image": "20250913_124802_1757782671385.jpg",
                "ron_per_trip": 5,
                "breakdown_chance": "26%",
                "fuel_price": "2 $Ron",
                "engine": "Advanced Diesel"
            },
            {
                "name": "Shift",
                "rarity": 3, 
               # "image": "20250913_124821_1757782671402.jpg",
                "ron_per_trip": 7,
                "breakdown_chance": "20%",
                "fuel_price": "2 $Ron",
                "engine": "Advanced Diesel"
            },
            {
                "name": "Electric",
                "rarity": 4,
                #"image": "20250913_124838_1757782671418.jpg", 
                "ron_per_trip": 9,
                "breakdown_chance": "17%",
                "fuel_price": "1 $Ron",
                "engine": "Electric Engine"
            },
            {
                "name": "Autonomous",
                "rarity": 5,
               # "image": "20250913_124853_1757782671434.jpg",
                "ron_per_trip": 11,
                "breakdown_chance": "14%", 
                "fuel_price": "1 $Ron",
                "engine": "Electric Engine"
            }
        ]
        
        for i, truck in enumerate(truck_data):
            with cols[i]:
                # Card header and stars
                st.markdown(f"""
                <div style="border: 2px solid #ddd; border-radius: 10px 10px 0 0; padding: 15px 15px 5px 15px; text-align: center; background: #f8f9fa;">
                    <h4 style="margin: 0;">{truck['name']} (Rarity {truck['rarity']})</h4>
                    <div style="margin: 10px 0;">
                        {'猸�' * truck['rarity']}{'鈽�' * (5 - truck['rarity'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Truck image
                try:
                    st.image(truck['image'], width=200, caption=f"{truck['name']} Truck")
                except:
                    st.error(f"Could not load image for {truck['name']}")
                
                # Card footer with specs
                st.markdown(f"""
                <div style="border: 2px solid #ddd; border-top: none; border-radius: 0 0 10px 10px; padding: 10px 15px; font-size: 0.9em; text-align: left;">
                    <strong>RON per trip:</strong> {truck['ron_per_trip']}<br>
                    <strong>Breakdown chance:</strong> {truck['breakdown_chance']}<br>
                    <strong>Fuel Price:</strong> {truck['fuel_price']}<br>
                    <strong>Engine Type:</strong> {truck['engine']}
                </div>
                """, unsafe_allow_html=True)
        
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
        
        # Summary statistics
        if 'comparison_baseline' in results and (st.session_state.use_repair_tool or st.session_state.referral_tier > 0):
            st.subheader("🆚️ Comparison: With vs Without Benefits")
            
            comparison = results['comparison_baseline']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                diff_profit = results['mean_profit'] - comparison['mean_profit']
                st.metric(
                    "💰 Average Profit",
                    f"{results['mean_profit']:.2f} RON",
                    delta=f"{diff_profit:+.2f} RON vs without benefits"
                )
            
            with col2:
                diff_max = results['max_profit'] - comparison['max_profit']
                st.metric(
                    "📈 Maximum Profit",
                    f"{results['max_profit']:.2f} RON",
                    delta=f"{diff_max:+.2f} RON"
                )
            
            with col3:
                diff_min = results['min_profit'] - comparison['min_profit']
                st.metric(
                    "📉 Minimum Profit",
                    f"{results['min_profit']:.2f} RON",
                    delta=f"{diff_min:+.2f} RON"
                )
            
            with col4:
                diff_prob = results['positive_probability'] - comparison['positive_probability']
                st.metric(
                    "🎯 Positive Profit Probability",
                    f"{results['positive_probability']:.1f}%",
                    delta=f"{diff_prob:+.1f}%"
                )
        else:
            # Show normal statistics if no comparison
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    " Average Profit",
                    f"{results['mean_profit']:.2f} RON",
                    delta=f"卤{results['std_profit']:.2f}"
                )
            
            with col2:
                st.metric(
                    "📈 Maximum Profit",
                    f"{results['max_profit']:.2f} RON"
                )
            
            with col3:
                st.metric(
                    "📉 Minimum Profit",
                    f"{results['min_profit']:.2f} RON"
                )
            
            with col4:
                st.metric(
                    "🎲 Positive Profit Probability",
                    f"{results['positive_probability']:.1f}%"
                )
        
        # Charts
        if 'comparison_baseline' in results and (st.session_state.use_repair_tool or st.session_state.referral_tier > 0):
            # Comparative charts
            st.subheader(" Comparative Charts")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Comparative histogram
                fig_hist_comp = go.Figure()
                
                # Data with benefits
                fig_hist_comp.add_trace(go.Histogram(
                    x=results['all_profits'],
                    name="With benefits",
                    opacity=0.7,
                    nbinsx=30,
                    histnorm='probability'
                ))
                
                # Data without benefits
                fig_hist_comp.add_trace(go.Histogram(
                    x=results['comparison_baseline']['all_profits'],
                    name="Without benefits",
                    opacity=0.7,
                    nbinsx=30,
                    histnorm='probability'
                ))
                
                fig_hist_comp.update_layout(
                    title="Comparison: Profit Distribution",
                    xaxis_title="Profit (RON)",
                    yaxis_title="Probability",
                    barmode='overlay'
                )
                
                st.plotly_chart(fig_hist_comp, use_container_width=True)
            
            with col2:
                # Box plot comparativo
                fig_box_comp = go.Figure()
                
                fig_box_comp.add_trace(go.Box(
                    y=results['all_profits'],
                    name="With benefits",
                    boxpoints="outliers"
                ))
                
                fig_box_comp.add_trace(go.Box(
                    y=results['comparison_baseline']['all_profits'],
                    name="Without benefits",
                    boxpoints="outliers"
                ))
                
                fig_box_comp.update_layout(
                    title="Comparison: Distribution Analysis",
                    yaxis_title="Profit (RON)"
                )
                
                st.plotly_chart(fig_box_comp, use_container_width=True)
        
        else:
            # Normal charts if no comparison
            col1, col2 = st.columns(2)
            
            with col1:
                # Profit distribution histogram
                fig_hist = px.histogram(
                    x=results['all_profits'],
                    nbins=50,
                    title="Profit Distribution",
                    labels={'x': 'Profit (RON)', 'y': 'Frequency'}
                )
                fig_hist.add_vline(
                    x=results['mean_profit'],
                    line_dash="dash",
                    line_color="red",
                    annotation_text="Average"
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col2:
                # Box plot
                fig_box = go.Figure()
                fig_box.add_trace(go.Box(
                    y=results['all_profits'],
                    name="Profit Distribution",
                    boxpoints="outliers"
                ))
                fig_box.update_layout(
                    title="Distribution Analysis",
                    yaxis_title="Profit (RON)"
                )
                st.plotly_chart(fig_box, use_container_width=True)
        
        # Detailed breakdown by truck rarity
        if 'rarity_breakdown' in results:
            st.subheader("📊 Analysis by Truck Rarity")
            
            breakdown_data = []
            for rarity, data in results['rarity_breakdown'].items():
                breakdown_data.append({
                    'Rarity': rarity,
                    'Count': data['count'],
                    'Average Profit': data['avg_profit'],
                    'Total Profit': data['total_profit'],
                    'Average Trips': data['avg_trips'],
                    'Average Repairs': data['avg_repairs']
                })
            
            breakdown_df = pd.DataFrame(breakdown_data)
            st.dataframe(breakdown_df, use_container_width=True)
            
            # Profitability chart by rarity
            fig_profit = px.bar(
                breakdown_df,
                x='Rarity',
                y='Total Profit',
                title="Total Profit by Rarity",
                labels={'Total Profit': 'Total Profit (RON)'}
            )
            st.plotly_chart(fig_profit, use_container_width=True)
            
            # Show benefits effectiveness if comparison exists
            if 'comparison_baseline' in results and (st.session_state.use_repair_tool or st.session_state.referral_tier > 0):
                st.subheader(" Benefits Effectiveness")
                
                comparison = results['comparison_baseline']
                tool_cost = len(st.session_state.fleet) * 1 if st.session_state.use_repair_tool else 0  # 1 RON por cami贸n
                
                # Calculate active benefits
                benefits_text = []
                if st.session_state.referral_tier > 0:
                    tier_reductions = {1: "2%", 2: "3%", 3: "5%"}
                    benefits_text.append(f"Tier {st.session_state.referral_tier}: -{tier_reductions[st.session_state.referral_tier]} permanent breakdown reduction")
                if st.session_state.use_repair_tool:
                    benefits_text.append("Tool: -5% breakdowns x 2 trips")
                
                effectiveness_data = {
                    'Metric': [
                        'Tool investment (RON)',
                        'Average profit improvement (RON)',
                        'Return on investment (%)',
                        'Active benefits',
                        'Positive profit probability improvement'
                    ],
                    'Value': [
                        f"{tool_cost}",
                        f"{results['mean_profit'] - comparison['mean_profit']:.2f}",
                        f"{((results['mean_profit'] - comparison['mean_profit']) / tool_cost * 100):.1f}%" if tool_cost > 0 else "Free" if len(benefits_text) > 0 else "N/A",
                        "; ".join(benefits_text) if benefits_text else "None",
                        f"{results['positive_probability'] - comparison['positive_probability']:.1f}%"
                    ]
                }
                
                effectiveness_df = pd.DataFrame(effectiveness_data)
                st.dataframe(effectiveness_df, use_container_width=True)
        
        # Download results
        st.subheader("💾 Download Results")
        
        # Prepare data for download
        if 'comparison_baseline' in results and (st.session_state.use_repair_tool or st.session_state.referral_tier > 0):
            # Comparative data
            comparison = results['comparison_baseline']
            results_summary = pd.DataFrame({
                'Metric': [
                    'Average Profit (With benefits)',
                    'Average Profit (Without benefits)',
                    'Average Profit Difference',
                    'Maximum Profit (With benefits)',
                    'Maximum Profit (Without benefits)',
                    'Positive Profit Probability (With benefits)',
                    'Positive Profit Probability (Without benefits)',
                    'Probability Improvement',
                    'Tool Cost',
                    'Total ROI (%)'
                ],
                'Value': [
                    f"{results['mean_profit']:.2f} RON",
                    f"{comparison['mean_profit']:.2f} RON",
                    f"{results['mean_profit'] - comparison['mean_profit']:.2f} RON",
                    f"{results['max_profit']:.2f} RON",
                    f"{comparison['max_profit']:.2f} RON",
                    f"{results['positive_probability']:.2f}%",
                    f"{comparison['positive_probability']:.2f}%",
                    f"{results['positive_probability'] - comparison['positive_probability']:.2f}%",
                    f"{len(st.session_state.fleet) if st.session_state.use_repair_tool else 0} RON",
                    f"{((results['mean_profit'] - comparison['mean_profit']) / max(len(st.session_state.fleet) if st.session_state.use_repair_tool else 1, 1) * 100):.1f}%"
                ]
            })
        else:
            # Normal data
            results_summary = pd.DataFrame({
                'Metric': [
                    'Average Profit',
                    'Standard Deviation',
                    'Minimum Profit',
                    'Maximum Profit',
                    'Positive Profit Probability (%)'
                ],
                'Value': [
                    f"{results['mean_profit']:.2f} RON",
                    f"{results['std_profit']:.2f} RON",
                    f"{results['min_profit']:.2f} RON",
                    f"{results['max_profit']:.2f} RON",
                    f"{results['positive_probability']:.2f}%"
                ]
            })
        
        csv = results_summary.to_csv(index=False)
        st.download_button(
            label="📥 Download Summary CSV",
            data=csv,
            file_name="mavis_road_simulation_results.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
