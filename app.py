import streamlit as st
import pandas as pd
import numpy as np

def random_digit_assignment(probabilities):
    cumulative_prob = np.cumsum(probabilities)
    ranges = []
    start = 1
    
    for i, prob in enumerate(cumulative_prob):
        if i == len(cumulative_prob) - 1:
            # For the last range, always end at 100
            end = 100
        else:
            # For all other ranges, round up to the nearest whole number
            end = int(np.ceil(prob * 100))
        
        ranges.append(f"{start}-{end}")
        start = end + 1
    
    return ranges

def determine_value_from_random_digit(random_digit, distribution):
    for value, info in distribution.items():
        if info['start'] <= random_digit <= info['end']:
            return value
    return None

def process_incoming_orders(outstanding_orders):
    arriving_quantity = 0
    updated_orders = []
    
    for qty, weeks_left in outstanding_orders:
        if weeks_left == 0:
            arriving_quantity += qty
        else:
            updated_orders.append((qty, weeks_left - 1))
                
    return arriving_quantity, updated_orders

def place_new_order(ending_inventory, outstanding_orders, lead_time_index, lead_time_random_digits, lead_time_distribution, order_point, max_inventory):
    if ending_inventory <= order_point and not outstanding_orders:
        quantity_ordered = max_inventory - ending_inventory
        if lead_time_index < len(lead_time_random_digits):
            lead_time_digit = lead_time_random_digits[lead_time_index]
            lead_time = determine_value_from_random_digit(lead_time_digit, lead_time_distribution)
            lead_time_index += 1
            return quantity_ordered, lead_time, lead_time_digit, lead_time_index
    return None, None, None, lead_time_index

def simulate_inventory_system(
    initial_inventory,
    order_point,
    max_inventory,
    shortage_cost_per_thousand,
    order_cost_per_order,
    demand_distribution,
    lead_time_distribution,
    demand_random_digits,
    lead_time_random_digits,
    num_weeks
):
    inventory = initial_inventory
    outstanding_orders = []
    results = []
    lead_time_index = 0
    total_ordering_cost = 0
    total_shortage_cost = 0
    
    for week in range(1, num_weeks + 1):
        arriving_qty, outstanding_orders = process_incoming_orders(outstanding_orders)
        beginning_inventory = inventory + arriving_qty
        
        if week-1 < len(demand_random_digits):
            demand_digit = demand_random_digits[week-1]
            demand = determine_value_from_random_digit(demand_digit, demand_distribution)
        else:
            demand_digit = None
            demand = 0
        
        if beginning_inventory >= demand:
            ending_inventory = beginning_inventory - demand
            shortage = 0
        else:
            ending_inventory = 0
            shortage = demand - beginning_inventory
        
        quantity_ordered, lead_time, lead_time_digit, lead_time_index = place_new_order(
            ending_inventory, outstanding_orders, lead_time_index, lead_time_random_digits, lead_time_distribution, order_point, max_inventory
        )
        
        ordering_cost = 0
        if quantity_ordered:
            outstanding_orders.append((quantity_ordered, lead_time))
            ordering_cost = order_cost_per_order
            total_ordering_cost += ordering_cost
        
        shortage_cost = shortage * shortage_cost_per_thousand
        total_shortage_cost += shortage_cost
        
        results.append({
            'Week': week,
            'Beginning Inventory': beginning_inventory * 1000,
            'Demand Digit': demand_digit if demand_digit else '-',
            'Demand (K)': int(demand) * 1000,
            'Ending Inventory': ending_inventory * 1000,
            'Shortage (k)': shortage if shortage else 0,
            'Shortage Cost (Rs)': shortage_cost if shortage_cost else 0,
            'Lead Time Digit': lead_time_digit if lead_time_digit else '-',
            'Lead Time (weeks)': lead_time if lead_time else '-',
            'Quantity Ordered': quantity_ordered * 1000 if quantity_ordered else '-'
        
            
           
        })
        
        inventory = ending_inventory
    
    results.append({
        'Week': 'Total',
        'Beginning Inventory': '-',
        'Demand Digit': '-',
        'Demand (K)': '-',
        'Ending Inventory': '-',
        'Shortage (k)': '-',
        'Shortage Cost (Rs)': total_shortage_cost,
        'Lead Time Digit': '-',
        'Lead Time (weeks)': '-',
        'Quantity Ordered': '-',
    })
    
    return results

