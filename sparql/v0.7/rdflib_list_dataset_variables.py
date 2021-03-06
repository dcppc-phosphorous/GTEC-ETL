#!/usr/bin/env python3

import argparse
import logging
import rdflib 
import rdflib_util as ru
import re
import sys

# Implementation of "list dataset variables" query directly in Python using
# rdflib API calls.

def list_dataset_variables(g, dataset_id=None):
    
    # obo:IAO_0000100 - "data set"
    # obo:IAO_0000577 - "centrally registered identifier symbol"
    # obo:BFO_0000051 - "has part"
    # obo:STATO_0000258 - "variable"
    # obo:IAO_0000300 - "textual entity"
    # obo:IAO_0000590 - "a textual entity that denotes a particular in reality"

    #            SELECT DISTINCT ?dbgap_study_acc ?dbgap_var_acc ?pname ?descr
    #            WHERE {
    #  ---->         ?dataset a obo:IAO_0000100.
    #                ?dataset obo:IAO_0000577 ?dataset_id.
    #                ?dataset_id sdo:identifier ?dbgap_study_acc.
    #                ?dataset obo:BFO_0000051 ?dim1.
    #                ?dim1 a obo:STATO_0000258.
    #                ?dim1 obo:IAO_0000300 ?descr.
    #                ?dim1 obo:IAO_0000577 ?dim1_id.
    #                ?dim1_id sdo:identifier ?dbgap_var_acc.
    #                ?dim1 obo:IAO_0000590 ?propname.
    #                ?propname sdo:value ?pname.
    #            }
    #            ORDER BY ?dbgap_study_acc ?dbgap_var_acc

    # find ALL Datasets
    all_datasets = [s for (s,p,o) in g.triples((None, None, ru.DATS_DATASET_TERM))]

    #            SELECT DISTINCT ?dbgap_study_acc ?dbgap_var_acc ?pname ?descr
    #            WHERE {
    #                ?dataset a obo:IAO_0000100.
    #  ---->         ?dataset obo:IAO_0000577 ?dataset_id.
    #  ---->         ?dataset_id sdo:identifier ?dbgap_study_acc.
    #                ?dataset obo:BFO_0000051 ?dim1.
    #                ?dim1 a obo:STATO_0000258.
    #                ?dim1 obo:IAO_0000300 ?descr.
    #                ?dim1 obo:IAO_0000577 ?dim1_id.
    #                ?dim1_id sdo:identifier ?dbgap_var_acc.
    #                ?dim1 obo:IAO_0000590 ?propname.
    #                ?propname sdo:value ?pname.
    #            }
    #            ORDER BY ?dbgap_study_acc ?dbgap_var_acc

    # get DATS identifier for each one - DATS schema specifies the mapping should be 1-1
    dataset_ids = {}
    datasets = []
    for d in all_datasets:
        for (s,p,o) in g.triples((d,ru.CENTRAL_ID_TERM,None)):
            for (s2,p2,o2) in g.triples((o, ru.SDO_IDENT_TERM, None)):
                dataset_ids[d] = o2
        if d in dataset_ids:
            datasets.append(d)
                
    # filter datasets by id if one was specified
    datasets = [d for d in datasets if (dataset_id is None) or (rdflib.term.Literal(dataset_id) == dataset_ids[d])]

    #            SELECT DISTINCT ?dbgap_study_acc ?dbgap_var_acc ?pname ?descr
    #            WHERE {
    #                ?dataset a obo:IAO_0000100.
    #                ?dataset obo:IAO_0000577 ?dataset_id.
    #                ?dataset_id sdo:identifier ?dbgap_study_acc.
    #  ---->         ?dataset obo:BFO_0000051 ?dim1.
    #  ---->         ?dim1 a obo:STATO_0000258
    #                ?dim1 obo:IAO_0000300 ?descr.
    #                ?dim1 obo:IAO_0000577 ?dim1_id.
    #                ?dim1_id sdo:identifier ?dbgap_var_acc.
    #                ?dim1 obo:IAO_0000590 ?propname.
    #                ?propname sdo:value ?pname.
    #            }
    #            ORDER BY ?dbgap_study_acc ?dbgap_var_acc

    # get all dimensions of each Dataset

    dataset_dims = {}
    for d in datasets:
        dims = []
        for (s,p,o) in g.triples((d, ru.HAS_PART_TERM, None)):
            for (s2,p2,o2) in g.triples((o, ru.RDF_TYPE_TERM, ru.DATS_DIMENSION_TERM)):
                dims.append(o)
        dataset_dims[d] = dims

    #            SELECT DISTINCT ?dbgap_study_acc ?dbgap_var_acc ?pname ?descr
    #            WHERE {
    #                ?dataset a obo:IAO_0000100.
    #                ?dataset obo:IAO_0000577 ?dataset_id.
    #                ?dataset_id sdo:identifier ?dbgap_study_acc.
    #                ?dataset obo:BFO_0000051 ?dim1.
    #                ?dim1 a obo:STATO_0000258.
    #  ---->         ?dim1 obo:IAO_0000300 ?descr.
    #  ---->         ?dim1 obo:IAO_0000577 ?dim1_id.
    #  ---->         ?dim1_id sdo:identifier ?dbgap_var_acc.
    #  ---->         ?dim1 obo:IAO_0000590 ?propname.
    #  ---->         ?propname sdo:value ?pname.
    #            }
    #            ORDER BY ?dbgap_study_acc ?dbgap_var_acc

    # get Dimension description
    dim_descrs = {}
    for d in datasets:
        for dim in dataset_dims[d]:
            for (s,p,o) in g.triples((dim, ru.DESCR_TERM, None)):
                dim_descrs[dim] = o

    # get Dimension identifier
    dim_ids = {}
    for d in datasets:
        for dim in dataset_dims[d]:
            for (s,p,o) in g.triples((dim, ru.CENTRAL_ID_TERM, None)):
                for(s2,p2,o2) in g.triples((o, ru.SDO_IDENT_TERM, None)):
                    dim_ids[dim] = o2

    # get Dimension name
    dim_names = {}
    for d in datasets:
        for dim in dataset_dims[d]:
            for (s,p,o) in g.triples((dim, ru.NAME_TERM, None)):
                for(s2,p2,o2) in g.triples((o, ru.SDO_VALUE_TERM, None)):
                    dim_names[dim] = o2

    #            SELECT DISTINCT ?dbgap_study_acc ?dbgap_var_acc ?pname ?descr
    #            WHERE {
    #                ?dataset a obo:IAO_0000100.
    #                ?dataset obo:IAO_0000577 ?dataset_id.
    #                ?dataset_id sdo:identifier ?dbgap_study_acc.
    #                ?dataset obo:BFO_0000051 ?dim1.
    #                ?dim1 a obo:STATO_0000258.
    #                ?dim1 obo:IAO_0000300 ?descr.
    #                ?dim1 obo:IAO_0000577 ?dim1_id.
    #                ?dim1_id sdo:identifier ?dbgap_var_acc.
    #                ?dim1 obo:IAO_0000590 ?propname.
    #                ?propname sdo:value ?pname.
    #            }
    #  ---->     ORDER BY ?dbgap_study_acc ?dbgap_var_acc

    datasets_with_ids = [{"d":d, "i":dataset_ids[d]} for d in datasets if d in dataset_ids]
    datasets_with_ids.sort(key=lambda x: x["i"])
    variables_l = []

    for ds in datasets_with_ids:
        dims = dataset_dims[ds['d']]
        # filter out those with no id
        # (may still fail if the description or name are missing)
        dims_with_atts = [{"d":d, "descr": dim_descrs[d], "id": dim_ids[d], "name": dim_names[d] } for d in dims if d in dim_ids]
        dims_with_atts.sort(key = lambda x: x["id"])
        for d in dims_with_atts:
            variables_l.append({"study": ds["i"], "var_dbgap_id": d["id"], "var_name": d["name"], "var_descr": d["descr"] })

    return variables_l

def print_results(variables, dataset_id=None):
    title = "Dataset variables"
    if dataset_id is not None:
        title += " for dataset " + dataset_id
    title += ":"

    print()
    print(title)
    print()
    print("dbGaP Study\tdbGaP variable\tName\tDescription")

    for v in variables:
        print("%s\t%s\t%s\t%s" % (v["study"], v["var_dbgap_id"], v["var_name"], v["var_descr"]))

    print()

# ------------------------------------------------------
# main()
# ------------------------------------------------------

def main():

    # input
    parser = argparse.ArgumentParser(description='List variables available in the DATS Dataset that corresponds to a given dbGaP study.')
    parser.add_argument('--dats_file', help ='Path to TOPMed or GTEx DATS JSON file.')
    parser.add_argument('--dataset_id', required=False, help ='DATS identifier of the Dataset whose variables should be retrieved.')
    args = parser.parse_args()

    # logging
    logging.basicConfig(level=logging.INFO)

    # parse JSON LD
    g = ru.read_json_ld_graph(args.dats_file)

    # run query
    variables = list_dataset_variables(g, args.dataset_id)
    print_results(variables, args.dataset_id)

if __name__ == '__main__':
    main()
