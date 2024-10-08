Inventory Management Simulation for Desk Calendars
Overview
This project simulates a wholesaler's inventory management system for desk calendars. The simulation models probabilistic demand and lead time scenarios, helping the wholesaler determine the optimal order size and understand how inventory changes over time. The simulation provides insights into how the wholesaler can manage their inventory costs, including ordering costs and shortage costs.

The system uses random digits to simulate the demand per week and lead times, providing a practical tool for decision-making in an uncertain environment.

Problem Description
A wholesaler dealing in desk calendars needs to manage inventory with the following conditions:

Initial Inventory: 3000 units (3k).
Order Point: If the inventory level drops to or below 2000 units, a replenishment order is placed to restore inventory up to 4000 units.
No Back Orders: Orders that cannot be fulfilled due to shortages are considered lost.
Replenishment Timing: Orders are placed at the beginning of the week after inventory falls below the order point, and replenishment arrives at the start of the lead time duration.
Costs
Ordering Cost: Rs. 50 per order.
Shortage Cost: Rs. 10 per thousand units.
Demand and Lead Time
The demand and lead time are both probabilistic, with the following distributions:

Demand (thousand units per week)	Probability	Cumulative Probability	Random Digit Assignment
0	0.2	0.2	01 - 20
1	0.4	0.6	21 - 60
2	0.3	0.9	61 - 90
3	0.1	1.0	91 - 00
Lead Time (weeks)	Probability	Cumulative Probability	Random Digit Assignment
2	0.3	0.3	01 - 30
3	0.4	0.7	31 - 70
4	0.3	1.0	71 - 00
Simulation
This simulation takes into account the randomness in demand and lead time over a specified number of weeks and calculates the following metrics for each week:

Beginning Inventory
Demand (in thousand units)
Ending Inventory
Shortage (if any)
Lead Time (if an order was placed)
Quantity Ordered (if any)
Shortage Cost
Ordering Cost
Random Digits Used in the Simulation
Random Digits for Demand: 31, 70, 53, 86, 32, 78, 26, 64, 45, 12, 99, 52, 43, 84, 38, 40, 19, 87, 83, 73.
Random Digits for Lead Time: 29, 83, 58, 41, 13.
Simulation Process
Demand is Determined: For each week, the random digit is used to simulate the demand based on the probability distribution.
Inventory is Updated: The beginning inventory is reduced by the demand to get the ending inventory.
Orders Are Placed: If the ending inventory is at or below the order point (2000 units), a replenishment order is placed, and the lead time is determined using the random digit assigned for lead time.
Shortage Costs: If there is any shortage, the shortage cost is calculated at Rs. 10 per thousand units short.
Simulation Results
At the end of the simulation, the tool generates a table displaying week-by-week data on inventory levels, orders, costs, and shortages. The total shortage cost and total ordering cost are calculated at the end of the simulation.

Features
Interactive Inputs: Allows users to specify the initial inventory, order point, maximum inventory, shortage cost, ordering cost, and random digits for demand and lead time.
Random Demand and Lead Time: Uses probabilistic modeling for demand and lead time to simulate realistic scenarios.
Cost Calculation: Calculates total ordering and shortage costs for better decision-making.
Download Results: Users can download the simulation results as a CSV file.
How to Run
Clone the repository:

bash
Copy code
git clone https://github.com/your-username/inventory-management-simulation.git
Install the required Python packages:

bash
Copy code
pip install -r requirements.txt
Run the simulation using Streamlit:

bash
Copy code
streamlit run inventory_simulation.py
Enter the required simulation parameters via the sidebar and click on Run Simulation to get results.

Example Output
A week-by-week breakdown of inventory levels, demand, shortage costs, and ordering decisions.
A summary of total costs at the end of the simulation.
License
This project is licensed under the MIT License.