def main():
    st.title("Inventory Management Simulation")
    st.markdown("""
    This simulation models a wholesaler's inventory system for desk calendars with probabilistic demand and lead times.
    """)

    st.sidebar.header("Simulation Parameters")

    # Constants
    st.sidebar.subheader("Constants")
    initial_inventory = st.sidebar.number_input("Initial Inventory (in thousands)", min_value=0, value=3, step=1)
    order_point = st.sidebar.number_input("Order Point (in thousands)", min_value=0, value=2, step=1)
    max_inventory = st.sidebar.number_input("Max Inventory Level (in thousands)", min_value=1, value=4, step=1)
    shortage_cost_per_thousand = st.sidebar.number_input("Shortage Cost per Thousand (Rs)", min_value=0, value=10, step=1)
    order_cost_per_order = st.sidebar.number_input("Ordering Cost per Order (Rs)", min_value=0, value=50, step=1)

    # Demand Distribution
    st.sidebar.subheader("Demand Distribution")
    demand_probs = [
        st.sidebar.number_input(f"Probability for Demand {i}", min_value=0.0, max_value=1.0, value=0.2, step=0.01)
        for i in range(4)
    ]
    demand_probs = [prob / sum(demand_probs) for prob in demand_probs]  # Normalize probabilities
    demand_ranges = random_digit_assignment(demand_probs)
    
    demand_distribution = {
        i: {'probability': prob, 'start': int(range.split('-')[0]), 'end': int(range.split('-')[1])}
        for i, (prob, range) in enumerate(zip(demand_probs, demand_ranges))
    }

    st.sidebar.markdown("**Demand Categories:**")
    for key, val in demand_distribution.items():
        st.sidebar.text(f"Demand {key} (k): {val['start']}-{val['end']} (Prob: {val['probability']:.2f})")

    # Lead Time Distribution
    st.sidebar.subheader("Lead Time Distribution")
    lead_time_probs = [
        st.sidebar.number_input(f"Probability for Lead Time {i} weeks", min_value=0.0, max_value=1.0, value=0.33, step=0.01)
        for i in range(2, 5)
    ]
    lead_time_probs = [prob / sum(lead_time_probs) for prob in lead_time_probs]  # Normalize probabilities
    lead_time_ranges = random_digit_assignment(lead_time_probs)
    
    lead_time_distribution = {
        i: {'probability': prob, 'start': int(range.split('-')[0]), 'end': int(range.split('-')[1])}
        for i, (prob, range) in zip(range(2, 5), zip(lead_time_probs, lead_time_ranges))
    }

    st.sidebar.markdown("**Lead Time Categories:**")
    for key, val in lead_time_distribution.items():
        st.sidebar.text(f"Lead Time {key} weeks: {val['start']}-{val['end']} (Prob: {val['probability']:.2f})")

    # Random Digits Input
    st.header("Random Digits for Simulation")

    st.subheader("Demand Random Digits")
    default_demand_random_digits = "31,70,53,86,32,78,26,64,45,12,99,52,43,84,38,40,19,87,83,73"
    demand_random_digits_input = st.text_area(
        "Enter Demand Random Digits (comma-separated, e.g., 31,70,53,...):",
        value=default_demand_random_digits
    )
    demand_random_digits = [int(x.strip()) for x in demand_random_digits_input.split(",") if x.strip().isdigit()]

    st.subheader("Lead Time Random Digits")
    default_lead_time_random_digits = "29,83,58,41,13"
    lead_time_random_digits_input = st.text_area(
        "Enter Lead Time Random Digits (comma-separated, e.g., 29,83,58,...):",
        value=default_lead_time_random_digits
    )
    lead_time_random_digits = [int(x.strip()) for x in lead_time_random_digits_input.split(",") if x.strip().isdigit()]

    # Simulation Control
    st.header("Run Simulation")
    num_weeks = st.number_input("Number of Weeks to Simulate", min_value=1, max_value=20, value=20, step=1)

    if st.button("Run Simulation"):
        results = simulate_inventory_system(
            initial_inventory=initial_inventory,
            order_point=order_point,
            max_inventory=max_inventory,
            shortage_cost_per_thousand=shortage_cost_per_thousand,
            order_cost_per_order=order_cost_per_order,
            demand_distribution=demand_distribution,
            lead_time_distribution=lead_time_distribution,
            demand_random_digits=demand_random_digits,
            lead_time_random_digits=lead_time_random_digits,
            num_weeks=num_weeks
        )

        df_results = pd.DataFrame(results)

        def highlight_total(row):
            if row['Week'] == 'Total':
                return ['background-color: Black'] * len(row)
            else:
                return [''] * len(row)

        styled_df = df_results.style.apply(highlight_total, axis=1)

        st.subheader("Simulation Results")
        st.dataframe(styled_df)

        csv = df_results.to_csv(index=False)
        st.download_button(
            label="Download Results as CSV",
            data=csv,
            file_name='simulation_results.csv',
            mime='text/csv',
        )

