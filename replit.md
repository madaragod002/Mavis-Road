# Mavis Road - Monte Carlo Simulator

## Overview

This is a Monte Carlo simulation application for the Mavis Road trucking game that helps users analyze monthly profit potential for their truck fleet. The application simulates various scenarios for different truck rarities, accounting for operational costs like fuel, tires, and repairs, to provide statistical insights into expected earnings. Built with Streamlit for an interactive web interface, it allows users to manage their fleet composition and run comprehensive Monte Carlo simulations to make informed decisions about their trucking operations.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Streamlit Web Application**: Single-page application with sidebar navigation for fleet management and main content area for simulation results
- **Interactive Visualization**: Plotly integration for dynamic charts and graphs showing simulation results and statistical distributions
- **Session State Management**: Persistent fleet configuration and simulation results across user interactions

### Backend Architecture
- **Object-Oriented Simulation Engine**: Modular design with separate classes for individual truck simulation (`TruckSimulator`) and Monte Carlo analysis (`MonteCarloSimulation`)
- **Probabilistic Modeling**: Each truck rarity has distinct operational parameters including earnings per trip, fuel costs, repair probabilities, and maintenance schedules
- **Concurrent Simulation Processing**: Multi-threaded execution using ThreadPoolExecutor for efficient Monte Carlo runs

### Data Processing
- **Statistical Analysis**: NumPy-based calculations for probability distributions and statistical metrics
- **Results Aggregation**: Pandas DataFrames for organizing and analyzing simulation outputs across different time periods
- **Time Period Modeling**: Configurable simulation periods (1 week, 30 days, 1 year) with hourly granularity

### Core Business Logic
- **Truck Rarity System**: Five-tier rarity system with escalating earnings and decreasing breakdown probabilities
- **Operational Cost Modeling**: Dynamic cost calculations for fuel (every 2 trips), tires (every 4 trips), and random repairs based on breakdown probability
- **Fleet Composition**: Support for mixed-rarity fleets with individual truck performance tracking

## External Dependencies

### Python Libraries
- **Streamlit**: Web application framework for the user interface
- **Pandas**: Data manipulation and analysis for simulation results
- **NumPy**: Numerical computing for statistical calculations and random number generation
- **Plotly Express & Graph Objects**: Interactive visualization library for charts and statistical plots
- **Concurrent.futures**: Built-in Python library for parallel processing of simulation runs

### Development Tools
- **Threading**: Python's threading module for thread-safe simulation execution
- **Random**: Python's random module for probabilistic events in truck operations

Note: This application is designed as a standalone simulation tool with no external database or API dependencies, making it suitable for local deployment and analysis.