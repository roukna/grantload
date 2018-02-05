import sys
import yaml
import csv

from vivo_connect import Connection
from owls import match_input
from author import Author
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
                item2 = params['AwardingDepartment']
                item2.name = row['Dept']

                # Check if Department exists
                try:
                    deets = {}
                    search_query = "get_department_list"
                    query_path = getattr(queries, search_query)
                    current_list = query_path.run(connection, **deets)
                    match = match_input(row['Dept'], current_list)
                except Exception as e:
                    print(e)
                    match = 'none'

                if match == 'none':
                    try:
                        item2.name = row['Dept']
                        item2.dep_type = 'Academic department'
                        params2 = {'Department': item2}
                        update_path = getattr(queries, 'make_department')
                        response = update_path.run(connection, **params2)
                        print(response)
                    except Exception as e:
                        print("Owl Post can not create a(n) " + item2.type +
                              " at this time. Please go to your vivo site and make it manually.")
                else:
                    item2.n_number = match
                    print("The n number for this " + item2.type + "is " + item2.n_number)

                item.direct_costs = row['Total_Direct']
                item.total_award_amount = row['Total_Awarded']
                item.name = row['Title']
                item3 = params['Contributor']
                item3.name = row['PI']

                # Check if Contributor exists
                try:
                    deets = {}
                    search_query = "get_person_list"
                    query_path = getattr(queries, search_query)
                    current_list = query_path.run(connection, **deets)
                    match2 = match_input(row['PI'], current_list)
                except Exception as e:
                    print(e)
                    match2 = 'none'

                if match2 == 'none':
                    try:
                        item3.name = row['PI']
                        item3.type = 'Co-Principal Investigator Role'
                        author = Author(connection)
                        author.name = row['PI']
                        author.first = row['PI'].split(" ")[0]
                        author.last = row['PI'].split(" ")[1]
                        update_path2 = getattr(queries, 'make_person')
                        params2 = {'Author': author}
                        try:
                            response2 = update_path2.run(connection, **params2)
                        except Exception as e:
                            print(e)
                            print("Owl Post can not create a(n) " + author.type +
                                  " at this time. Please go to your vivo site and make it manually.")

                        params3 = {'Contributor': item3, 'Author': author}
                        update_path3 = getattr(queries, 'make_contributor')
                        response3 = update_path3.run(connection, **params3)
                    except Exception as e:
                        print e
                        print("Owl Post can not create a(n) " + item3.type +
                              " at this time. Please go to your vivo site and make it manually.")
                else:
                    author = Author(connection)
                    author.n_number = match2
                    item3.type = 'Co-Principal Investigator Role'
                    print("The n number for this " + author.type + "is " + author.n_number)
                    try:
                        params3 = {'Contributor': item3, 'Author': author}
                        update_path3 = getattr(queries, 'make_contributor')
                        response3 = update_path3.run(connection, **params3)
                    except Exception as e:
                        print e
                        print("Owl Post can not create a(n) " + item3.type +
                              " at this time. Please go to your vivo site and make it manually.")

                item.start_date = row['Budget_Begin_Date']
                item.end_date = row['Budget_End_Date']
                print params
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

    connection = Connection(vivo_url, email, password, update_endpoint, query_endpoint)
    prepare_query(connection, input_file)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