if __name__ == "__main__":
    main()


# import streamlit as st
# import pandas as pd
# import numpy as np

# def random_digit_assignment(probabilities):
#     cumulative_prob = np.cumsum(probabilities)
#     ranges = []
#     start = 1
    
#     for i, prob in enumerate(cumulative_prob):
#         if i == len(cumulative_prob) - 1:
#             # For the last range, always end at 100
#             end = 100
#         else:
#             # For all other ranges, round up to the nearest whole number
#             end = int(np.ceil(prob * 100))
        
#         ranges.append(f"{start}-{end}")
#         start = end + 1
    
#     return ranges

# def determine_value_from_random_digit(random_digit, distribution):
#     for value, info in distribution.items():
#         if info['start'] <= random_digit <= info['end']:
#             return value
#     return None

# def process_incoming_orders(outstanding_orders):
#     arriving_quantity = 0
#     updated_orders = []
    
#     for qty, weeks_left in outstanding_orders:
#         if weeks_left == 0:
#             arriving_quantity += qty
#         else:
#             updated_orders.append((qty, weeks_left - 1))
                
#     return arriving_quantity, updated_orders

# def place_new_order(ending_inventory, outstanding_orders, lead_time_index, lead_time_random_digits, lead_time_distribution, order_point, max_inventory):
#     if ending_inventory <= order_point and not outstanding_orders:
#         quantity_ordered = max_inventory - ending_inventory
#         if lead_time_index < len(lead_time_random_digits):
#             lead_time_digit = lead_time_random_digits[lead_time_index]
#             lead_time = determine_value_from_random_digit(lead_time_digit, lead_time_distribution)
#             lead_time_index += 1
#             return quantity_ordered, lead_time, lead_time_digit, lead_time_index
#     return None, None, None, lead_time_index

# def simulate_inventory_system(
#     initial_inventory,
#     order_point,
#     max_inventory,
#     shortage_cost_per_thousand,
#     order_cost_per_order,
#     demand_distribution,
#     lead_time_distribution,
#     demand_random_digits,
#     lead_time_random_digits,
#     num_weeks
# ):
#     inventory = initial_inventory
#     outstanding_orders = []
#     results = []
#     lead_time_index = 0
#     total_ordering_cost = 0
#     total_shortage_cost = 0
    
