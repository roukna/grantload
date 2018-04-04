import sys
import yaml
import csv

from owlpost.vivo_connect import Connection
from owlpost.owls import match_input
from vivo_queries.vdos import Author
from vivo_queries import queries
from parseinput import parse_input
import datetime


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
        for row in reader:

            params = template_mod.get_params(connection)
            grant_item = params['Grant']

            # Record ID
            row_id = row['recid']

            # Grant Name
            grant_item.name = row['Title'].strip()

            # Check if grant already exists
            match = match_input(connection, grant_item.name, "grant", True)

            if match:
                print "Grant" + grant_item.name + "already exists."
            else:
                # If grant does not exist, create one
                print "Grant:" + str(grant_item.name)

                # Awarding Organization
                if row['Prime_Sponsor_Division'].strip():
                    awardedby_item = params['AwardingDepartment']
                    awardedby_item.name = row['Prime_Sponsor_Division'].strip()

                    # Check if Organization exists
                    match = match_input(connection, awardedby_item.name, "organization", True)
                    # If not create one
                    if not match:
                        try:
                            awardedby_params = {'Organization': awardedby_item}
                            update_path = getattr(queries, 'make_organization')
                            update_path.run(connection, **awardedby_params)
                        except Exception as e:
                            print("Record ID: " + row_id + ". Unable to create Awarding Organization - " + awardedby_item.name)
                    else:
                        awardedby_item.n_number = match
                        print("Record ID: " + row_id + ". The n number for this Awarding Organization " + awardedby_item.name + " is " + awardedby_item.n_number)

                # Direct Costs
                if row['Total_Direct'].strip():
                    grant_item.direct_costs = row['Total_Direct'].strip()

                # Total Awarded Amount
                if row['Total_Awarded'].strip():
                    grant_item.total_award_amount = row['Total_Awarded'].strip()

                # Sponsor Award ID
                if row['Agency_Number'].strip():
                    grant_item.sponsor_award_id = row['Agency_Number'].strip()

                # Direct Award ID
                if row['DSR_Number'].strip():
                    grant_item.direct_award_id = row['DSR_Number'].strip()

                # Contributor PI
                if row['PI'].strip():
                    contributor_item = params['Contributor_PI']
                    contributor_item.name = row['PI'].strip()

                    # Check if Contributor PI exists
                    match = match_input(connection, contributor_item.name, "contributor", True)

                    # If not create one
                    if not match:
                        try:
                            contributor_item.type = 'Principal Investigator Role'

                            # Contributor Person details: First name, Last Name
                            author = Author(connection)
                            author.name = row['PI'].strip()
                            author.first = row['PI'].strip().split(" ")[0]
                            author.last = row['PI'].strip().split(" ")[-1]

                            # Create Person
                            update_path = getattr(queries, 'make_person')
                            author_params = {'Author': author}
                            update_path.run(connection, **author_params)
                        except Exception as e:
                            print("Record ID: " + row_id + ". Unable to create PI Person - " + contributor_item.name)
                            print e

                    else:
                        # Person exists
                        author = Author(connection)
                        author.n_number = match
                        author.name = row['PI'].strip()
                        contributor_item.type = 'Principal Investigator Role'
                        print("Record ID: " + row_id + ". The n number for this PI " + author.name + " is " + author.n_number)

                    # Create a contributor to the grant with the Person
                    try:
                        contributor_params = {'Contributor': contributor_item, 'Author': author}
                        update_path = getattr(queries, 'make_contributor')
                        update_path.run(connection, **contributor_params)
                    except Exception as e:
                        print("Record ID: " + row_id + ". Unable to create PI Contributor - " + contributor_item.name)
                        print e

                # Contributor Co-PI
                if row['CoPI'].strip():
                    contributor_item = params['Contributor_CoPI']
                    contributor_item.name = row['CoPI'].strip()

                    # Check if Contributor PI exists
                    match = match_input(connection, contributor_item.name, "contributor", True)

                    # If not create one
                    if not match:
                        try:
                            contributor_item.name = row['CoPI'].strip()
                            contributor_item.type = 'Co-Principal Investigator Role'

                            # Contributor Person details: First name, Last Name
                            author = Author(connection)
                            author.name = row['CoPI'].strip()
                            author.first = row['CoPI'].strip().split(" ")[0]
                            author.last = row['CoPI'].strip().split(" ")[-1]

                            # Create Person
                            update_path = getattr(queries, 'make_person')
                            author_params = {'Author': author}
                            update_path.run(connection, **author_params)

                        except Exception as e:
                            print("Record ID: " + row_id + ". Unable to create Co-PI Person - " + contributor_item.name)
                            print e
                    else:
                        # Person exists
                        author = Author(connection)
                        author.n_number = match
                        author.name = row['PI'].strip()
                        contributor_item.type = 'Co-Principal Investigator Role'
                        print("Record ID: " + row_id + ". The n number for this " + author.type + " is " + author.n_number)

                    # Create a contributor to the grant with the Person
                    try:
                        contributor_params = {'Contributor': contributor_item, 'Author': author}
                        update_path3 = getattr(queries, 'make_contributor')
                        update_path3.run(connection, **contributor_params)
                    except Exception as e:
                        print("Record ID: " + row_id + ". Unable to create Co-PI Contributor - " + contributor_item.name)
                        print e

                # Administered By
                if row['Prime_Sponsor']:
                    adminby_item = params['AdministeredBy']
                    adminby_item.name = row['Prime_Sponsor'].strip()

                    # Check if Administered By Organization exists
                    match = match_input(connection, adminby_item.name, "organization", True)
                    # If not create one
                    if not match:
                        try:
                            adminby_params = {'Organization': adminby_item}
                            update_path = getattr(queries, 'make_organization')
                            update_path.run(connection, **adminby_params)
                        except Exception as e:
                            print("Record ID: " + row_id + ". Unable to create Administered By Organization - " + adminby_item.name)
                            print e
                    else:
                        adminby_item.n_number = match
                        print("Record ID: " + row_id + ". The n number for this " + adminby_item.type + " is " + adminby_item.n_number)

                # Start and End date
                if row['Project_Begin_Date'] and row['Project_End_Date']:
                    # Start date
                    grant_item.start_date = datetime.datetime.strptime(row['Project_Begin_Date'], '%m/%d/%y').strftime('%Y-%m-%dT%H:%M:%S')
                    # End date
                    grant_item.end_date = datetime.datetime.strptime(row['Project_End_Date'], '%m/%d/%y').strftime('%Y-%m-%dT%H:%M:%S')
                    print params

                template_mod.run(connection, **params)


def main(argv1, argv2):
    config_path = argv1
    input_file = argv2
    output_file = input_file + "_" + datetime.datetime.now().strftime("%Y%m%d") + '.csv'
    parse_input(input_file, output_file)
    config = get_config(config_path)
    email = config.get('email')
    password = config.get('password')
    update_endpoint = config.get('update_endpoint')
    query_endpoint = config.get('query_endpoint')
    vivo_url = config.get('upload_url')

    connection = Connection(vivo_url, email, password, update_endpoint, query_endpoint)
    prepare_query(connection, output_file)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
