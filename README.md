# energy_management_simpy

## Simpy / Dash prototype of energy consumers/producers dashboard

Run `./check_update.py` anytime to create and populate the configuration database and to upgrade the database schema whenever you update the code. 

Run `./readplan.py` to read the plan and forecast, run the simulation and generate the output file `energy.csv` in the `data/files` directory.

To plot the data, run `./plotplan.py` which runs a simple webserver at `http://127.0.0.1:8050/`