#     for week in range(1, num_weeks + 1):
#         arriving_qty, outstanding_orders = process_incoming_orders(outstanding_orders)
#         beginning_inventory = inventory + arriving_qty
        
#         if week-1 < len(demand_random_digits):
#             demand_digit = demand_random_digits[week-1]
#             demand = determine_value_from_random_digit(demand_digit, demand_distribution)
#         else:
#             demand_digit = None
#             demand = 0
        
#         if beginning_inventory >= demand:
#             ending_inventory = beginning_inventory - demand
#             shortage = 0
#         else:
#             ending_inventory = 0
#             shortage = demand - beginning_inventory
        
#         quantity_ordered, lead_time, lead_time_digit, lead_time_index = place_new_order(
#             ending_inventory, outstanding_orders, lead_time_index, lead_time_random_digits, lead_time_distribution, order_point, max_inventory
#         )
        
#         ordering_cost = 0
#         if quantity_ordered:
#             outstanding_orders.append((quantity_ordered, lead_time))
#             ordering_cost = order_cost_per_order
#             total_ordering_cost += ordering_cost
        
#         shortage_cost = shortage * shortage_cost_per_thousand
#         total_shortage_cost += shortage_cost
        
#         results.append({
#             'Week': week,
#             'Beginning Inventory': beginning_inventory * 1000,
#             'Demand Digit': demand_digit if demand_digit else '-',
#             'Demand (K)': int(demand) * 1000,
#             'Ending Inventory': ending_inventory * 1000,
#             'Shortage (k)': shortage if shortage else 0,
#             'Shortage Cost (Rs)': shortage_cost if shortage_cost else 0,
#             'Lead Time Digit': lead_time_digit if lead_time_digit else '-',
#             'Lead Time (weeks)': lead_time if lead_time else '-',
#             'Quantity Ordered': quantity_ordered * 1000 if quantity_ordered else '-'
        
            
           
#         })
        
#         inventory = ending_inventory
    
#     results.append({
#         'Week': 'Total',
#         'Beginning Inventory': '-',
#         'Demand Digit': '-',
#         'Demand (K)': '-',
#         'Ending Inventory': '-',
#         'Shortage (k)': '-',
#         'Shortage Cost (Rs)': total_shortage_cost,
#         'Lead Time Digit': '-',
#         'Lead Time (weeks)': '-',
#         'Quantity Ordered': '-',
#     })
    
#     return results

# def main():
#     st.title("Inventory Management Simulation")
#     st.markdown("""
#     This simulation models a wholesaler's inventory system for desk calendars with probabilistic demand and lead times.
#     """)

#     st.sidebar.header("Simulation Parameters")

#     # Constants
#     st.sidebar.subheader("Constants")
#     initial_inventory = st.sidebar.number_input("Initial Inventory (in thousands)", min_value=0, value=3, step=1)
#     order_point = st.sidebar.number_input("Order Point (in thousands)", min_value=0, value=2, step=1)
#     max_inventory = st.sidebar.number_input("Max Inventory Level (in thousands)", min_value=1, value=4, step=1)
#     shortage_cost_per_thousand = st.sidebar.number_input("Shortage Cost per Thousand (Rs)", min_value=0, value=10, step=1)
#     order_cost_per_order = st.sidebar.number_input("Ordering Cost per Order (Rs)", min_value=0, value=50, step=1)

#     # Demand Distribution
#     st.sidebar.subheader("Demand Distribution")
#     demand_probs = [
#         st.sidebar.number_input(f"Probability for Demand {i}", min_value=0.0, max_value=1.0, value=0.2, step=0.01)
#         for i in range(4)
#     ]
#     demand_probs = [prob / sum(demand_probs) for prob in demand_probs]  # Normalize probabilities
#     demand_ranges = random_digit_assignment(demand_probs)
    
