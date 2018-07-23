$csvName = "customer_info.csv"

$output = new-object PSObject
$vlan = "VLAN*"
$output = Get-ADGroup -filter {name -like $vlan} | Select-Object Name, SID
$output | Export-Csv $csvName -NoTypeInformation


