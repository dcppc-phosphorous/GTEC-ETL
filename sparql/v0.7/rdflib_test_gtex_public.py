#!/usr/bin/env python3

import argparse
import logging
import rdflib 
import rdflib_util as ru
import rdflib_list_2nd_level_datasets
import rdflib_list_dataset_variables
import rdflib_list_study_group_members
import rdflib_tabular_dump
import re
import sys

# Run test queries on TOPMed instance.

DATASETS = ['phs000424.v7.p2']
STUDY_GROUPS = ['all subjects']

# ------------------------------------------------------
# main()
# ------------------------------------------------------

def main():
    
    # input
    parser = argparse.ArgumentParser(description='Run test queries on TOPMed instance.')
    parser.add_argument('--dats_file', help ='Path to TOPMed or GTEx DATS JSON-LD file.')
    args = parser.parse_args()

    # logging
    logging.basicConfig(level=logging.INFO)

    # parse JSON LD
    g = ru.read_json_ld_graph(args.dats_file)

    # list 2nd-level datasets
    datasets = rdflib_list_2nd_level_datasets.list_2nd_level_datasets(g)
    rdflib_list_2nd_level_datasets.print_results(datasets)

    variables = rdflib_list_dataset_variables.list_dataset_variables(g)
    rdflib_list_dataset_variables.print_results(variables)
    
    # list study group members
    for dataset_id in (DATASETS):
        for study_group in (STUDY_GROUPS):
            members = rdflib_list_study_group_members.list_study_group_members(g, dataset_id, study_group)
            rdflib_list_study_group_members.print_results(members, dataset_id, study_group)

    # create tabular data dump
    rdflib_tabular_dump.print_tabular_dump(g)

if __name__ == '__main__':
    main()