#     demand_distribution = {
#         i: {'probability': prob, 'start': int(range.split('-')[0]), 'end': int(range.split('-')[1])}
#         for i, (prob, range) in enumerate(zip(demand_probs, demand_ranges))
#     }

#     st.sidebar.markdown("**Demand Categories:**")
#     for key, val in demand_distribution.items():
#         st.sidebar.text(f"Demand {key} (k): {val['start']}-{val['end']} (Prob: {val['probability']:.2f})")

#     # Lead Time Distribution
#     st.sidebar.subheader("Lead Time Distribution")
#     lead_time_probs = [
#         st.sidebar.number_input(f"Probability for Lead Time {i} weeks", min_value=0.0, max_value=1.0, value=0.33, step=0.01)
#         for i in range(2, 5)
#     ]
#     lead_time_probs = [prob / sum(lead_time_probs) for prob in lead_time_probs]  # Normalize probabilities
#     lead_time_ranges = calculate_random_digit_ranges(lead_time_probs)
    
#     lead_time_distribution = {
#         i: {'probability': prob, 'start': int(range.split('-')[0]), 'end': int(range.split('-')[1])}
#         for i, (prob, range) in zip(range(2, 5), zip(lead_time_probs, lead_time_ranges))
#     }

#     st.sidebar.markdown("**Lead Time Categories:**")
#     for key, val in lead_time_distribution.items():
#         st.sidebar.text(f"Lead Time {key} weeks: {val['start']}-{val['end']} (Prob: {val['probability']:.2f})")

#     # Random Digits Input
#     st.header("Random Digits for Simulation")

#     st.subheader("Demand Random Digits")
#     default_demand_random_digits = "31,70,53,86,32,78,26,64,45,12,99,52,43,84,38,40,19,87,83,73"
#     demand_random_digits_input = st.text_area(
#         "Enter Demand Random Digits (comma-separated, e.g., 31,70,53,...):",
#         value=default_demand_random_digits
#     )
#     demand_random_digits = [int(x.strip()) for x in demand_random_digits_input.split(",") if x.strip().isdigit()]

#     st.subheader("Lead Time Random Digits")
#     default_lead_time_random_digits = "29,83,58,41,13"
#     lead_time_random_digits_input = st.text_area(
#         "Enter Lead Time Random Digits (comma-separated, e.g., 29,83,58,...):",
#         value=default_lead_time_random_digits
#     )
#     lead_time_random_digits = [int(x.strip()) for x in lead_time_random_digits_input.split(",") if x.strip().isdigit()]

#     # Simulation Control
#     st.header("Run Simulation")
#     num_weeks = st.number_input("Number of Weeks to Simulate", min_value=1, max_value=20, value=20, step=1)

#     if st.button("Run Simulation"):
#         results = simulate_inventory_system(
#             initial_inventory=initial_inventory,
#             order_point=order_point,
#             max_inventory=max_inventory,
#             shortage_cost_per_thousand=shortage_cost_per_thousand,
#             order_cost_per_order=order_cost_per_order,
#             demand_distribution=demand_distribution,
#             lead_time_distribution=lead_time_distribution,
#             demand_random_digits=demand_random_digits,
#             lead_time_random_digits=lead_time_random_digits,
#             num_weeks=num_weeks
#         )

#         df_results = pd.DataFrame(results)

#         def highlight_total(row):
#             if row['Week'] == 'Total':
#                 return ['background-color: Black'] * len(row)
#             else:
#                 return [''] * len(row)

#         styled_df = df_results.style.apply(highlight_total, axis=1)

#         st.subheader("Simulation Results")
#         st.dataframe(styled_df)

#         csv = df_results.to_csv(index=False)
#         st.download_button(
#             label="Download Results as CSV",
#             data=csv,
#             file_name='simulation_results.csv',
#             mime='text/csv',
#         )

# if __name__ == "__main__":
#     main()