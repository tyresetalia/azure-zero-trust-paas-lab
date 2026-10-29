# Troubleshooting Scenario's & Opgeloste Uitdagingen

In dit document worden de reële foutmeldingen en technische uitdagingen beschreven die tijdens de uitrol van het **Azure Zero-Trust PaaS Lab** zijn opgetreden, inclusief root-cause analyse en de toegepaste oplossingen.

---

## Scenario 1: Regionale Capaciteit & Quota Restricties (West Europe & North Europe)

### Symptoom
Tijdens het aanmaken van het virtuele netwerk in `westeurope` en later de Azure SQL Database server in `northeurope` gaf de Azure CLI de volgende foutmeldingen:
```text
(RequestDisallowedByAzure) Resource 'vnet-zerotrust-lab' was disallowed by Azure: The selected region is currently not accepting new customers: https://aka.ms/locationineligible.
```
en voor SQL Server:
```text
(RegionDoesNotAllowProvisioning) Location 'North Europe' is not accepting creation of new Windows Azure SQL Database servers at this time.
```

### Root Cause
Veelgebruikte Azure-regio's (zoals West en North Europe) hanteren tijdelijke capaciteitsstops en quota-restricties voor specifieke resources in test-, student- of nieuwe subscriptions.

### Oplossing
1. De infrastructuur is flexibel verplaatst naar **`francecentral`** (Parijs).
2. De Azure SQL Server (`sql-zt-9935`) is succesvol uitgerold in France Central met `publicNetworkAccess: Disabled`.
3. Er is een lokaal VNet (`vnet-francecentral-lab`) opgezet met subnets voor zowel de App Service (`snet-app-fc`) als Private Endpoints.
4. **Architectuurinzicht**: Private Endpoints kunnen naadloos gekoppeld worden aan Private DNS Zones over meerdere VNets, waardoor cross-region netwerkrelaties transparant blijven functioneren.

---

## Scenario 2: Resource Provider Namespace Registratie

### Symptoom
Bij het aanmaken van de Azure Key Vault trad de volgende fout op:
```text
(MissingSubscriptionRegistration) The subscription is not registered to use namespace 'Microsoft.KeyVault'.
See https://aka.ms/rps-not-found for how to register subscriptions.
```

### Root Cause
In nieuwe of recent geactiveerde subscriptions zijn niet alle Azure Resource Providers standaard geactiveerd. Voordat resources in een namespace aangemaakt kunnen worden, moet de provider eenmalig geregistreerd worden.

### Oplossing
De providers zijn via de Azure CLI geregistreerd:
```bash
az provider register --namespace Microsoft.KeyVault
az provider register --namespace Microsoft.Sql
```
Na statuscontrole (`registrationState = Registered`) kon de provisioning direct succesvol worden hervat.

---

## Scenario 3: Resource Group Locatie Mismatch

### Symptoom
Bij het heraanmaken van de Resource Group in een andere regio gaf de CLI:
```text
(InvalidResourceGroupLocation) Invalid resource group location 'northeurope'. The Resource group already exists in location 'westeurope'.
```

### Root Cause
Een bestaande lege Resource Group behoudt zijn metadata-locatie. Azure staat niet toe dat een bestaande resource group van datacenter verandert door simpelweg hetzelfde commando met een andere `--location` uit te voeren.

### Oplossing
De lege resource group is verwijderd:
```bash
az group delete --name rg-zerotrust-paas-lab --yes --no-wait
```
Vervolgens is de Resource Group opnieuw aangemaakt in de gewenste regio.

---

## Scenario 4: App Service SKU Quota Limieten

### Symptoom
Tijdens de uitrol van de Web App via de Azure Portal wizard in North Europe verscheen:
```text
Operation cannot be completed without additional quota.
Current Limit (B1 VMs): 0, Current Usage: 0. Amount required for this deployment: 1.
```
Hetzelfde gold voor de P1v3 SKU in die regio.

### Root Cause
Het abonnement had een VM core limit van 0 voor Basic en Premium Linux App Service Plans in het datacenter North Europe.

### Oplossing
De Web App (`app-zerotrust-lab-4405`) is uitgerold in **`France Central`** op een Basic B1 plan. Vervolgens is via de VNet Integration blade direct verbinding gelegd met `vnet-francecentral-lab` en het gedelegeerde subnet `snet-app-fc`.

---

## Scenario 5: Web App Portal Pre-flight Validatiefout

### Symptoom
Tijdens de wizard gaf de Portal een pre-flight validatiefout (`Microsoft.Web/sites reported preflight validation errors`) wanneer VNet Integration direct in de wizard werd aangevinkt.

### Root Cause
In de portal wizard probeert Azure het integratie-subnet te binden aan een Web App die op dat moment nog niet fysiek bestaat in het App Service Plan.

### Oplossing
De app is eerst zonder netwerkinjectie aangemaakt (`Integratie van virtuele netwerken inschakelen: Uit`). Zodra de Web App leefde, is de VNet Integration met 1 klik gekoppeld via het **Networking** menu van de resource zelf.
