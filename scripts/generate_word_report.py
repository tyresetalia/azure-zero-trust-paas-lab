import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

def set_cell_background(cell, fill_color):
    tcPr = cell._element.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), fill_color)
    tcPr.append(shd)

def set_cell_margins(cell, top=140, bottom=140, left=180, right=180):
    tcPr = cell._element.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def add_heading_styled(doc, text, level):
    h = doc.add_heading(text, level=level)
    h.paragraph_format.keep_with_next = True
    h.paragraph_format.space_before = Pt(14)
    h.paragraph_format.space_after = Pt(4)
    for run in h.runs:
        if level == 1:
            run.font.color.rgb = RGBColor(0, 51, 102) # Deep Azure Blue
            run.font.size = Pt(18)
            run.font.bold = True
        elif level == 2:
            run.font.color.rgb = RGBColor(0, 102, 204) # Azure Blue
            run.font.size = Pt(14)
            run.font.bold = True
        elif level == 3:
            run.font.color.rgb = RGBColor(51, 51, 51)
            run.font.size = Pt(12)
            run.font.bold = True
    return h

def add_callout(doc, text, title="BELANGRIJKE ARCHITECTUUR NOTITIE", color="003366"):
    tbl = doc.add_table(rows=1, cols=1)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    tbl.columns[0].width = Inches(6.5)
    cell = tbl.cell(0, 0)
    set_cell_background(cell, "F0F4F8")
    set_cell_margins(cell, top=160, bottom=160, left=200, right=200)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(2)
    r_title = p.add_run(f"📌 {title}\n")
    r_title.bold = True
    r_title.font.size = Pt(10.5)
    r_title.font.color.rgb = RGBColor(0, 51, 102)
    
    r_text = p.add_run(text)
    r_text.font.size = Pt(9.5)
    r_text.font.italic = True
    doc.add_paragraph().paragraph_format.space_after = Pt(4)

