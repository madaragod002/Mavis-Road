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
    page_icon="🚛",
    layout="wide"
)

# Initialize session state
if 'fleet' not in st.session_state:
    st.session_state.fleet = []

if 'simulation_results' not in st.session_state:
    st.session_state.simulation_results = None
    
if 'use_repair_tool' not in st.session_state:
    st.session_state.use_repair_tool = False

def main():
    st.title("🚛 Mavis Road - Simulador Monte Carlo")
    st.markdown("### Herramienta de simulación de ganancias mensuales")
    
    # Sidebar for truck management
    with st.sidebar:
        st.header("🔧 Gestión de Flota")
        
        # Truck rarity selection
        rarity_options = {
            1: "Rareza 1 (4 RON/viaje)",
            2: "Rareza 2 (5 RON/viaje)",
            3: "Rareza 3 (7 RON/viaje)",
            4: "Rareza 4 (9 RON/viaje)",
            5: "Rareza 5 (11 RON/viaje)"
        }
        
        selected_rarity = st.selectbox(
            "Seleccionar tipo de camión:",
            options=list(rarity_options.keys()),
            format_func=lambda x: rarity_options[x]
        )
        
        quantity = st.number_input(
            "Cantidad a agregar:",
            min_value=1,
            max_value=100,
            value=1
        )
        
        # Herramienta de reducción de averías
        st.session_state.use_repair_tool = st.checkbox(
            "🔧 Usar herramienta anti-averías",
            value=st.session_state.use_repair_tool,
            help="Reduce la probabilidad de avería en 5% durante los primeros 2 viajes. Cuesta 1 RON por camión."
        )
        
        if st.button("➕ Agregar Camiones"):
            for _ in range(quantity):
                st.session_state.fleet.append(selected_rarity)
            st.success(f"¡{quantity} camión(es) de rareza {selected_rarity} agregado(s)!")
            st.rerun()
        
        # Fleet summary
        if st.session_state.fleet:
            st.subheader("📊 Resumen de Flota")
            fleet_summary = pd.Series(st.session_state.fleet).value_counts().sort_index()
            
            for rarity, count in fleet_summary.items():
                st.write(f"**Rareza {rarity}:** {count} camión(es)")
            
            st.write(f"**Total:** {len(st.session_state.fleet)} camiones")
            
            if st.session_state.use_repair_tool:
                st.info("🔧 Herramienta anti-averías activa\n\n• Reduce avería 5% x 2 viajes\n• Costo: 1 RON por camión")
            
            if st.button("🗑️ Limpiar Flota"):
                st.session_state.fleet = []
                st.session_state.simulation_results = None
                st.rerun()
    
    # Main content area
    if not st.session_state.fleet:
        st.info("👆 Agrega camiones a tu flota usando el panel lateral para comenzar la simulación.")
        
        # Display truck specifications
        st.subheader("📋 Especificaciones de Camiones")
        
        specs_data = {
            'Rareza': [1, 2, 3, 4, 5],
            'RON por viaje': [4, 5, 7, 9, 11],
            'Gasolina (cada 2 viajes)': [2, 2, 2, 1, 1],
            'Gomas (cada 4 viajes)': [4, 4, 4, 4, 4],
            'Costo reparación': [6, 6, 6, 10, 10],
            'Probabilidad avería (%)': [30, 26, 20, 17, 14]
        }
        
        st.info("💡 **Nueva herramienta disponible**: Herramienta anti-averías\n\n"
                "Reduce la probabilidad de avería en 5% durante los primeros 2 viajes.\n"
                "Costo: 1 RON por camión. Activa la opción al agregar camiones a tu flota.")
        
        specs_df = pd.DataFrame(specs_data)
        st.dataframe(specs_df, use_container_width=True)
        
    else:
        # Simulation parameters
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("⚙️ Parámetros de Simulación")
            
            time_period = st.selectbox(
                "Período de simulación:",
                options=['1_week', '30_days', '1_year'],
                format_func=lambda x: {
                    '1_week': '1 Semana (7 días)',
                    '30_days': '30 Días (1 mes)',
                    '1_year': '1 Año (365 días)'
                }[x]
            )
            
            st.write("**Iteraciones:** 10,000")
            st.write("**Viajes cada:** 12 horas")
            
            if st.button("🎲 Ejecutar Simulación Monte Carlo", type="primary"):
                with st.spinner("Ejecutando simulación..."):
                    # Ejecutar simulación principal
                    simulator = MonteCarloSimulation(st.session_state.fleet, st.session_state.use_repair_tool)
                    results = simulator.run_simulation(time_period, iterations=10000)
                    st.session_state.simulation_results = results
                    
                    # Si se usa herramienta, ejecutar simulación comparativa sin herramienta
                    if st.session_state.use_repair_tool:
                        st.text("Ejecutando simulación comparativa sin herramienta...")
                        simulator_no_tool = MonteCarloSimulation(st.session_state.fleet, use_repair_tool=False)
                        results_no_tool = simulator_no_tool.run_simulation(time_period, iterations=10000)
                        st.session_state.simulation_results['comparison_no_tool'] = results_no_tool
                
                st.success("¡Simulación completada!")
                st.rerun()
        
        with col2:
            st.subheader("🚛 Tu Flota Actual")
            fleet_df = pd.DataFrame({
                'Camión': [f"Camión {i+1}" for i in range(len(st.session_state.fleet))],
                'Rareza': st.session_state.fleet
            })
            st.dataframe(fleet_df, use_container_width=True)
    
    # Display results
    if st.session_state.simulation_results:
        results = st.session_state.simulation_results
        
        st.header("📈 Resultados de la Simulación")
        
        # Summary statistics
        if 'comparison_no_tool' in results and st.session_state.use_repair_tool:
            st.subheader("🔧 Comparación: Con vs Sin Herramienta")
            
            comparison = results['comparison_no_tool']
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                diff_profit = results['mean_profit'] - comparison['mean_profit']
                st.metric(
                    "💰 Ganancia Promedio",
                    f"{results['mean_profit']:.2f} RON",
                    delta=f"{diff_profit:+.2f} RON vs sin herramienta"
                )
            
            with col2:
                diff_max = results['max_profit'] - comparison['max_profit']
                st.metric(
                    "📈 Ganancia Máxima",
                    f"{results['max_profit']:.2f} RON",
                    delta=f"{diff_max:+.2f} RON"
                )
            
            with col3:
                diff_min = results['min_profit'] - comparison['min_profit']
                st.metric(
                    "📉 Ganancia Mínima",
                    f"{results['min_profit']:.2f} RON",
                    delta=f"{diff_min:+.2f} RON"
                )
            
            with col4:
                diff_prob = results['positive_probability'] - comparison['positive_probability']
                st.metric(
                    "🎯 Probabilidad Ganancia +",
                    f"{results['positive_probability']:.1f}%",
                    delta=f"{diff_prob:+.1f}%"
                )
        else:
            # Mostrar estadísticas normales si no hay comparación
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "💰 Ganancia Promedio",
                    f"{results['mean_profit']:.2f} RON",
                    delta=f"±{results['std_profit']:.2f}"
                )
            
            with col2:
                st.metric(
                    "📈 Ganancia Máxima",
                    f"{results['max_profit']:.2f} RON"
                )
            
            with col3:
                st.metric(
                    "📉 Ganancia Mínima",
                    f"{results['min_profit']:.2f} RON"
                )
            
            with col4:
                st.metric(
                    "🎯 Probabilidad Ganancia +",
                    f"{results['positive_probability']:.1f}%"
                )
        
        # Charts
        if 'comparison_no_tool' in results and st.session_state.use_repair_tool:
            # Gráficas comparativas
            st.subheader("📈 Gráficas Comparativas")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Histograma comparativo
                fig_hist_comp = go.Figure()
                
                # Datos con herramienta
                fig_hist_comp.add_trace(go.Histogram(
                    x=results['all_profits'],
                    name="Con herramienta",
                    opacity=0.7,
                    nbinsx=30,
                    histnorm='probability'
                ))
                
                # Datos sin herramienta
                fig_hist_comp.add_trace(go.Histogram(
                    x=results['comparison_no_tool']['all_profits'],
                    name="Sin herramienta",
                    opacity=0.7,
                    nbinsx=30,
                    histnorm='probability'
                ))
                
                fig_hist_comp.update_layout(
                    title="Comparación: Distribución de Ganancias",
                    xaxis_title="Ganancia (RON)",
                    yaxis_title="Probabilidad",
                    barmode='overlay'
                )
                
                st.plotly_chart(fig_hist_comp, use_container_width=True)
            
            with col2:
                # Box plot comparativo
                fig_box_comp = go.Figure()
                
                fig_box_comp.add_trace(go.Box(
                    y=results['all_profits'],
                    name="Con herramienta",
                    boxpoints="outliers"
                ))
                
                fig_box_comp.add_trace(go.Box(
                    y=results['comparison_no_tool']['all_profits'],
                    name="Sin herramienta",
                    boxpoints="outliers"
                ))
                
                fig_box_comp.update_layout(
                    title="Comparación: Análisis de Distribución",
                    yaxis_title="Ganancia (RON)"
                )
                
                st.plotly_chart(fig_box_comp, use_container_width=True)
        
        else:
            # Gráficas normales si no hay comparación
            col1, col2 = st.columns(2)
            
            with col1:
                # Profit distribution histogram
                fig_hist = px.histogram(
                    x=results['all_profits'],
                    nbins=50,
                    title="Distribución de Ganancias",
                    labels={'x': 'Ganancia (RON)', 'y': 'Frecuencia'}
                )
                fig_hist.add_vline(
                    x=results['mean_profit'],
                    line_dash="dash",
                    line_color="red",
                    annotation_text="Promedio"
                )
                st.plotly_chart(fig_hist, use_container_width=True)
            
            with col2:
                # Box plot
                fig_box = go.Figure()
                fig_box.add_trace(go.Box(
                    y=results['all_profits'],
                    name="Distribución de Ganancias",
                    boxpoints="outliers"
                ))
                fig_box.update_layout(
                    title="Análisis de Distribución",
                    yaxis_title="Ganancia (RON)"
                )
                st.plotly_chart(fig_box, use_container_width=True)
        
        # Detailed breakdown by truck rarity
        if 'rarity_breakdown' in results:
            st.subheader("📊 Análisis por Rareza de Camión")
            
            breakdown_data = []
            for rarity, data in results['rarity_breakdown'].items():
                breakdown_data.append({
                    'Rareza': rarity,
                    'Cantidad': data['count'],
                    'Ganancia Promedio': data['avg_profit'],
                    'Ganancia Total': data['total_profit'],
                    'Viajes Promedio': data['avg_trips'],
                    'Reparaciones Promedio': data['avg_repairs']
                })
            
            breakdown_df = pd.DataFrame(breakdown_data)
            st.dataframe(breakdown_df, use_container_width=True)
            
            # Profitability chart by rarity
            fig_profit = px.bar(
                breakdown_df,
                x='Rareza',
                y='Ganancia Total',
                title="Ganancia Total por Rareza",
                labels={'Ganancia Total': 'Ganancia Total (RON)'}
            )
            st.plotly_chart(fig_profit, use_container_width=True)
            
            # Mostrar efectividad de la herramienta si hay comparación
            if 'comparison_no_tool' in results and st.session_state.use_repair_tool:
                st.subheader("🔧 Efectividad de la Herramienta")
                
                comparison = results['comparison_no_tool']
                tool_cost = len(st.session_state.fleet) * 1  # 1 RON por camión
                
                effectiveness_data = {
                    'Métrica': [
                        'Inversión en herramienta (RON)',
                        'Mejora en ganancia promedio (RON)',
                        'Retorno de inversión (%)',
                        'Reducción en reparaciones promedio',
                        'Mejora en probabilidad de ganancia (+)'
                    ],
                    'Valor': [
                        f"{tool_cost}",
                        f"{results['mean_profit'] - comparison['mean_profit']:.2f}",
                        f"{((results['mean_profit'] - comparison['mean_profit']) / tool_cost * 100):.1f}%" if tool_cost > 0 else "N/A",
                        "~5% por 2 viajes por camión",
                        f"{results['positive_probability'] - comparison['positive_probability']:.1f}%"
                    ]
                }
                
                effectiveness_df = pd.DataFrame(effectiveness_data)
                st.dataframe(effectiveness_df, use_container_width=True)
        
        # Download results
        st.subheader("💾 Descargar Resultados")
        
        # Prepare data for download
        if 'comparison_no_tool' in results and st.session_state.use_repair_tool:
            # Datos comparativos
            comparison = results['comparison_no_tool']
            results_summary = pd.DataFrame({
                'Métrica': [
                    'Ganancia Promedio (Con herramienta)',
                    'Ganancia Promedio (Sin herramienta)',
                    'Diferencia en Ganancia Promedio',
                    'Ganancia Máxima (Con herramienta)',
                    'Ganancia Máxima (Sin herramienta)',
                    'Probabilidad Ganancia + (Con herramienta)',
                    'Probabilidad Ganancia + (Sin herramienta)',
                    'Mejora en Probabilidad',
                    'Costo de Herramienta',
                    'ROI de Herramienta (%)'
                ],
                'Valor': [
                    f"{results['mean_profit']:.2f} RON",
                    f"{comparison['mean_profit']:.2f} RON",
                    f"{results['mean_profit'] - comparison['mean_profit']:.2f} RON",
                    f"{results['max_profit']:.2f} RON",
                    f"{comparison['max_profit']:.2f} RON",
                    f"{results['positive_probability']:.2f}%",
                    f"{comparison['positive_probability']:.2f}%",
                    f"{results['positive_probability'] - comparison['positive_probability']:.2f}%",
                    f"{len(st.session_state.fleet)} RON",
                    f"{((results['mean_profit'] - comparison['mean_profit']) / len(st.session_state.fleet) * 100):.1f}%"
                ]
            })
        else:
            # Datos normales
            results_summary = pd.DataFrame({
                'Métrica': [
                    'Ganancia Promedio',
                    'Desviación Estándar',
                    'Ganancia Mínima',
                    'Ganancia Máxima',
                    'Probabilidad Ganancia Positiva (%)'
                ],
                'Valor': [
                    f"{results['mean_profit']:.2f} RON",
                    f"{results['std_profit']:.2f} RON",
                    f"{results['min_profit']:.2f} RON",
                    f"{results['max_profit']:.2f} RON",
                    f"{results['positive_probability']:.2f}%"
                ]
            })
        
        csv = results_summary.to_csv(index=False)
        st.download_button(
            label="📥 Descargar Resumen CSV",
            data=csv,
            file_name="mavis_road_simulation_results.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
