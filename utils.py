import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import numpy as np
import atomica as at

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import atomica as at

def calc_emissions(results, start_year, facility_code, file_name, title=None):
    '''
    Calculate emissions before and after program implementation, export results to Excel, and generate bar plots.
    :param results: list of Atomica result objects.
    :param start_year: Start year of programs.
    :param facility_code: Code of the facility.
    :param file_name: Specify Excel file name for saving.
    :param title: Title for the plot.
    :return: DataFrame of emissions results.
    '''
    # Extract relevant parameter names for plotting
    pop = results[0].pop_names[0]
    pars = results[0].par_names(pop)
    parameters = [par for par in pars if '_mult' not in par and '_emissions' not in par and '_baseline' not in par]
    par_labels = [par.replace('_', ' ').title() for par in parameters]
    
    # Set up DataFrame for emissions
    rows = ['Status-quo'] + [res.name for res in results]
    df_emissions = pd.DataFrame(index=rows, columns=par_labels)
    start_i = list(results[0].t).index(start_year)
    
    # Populate the DataFrame with emissions data
    for par, par_label in zip(parameters, par_labels):
        df_emissions.loc['Status-quo', par_label] = results[0].get_variable(par, facility_code)[0].vals[start_i - 1]
        for res in results:
            df_emissions.loc[res.name, par_label] = res.get_variable(par, facility_code)[0].vals[start_i]
    
    # Export the DataFrame to Excel
    writer_emissions = pd.ExcelWriter(f'results/{file_name}.xlsx', engine='xlsxwriter')
    df_emissions.to_excel(writer_emissions, sheet_name=facility_code)
    writer_emissions.save()
    
    # Generate the bar plot
    fig_width = max(20, len(par_labels) * 1.5)
    fig_height = 10
    font_size = 12
    plt.figure(figsize=(fig_width, fig_height))
    ax = df_emissions.plot(kind='bar', stacked=True, fontsize=font_size)
    
    # Set plot title
    plt.title(title or 'Total CO2e Emissions', fontsize=font_size + 2)
    
    # Adjust legend
    ax.legend(title='Emission Sources', bbox_to_anchor=(1.0, 1.0), loc='upper left')
    
    # Format the y-axis
    ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
    
    # Adjust x-axis labels
    plt.xticks(rotation=90, ha='center')
    plt.ylabel('Emissions (CO2e)', fontsize=font_size)
    
    # Tight layout and save figure
    plt.tight_layout()
    plt.savefig(f'figs/{file_name}.png', bbox_inches='tight')
    plt.show()
    
    # Close the writer and release Excel file
    writer_emissions.close()
    
    print(f'Emissions results saved: results/{file_name}.xlsx')
    print(f'Emissions bar plots saved: figs/{file_name}.png')

    return df_emissions

# You can call the function with the appropriate parameters to generate the emissions calculations and visualizations.



import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import atomica as at

def calc_emissions(results, start_year, facility_code, file_name, title=None):
    '''
    Calculate emissions before and after program implementation, export results to Excel, and generate bar plots.
    :param results: list of Atomica result objects.
    :param start_year: Start year of programs.
    :param facility_code: Code of the facility.
    :param file_name: Specify Excel file name for saving.
    :param title: Title for the plot.
    :return: DataFrame of emissions results.
    '''
    # Extract relevant parameter names for plotting
    pop = results[0].pop_names[0]
    pars = results[0].par_names(pop)
    parameters = [par for par in pars if '_mult' not in par and '_emissions' not in par and '_baseline' not in par]
    par_labels = [par.replace('_', ' ').title() for par in parameters]  # Ensure this is defined within the function scope

    # Set up DataFrame for emissions
    rows = ['Status-quo'] + [res.name for res in results]
    df_emissions = pd.DataFrame(index=rows, columns=par_labels)
    start_i = list(results[0].t).index(start_year)
    
    # Populate the DataFrame with emissions data
    for par, par_label in zip(parameters, par_labels):
        df_emissions.loc['Status-quo', par_label] = results[0].get_variable(par, facility_code)[0].vals[start_i-1]
        for res in results:
            df_emissions.loc[res.name, par_label] = res.get_variable(par, facility_code)[0].vals[start_i]
    
    # Export the DataFrame to Excel
    writer_emissions = pd.ExcelWriter(f'results/{file_name}.xlsx', engine='xlsxwriter')
    df_emissions.to_excel(writer_emissions, sheet_name=facility_code)
    # writer_emissions.save()
    
    # Generate the bar plot
    num_parameters = len(par_labels)  # Use par_labels after it is defined
    fig_width = max(20, num_parameters * 1.5)
    fig_height = 10
    font_size = 12
    plt.figure(figsize=(fig_width, fig_height))
    ax = df_emissions.plot(kind='bar', stacked=True, fontsize=font_size)
    
    # Set plot title
    plt.title(title or 'Total CO2e Emissions', fontsize=font_size + 2)
    
    # Adjust legend
    ax.legend(title='Emission Sources', bbox_to_anchor=(1.0, 1.0), loc='upper left')
    
    # Format the y-axis
    ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('{x:,.0f}'))
    
    # Adjust x-axis labels
    plt.xticks(rotation=90, ha='center')
    plt.ylabel('Emissions (CO2e)', fontsize=font_size)
    
    # Tight layout and save figure
    plt.tight_layout()
    plt.savefig(f'figs/{file_name}.png', bbox_inches='tight')
    plt.show()
    
    # Close the writer and release Excel file
    writer_emissions.close()
    
    print(f'Emissions results saved: results/{file_name}.xlsx')
    print(f'Emissions bar plots saved: figs/{file_name}.png')

    return df_emissions



    
