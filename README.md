# Enterprise Zero-Trust PaaS Architecture — Microsoft Azure

Ontwerp, implementatie en end-to-end validatie van een enterprise Zero-Trust Platform-as-a-Service (PaaS) architectuur op Microsoft Azure. Volledige netwerkisolatie en identiteitsbeveiliging van **Azure App Service**, **Azure SQL Database** en **Azure Key Vault** via **Private Endpoints (Azure Private Link)**, **Private DNS Zones**, **Regional VNet Integration** en **Microsoft Entra ID Managed Identities**.

---

## 🎯 Doel

Aantonen dat ik een enterprise-grade, compliance-ready **Zero-Trust PaaS** cloudarchitectuur kan ontwerpen, via een **hybride methode (Azure CLI + Azure Portal)** kan bouwen en beveiligen:
- **Zero-Exposure PaaS**: Backend services (SQL Database & Key Vault) draaien met `publicNetworkAccess: Disabled` — fysiek onbereikbaar vanaf het internet.
- **Azure Private Link & DNS CNAME Ketens**: Privé IPv4-adressering (`10.20.2.x`) binnen het Virtual Network met automatische FQDN-resolutie via Private DNS Zones.
- **Regional VNet Integration & Subnet Delegatie**: Uitgaand verkeer van de Linux App Service forceren via een afgeschermd subnet met `Route All = Enabled` en delegatie naar `Microsoft.Web/serverFarms`.
- **Wachtwoordloze Authenticatie (Zero Credentials)**: Volledige eliminatie van connection strings en wachtwoorden door inzet van **System-Assigned Managed Identity** en granulaire **Azure RBAC** (`Key Vault Secrets User`).
- **Real-World Incident Response & Troubleshooting**: Oplossen van Azure datacenter quota-restricties (`RequestDisallowedByAzure` & `RegionDoesNotAllowProvisioning`), namespace registraties en cross-region architectuuroverwegingen.
- **FinOps & Resource Lifecycle**: Kostenbeheersing door gestructureerd resourcebeheer en geautomatiseerde teardown (`cleanup.ps1`).

---

## 🏗️ Architectuur & Netwerkontwerp

```
                                [ Publiek Internet ]
                                          │
                                          │ HTTPS (Poort 443)
                                          ▼
                      ┌───────────────────────────────────────┐
                      │    app-zerotrust-lab-4405 (Linux)     │
                      │  • SKU: Basic B1 (France Central)     │
                      │  • System-Assigned Managed Identity   │
                      │    OID: 88e1b2f9-2169-4691-...        │
                      └───────────────────┬───────────────────┘
                                          │ Regional VNet Integration
                                          │ (Route All: Enabled)
                                          ▼
                      ┌───────────────────────────────────────┐
                      │    vnet-francecentral-lab / Hub       │
                      │  • snet-app-fc: 10.30.1.0/24          │
                      │    (Delegation: serverFarms)          │
                      └───────────────────┬───────────────────┘
                                          │ Interne backbone
                                          ▼
                      ┌───────────────────────────────────────┐
                      │  snet-private-endpoints (10.20.2.0/24)│
                      │                                       │
                      │  [ pe-sql ]       [ pe-keyvault ]     │
                      │   10.20.2.5        10.20.2.4          │
                      │  (Poort 1433)     (Poort 443)         │
                      └─────────┬─────────────────┬───────────┘
                                │                 │
        Private Link Backbone   │                 │   Private Link Backbone
                                ▼                 ▼
        ┌──────────────────────────────┐   ┌──────────────────────────────┐
        │       Azure SQL Server       │   │       Azure Key Vault        │
        │         sql-zt-9935          │   │         kv-zt-26595          │
        │   Database: sqldb-lab        │   │   RBAC: Secrets User         │
        │   Public Access: DISABLED ❌ │   │   Public Access: DISABLED ❌ │
        └──────────────────────────────┘   └──────────────────────────────┘
                       ▲                                  ▲
                       │                                  │
       [ Onbevoegde Aanvaller / Internet ] ───────────────┘
          (❌ Fysiek GEBLOKKEERD door Zero-Trust Firewall)
```

