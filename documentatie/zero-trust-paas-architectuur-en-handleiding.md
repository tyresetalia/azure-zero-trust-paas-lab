# Azure Zero-Trust PaaS Architectuur & Handleiding

Dit document bevat de volledige technische architectuur, implementatiestappen, ontwerpoverwegingen en validatieprocedures voor het **Azure Zero-Trust PaaS Lab**.

---

## 1. Executive Summary & Architectuurdoel

In traditionele cloud-omgevingen hebben PaaS-diensten zoals **Azure SQL Database** en **Azure Key Vault** standaard een publiek IP-adres dat bereikbaar is vanaf het internet. Zelfs met IP-firewall regels brengt dit substantiële risico's met zich mee:
- **Data Exfiltration**: Als inloggegevens lekken, kan een kwaadwillende vanaf elk willekeurig IP proberen in te loggen.
- **Credential Exposure**: Hardcoded connection strings en secrets in code of configuratiebestanden belanden vaak per ongeluk in versiebeheer (Git).
- **Compliance & Audits**: Standaarden zoals ISO 27001, NIS2, SOC2 en HIPAA vereisen dat gevoelige backend-data nimmer over het publieke internet reist.

### De Zero-Trust Pijlers in dit Lab
1. **Explicit Verification**: Toegang tot Key Vault en Azure SQL verloopt uitsluitend via cryptografische token-uitgifte van Microsoft Entra ID.
2. **Least Privilege**: De App Service krijgt strikt alleen de rol `Key Vault Secrets User`, geen administratieve rechten.
3. **Assume Breach**: Publieke internettoegang staat fysiek uitgeschakeld (`publicNetworkAccess = Disabled`). Dataverkeer blijft binnen het private netwerk via Azure Private Link.

---

## 2. Architectuur & Netwerk Topologie

```
[ Publiek Internet ]
        |
        v (HTTPS :443)
[ Azure App Service: app-zerotrust-lab-4405 ]
        |
        | Regional VNet Integration (Route All = Enabled)
        v
[ VNet: vnet-francecentral-lab / vnet-zerotrust-lab ]
        |
        +---> Subnet: snet-app-fc (10.30.1.0/24)
        |       Delegation: Microsoft.Web/serverFarms
        |
        +---> Subnet: snet-private-endpoints (10.20.2.0/24)
        |       |
        |       +---> Private Endpoint: pe-sql (10.20.2.5:1433)
        |       |       ===> Azure SQL Database (sql-zt-9935 / sqldb-lab)
        |       |
        |       +---> Private Endpoint: pe-keyvault (10.20.2.4:443)
        |               ===> Azure Key Vault (kv-zt-26595)
        |
        +---> Azure Private DNS Zones (Virtual Network Links)
                + privatelink.database.windows.net
                + privatelink.vaultcore.azure.net
```

---

## 3. Implementatiestappen (CLI & Azure Portal Hybride)

### Fase 1: Netwerk Fundament & Private DNS (Azure CLI)
1. **Resource Group Aanmaken**:
   ```bash
   az group create --name rg-zerotrust-paas-lab --location northeurope
   ```
2. **VNet & Subnets met Delegatie**:
   ```bash
   az network vnet create -g rg-zerotrust-paas-lab -n vnet-zerotrust-lab --address-prefixes 10.20.0.0/16 --subnet-name snet-app-integration --subnet-prefixes 10.20.1.0/24
   az network vnet subnet update -g rg-zerotrust-paas-lab --vnet-name vnet-zerotrust-lab -n snet-app-integration --delegations Microsoft.Web/serverFarms
   az network vnet subnet create -g rg-zerotrust-paas-lab --vnet-name vnet-zerotrust-lab -n snet-private-endpoints --address-prefixes 10.20.2.0/24
   ```
3. **Private DNS Zones & Koppelingen**:
   ```bash
   az network private-dns zone create -g rg-zerotrust-paas-lab -n "privatelink.database.windows.net"
   az network private-dns zone create -g rg-zerotrust-paas-lab -n "privatelink.vaultcore.azure.net"
   az network private-dns link vnet create -g rg-zerotrust-paas-lab --zone-name "privatelink.database.windows.net" -n link-sql -v vnet-zerotrust-lab -e false
   az network private-dns link vnet create -g rg-zerotrust-paas-lab --zone-name "privatelink.vaultcore.azure.net" -n link-kv -v vnet-zerotrust-lab -e false
   ```

