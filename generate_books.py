import atomica as at
import pandas as pd
'''
Script to generate a framework, databook and progbook.
'''
#%% Define facilities and interventions here (please remember to update interventions list here)
facilities = {
    'aga-khan_hosp_KE': {'label': 'Aga Khan Hospital, Kenya', 'type': 'facilities'},
    'aga-khan_medi_KE': {'label': 'Aga Khan Medical Centre, Kenya', 'type': 'facilities'},
    'laudium_chc_SA': {'label': 'Laudium Community Health Centre, South Africa', 'type': 'facilities'},
    'stanza-bopape_chc_SA': {'label': 'Stanza Bopape Community Health Centre, South Africa', 'type': 'facilities'},
    'mamelodi_hosp_SA': {'label': 'Mamelodi Regional Hospital, South Africa', 'type': 'facilities'},
    'mt-darwin_hosp_ZW': {'label': 'Mt Darwin District Hospital, Zimbabwe', 'type': 'facilities'},
    'dotito_rhcc_ZW': {'label': 'Dotito Rural Health Care Clinic, Zimbabwe', 'type': 'facilities'},
    'chitse_rhcc_ZW': {'label': 'Chitse Rural Health Care Clinic, Zimbabwe', 'type': 'facilities'}
    }

# /!\ TO UPDATE:
interventions = {
    'energy_led': 'Energy saving LED',
    'low_emit_mat': 'Low emitting materials',
    'electric_cars': 'Electric cars',
    'low_emit_gas': 'Low emitting anesthetic gases',
    'borehole_water': 'Borehole water',
    'recycle': 'Recycling',
    'low_emit_inhale': 'Low emitting inhalers',
    'local_procure': 'Local procurements'
    } # /!\ TO UPDATE

#%% Create input data spreadsheet headers 
# The file is saved in "templates/input_data_headers.xlsx", and is useful when the list of interventions above is updated
# and you don't want to manually update the headers of input_data.xlsx
columns = ['facilities_number', 'co2e_emissions']
for intervention in interventions:
    columns.append(intervention+'_effect')
df_data = pd.DataFrame(columns=columns, index=facilities)
df_data.index = df_data.index.rename('facilities')
df_costs = pd.DataFrame(columns=interventions, index=facilities)
df_costs.index = df_costs.index.rename('facilities')
with pd.ExcelWriter('templates/input_data_headers.xlsx') as writer:
    df_data.to_excel(writer, sheet_name='data')
    df_costs.to_excel(writer, sheet_name='costs')
    
#%% Step 1: read in base framework, and generate intervention-specific parameters 
# read framework base from template
dfs = pd.read_excel(pd.ExcelFile('templates/carbomica_framework_base.xlsx'), sheet_name=None)

# define intervention-specific parameters and add to the Parameters sheet as a new row
for key in interventions:
    coverage = {'Code Name': key + '_cov', 
                'Display Name': interventions[key] + ' - coverage',
                'Default Value': 0,
                'Minimum Value': 0,
                'Maximum Value': 1,
                'Targetable': 'y',
                'Databook Page': 'coverage',
                'Population type': 'facilities',
                'Timed': 'n', 'Is derivative': 'n'} # define coverage of intervention as a new row in framework
    effect = {'Code Name': key + '_effect', 
              'Display Name': interventions[key] + ' - effect',
              'Format': 'number',
              'Targetable': 'n',
              'Databook Page': 'intervention',
              'Guidance': 'Reduction in emissions (proportion)',
              'Population type': 'facilities',
              'Timed': 'n', 'Is derivative': 'n'} # define effect of intervention as a new row in framework
    dfs['Parameters'] = dfs['Parameters'].append(coverage, ignore_index=True) # add the coverage row to the framework
    dfs['Parameters'] = dfs['Parameters'].append(effect, ignore_index=True) # add the effect row to the framework
    # update the function for overall_multiplier such as the impact interactions between interventions work independently:
    dfs['Parameters'].loc[dfs['Parameters']['Code Name']=='overall_multiplier','Function']+='*(1-'+coverage['Code Name']+'*'+effect['Code Name']+')'
    
with pd.ExcelWriter('carbomica_framework.xlsx') as writer:
    for sheet_name, df in dfs.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    

#%% Step 2: generate and populate the databook (saved in "books/")
F = at.ProjectFramework('carbomica_framework.xlsx')  # load framework
data_years = 2023 # years for input data

D = at.ProjectData.new(framework=F, tvec=data_years, pops=facilities, transfers=0)
db_data = pd.read_excel('input_data.xlsx', sheet_name='data', index_col='facilities')

for facility in facilities:
    for parameter in db_data.columns:
        D.tdve[parameter].ts[facility] = at.TimeSeries(data_years, db_data.loc[facility,parameter], units='Number')
        D.tdve[parameter].write_assumption = True
    
D.save('books/carbomica_databook.xlsx')
    
#%% Step 3: generate empty progbooks in folder "templates/"
databook_name = 'books/carbomica_databook.xlsx'
P = at.Project(framework=F,databook=databook_name, do_run=False)
for facility in facilities:
    progbook_path = 'templates/carbomica_progbook_{}.xlsx'.format(facility)
    P.make_progbook(progbook_path,progs=interventions,data_start=data_years,data_end=data_years)
        
# Populate the progbooks that were just created and save the files to "books/"
D = at.ProjectData.from_spreadsheet(databook_name,framework=F) 
pb_costs = pd.read_excel('input_data.xlsx', sheet_name='costs', index_col='facilities')  
for facility in facilities:
    P = at.ProgramSet.from_spreadsheet(spreadsheet='templates/carbomica_progbook_{}.xlsx'.format(facility), framework=F, data=D, _allow_missing_data=True)
    for intervention in interventions:
        # Write in 'Program targeting' sheet
        P.programs[intervention].target_pops = [facility]
        P.programs[intervention].target_comps = ['facilities_number']
        
        # Write in 'Spending data' sheet
        P.programs[intervention].unit_cost = at.TimeSeries(assumption=pb_costs.loc[facility,intervention], units='$/person/year')
        P.programs[intervention].spend_data = at.TimeSeries(data_years,1e-16, units='$/year') # make initial spending a small, negligible but non-zero number for optimisation initialisation
        P.programs[intervention].capacity_constraint = at.TimeSeries(units='people')
        P.programs[intervention].coverage = at.TimeSeries(units='people')
        
        # Write in 'Program effects' sheet
        P.covouts[(intervention+'_cov', facility)] = at.programs.Covout(par=intervention+'_cov',pop=facility,cov_interaction='random',baseline=0,progs={intervention:1})
    
    P.save('books/carbomica_progbook_{}.xlsx'.format(facility))  
