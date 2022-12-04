$Network = "{0}_airflow" -f @(Split-Path $PSScriptRoot -Leaf)
# $Network = "walletflow_airflow"
$Network = "walletflow_default"

echo $Network


docker run --rm --network $Network --volume "${PSScriptRoot}\walletflow:/opt/airflow" apache/airflow @Args