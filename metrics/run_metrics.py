import metrics
from pydriller import Repository
from metrics.data_provider.external_service_provider import External_Service_Provider

#Creates metric calculators and runs them on the given repository
#metrics_to_run - List of metric_* types to run
#Repository - Repository to analyze
#refactored_commits_list - List of commit hashes that contain refactoring work
#Returns list of calculated metrics, keyd with type of metric
def run_metrics(metrics_to_run, repository, branch, commits_of_interest, analyze_only_commits_of_interest):
    #Create metric calculators
    metric_calculators = {}
    for metric_to_run in metrics_to_run:
        metric_calculators[metric_to_run] = metric_to_run()
    #Run precalculations on the metric calculators
    if not branch:
        branch = None
    run_metric_precalculations(repository, branch, commits_of_interest, metric_calculators, analyze_only_commits_of_interest)
    return metric_calculators

#Get all unique data providers from the given metrics
def get_data_providers(metrics):
    all_providers = [dp for m in metrics for dp in metrics[m].get_data_providers()]
    #List of all unique providers
    unique_providers = []
    for provider in all_providers:
        if provider:
            #Is in the provider list?
            if not isinstance(provider, tuple([type(up) for up in unique_providers])):
                unique_providers.append(provider)
    return unique_providers

#Runs precalculations on the given metric calculators
def run_metric_precalculations(repository, branch, commits_of_interest, metrics_calculators, analyze_only_commits_of_interest):
    #All calculators, providers first then metric calculators
    #Order of placement is relevant for order of executions (data_providers => external_service_provider => metrics)
    data_calculators = get_data_providers(metrics_calculators) + [External_Service_Provider()] + [metrics_calculators[mc] for mc in metrics_calculators]

    #Reset all collectors
    for calculator in data_calculators:
        calculator.reset_data()

    #start tools and run repository pre_calcs
    for calculator in data_calculators:
        calculator.pre_calc_run_external(repository, branch, commits_of_interest, analyze_only_commits_of_interest)
        calculator.pre_calc_per_repository()

    #Run calculations on the commits and files
    for commit in Repository(repository, only_in_branch=branch).traverse_commits():
        try:
            #Are we a coi commit?
            is_commit_of_interest = (commit.hash in commits_of_interest)

            #Run exclusive commit calculations
            for calculator in data_calculators:
                calculator.pre_calc_per_commit_exlusive(commit, is_commit_of_interest, analyze_only_commits_of_interest)
            
            #Run per file calculations
            for modified_file in commit.modified_files:
                for calculator in data_calculators:
                    #if not deletion of the file
                    if modified_file.new_path:
                        calculator.pre_calc_per_file(modified_file, commit, is_commit_of_interest, analyze_only_commits_of_interest)
            
            #Run inclusive commit calculations
            for calculator in data_calculators:
                calculator.pre_calc_per_commit_inclusive(commit, is_commit_of_interest, analyze_only_commits_of_interest)
            
            #Run reset checks for calculators
            for calculator in data_calculators:
                calculator.pre_calc_check_for_reset(commit, is_commit_of_interest, analyze_only_commits_of_interest)
        except:
            #Git might trow not found errors so just continue
            continue

    #Wait for external tools to finish
    for calculator in data_calculators:
        calculator.pre_calc_wait_for_external()