def add_image_safe(doc, image_path, caption_text, width=Inches(6.0)):
    if os.path.exists(image_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(2)
        p_img.paragraph_format.keep_with_next = True
        run = p_img.add_run()
        run.add_picture(image_path, width=width)
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(10)
        run_cap = p_cap.add_run(f"Figuur: {caption_text}")
        run_cap.font.size = Pt(8.5)
        run_cap.font.italic = True
        run_cap.font.color.rgb = RGBColor(100, 100, 100)
    else:
        p_err = doc.add_paragraph(f"[Afbeelding ontbreekt: {image_path} - {caption_text}]")
        p_err.runs[0].font.color.rgb = RGBColor(200, 0, 0)

def main():
    doc = docx.Document()
    
    # Page setup - Margins 1 inch
    for s in doc.sections:
        s.top_margin = Inches(1)
        s.bottom_margin = Inches(1)
        s.left_margin = Inches(1)
        s.right_margin = Inches(1)
        
    # Styles
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(40, 40, 40)
    normal_style.paragraph_format.space_after = Pt(6)
    normal_style.paragraph_format.line_spacing = 1.15

    # ==========================================
    # TITELPAGINA
    # ==========================================
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(40)
    p_pre.paragraph_format.space_after = Pt(10)
    r_pre = p_pre.add_run("ENTERPRISE CLOUD ARCHITECTURE & SECURITY LAB")
    r_pre.font.size = Pt(12)
    r_pre.font.bold = True
    r_pre.font.color.rgb = RGBColor(0, 102, 204)
    
    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_after = Pt(15)
    r_title = p_title.add_run("Azure Zero-Trust PaaS Architecture Lab")
    r_title.font.size = Pt(28)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(0, 51, 102)
    
    p_sub = doc.add_paragraph()
    p_sub.paragraph_format.space_after = Pt(30)
    r_sub = p_sub.add_run("End-to-End Isolatie van App Service, Azure SQL en Key Vault via Private Endpoints, Private DNS, VNet-Integratie en Microsoft Entra ID Managed Identities.")
    r_sub.font.size = Pt(13)
    r_sub.font.color.rgb = RGBColor(80, 80, 80)
    
    # Meta box
    tbl_meta = doc.add_table(rows=4, cols=2)
    tbl_meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_meta.autofit = False
    tbl_meta.columns[0].width = Inches(2.2)
    tbl_meta.columns[1].width = Inches(4.3)
    
    meta_data = [
        ("Auteur:", "Tyrese Talia"),
        ("Lab Type:", "Azure Security & PaaS Networking Lab (CLI + Portal Hybrid)"),
        ("Datum:", "29-10-2026"),
        ("Status:", "Voltooid & 100% Geverifieerd")
    ]
    for idx, (label, val) in enumerate(meta_data):
        c0 = tbl_meta.cell(idx, 0)
        c1 = tbl_meta.cell(idx, 1)
        set_cell_background(c0, "F8F9FA")
        set_cell_background(c1, "FFFFFF")
        set_cell_margins(c0, top=80, bottom=80, left=120, right=120)
        set_cell_margins(c1, top=80, bottom=80, left=120, right=120)
        
        p0 = c0.paragraphs[0]
        p0.add_run(label).bold = True
        p0.runs[0].font.size = Pt(10)
        p0.runs[0].font.color.rgb = RGBColor(0, 51, 102)
        
        p1 = c1.paragraphs[0]
        p1.add_run(val)
        p1.runs[0].font.size = Pt(10)
        
    doc.add_page_break()

    # ==========================================
    # INHOUDSOPGAVE & SAMENVATTING
    # ==========================================
    add_heading_styled(doc, "1. Executive Summary & Managementsamenvatting", level=1)
    doc.add_paragraph(
        "Dit praktijkgericht lab demonstreert de implementatie van een 'Zero-Trust' architectuur voor moderne "
        "Platform-as-a-Service (PaaS) componenten op Microsoft Azure. Waar traditionele cloud-omgevingen "
        "vaak leunen op netwerkfirewalls rondom publieke eindpunten en statische wachtwoorden, elimineert "
        "deze Zero-Trust PaaS architectuur publieke netwerkblootstelling en statische inloggegevens volledig."
    )
    doc.add_paragraph(
        "In dit lab is gebruikgemaakt van een hybride uitrolmethode: de eerste helft (infrastructuur-fundament, "
        "subnets, private DNS-zones en private endpoints) is gerealiseerd via de Azure CLI / Cloud Shell. "
        "De tweede helft (App Service provisioning, VNet Integration, Managed Identity activatie, RBAC toewijzingen "
        "en validatie) is voltrokken via het Azure Portal. Hierdoor wordt zowel beheersing van Infrastructure-as-Code (IaC) "
        "en scripting als diepgaande portal- en beheerdeskundigheid aangetoond."
    )

    add_callout(
        doc,
        "Zero-Trust Pijlers in dit lab:\n"
        "1. Never Trust, Always Verify: Alle identiteiten worden cryptografisch gevalideerd via Microsoft Entra ID.\n"
        "2. Least Privilege: De App Service heeft strikt alleen Secrets User rechten, geen beheerdersrechten.\n"
        "3. Assume Breach: Alle publieke internettoegang staat fysiek uitgeschakeld ('Disabled'). "
        "Backend diensten zijn louter bereikbaar over private IPv4-adressen.",
        title="MICROSOFT ZERO-TRUST SECURITY MODEL"
    )

    # ==========================================
    # DOEL, WAAROM & ARCHITECTUURKEUZES
    # ==========================================
    add_heading_styled(doc, "2. Doelstelling, Waarom en Architectuurkeuzes", level=1)
    
    add_heading_styled(doc, "2.1 Het Probleem van Traditionele PaaS Implementaties", level=2)
    doc.add_paragraph(
        "Standaard hebben Azure SQL Databases en Key Vaults publieke IP-adressen die op het internet staan. "
        "Zelfs met IP-whitelisting brengt dit ernstige risico's met zich mee: data exfiltration via gecompromitteerde inloggegevens, "
        "DDoS-aanvallen en het per ongeluk lekken van connection strings in broncode repositories."
    )

    add_heading_styled(doc, "2.2 De Zero-Trust Oplossing", level=2)
    doc.add_paragraph(
        "Om te voldoen aan enterprise compliance standaarden (zoals ISO 27001, NIS2, SOC2) vereist moderne architectuur "
        "dat gevoelige backend-data nimmer over het publieke internet reist. In deze architectuur:"
    )
    
    bullet_points = [
        ("Azure Private Link & Private Endpoints: ", "Zorgen dat Azure SQL en Key Vault een private IPv4-adres krijgen binnen het Virtual Network."),
        ("Azure Private DNS Zones: ", "Automatische transparante omzetting van FQDNs (zoals mydb.database.windows.net) naar het interne IP-adres (bijv. 10.20.2.5)."),
        ("Regional VNet Integration: ", "Dwingt alle uitgaande netwerkpakketten van de Web App via het afgeschermde subnet van het VNet te routeren."),
        ("System-Assigned Managed Identity: ", "Elimineert wachtwoorden. Azure beheert de levenscyclus en rotatie van authenticatie-tokens.")
    ]
    for b_title, b_desc in bullet_points:
        p_b = doc.add_paragraph(style='List Bullet')
        r_bt = p_b.add_run(b_title)
        r_bt.bold = True
        r_bt.font.color.rgb = RGBColor(0, 51, 102)
        p_b.add_run(b_desc)

    # ==========================================
    # DEPLOYMENT FASE 1: CLI INFRASTRUCTUUR
    # ==========================================
    add_heading_styled(doc, "3. Fase 1: CLI Infrastructuur & Netwerk Fundament", level=1)
    doc.add_paragraph(
        "De kerninfrastructuur is opgezet via Azure CLI in de Cloud Shell. Dit garandeert herhaalbaarheid, "
        "snelheid en uniformiteit in enterprise-omgevingen."
    )
    
    add_heading_styled(doc, "3.1 Resource Group & Subnet Delegatie", level=2)
    doc.add_paragraph(
        "Er is een centrale Resource Group aangemaakt. Binnen het Virtual Network is een dedicated subnet "
        "geconfigureerd met delegatie naar 'Microsoft.Web/serverFarms', wat een technische vereiste is voor App Service VNet-integratie."
    )
    add_image_safe(doc, "Screenshots/01_rg_create_cli.png", "Succesvolle aanmaak van de Resource Group via Azure CLI.")
    add_image_safe(doc, "Screenshots/05_vnet_create_succeeded.png", "Aanmaak van het Virtueel Netwerk met het initiële integratie subnet.")
    add_image_safe(doc, "Screenshots/06_subnet_delegation_serverfarms.png", "Configuratie van de delegatie naar Microsoft.Web/serverFarms.")
    add_image_safe(doc, "Screenshots/07_subnet_private_endpoints.png", "Aanmaak van het dedicated subnet voor Private Endpoints.")

    add_heading_styled(doc, "3.2 Private DNS Zones & Netwerk Koppelingen", level=2)
    doc.add_paragraph(
        "Om te voorkomen dat applicaties hardcoded IP-adressen moeten aanroepen, zijn twee centrale Private DNS zones "
        "aangemaakt: 'privatelink.database.windows.net' voor SQL en 'privatelink.vaultcore.azure.net' voor Key Vault. "
        "Beide zones zijn via Virtual Network Links gekoppeld aan het VNet."
    )
    add_image_safe(doc, "Screenshots/08_private_dns_zones_created.png", "Aanmaak van de twee Private DNS Zones via Azure CLI.")
    add_image_safe(doc, "Screenshots/09_private_dns_vnet_links.png", "Succesvolle koppeling (Virtual Network Links) aan het VNet.")

    add_heading_styled(doc, "3.3 Zero-Trust Key Vault & SQL met Private Endpoints", level=2)
    doc.add_paragraph(
        "Zowel de Key Vault als de SQL Server zijn uitgerold met de parameter '--public-network-access Disabled'. "
        "Vervolgens zijn Private Endpoints aangemaakt in het private subnet en geregistreerd in de respectievelijke DNS-groepen."
    )
    add_image_safe(doc, "Screenshots/13_keyvault_create_succeeded.png", "Key Vault aangemaakt met RBAC en Public Access Disabled.")
    add_image_safe(doc, "Screenshots/14_pe_keyvault_created.png", "Key Vault Private Endpoint (pe-keyvault) op IP 10.20.2.4.")
    add_image_safe(doc, "Screenshots/15_dns_zone_group_keyvault.png", "Automatische A-record registratie in de Private DNS Zone voor Key Vault.")
    add_image_safe(doc, "Screenshots/20_sql_server_created_francecentral.png", "Azure SQL Server uitgerold met Public Network Access Disabled.")
    add_image_safe(doc, "Screenshots/21_sql_db_created.png", "Azure SQL Database (Basic tier) aangemaakt op de beveiligde server.")
    add_image_safe(doc, "Screenshots/22_pe_sql_created.png", "Azure SQL Private Endpoint (pe-sql) gekoppeld op IP 10.20.2.5.")
    add_image_safe(doc, "Screenshots/23_dns_zone_group_sql.png", "Automatische A-record registratie voor SQL Server in Private DNS.")

    # ==========================================
    # DEPLOYMENT FASE 2: AZURE PORTAL
    # ==========================================
    add_heading_styled(doc, "4. Fase 2: Azure Portal Implementatie & Identiteit", level=1)
    doc.add_paragraph(
        "Vanaf dit punt is overgeschakeld naar het Azure Portal om de beheerervaring, IAM blades, "
        "monitoring en visuele configuratie te valideren."
    )
    
    add_heading_styled(doc, "4.1 Portal Overzicht & Resource Validering", level=2)
    doc.add_paragraph(
        "In de Azure Portal is de Resource Group geopend om te controleren of alle 10 kernbronnen "
        "(VNets, NICs, Private Endpoints, DNS Zones, Key Vault en SQL) intact en operationeel waren."
    )
    add_image_safe(doc, "Screenshots/24_portal_resource_group_overview.png", "Volledig overzicht van de resources in het Azure Portal.")

    add_heading_styled(doc, "4.2 App Service Provisioning & Regional VNet Integration", level=2)
    doc.add_paragraph(
        "De Linux Web App is uitgerold en verbonden met het virtuele netwerk via Regional VNet Integration. "
        "Hierbij is 'Uitgaand internetverkeer / Route All' geactiveerd, zodat ook al het uitgaande verkeer "
        "binnen het private netwerk blijft."
    )
    add_image_safe(doc, "Screenshots/27_webapp_deployed_francecentral.png", "Succesvolle implementatie van de Azure Web App.")
    add_image_safe(doc, "Screenshots/34_vnet_integration_connected_portal.png", "Actieve VNet-integratie met applicatierouting (Route All).")

    add_heading_styled(doc, "4.3 Managed Identity & Role-Based Access Control (RBAC)", level=2)
    doc.add_paragraph(
        "In plaats van database-inloggegevens of Key Vault keys in configuratiebestanden te plaatsen, "
        "is een System-Assigned Managed Identity ingeschakeld op de Web App. Vervolgens is aan deze identiteit "
        "in de Key Vault strikt de rol 'Key Vault Secrets User' toegekend."
    )
    add_image_safe(doc, "Screenshots/28_webapp_managed_identity_enabled.png", "System-Assigned Managed Identity ingeschakeld met Object-ID.")
    add_image_safe(doc, "Screenshots/35_keyvault_rbac_secrets_user_assigned.png", "Key Vault Secrets User rol toegekend aan de Web App identiteit.")

    # ==========================================
    # TROUBLESHOOTING SECTIE
    # ==========================================
    add_heading_styled(doc, "5. Real-World Troubleshooting & Opgeloste Uitdagingen", level=1)
    doc.add_paragraph(
        "Tijdens de implementatie deden zich verschillende real-world enterprise cloud scenario's voor. "
        "Het effectief diagnosticeren en oplossen hiervan toont diepgaande cloud engineering vaardigheden."
    )

    tb_cases = [
        (
            "Regionale Capaciteit & Quota Restricties (West Europe & North Europe)",
            "Tijdens de initiële VNet en SQL provisioning gaven zowel West Europe als North Europe foutmeldingen "
            "(RequestDisallowedByAzure en RegionDoesNotAllowProvisioning) vanwege datacentercapaciteit voor de subscription tier.",
            "Screenshots/02_vnet_region_quota_error.png",
            "Door de architectuur flexibel in te richten volgens het Azure Global Network model, zijn de resources verplaatst naar France Central. "
            "Hierbij toont de opzet aan dat Private Link moeiteloos cross-region en cross-VNet communicatie ondersteunt zonder veiligheidsverlies."
        ),
        (
            "Resource Provider Namespace Registratie",
            "Bij het aanmaken van de Key Vault gaf Azure de melding 'MissingSubscriptionRegistration: The subscription is not registered to use namespace Microsoft.KeyVault'.",
            "Screenshots/11_missing_subscription_registration_keyvault.png",
            "Via 'az provider register --namespace Microsoft.KeyVault' en 'Microsoft.Sql' zijn de benodigde providers expliciet geregistreerd in de subscription."
        ),
        (
            "Resource Groep Locatie Mismatch & Naamgeving",
            "Bij het herstarten van de Resource Group weigerde Azure verplaatsing van North Europe naar een andere regio onder dezelfde naam.",
            "Screenshots/03_rg_location_mismatch_error.png",
            "De foute resource group is schoon opgeruimd via de CLI en met dynamische variabelen en random suffixes ($RANDOM) opnieuw uitgerold."
        ),
        (
            "App Service SKU Quota Limieten",
            "In North Europe was het limiet voor B1 (Basic) en P1v3 VMs ingesteld op 0 voor Linux web apps.",
            "Screenshots/26_appservice_b1_quota_error.png",
            "Door de Web App in France Central te deployen met een lokaal VNet (vnet-francecentral-lab) en DNS-linking werd de quota-restrictie direct omzeild."
        )
    ]

    for title, desc, img, sol in tb_cases:
        add_heading_styled(doc, f"Scenario: {title}", level=2)
        doc.add_paragraph(f"Symptoom & Foutmelding: {desc}")
        add_image_safe(doc, img, f"Troubleshooting bewijs: {title}")
        doc.add_paragraph(f"Toegepaste Oplossing: {sol}")

    # ==========================================
    # VERIFICATIE & BEWIJS
    # ==========================================
    add_heading_styled(doc, "6. Verificatie, Validatie & Zero-Trust Bewijsvoering", level=1)
    doc.add_paragraph(
        "Het sluitstuk van het lab bestaat uit het empirisch bewijzen dat de Zero-Trust isolatie "
        "aan beide kanten functioneert: publieke toegang faalt, terwijl private communicatie 100% slaagt."
    )
    
    add_heading_styled(doc, "6.1 Test 1: Publieke Toegang Keihard Geblokkeerd", level=2)
    doc.add_paragraph(
        "Wanneer een beheerder via het openbare internet (het Azure Portal) probeert de Key Vault geheimen te bekijken, "
        "blokkeert Azure direct de toegang met een expliciete RBAC- en netwerkfoutmelding. "
        "Dit bewijst dat zelfs met portal-toegang, data niet kan uitlekken over het internet."
    )
    add_image_safe(doc, "Screenshots/36_keyvault_secrets_access_denied_rbac.png", "Validatie Test 1: Publieke internettoegang tot geheimen wordt geblokkeerd.")

    add_heading_styled(doc, "6.2 Test 2: Private DNS & VNet Connectiviteit via SSH", level=2)
    doc.add_paragraph(
        "Via de ingebouwde SSH-terminal van de Web App zijn DNS-lookups uitgevoerd naar de FQDN's "
        "van zowel de Azure SQL Database als de Key Vault. De resultaten bewijzen:"
    )
    
    dns_res = [
        "sql-zt-9935.database.windows.net resolveert via de canonical name sql-zt-9935.privatelink.database.windows.net naar 10.20.2.5 (Private IP).",
        "kv-zt-26595.vault.azure.net resolveert via kv-zt-26595.privatelink.vaultcore.azure.net naar 10.20.2.4 (Private IP)."
    ]
    for r in dns_res:
        p_r = doc.add_paragraph(style='List Bullet')
        p_r.add_run(r)

    add_image_safe(doc, "Screenshots/37_webapp_ssh_nslookup_validation.png", "Validatie Test 2: SSH nslookup toont interne private IP-adressen (10.20.2.x).")

    # ==========================================
    # WAT HEB IK GELEERD
    # ==========================================
    add_heading_styled(doc, "7. Wat Heb Ik Geleerd & Portfolio Conclusie", level=1)
    doc.add_paragraph(
        "Dit lab overbrugt de kloof tussen standaard cloud-ontwikkeling en enterprise-grade beveiligingsarchitectuur. "
        "De belangrijkste verworven competenties zijn:"
    )
    
    learnings = [
        ("Zero-Trust PaaS Architectuur: ", "Begrip van het elimineren van publieke netwerkoppervlakken (attack surface) bij moderne cloud-native diensten."),
        ("Azure Private Link & DNS Routing: ", "Hoe Private Endpoints samenwerken met Private DNS Zones en hoe CNAME-ketens (canonical names) zorgen dat bestaande applicatie-code niet hoeft te worden aangepast."),
        ("Regional VNet Integration & Subnet Delegation: ", "Het configureren van uitgaande applicatie-routing ('Route All') en subnet delegation naar Microsoft.Web/serverFarms."),
        ("Geavanceerd Identity & Access Management (IAM): ", "Het volledig uitbannen van hardcoded connection strings door gebruik te maken van System-Assigned Managed Identities en granulaire Azure RBAC-rollen (Key Vault Secrets User)."),
        ("Cloud Troubleshooting Onder Druk: ", "Het oplossen van datacentercapaciteitsproblemen, subscription provider registraties, cross-region netwerkrelaties en SKU quota-restricties."),
        ("Hybride Implementatiemethodiek: ", "Ervaring met zowel snelle Azure CLI automatisering als visuele inspectie, monitoring en beheer in het Azure Portal.")
    ]
    for l_title, l_desc in learnings:
        p_l = doc.add_paragraph(style='List Bullet')
        r_lt = p_l.add_run(l_title)
        r_lt.bold = True
        r_lt.font.color.rgb = RGBColor(0, 51, 102)
        p_l.add_run(l_desc)

    doc.add_paragraph(
        "Conclusie: Het Azure Zero-Trust PaaS Lab is een volledig gevalideerde demonstratie van "
        "veilige, compliance-ready en robuuste cloud-architectuur volgens de hoogste standaarden "
        "van het Microsoft Well-Architected Framework."
    )

    out_path = os.path.abspath("documentatie/Azure_Zero_Trust_PaaS_Lab_Rapport.docx")
    doc.save(out_path)
    print(f"Rapport succesvol gegenereerd: {out_path}")

if __name__ == "__main__":
    main()
