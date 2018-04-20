import yaml
import csv
import json

from owlpost.vivo_connect import Connection
from owlpost.owls import match_input
from vivo_queries import queries
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

    # table1_fields = ['recid', 'Fiscal_Year', 'Academic_Unit', 'College', 'Dept', 'DeptID', 'Record_Status',
    #                  'PS_Project', 'DSR_Number', 'Award_Date', 'Total_Direct', 'Total_Indirect', 'Total_Awarded',
    #                  'Prime_Sponsor_Type', 'Prime_Sponsor', 'Prime_Sponsor_Division', 'Project_UPN', 'Title', 'PI',
    #                  'PI_UFID', 'CoPI_UFID', 'Budget_Begin_Date', 'Budget_End_Date', 'Project_Begin_Date',
    #                  'Project_End_Date', 'Proj_Funding_to_Date', 'Type', 'Category', 'Program_Code',
    #                  'No_Cost_Extension', 'Special_Program', 'CFDA_Number', 'Humans', 'Human_Approval_Number',
    #                  'Human_Cert_Expiration', 'Animals', 'Animal_Approval_Number', 'Animal_Cert_Expiration',
    #                  'IRB_MultiProjects', 'IRB_MultiApprovals', 'DNA', 'BioHazards', 'Clinical_Trial',
    #                  'Funds_Restricted', 'Terms_Conditions', 'KK_Level', 'Prime_Agency', 'Prime_Agency_Flag',
    #                  'Agency_Category', 'Sponsoring_Agency', 'Agency_Number', 'Subcontract_Type', 'SubAgency_Category',
    #                  'Subcontract_Agency', 'CFSA_Number', 'Financial_Disclosure', 'Financial_Disclosure_Date',
    #                  'IDC_Prohibited', 'Indirect_Base_On', 'Indirect_Rate_On', 'Indirect_Base_Off',
    #                  'Indirect_Rate_Off', 'Cost_Share_On', 'Cost_Share_Off', 'VolCostshareOn', 'VolCostShareOff',
    #                  'PS_Contract', 'Contract_DeptID', 'Contract_PI_UFID', 'Contract_PI', 'Project_DeptID',
    #                  'Project_PI_UFID', 'CoPI', 'Major_Subdivision']
    #
    # vivo_fields = ['Dept', 'Total_Direct', 'Total_Awarded', 'Title', 'PI', 'Budget_Begin_Date',
    #                'Budget_End_Date', 'Project_PI_UFID']

    data = json.load(open(input_file), strict=False)
    row_id = 0

    for row in data:

        params = template_mod.get_params(connection)
        grant_item = params['Grant']

        # Record ID
        row_id = row['awards_history_id']

        # Grant Name
        grant_item.name = scrub(row['CLK_AWD_FULL_TITLE'].strip())

        # Check if grant already exists
        match = match_input(connection, grant_item.name, "grant", True)

        if match:
            print("Record ID: " + str(row_id) + " Grant" + grant_item.name + "already exists.")
        else:
            # If grant does not exist, create one
            print("Grant:" + str(grant_item.name))

            # Awarding Organization
            if row['REPORTING_SPONSOR_NAME'].strip():
                awardedby_item = params['AwardingDepartment']
                awardedby_item.name = row['REPORTING_SPONSOR_NAME'].strip()

                # Check if Organization exists
                match = match_input(connection, awardedby_item.name, "organization", True)
                # If not create one
                if not match:
                    try:
                        update_path = getattr(queries, 'make_organization')
                        awardedby_params = update_path.get_params(connection)
                        awardedby_params['Organization'] = awardedby_item
                        update_path.run(connection, **awardedby_params)
                    except Exception as e:
                        print("Record ID: " + str(row_id) + ". Unable to create Awarding Organization - " + awardedby_item.name)
                else:
                    awardedby_item.n_number = match
                    print("Record ID: " + str(row_id) + ". The n number for this Awarding Organization " + awardedby_item.name + " is " + awardedby_item.n_number)

            # Direct Costs
            if row['DIRECT_AMOUNT']:
                grant_item.direct_costs = row['DIRECT_AMOUNT']

            # Total Awarded Amount
            if row['SPONSOR_AUTHORIZED_AMOUNT']:
                grant_item.total_award_amount = row['SPONSOR_AUTHORIZED_AMOUNT']

            # Sponsor Award ID
            if row['CLK_AWD_SPONSOR_AWD_ID'].strip():
                grant_item.sponsor_award_id = row['CLK_AWD_SPONSOR_AWD_ID'].strip()

            # Local Award ID
            if row['CLK_AWD_ID'].strip():
                grant_item.direct_award_id = row['CLK_AWD_ID'].strip()

            # Contributor PI
            if row['CLK_AWD_PI'].strip():
                contributor_item = params['Contributor_PI']
                contributor_item.name = row['CLK_AWD_PI'].strip()

                # Check if Contributor PI exists
                match = match_input(connection, contributor_item.name, "contributor_pi", True)

                # If not create one
                if not match:
                    try:
                        contributor_item.type = 'Principal Investigator Role'

                        # Contributor Person details: First name, Last Name
                        contributor_item.name = row['CLK_AWD_PI'].strip()
                        contributor_item.first = row['CLK_AWD_PI'].strip().split(" ")[0]
                        if len(row['CLK_AWD_PI'].strip().split(" ")) == 3:
                            contributor_item.middle = row['CLK_AWD_PI'].strip().split(" ")[1]
                        else:
                            contributor_item.middle = ''
                        contributor_item.last = row['CLK_AWD_PI'].strip().split(" ")[-1]

                        update_path = getattr(queries, 'make_contributor')
                        contributor_params = update_path.get_params(connection)
                        contributor_params['Contributor'] = contributor_item
                        update_path.run(connection, **contributor_params)
                    except Exception as e:
                        print(e)
                        print("Record ID: " + str(row_id) + ". Unable to create Principle Investigator - " + contributor_item.name)

            # Contributor Co-PI
            # if row['CoPI'].strip():
            #     contributor_item = params['Contributor_CoPI']
            #     contributor_item.name = row['CoPI'].strip()
            #
            #     # Check if Contributor PI exists
            #     match = match_input(connection, contributor_item.name, "contributor_copi", True)
            #
            #     # If not create one
            #     if not match:
            #         try:
            #             contributor_item.name = row['CoPI'].strip()
            #             contributor_item.type = 'Co-Principal Investigator Role'
            #
            #             # Contributor Person details: First name, Last Name
            #             contributor_item.name = row['CoPI'].strip()
            #             contributor_item.first = row['CoPI'].strip().split(" ")[0]
            #             if len(row['CoPI'].strip().split(" ")) == 3:
            #                 contributor_item.middle = row['CoPI'].strip().split(" ")[1]
            #             else:
            #                 contributor_item.middle = ''
            #             contributor_item.last = row['CoPI'].strip().split(" ")[-1]
            #
            #             update_path3 = getattr(queries, 'make_contributor')
            #             contributor_params = update_path3.get_params(connection)
            #             contributor_params['Contributor'] = contributor_item
            #             update_path3.run(connection, **contributor_params)
            #         except Exception as e:
            #             print("Record ID: " + row_id + ". Unable to create Co-Principle Investigator - " + contributor_item.name)

            # Administered By
            if row['CLK_AWD_PRIME_SPONSOR_NAME']:
                adminby_item = params['AdministeredBy']
                adminby_item.name = row['CLK_AWD_PRIME_SPONSOR_NAME'].strip()

                # Check if Administered By Organization exists
                match = match_input(connection, adminby_item.name, "organization", True)
                # If not create one
                if not match:
                    try:
                        update_path = getattr(queries, 'make_organization')
                        adminby_params = update_path.get_params(connection)
                        adminby_params['Organization'] = adminby_item
                        update_path.run(connection, **adminby_params)
                    except Exception as e:
                        print("Record ID: " + str(row_id) + ". Unable to create Administered By Organization - " + adminby_item.name)
                        print(e)
                else:
                    adminby_item.n_number = match
                    print("Record ID: " + str(row_id) + ". The n number for this " + adminby_item.type + " is " + adminby_item.n_number)

            # Start and End date
            if row['CLK_AWD_OVERALL_START_DATE'] and row['CLK_AWD_OVERALL_END_DATE']:
                # Start date
                try:
                    grant_item.start_date = datetime.datetime.strptime(row['CLK_AWD_OVERALL_START_DATE'],
                                                                       '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S')
                    grant_item.end_date = datetime.datetime.strptime(row['CLK_AWD_OVERALL_END_DATE'],
                                                                     '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%dT%H:%M:%S')
                except Exception as e:
                    print("Record ID: " + str(row_id) + ". Unable to parse datetime interval: " +
                          str(row['CLK_AWD_OVERALL_START_DATE']) + "-" + str(row['CLK_AWD_OVERALL_END_DATE']))
                    print(e)
                print(params)

            template_mod.run(connection, **params)


def scrub(label):
    clean_label = label.replace('"', '\\"')
    return clean_label


def main():
    input_dir = '/var'
    config_path = input_dir + '/config.yaml'
    input_file = input_dir + '/UF_Grant_Data.json'
    config = get_config(config_path)
    email = config.get('email')
    password = config.get('password')
    update_endpoint = config.get('update_endpoint')
    query_endpoint = config.get('query_endpoint')
    vivo_url = config.get('upload_url')

    connection = Connection(vivo_url, email, password, update_endpoint, query_endpoint)
    prepare_query(connection, input_file)


if __name__ == '__main__':
    main()