def calc_allocation(results,file_name):
    '''
    Prints allocation to excel
    :param results: list of atomica result objects
    :param file_name: (optional) specify excel file name for saving
    '''
    prog_codes = results[0].model.progset.programs
    prog_labels = [results[0].model.progset.programs[prog].label for prog in prog_codes]
    res_names = [res.name for res in results]
    df_spending_optimized = pd.DataFrame(index=res_names, columns=prog_labels)
    
    for res in results:
        for prog_code, prog_name in zip(prog_codes,prog_labels):
            df_spending_optimized.loc[res.name,prog_name] = res.get_alloc()[prog_code][0]
    
    # https://matplotlib.org/stable/users/explain/colors/colormaps.html#qualitative
    colormap = plt.cm.tab20
    colors = [colormap(i) for i in range(len(df_spending_optimized.columns))]
    
    plt.figure()
    ax = df_spending_optimized.plot.bar(stacked=True, color=colors, figsize=(15,10), fontsize=20)
    ax.legend(loc='upper left', bbox_to_anchor=(1.05,1), title='Interventions', prop={'size':18}, title_fontsize=22)
    ax.yaxis.set_major_formatter(mpl.ticker.StrMethodFormatter('${x:,.0f}'))
    plt.title('Budget allocation', fontsize=25)
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig('figs/{}.png'.format(file_name))
    plt.show()
    plt.close()
    
    # writer_optim = pd.ExcelWriter('results/{}.xlsx'.format(file_name), engine='xlsxwriter')    
    # df_spending_optimized.to_excel(writer_optim, sheet_name='Optimized allocation', index=True)
    
    # workbook  = writer_optim.book
    # worksheet = writer_optim.sheets['Optimized allocation']
    # format_cost = workbook.add_format({'num_format': '$#,##0.0'})
    # for i in np.arange(len(res_names)):
    #     worksheet.set_row(i+1, None, format_cost) 
    # writer_optim.close()
    # print('Allocation results saved: results/{}.xlsx'.format(file_name))
    print('Allocation bar plots saved: figs/{}.xlsx'.format(file_name))
    
    return df_spending_optimized

def write_alloc_excel(progset, results, year, print_results=True,file_name=None):
    """Write optimized budget alloations onto an excel file
        :param: P: atomica project
        :param: results: results from optimization runs
        :param: save_dir: path for saving the plot
        :param: name to be given to excel file (string)"""
        
    progname = []
    prog_labels = []
    for prog in progset.programs:
        progname += [prog]
        prog_labels += [progset.programs[prog].label]
        
    bars = []
    for i in range(0, len(results)):
         bar_name = results[i].name
         bars.append(bar_name)
         
    d1 = at.PlotData.programs(results, quantity='spending')
    d1.interpolate(year)
    spending_raw_data = {(x.result, x.output): x.vals[0] for x in d1.series}
    spending_data = {res: {prog:0 for prog in progname} for res in bars}
    
    d2 = at.PlotData.programs(results, quantity='coverage_fraction')
    d2.interpolate(year)
    cov_raw_data = {(x.result, x.output): x.vals[0] for x in d2.series}
    cov_data = {res: {prog:0 for prog in progname} for res in bars}
    for br in bars:
        for prog in progname:
            spending_data[br][prog] = spending_raw_data[(br, prog)]
            cov_data[br][prog] = cov_raw_data[(br, prog)]
    df1 = pd.DataFrame(spending_data)
    df2 = pd.DataFrame(cov_data)
    df1.index = prog_labels
    df2.index = prog_labels
    
    if print_results:
        writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
        df1.to_excel(writer, sheet_name="Budgets")
        df2.to_excel(writer, sheet_name="Coverages")
        writer.save()
        print('Excel file saved: {}'.format(file_name))
    
    return df1, df2