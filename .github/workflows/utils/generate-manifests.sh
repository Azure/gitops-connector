#!/bin/bash

# Generates K8s manifests from Helm + Kustomize templates
# Uses env variables to substitute values 
# Requires to be installed:  
#   - helm 
#   - kubectl
#   - envsubst (https://command-not-found.com/envsubst)
# 
echo $1
echo $2
echo $3

set -euo pipefail  # fail on error

export gen_manifests_file_name='gen_manifests.yaml'

# Usage:
# generate-manifests.sh FOLDER_WITH_MANIFESTS GENERATED_MANIFESTS_FOLDER
# e.g.:
# generate-manifests.sh cloud-native-ops/azure-vote/manifests gen_manifests
# 
# the script will put Helm + Kustomize manifests with substituted variable values
# to gen_manifests/hld folder and plain yaml manifests to gen_manifests/gen_manifests.yaml file


mkdir -p $2
mkdir -p $2/hld
mkdir -p $2/manifest

# Substitute env variables in all yaml files in the manifest folder
for file in `find $1 -name '*.yaml'`; do envsubst <"$file" > "$file"1 && mv "$file"1 "$file"; done

# Generate manifests
# for app in `find $1 -type d -maxdepth 1 -mindepth 1`; do \
cp -r "$1"/helm $2/hld/

if [[ $3 == "all" ]]; then 
helm template "$1"/helm > $2/manifest/$gen_manifests_file_name && \
cat $2/manifest/$gen_manifests_file_name
if [ $? -gt 0 ]
  then
    error "Could not render manifests"
    return 1
  fi
fi
# done
pwd

