#!/bin/bash
set -e
RG=${RG:-rg-notes-cea}
for vmss in vmss-app vmss-web; do
  for id in $(az vmss list-instances -g $RG -n $vmss --query "[].instanceId" -o tsv); do
    echo "Deploying to $vmss instance $id"
    az vmss run-command invoke -g $RG -n $vmss --instance-id $id \
      --command-id RunShellScript --scripts "/opt/notes/deploy.sh" -o none
  done
done

IP=$(az network public-ip show -g $RG -n pip-lb-web --query ipAddress -o tsv)
echo "Checking http://$IP/api/items"
for i in $(seq 1 12); do
  code=$(curl -s -o /dev/null -w "%{http_code}" http://$IP/api/items || true)
  [ "$code" = "200" ] && echo "Healthy" && exit 0
  sleep 10
done
echo "Application not healthy after deploy"; exit 1