---

## 📋 Componenten & Specificaties

| Component | Resource Naam | Subnet / IP-Bereik | Specificaties | Doel / Functie |
|---|---|---|---|---|
| **Resource Group** | `rg-zerotrust-paas-lab` | Regio: `North Europe / France Central` | N.v.t. | Centrale lifecycle container voor alle lab-resources |
| **Virtual Network** | `vnet-francecentral-lab` | `10.30.0.0/16` | DNS: Default Azure | Private netwerklaag voor de backend workloads |
| **App Subnet** | `snet-app-fc` | `10.30.1.0/24` | Delegation: `serverFarms` | Dedicated integratiesubnet voor de Web App |
| **Private Endpoint Subnet**| `snet-private-endpoints` | `10.20.2.0/24` | Policies Disabled | Subnet voor netwerkinterfaces van Private Link |
| **Web App** | `app-zerotrust-lab-4405` | VNet Outbound | Python 3.11 / Linux (B1) | Frontend web-applicatie met Managed Identity |
| **Azure SQL Server** | `sql-zt-9935` | Private IP: `10.20.2.5` | Basic Tier (`sqldb-lab`) | Beveiligde database met `publicNetworkAccess: Disabled` |
| **Azure Key Vault** | `kv-zt-26595` | Private IP: `10.20.2.4` | RBAC Authorized | Opslag van geheimen met `publicNetworkAccess: Disabled` |
| **Private DNS SQL** | `privatelink.database.windows.net` | Global / VNet Link | A-record naar `10.20.2.5` | DNS-vertaling van SQL Server FQDN |
| **Private DNS Vault** | `privatelink.vaultcore.azure.net` | Global / VNet Link | A-record naar `10.20.2.4` | DNS-vertaling van Key Vault FQDN |

---

## 🛠️ Hybride Implementatiemethode (CLI & Portal)

Het lab is bewust uitgevoerd in een **50/50 hybride opzet** om zowel command-line automation als diepgaande Azure Portal configuratie aan te tonen:

1. **Eerste Helft (Azure CLI / Cloud Shell)**:
   - Resource Groups, Virtual Networks, subnet delegaties en routering.
   - Private DNS Zones aanmaken en koppelen aan de VNets via Virtual Network Links.
   - Azure Key Vault en Azure SQL Database provisionen met `--public-network-access Disabled`.
   - Private Endpoints (`pe-sql` en `pe-keyvault`) uitrollen en DNS Zone Groups koppelen.

2. **Tweede Helft (Azure Portal)**:
   - Resource Group overzicht en netwerktopologie inspecteren.
   - App Service (Linux Web App) aanmaken en afstemmen op beschikbare compute-quota.
   - **Regional VNet Integration** inschakelen en verbinden met het gedelegeerde subnet.
   - **System-Assigned Managed Identity** activeren en het Entra ID Object-ID verifiëren.
   - **Azure RBAC Roltoewijzing** (`Key Vault Secrets User`) configureren onder Access Control (IAM).
   - Validatietesten uitvoeren vanuit de ingebouwde SSH-console.

---

## 🧪 Validatie & Zero-Trust Bewijsvoering

### 1. Test 1: Publieke Internettoegang Geblokkeerd (Assume Breach)
Wanneer een gebruiker via het internet (zelfs ingelogd in het Azure Portal) probeert de geheimen in de Key Vault te bekijken, weigert Azure categorisch de toegang:
> ⚠️ **"De bewerking is niet toegestaan door RBAC... U hebt geen machtiging om deze inhoud weer te geven."**

