# -*- coding: utf-8 -*-

"""This module can be used to validate DESTEST data
The module serves as validation for DESTEST heat demand
It compares the DESTEST data with data simulated using the demandlib
"""

import datetime
import os
import pandas as pd
import demandlib.bdew as bdew
import matplotlib.dates as mdates
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

"""
----------------------
    DESTEST Data
----------------------

Processing of DESTEST Heat Demand Data:
    - Calculation of total annual heat demand for each apartment
    - Calculation of apartment with highest and lowest heat demand in DESTEST
"""

# Import DESTEST Data
# Data preprocessed unit in W
# imaginary timestamp matches demandlib timestamp and not actual one of data)
PATH_DATA = '../data_preprocessed/Destest_heat_demand.csv'
DATA = pd.read_csv(PATH_DATA, delimiter=',', index_col=0)
IM_TIMESTAMP = '2010-01-01 00:00:00'
TIME_EXAMPLE = pd.to_datetime(DATA.index, unit='s', origin=IM_TIMESTAMP)


# Calculation of value "annual_heat_demand" for bdew.HeatBuilding function in demandlib
# Create data frame with annual heat demand of each building
for i in range(1, len(DATA.columns)+1):
    if i == 1:
        demand_annual = pd.DataFrame(data={'Apartment No.': [i],
                                           'Total annual demand': [sum(DATA[str(i)])
                                                                   * 900/3600/1000]})\
            .astype({'Apartment No.': 'int64'})
    else:
        demand_annual = demand_annual.append({'Apartment No.': i,
                                              'Total annual demand': sum(DATA[str(i)])
                                                                     * 900/3600/1000},
                                             ignore_index=True).astype({'Apartment No.': 'int64'})
print('\nAnnual heat demand in DESTEST project: \n', demand_annual)

# Save annual demand of apartments in DESTEST project
demand_annual.to_csv('demand_annual.csv')

# Find the apartment for each minimum and maximum heat demand as representatives
AP_MIN_DEMAND = demand_annual['Total annual demand'].idxmin() + 1
AP_MAX_DEMAND = demand_annual['Total annual demand'].idxmax() + 1


"""
----------------------------
    Demandlib simulation
----------------------------

Demandlib simulation:
    - Simulation of heat demand of all apartments
"""
# read example temperature series
DATAPATH = os.path.join(os.path.dirname(__file__), 'example_data.csv')
TEMPERATURE = pd.read_csv(DATAPATH)["temperature"]


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
    for j in range(0, len(demand_annual)):
        # Create curve for every apartment in DESTEST regarding its annual heat demand
        demand['Apartment No. '+str(j+1)] = bdew.HeatBuilding(
            demand.index, holidays=holidays, temperature=TEMPERATURE,
            shlp_type='EFH', building_class=1, wind_class=1,
            annual_heat_demand=demand_annual['Total annual demand'].loc[j],
            name='Apartment No. '+str(j+1)).get_bdew_profile()
    """
    ---------------------
        Visualisation
    ---------------------
    
    - Visualisation of heat demand of all apartments
        - DESTEST
        - demandlib simulation
    - Visualisation of heat demand of the apartments with the highest and lowest
      annual heat demand
        - DESTEST
        - demandlib simulation
    """

    if plt is not None:

        # Plot heat demand over time
        fig1 = plt.figure('Heat_demand', figsize=(11.69, 8.27))
        fig1.suptitle('Heat demand', fontsize=14)
        ax1, ax2 = fig1.subplots(2, 1, sharex=True)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        for k in range(1, len(DATA.columns) + 1):
            ax1.plot(TIME_EXAMPLE, DATA[str(k)]/1000, label=str(k))
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Heat demand in kW')
        ax1.set_title('DESTEST')
        ax1.legend(loc="best", ncol=3)

        for k in range(1, len(demand.columns) + 1):
            ax2.plot(demand['Apartment No. ' + str(k)], label=str(k))
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Heat demand in kW')
        ax2.set_title('demandlib')
        ax2.legend(loc="best", ncol=3)

        # Plot heat demand of apartment with maximum and minimum heat demand
        fig2 = plt.figure('Heat_demand_apartment_' + str(AP_MIN_DEMAND) + '_and_'
                          + str(AP_MAX_DEMAND), figsize=(11.69, 8.27))
        fig2.suptitle('Heat demand apartment ' + str(AP_MIN_DEMAND) + ' and '
                      + str(AP_MAX_DEMAND), fontsize=14)
        ax3, ax4 = fig2.subplots(2, 1, sharex=True)
        ax3.plot(TIME_EXAMPLE, DATA[str(AP_MIN_DEMAND)]/1000, label=str(AP_MIN_DEMAND),
                 color='mediumaquamarine')
        ax3.plot(TIME_EXAMPLE, DATA[str(AP_MAX_DEMAND)]/1000, label=str(AP_MAX_DEMAND),
                 color='tomato')
        ax3.set_xlabel('Date')
        ax3.set_ylabel('Heat demand in kW')
        ax3.legend(loc="best")
        ax3.set_title('DESTEST')

        ax4.plot(demand['Apartment No. ' + str(AP_MIN_DEMAND)], label=str(AP_MIN_DEMAND),
                 color='mediumaquamarine')
        ax4.plot(demand['Apartment No. ' + str(AP_MAX_DEMAND)], label=str(AP_MAX_DEMAND),
                 color='tomato')
        ax4.set_xlabel('Date')
        ax4.set_ylabel('Heat demand in kW')
        ax4.legend(loc="best")
        ax4.set_title('demandlib')

        fig3 = plt.figure('Heat_demand_comparison_DESTEST_demandlib', figsize=(11.69, 8.27))
        fig3.suptitle('Heat demand comparison DESTEST demandlib')
        ax5 = fig3.subplots(1, 1, sharex=True)
        ax5.plot(TIME_EXAMPLE, DATA[str(AP_MAX_DEMAND)]/1000, label=str(AP_MAX_DEMAND) +
                                                                    ' - DESTEST',
                 color='goldenrod')
        ax5.plot(demand['Apartment No. ' + str(AP_MAX_DEMAND)], label=str(AP_MAX_DEMAND) +
                                                                      ' - demandlib',
                 color='lightsteelblue')
        ax5.set_xlabel('Date')
        ax5.set_ylabel('Heat demand in kW')
        ax5.set_title('DESTEST')
        ax5.legend(loc="best")

        plt.show()
    else:
        print('Annual consumption: \n{}'.format(demand.sum()))


if __name__ == '__main__':
    heat_example()
