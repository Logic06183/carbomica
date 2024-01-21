import atomica as at
import utils as ut
import os
if not os.path.exists('results'): os.makedirs('results')
if not os.path.exists('figs'): os.makedirs('figs')


def coverage_scenario(P, progset, start_year, facility_code):
    '''
    Run a scenario where interventions are individually fully covered.
    Results on emission reductions are saved in an excel sheet.
    :param P: Atomica project.
    :param start_year: Start year of simulations.
    :param facility_code: Code of the facility.
    :return: 
    '''
    results_scenario = [P.run_sim(parset='default',result_name='Status-quo')] # run status-quo
    
    for prog in progset.programs:
        coverage_scenario = {prog_all: 0 for prog_all in progset.programs}
        coverage_scenario[prog] = 1
        instructions = at.ProgramInstructions(start_year=start_year, coverage=coverage_scenario) # define program instructions
        result_coverage = P.run_sim(parset='default',progset=P.progsets[0], progset_instructions=instructions, result_name=progset.programs[prog].label) # run budget scenario
        results_scenario.append(result_coverage)
        
    # Calculate emissions 
    ut.calc_emissions(results_scenario,start_year,facility_code,file_name='coverage_scenario_Emissions_{}'.format(facility_code),title='CO2e emissions - full coverage')

def budget_scenario(P, progset, start_year, facility_code, spending:int):
    '''
    Run a scenario where spending on interventions are individually specified.
    Results on emission reductions are saved in an excel sheet.
    :param P: Atomica project.
    :param start_year: Start year of simulations.
    :param facility_code: Code of the facility.
    :param spending: Spending on individual interventions.
    :return: 
    '''
    results_scenario = [P.run_sim(parset='default',result_name='Status-quo')] # run status-quo
    
    for prog in progset.programs:
        budget_scenario = {prog_all: 0 for prog_all in progset.programs}
        budget_scenario[prog] = spending
        instructions = at.ProgramInstructions(start_year=start_year, alloc=budget_scenario) # define program instructions
        result_budget = P.run_sim(parset='default',progset=P.progsets[0], progset_instructions=instructions, result_name=progset.programs[prog].label) # run budget scenario
        results_scenario.append(result_budget)
        
    # Calculate emissions 
    ut.calc_emissions(results_scenario,start_year,facility_code,file_name='budget_scenario_Emissions_{}'.format(facility_code),title='CO2e emissions - fixed budget (${:0,.0f})'.format(spending))

def optimization(P, progset, start_year, facility_code, budgets:list):
    '''
    Optimize spending allocation on interventions by minizing emissions for a set total budget.
    Results on emission reductions and optimized budget allocations are saved in an excel sheet.
    :param P: Atomica project.
    :param start_year: Start year of simulations.
    :param facility_code: Code of the facility.
    :param budgets: List of budgets to optimize.
    :return: 
    '''
    instructions = at.ProgramInstructions(alloc=P.progsets[0], start_year=start_year) # Baseline spending
    adjustments = [at.SpendingAdjustment(prog, start_year, 'abs', 0.0, 10e6) for prog in progset.programs] # Adjustments (no spending constraint on any intervention)
    measurables = [at.MinimizeMeasurable('co2e_emissions',start_year)] # Measurables (objective function: minimize total emissions)
    
    # Run optimization
    # Initialize with PSO
    result_names = []
    for budget in budgets:
        result_names.append('${:0,.0f}'.format(budget))
        
    results_optimized = []
    for budget, name in zip(budgets, result_names):
        constraints = at.TotalSpendConstraint(total_spend=budget, t=start_year) # constraint on total spending
        # Run optimization
        optimization = at.Optimization(name='default', method='pso', 
                                       adjustments=adjustments, measurables=measurables, constraints=constraints)
        optimized_instructions = at.optimize(P, optimization, P.parsets[0],P.progsets[0], instructions=instructions, optim_args={"maxiter": 10})
        result_optimized = P.run_sim(P.parsets[0],P.progsets[0], progset_instructions=optimized_instructions)
        
        # Compile results
        result_optimized.name = name
        results_optimized.append(result_optimized)
    
    # Extract spending to use as initial conditions in ASD loop
    allocation_initial, _ = ut.write_alloc_excel(progset, results_optimized, start_year, print_results=False)
    
    # Refine optimization with ASD
    results_optimized = [P.run_sim(parset='default',result_name='Status-quo')]
    for budget, name in zip(budgets, result_names):
        constraints = at.TotalSpendConstraint(total_spend=budget, t=start_year) # constraint on total spending
        adjustments = [at.SpendingAdjustment(prog, start_year, initial=allocation_initial[name][progset.programs[prog].label]) for prog in progset.programs.keys()]
        
        # Run optimization
        optimization = at.Optimization(name='default', method='asd', 
                                       adjustments=adjustments, measurables=measurables, constraints=constraints)
        optimized_instructions = at.optimize(P, optimization, P.parsets[0],P.progsets[0], instructions=instructions)
        result_optimized = P.run_sim(P.parsets[0],P.progsets[0], progset_instructions=optimized_instructions)
        
        # Compile results
        result_optimized.name = name
        results_optimized.append(result_optimized)
        
    # Plot and save emissions
    ut.calc_emissions(results_optimized,start_year,facility_code,file_name='optimization_Emissions_{}'.format(facility_code))
    
    # Plot budget allocation (exclude status-quo result)
    ut.plot_allocation(results_optimized[1:],file_name='optimization_Budget_Allocation_{}'.format(facility_code)) # allocation
    
    # Save budget allocation and interventions coverage (exclude status-quo result)
    ut.write_alloc_excel(progset, results_optimized[1:], start_year,file_name='results/optimization_Budget_Allocation_{}'.format(facility_code))
