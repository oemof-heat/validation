# -*- coding: utf-8 -*-
import pandas as pd
import demandlib.bdew as bdew
import datetime
import os
import matplotlib.dates as mdates
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

"""
----------------------
    DESTEST Data
----------------------

Processing of DESTEST Heat Demand Data:
    - Calculation of total annual heat demand for each apartment
    - Calculation of apartment with highest and lowest heat demand in DESTEST
    
"""

# Import DESTEST Data
path_data_preprocessed = '../data_preprocessed/Destest_heat_demand.csv'     # Data preprocessed in W
path_data_kWh = '../data_preprocessed/Destest_heat_demand_kWh.csv'  # Data in kWh (calculated with W_to_kWh.py)
data = pd.read_csv(path_data_preprocessed, delimiter=',', index_col=0)
data_kWh = pd.read_csv(path_data_kWh, delimiter=',', index_col=0)

im_timestamp = '2010-01-01 00:00:00'    # imaginary timestamp (Not actual timestamp of data. Same as demandlib)
time_example = pd.to_datetime(data.index, unit='s', origin=im_timestamp)

# Calculation of value "annual_heat_demand" for bdew.HeatBuilding function in demandlib
# Create data frame with annual heat demand of each building
for i in range(1, len(data.columns)+1):
    if i == 1:
        demand_annual = pd.DataFrame(data={'Apartment No.': [i], 'Total annual demand': [sum(data_kWh[str(i)])*1000]})\
            .astype({'Apartment No.': 'int64'})
    else:
        demand_annual = demand_annual.append({'Apartment No.': i, 'Total annual demand': sum(data_kWh[str(i)])*1000},
                                         ignore_index=True).astype({'Apartment No.': 'int64'})

print('\nAnnual heat demand in DESTEST project: \n', demand_annual)

# Save annual demand of apartments in DESTEST project
demand_annual.to_csv('demand_annual.csv')

# Find the apartment for each minimum and maximum heat demand as representatives
ap_min_demand = demand_annual['Total annual demand'].idxmin() + 1
ap_max_demand = demand_annual['Total annual demand'].idxmax() + 1


"""

----------------------------
    Demandlib simulation
----------------------------

Demandlib simulation:
    - Simulation of heat demand of all apartments

"""
# read example temperature series
datapath = os.path.join(os.path.dirname(__file__), 'example_data.csv')
temperature = pd.read_csv(datapath)["temperature"]


# The following dictionary is create by "workalendar"
# pip3 install workalendar
# >>> from workalendar.europe import Germany
# >>> cal = Germany()
# >>> holidays = dict(cal.holidays(2010))


def heat_example():
    holidays = {
        datetime.date(2010, 5, 24): 'Whit Monday',
        datetime.date(2010, 4, 5): 'Easter Monday',
        datetime.date(2010, 5, 13): 'Ascension Thursday',
        datetime.date(2010, 1, 1): 'New year',
        datetime.date(2010, 10, 3): 'Day of German Unity',
        datetime.date(2010, 12, 25): 'Christmas Day',
        datetime.date(2010, 5, 1): 'Labour Day',
        datetime.date(2010, 4, 2): 'Good Friday',
        datetime.date(2010, 12, 26): 'Second Christmas Day'}

    # Create DataFrame for 2010
    demand = pd.DataFrame(
        index=pd.date_range(pd.datetime(2010, 1, 1, 0),
                            periods=8760, freq='H'))

    # Heat demand plot for all 24 apartments (efh: Einfamilienhaus)
    for i in range(0, len(demand_annual)):
        # Create curve for every apartment in DESTEST regarding its annual heat demand
        demand['Apartment No. '+str(i+1)] = bdew.HeatBuilding(
            demand.index, holidays=holidays, temperature=temperature,
            shlp_type=('EFH'),
            building_class=1, wind_class=1, annual_heat_demand=demand_annual['Total annual demand'].loc[i],
            name='Apartment No. '+str(i+1)).get_bdew_profile()

    '''
    ---------------------
        Visualisation
    ---------------------
    
    - Visualisation of heat demand of all apartments
        - DESTEST
        - demandlib simulation
        
    - Visualisation of heat demand of the apartments with the highest and lowest annual heat demand
        - DESTEST
        - demandlib simulation
    
    '''

    if plt is not None:

        # Plot heat demand over time
        fig1 = plt.figure('Heat_demand', figsize=(11.69, 8.27))
        fig1.suptitle('Heat demand', fontsize=14)
        ax1, ax2 = fig1.subplots(2, 1, sharex=True)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        for i in range(1, len(data.columns) + 1):
            ax1.plot(time_example, data[str(i)], label=str(i))
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Heat demand in W')
        ax1.set_title('DESTEST')
        ax1.legend(loc="best", ncol=3)
        ax2.plot(demand)
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Heat demand in W')
        ax2.set_title('demandlib')

        # Plot heat demand of apartment with maximum and minimum heat demand
        fig2 = plt.figure('Heat_demand_apartment_' + str(ap_min_demand) + '_and_' + str(ap_max_demand),
                          figsize=(11.69, 8.27))
        fig2.suptitle('Heat demand apartment ' + str(ap_min_demand) + ' and ' + str(ap_max_demand), fontsize=14)
        ax3, ax4 = fig2.subplots(2, 1, sharex=True)
        ax3.plot(time_example, data[str(ap_min_demand)], label=str(ap_min_demand), color='mediumaquamarine')
        ax3.plot(time_example, data[str(ap_max_demand)], label=str(ap_max_demand), color='tomato')
        ax3.set_xlabel('Date')
        ax3.set_ylabel('Heat demand in W')
        ax3.legend(loc="best")
        ax3.set_title('DESTEST')

        ax4.plot(demand['Apartment No. ' + str(ap_min_demand)], color='mediumaquamarine')
        ax4.plot(demand['Apartment No. ' + str(ap_max_demand)], color='tomato')
        ax4.set_xlabel('Date')
        ax4.set_ylabel('Heat demand in W')
        ax4.set_title('demandlib')

        plt.show()
    else:
        print('Annual consumption: \n{}'.format(demand.sum()))


if __name__ == '__main__':
    heat_example()
