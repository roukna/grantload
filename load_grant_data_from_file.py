import sys
import yaml
import csv

from owlery import Connection
import queries


def get_config(config_path):
    try:
        with open(config_path, 'r') as config_file:
            config = yaml.load(config_file.read())
    except:
        print("Error: Check config file")
        exit()
    return config


def prepare_query(connection, input_file):
    template_choice = 'make_grant'

    template_mod = getattr(queries, template_choice)
    params = template_mod.get_params(connection)

    table1_fields = ['recid', 'Fiscal_Year', 'Academic_Unit', 'College', 'Dept', 'DeptID', 'Record_Status',
                     'PS_Project', 'DSR_Number', 'Award_Date', 'Total_Direct', 'Total_Indirect', 'Total_Awarded',
                     'Prime_Sponsor_Type', 'Prime_Sponsor', 'Prime_Sponsor_Division', 'Project_UPN', 'Title', 'PI',
                     'PI_UFID', 'CoPI_UFID', 'Budget_Begin_Date', 'Budget_End_Date', 'Project_Begin_Date',
                     'Project_End_Date', 'Proj_Funding_to_Date', 'Type', 'Category', 'Program_Code',
                     'No_Cost_Extension', 'Special_Program', 'CFDA_Number', 'Humans', 'Human_Approval_Number',
                     'Human_Cert_Expiration', 'Animals', 'Animal_Approval_Number', 'Animal_Cert_Expiration',
                     'IRB_MultiProjects', 'IRB_MultiApprovals', 'DNA', 'BioHazards', 'Clinical_Trial',
                     'Funds_Restricted', 'Terms_Conditions', 'KK_Level', 'Prime_Agency', 'Prime_Agency_Flag',
                     'Agency_Category', 'Sponsoring_Agency', 'Agency_Number', 'Subcontract_Type', 'SubAgency_Category',
                     'Subcontract_Agency', 'CFSA_Number', 'Financial_Disclosure', 'Financial_Disclosure_Date',
                     'IDC_Prohibited', 'Indirect_Base_On', 'Indirect_Rate_On', 'Indirect_Base_Off',
                     'Indirect_Rate_Off', 'Cost_Share_On', 'Cost_Share_Off', 'VolCostshareOn', 'VolCostShareOff',
                     'PS_Contract', 'Contract_DeptID', 'Contract_PI_UFID', 'Contract_PI', 'Project_DeptID',
                     'Project_PI_UFID', 'CoPI', 'Major_Subdivision']

    vivo_fields = ['Dept', 'Total_Direct', 'Total_Awarded', 'Title', 'PI', 'Budget_Begin_Date',
                   'Budget_End_Date', 'Project_PI_UFID']

    with open(input_file) as csvfile:
        reader = csv.DictReader(csvfile, fieldnames=table1_fields)
        reader.next()
        item = params['Grant']
        for row in reader:

            # Check if grant already exists
            query = "SELECT ?n_number WHERE {?n_number <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://vivoweb.org/ontology/core#Grant> . " + "?n_number <http://www.w3.org/2000/01/rdf-schema#label> \"" + row['Title'] + "\"}"
            response = (connection.run_query(query)).json()

            if not response['results']['bindings']:
                print "Grant:" + str(item.name)
                item.awarded_by = row['Dept']
                item.awarding_dep_type = 'Academic department'
                item.direct_costs = row['Total_Direct']
                item.total_award_amount = row['Total_Awarded']
                item.name = row['Title']
                item.contributor_role = 'Co-Principal Investigator Role'
                item.contributor = row['PI']
                item.start_date = row['Budget_Begin_Date']
                item.end_date = row['Budget_Begin_Date']
                response = template_mod.run(connection, **params)
            else:
                # Grant already exist
                pass


def main(argv1, argv2):
    config_path = argv1
    input_file = argv2
    config = get_config(config_path)
    email = config.get('email')
    password = config.get('password')
    update_endpoint = config.get('update_endpoint')
    query_endpoint = config.get('query_endpoint')
    vivo_url = config.get('upload_url')
    check_url = config.get('checking_url')

    connection = Connection(vivo_url, check_url, email, password, update_endpoint, query_endpoint)
    prepare_query(connection, input_file)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