### Fase 2: Zero-Trust PaaS & Private Endpoints (Azure CLI)
1. **Key Vault met RBAC & Public Access Disabled**:
   ```bash
   az keyvault create -g rg-zerotrust-paas-lab -n kv-zt-26595 --enable-rbac-authorization true --public-network-access Disabled
   az network private-endpoint create -g rg-zerotrust-paas-lab -n pe-keyvault --vnet-name vnet-zerotrust-lab --subnet snet-private-endpoints --private-connection-resource-id $KV_ID --group-id vault --connection-name conn-pe-kv
   az network private-endpoint dns-zone-group create -g rg-zerotrust-paas-lab --endpoint-name pe-keyvault -n kv-zone-group --private-dns-zone privatelink.vaultcore.azure.net --zone-name privatelink.vaultcore.azure.net
   ```
2. **Azure SQL Server & Database**:
   ```bash
   az sql server create -g rg-zerotrust-paas-lab -n sql-zt-9935 -l francecentral --admin-user sqladminuser --admin-password "P@ssw0rdZeroTrust2026!" --enable-public-network false
   az sql db create -g rg-zerotrust-paas-lab -s sql-zt-9935 -n sqldb-lab --service-objective Basic
   az network private-endpoint create -g rg-zerotrust-paas-lab -n pe-sql --vnet-name vnet-zerotrust-lab --subnet snet-private-endpoints --private-connection-resource-id $SQL_ID --group-id sqlServer --connection-name conn-pe-sql
   az network private-endpoint dns-zone-group create -g rg-zerotrust-paas-lab --endpoint-name pe-sql -n sql-zone-group --private-dns-zone privatelink.database.windows.net --zone-name privatelink.database.windows.net
   ```

### Fase 3: App Service, VNet Integration & Managed Identity (Azure Portal)
1. **Web App Aanmaken**: Linux Web App (`app-zerotrust-lab-4405`) in France Central (Basic B1 SKU).
2. **System-Assigned Managed Identity**: Ingeschakeld onder *Settings -> Identity* (Object ID: `88e1b2f9-2169-4691-86ba-14c2b8b62152`).
3. **Regional VNet Integration**: Gekoppeld aan `vnet-francecentral-lab / snet-app-fc` met *Route All (Uitgaand internetverkeer)* ingeschakeld.
4. **Key Vault RBAC Toewijzing**: Rol `Key Vault Secrets User` toegekend aan de Web App identiteit onder *Access Control (IAM)*.

---

## 4. Validatie & Verificatie

### Test 1: Publieke Toegang Geblokkeerd (Assume Breach)
Via de browser/portal probeert een beheerder direct de geheimen van de Key Vault te bekijken.
**Resultaat:**
> `De bewerking is niet toegestaan door RBAC... U hebt geen machtiging om deze inhoud weer te geven.`

### Test 2: Private DNS Resolutie via Web App SSH
Vanuit de SSH-terminal van de Web App worden DNS lookups uitgevoerd:
```bash
root@1e57e3e8b822:/home/site/wwwroot# nslookup sql-zt-9935.database.windows.net
Non-authoritative answer:
sql-zt-9935.database.windows.net       canonical name = sql-zt-9935.privatelink.database.windows.net.
Name:   sql-zt-9935.privatelink.database.windows.net
Address: 10.20.2.5

root@1e57e3e8b822:/home/site/wwwroot# nslookup kv-zt-26595.vault.azure.net
Non-authoritative answer:
kv-zt-26595.vault.azure.net            canonical name = kv-zt-26595.privatelink.vaultcore.azure.net.
Name:   kv-zt-26595.privatelink.vaultcore.azure.net
Address: 10.20.2.4
```
**Conclusie:** Het verkeer bereikt de database en Key Vault uitsluitend via private IP-adressen over de Azure backbone.

---

## 5. Wat Heb Ik Geleerd?

1. **Enterprise Cloud Security**: Hoe het Zero-Trust principe concreet wordt vertaald naar PaaS netwerkisolatie en identiteitsbeveiliging.
2. **Private Link & DNS Ketens**: Hoe CNAME-aliassen in combinatie met Private DNS Zones ervoor zorgen dat bestaande applicaties geen hardcoded IP's nodig hebben.
3. **Wachtwoordloos Ontwikkelen**: Hoe Managed Identities en Azure RBAC connection string lekken voorkomen.
4. **Cloud Troubleshooting**: Oplossen van datacenter capaciteitsproblemen, subscription namespace registraties en SKU restricties.