### 2. Test 2: Private DNS Resolutie via Web App SSH Terminal
Vanuit de Linux Web App SSH console zijn DNS-queries uitgevoerd naar de publieke FQDN's van de PaaS-diensten:
```bash
root@1e57e3e8b822:/home/site/wwwroot# nslookup sql-zt-9935.database.windows.net
Server:    127.0.0.11
Address:   127.0.0.11#53

Non-authoritative answer:
sql-zt-9935.database.windows.net       canonical name = sql-zt-9935.privatelink.database.windows.net.
Name:   sql-zt-9935.privatelink.database.windows.net
Address: 10.20.2.5

root@1e57e3e8b822:/home/site/wwwroot# nslookup kv-zt-26595.vault.azure.net
Server:    127.0.0.11
Address:   127.0.0.11#53

Non-authoritative answer:
kv-zt-26595.vault.azure.net            canonical name = kv-zt-26595.privatelink.vaultcore.azure.net.
Name:   kv-zt-26595.privatelink.vaultcore.azure.net
Address: 10.20.2.4
```
**Conclusie**: De applicatie gebruikt transparant de officiële Azure URL's, maar het verkeer wordt via Private DNS en Private Link binnendoor gerouteerd naar interne IP-adressen (`10.20.2.5` en `10.20.2.4`). Publieke blootstelling is nul.

---

## 💡 Troubleshooting & Incident Response

| Uitdaging / Foutmelding | Oorzaak | Toegepaste Oplossing |
|---|---|---|
| `RequestDisallowedByAzure` & `RegionDoesNotAllowProvisioning` | Quota- en capaciteitsstops in West Europe en North Europe voor nieuwe SQL/VNet resources. | Architectuur verplaatst naar France Central; Private DNS links garanderen transparante multiregionale connectiviteit. |
| `MissingSubscriptionRegistration` (`Microsoft.KeyVault`) | Provider namespace was niet geregistreerd in de subscription. | Handmatige CLI registratie via `az provider register --namespace Microsoft.KeyVault` en `Microsoft.Sql`. |
| `InvalidResourceGroupLocation` | Bestaande Resource Group kan niet van datacenter-locatie wijzigen. | Lege resource group verwijderd via `az group delete` en opnieuw aangemaakt in de juiste regio met dynamische `$RANDOM` naming. |
| `Current Limit (B1 VMs): 0` | Subscription had 0 vCPU quota voor B1 Linux VMs in North Europe. | Web App uitgerold in France Central waar de Basic SKU wel direct beschikbaar was. |
| Pre-flight validatiefout in Web App Wizard | Portal kan VNet-integratie niet binden aan een nog niet-bestaande app. | App Service eerst aangemaakt met VNet uitgeschakeld; daarna met 1 klik gekoppeld via het Networking-menu. |

---

## 🎓 Wat Heb Ik Geleerd?

- **Zero-Trust PaaS Architectuur**: Hoe enterprise organisaties voldoen aan ISO 27001 en NIS2 door PaaS-diensten volledig af te sluiten van het openbare internet.
- **Azure Private Link & DNS**: De werking van CNAME-aliassen en hoe Private DNS Zones automatisch communicatie over het interne netwerk afdwingen zonder applicatie-wijzigingen.
- **Subnet Delegation & Route All**: Waarom een App Service een dedicated subnet vereist en hoe alle uitgaande netwerkstromen via het VNet worden gedwongen.
- **Wachtwoordloos Ontwikkelen (IAM)**: Waarom Managed Identities superieur zijn aan connection strings met statische wachtwoorden.
- **Troubleshooting Onder Druk**: Snel schakelen bij cloud datacenter restricties, quota-limieten en IAM permissiefouten.

---

## 📁 Repository Structuur

```text
azure-zero-trust-paas-lab/
├── documentatie/
│   ├── Azure_Zero_Trust_PaaS_Lab_Rapport.docx           # Officieel Word rapport met alle 37 screenshots
│   ├── zero-trust-paas-architectuur-en-handleiding.md  # Uitgebreide handleiding en architectuur
│   └── troubleshooting-scenario.md                     # Gedetailleerde incident logs en oplossingen
├── scripts/
│   └── cleanup.ps1                                     # Geautomatiseerd opruimscript (kostenpreventie)
├── Screenshots/                                        # 37 verscherpte bewijsscreenshots (01 t/m 37)
└── README.md                                           # Dit portfolio document
```
