#!/bin/tcsh

setenv PYTHONPATH ./

# Script to create the crosscut metadata model instance. 
#
# The public or non-access-controlled crosscut metadata model instance is a
# BDBag that contains DATS JSON-LD files that describe the metadata from the 
# following resources:
#
# 1. Public AGR ortholog, disease, phenotype and gene coordinate data from mouse and rat.
# 2. Public GTEx v7 metadata from dbGaP and the GTEx portal.
# 3. Public TOPMed metadata from non-access-controlled dbGaP files.
# 
# In the case of both GTEx and TOPMed the crosscut metadata model instance may 
# be expanded to include access-controlled dbGaP metadata (see the relevant script 
# invocation below) but this expanded instance may not be publicly distributed.

setenv VERSION 0.7
setenv EXTERNAL_ID "KC7-crosscut-metadata-v${VERSION}"
setenv EXTERNAL_DESCR "v${VERSION} release of the KC7 crosscut metadata model for GTEx v7 and TOPMed public metadata using DATS v2.2+"

# set up internal bag structure
mkdir -p $EXTERNAL_ID/docs
mkdir -p $EXTERNAL_ID/datasets

## -----------------------------------------------
## AGR 
## -----------------------------------------------

# First download the AGR filtered ortholog file:
#  alliance-orthology-july-19-2018-stable-1.6.0-v4.tsv
#
# Then create/find the directory that contains the requisite BGI, disease, and GFF files.
# For the current mouse and rat instance, for example, a new directory could be created:
#
#  mkdir bgi_gff3_disease
#
# and the following files copied into it or symlinked from there:
#
#  MGI_1.0.4_BGI.json
#  MGI_1.0.4_disease.json
#  MGI_1.0.4_GFF.gff
#  RGD_1.0.4_BGI.json
#  RGD_1.0.4_disease.json
#  RGD_1.0.4_GFF.gff
#
# Finally, run the command to generate the corresponding DATS JSON-LD, providing 
# the location of the ortholog file and the directory containing all the rest:

./bin/agr_to_dats.py \
 --agr_genomes_list='MGI_1.0.4_2,RGD_1.0.4_3' \
 --bgi_gff3_disease_path=./bgi_gff3_disease \
 --ortholog_file=alliance-orthology-july-19-2018-stable-1.6.0-v4.tsv \
 --output_file=AGR_MGI_RGD.jsonld

# NOTE: AGR file is staged remotely and referenced from remote-files.json

## -----------------------------------------------
## Public GTEx v7 dbGaP metadata
## -----------------------------------------------

# Convert public dbGaP metadata for GTEx to DATS JSON.
#
# First retrieve the pheno_variable_summaries files for GTEx into a local directory:
#  1. create local directory dbgap-data if it does not already exist
#  2. pull ftp://ftp.ncbi.nlm.nih.gov/dbgap/studies/phs000424/phs000424.v7.p2/pheno_variable_summaries/ into dbgap-data/phs000424.v7.p2
#
# Then make sure the dcppc/data-stewards repo is cloned or downloaded locally:
#  3. git clone https://github.com/dcppc/data-stewards.git
#  4. modify --data_stewards_repo_path accordingly
# 
#  5. Run the command below

./bin/gtex_v7_to_dats.py --dbgap_public_xml_path=./dbgap-data/phs000424.v7.p2 \
  --data_stewards_repo_path=./data-stewards \
  --output_file=$EXTERNAL_ID/datasets/GTEx_v7_public.jsonld 

# Command used to create instance for validation. Due to limitations with the current DATS
# validator, the following 2 changes must be applied to generate an instance that can 
# pass validation:
#
#  1. Run gtex_v7_to_dats.py with the --no_circular_links flag
#  2. Set datsobj.DEBUG_NO_ID_REFS to True (for both GTEx and TOPMed)
#
#./bin/gtex_v7_to_dats.py --dbgap_public_xml_path=./dbgap-data/phs000424.v7.p2 \
#  --data_stewards_repo_path=./data-stewards \
#  --no_circular_links \
#  --output_file=$EXTERNAL_ID/datasets/GTEx_v7_public_no_cycles.jsonld 

## -----------------------------------------------
## CONTROLLED ACCESS GTEx v7 dbGaP metadata
## -----------------------------------------------

# Convert CONTROLLED ACCESS dbGaP metadata for GTEx to DATS JSON.

#./bin/dbgap_gtex_to_dats.py --dbgap_public_xml_path=./dbgap-data/phs000424.v7.p2 \
#  --dbgap_protected_metadata_path=./controlled-access-dbgap-data/phs000424.v7.p2 \
#  --data_stewards_repo_path=./data-stewards \
#  --output_file=$EXTERNAL_ID/datasets/GTEx_v7_CONTROLLED_ACCESS-v${VERSION}.jsonld

## -----------------------------------------------
## Public TOPMed metadata
## -----------------------------------------------

# Convert public dbGaP metadata for selected TOPMed studies to DATS JSON.
#
# First retrieve the pheno_variable_summaries from the desired TOPMed studies into a local directory: 
#  1. create local directory dbgap-data if it does not already exist
#  2. pull ftp://ftp.ncbi.nlm.nih.gov/dbgap/studies/phs001024/phs001024.v3.p1/pheno_variable_summaries/ into dbgap-data/phs001024.v3.p1
#  3. pull ftp://ftp.ncbi.nlm.nih.gov/dbgap/studies/phs000951/phs000951.v2.p2/pheno_variable_summaries/ into dbgap-data/phs000951.v2.p2
#  4. pull ftp://ftp.ncbi.nlm.nih.gov/dbgap/studies/phs000179/phs000179.v5.p2/pheno_variable_summaries/ into dbgap-data/phs000179.v5.p2
#  5. run the command below

./bin/topmed_to_dats.py --dbgap_accession_list='phs001024.v3.p1,phs000951.v2.p2,phs000179.v5.p2' \
  --dbgap_public_xml_path=./dbgap-data \
  --output_file=$EXTERNAL_ID/datasets/TOPMed_phs000951_phs000946_phs001024_wgs_public.jsonld

## -----------------------------------------------
## CONTROLLED ACCESS TOPMed metadata
## -----------------------------------------------

# Convert CONTROLLED ACCESS TOPMed metadata to DATS JSON.

#./bin/topmed_to_dats.py --dbgap_accession_list='phs001024.v3.p1,phs000951.v2.p2,phs000179.v5.p2' \
#  --dbgap_public_xml_path=./dbgap-data \
#  --dbgap_protected_metadata_path=./controlled-access-dbgap-data \
#  --output_file=$EXTERNAL_ID/datasets/TOPMed_phs000951_phs000946_phs001024_wgs_CONTROLLED_ACCESS-v${VERSION}.jsonld

## -----------------------------------------------
## Add documentation
## -----------------------------------------------

cp releases/ChangeLog $EXTERNAL_ID/docs/
cp RELEASE_NOTES $EXTERNAL_ID/docs/

## -----------------------------------------------
## Create BDBag
## -----------------------------------------------

bdbag --archive tgz \
 --source-organization 'NIH DCPPC KC7 Working Group' \
 --contact-name 'Jonathan Crabtree' \
 --contact-email 'jcrabtree@som.umaryland.edu' \
 --external-description "$EXTERNAL_DESCR" \
 --external-identifier $EXTERNAL_ID \
 --remote-file-manifest remote-files.json \
$EXTERNAL_ID

## -----------------------------------------------
## Validate BDBag
## -----------------------------------------------

#bdbag $EXTERNAL_ID.tgz
#bdbag --resolve-fetch missing --validate full $EXTERNAL_ID
