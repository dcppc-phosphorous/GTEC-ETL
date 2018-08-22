#!/usr/bin/env python3

# Create DATS JSON description of TOPMed public data.

import argparse
from ccmm.dats.datsobj import DatsObj
from collections import OrderedDict
from ccmm.dats.datsobj import DATSEncoder
import ccmm.topmed.dna_extracts
import ccmm.topmed.wgs_datasets
import ccmm.topmed.public_metadata
import ccmm.topmed.restricted_metadata
import json
import logging
import os
import re
import sys

# Record study variables as dimensions of the study/Dataset.
def add_study_vars(study, study_md):
    all_vars = []
    dbgap_vars = {}

    for var_type in ('Subject', 'Subject_Phenotypes', 'Sample', 'Sample_Attributes'):
        if var_type in study_md:
            var_data = study_md[var_type]['var_report']['data']
            vars = var_data['vars']
            all_vars.extend(vars)

    # create a Dimension for each one
    for var in all_vars:
        var_name = var['var_name']
        id = DatsObj("Identifier", [
                ("identifier",  var['id']),
                ("identifierSource", "dbGaP")])
        
        dim = DatsObj("Dimension", [
                ("identifier", id),
                ("name", DatsObj("Annotation", [("value", var_name)])),
                ("description", var['description'])
                # TODO: include stats
                ])  
        study.getProperty("dimensions").append(dim)

        # track dbGaP variable Dimensions by dbGaP id
        if var['id'] in dbgap_vars:
            logging.fatal("duplicate definition found for dbGaP variable " + var_name + " with accession=" + var['id'])
            sys.exit(1)
        dbgap_vars[var['id']] = dim

    return dbgap_vars

# ------------------------------------------------------
# main()
# ------------------------------------------------------

def main():

    # input
    parser = argparse.ArgumentParser(description='Create DATS JSON for TOPMed public metadata.')
    parser.add_argument('--output_file', default='.', help ='Output file path for the DATS JSON file containing the top-level DATS Dataset.')
    parser.add_argument('--dbgap_public_xml_path', required=True, help ='Path to directory that contains public dbGaP metadata files e.g., *.data_dict.xml and *.var_report.xml')
    parser.add_argument('--dbgap_protected_metadata_path', required=False, help ='Path to directory that contains access-controlled dbGaP tab-delimited metadata files.')
    args = parser.parse_args()

    # logging
    logging.basicConfig(level=logging.INFO)
#    logging.basicConfig(level=logging.DEBUG)

    # create top-level dataset
    topmed_dataset = ccmm.topmed.wgs_datasets.get_dataset_json()

    # index studies by id
    studies_by_id = {}
    for tds in topmed_dataset.get("hasPart"):
        study_id = tds.get("identifier").get("identifier")
        if study_id in studies_by_id:
            logging.fatal("encountered duplicate study_id " + study_id)
            sys.exit(1)
        m = re.match(r'^(phs\d+\.v\d+)\.p\d+$', study_id)
        if m is None:
            logging.fatal("unable to parse study_id " + study_id)
            sys.exit(1)
        studies_by_id[m.group(1)] = tds

    # if not processing protected metadata then generate representative DATS JSON using only the public metadata
    pub_xp = args.dbgap_public_xml_path
    restricted_mp = args.dbgap_protected_metadata_path
    # read public metadata
    study_pub_md = ccmm.topmed.public_metadata.read_study_metadata(pub_xp)
    
    # Study Variables
    STUDY_VARS = OrderedDict([("value", "Property or Attribute"), ("valueIRI", "http://purl.obolibrary.org/obo/NCIT_C20189")])

    # case 1: process public metadata only (i.e., data dictionaries and variable reports only)
    if restricted_mp is None:
        for study_id in study_pub_md:
            study = studies_by_id[study_id]
            study_md = study_pub_md[study_id]
            study_md['dbgap_vars'] = add_study_vars(study, study_md)
            # only create DNA extracts if there are sample attributes
            if 'Sample_Attributes' in study_md:
                # create dummy/synthetic DATS instance based on variable reports
                # note that this may result in nonsensical combinations of sample and/or subject variable values
                dna_extract = ccmm.topmed.dna_extracts.get_synthetic_single_dna_extract_json_from_public_metadata(study, study_md)
                # insert synthetic sample into relevant study/Dataset
                study.set("isAbout", [dna_extract])

    # case 2: process both public metadata and access-controlled dbGaP metadata
    else:
        study_restricted_md = ccmm.topmed.restricted_metadata.read_study_metadata(restricted_mp)
        for study_id in study_pub_md:
            study = studies_by_id[study_id]
            study_md = study_pub_md[study_id]
            study_md['dbgap_vars'] = add_study_vars(study, study_md)
            # only create DNA extracts if there are sample attributes
            if 'Sample_Attributes' in study_md:
                dna_extracts = ccmm.topmed.dna_extracts.get_dna_extracts_json_from_restricted_metadata(study, study_md, study_restricted_md[study_id])
                study.set("isAbout", dna_extracts)

    # write Dataset to DATS JSON file
    with open(args.output_file, mode="w") as jf:
        jf.write(json.dumps(topmed_dataset, indent=2, cls=DATSEncoder))

if __name__ == '__main__':
    main()
