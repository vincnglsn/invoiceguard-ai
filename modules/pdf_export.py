"""
InvoiceGuard AI — Module Export PDF
Génère des rapports professionnels pour expert-comptable et DAF.
"""

from datetime import date
import io

try:
    from fpdf import FPDF
    PDF_OK = True
except ImportError:
    PDF_OK = False


class InvoiceGuardReport(FPDF):
    """Rapport PDF InvoiceGuard — style professionnel."""

    PRIMARY = (0, 212, 170)
    DARK = (17, 24, 39)
    MUTED = (107, 114, 128)
    DANGER = (220, 38, 38)
    WARNING = (234, 88, 12)
    WHITE = (255, 255, 255)
    LIGHT_BG = (249, 250, 251)

    def header(self):
        # Barre header
        self.set_fill_color(*self.DARK)
        self.rect(0, 0, 210, 22, "F")
        self.set_text_color(*self.PRIMARY)
        self.set_font("Helvetica", "B", 14)
        self.set_xy(10, 6)
        self.cell(0, 10, "INVOICEGUARD AI", align="L")
        self.set_text_color(*self.MUTED)
        self.set_font("Helvetica", "", 9)
        self.set_xy(0, 6)
        self.cell(200, 10, f"Rapport du {date.today().strftime('%d/%m/%Y')}", align="R")
        self.ln(20)

    def footer(self):
        self.set_y(-15)
        self.set_text_color(*self.MUTED)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"InvoiceGuard AI · Page {self.page_no()} · Conforme RGPD & Loi LME", align="C")

    def section_title(self, title: str):
        self.set_fill_color(*self.PRIMARY)
        self.set_text_color(0, 0, 0)
        self.set_font("Helvetica", "B", 11)
        self.cell(0, 9, f"  {title}", fill=True, ln=True)
        self.ln(4)

    def kpi_row(self, kpis: list):
        """Ligne de KPIs : liste de (label, valeur, couleur_optionnelle)."""
        col_w = 190 / len(kpis)
        for label, valeur, *color in kpis:
            x = self.get_x()
            y = self.get_y()
            self.set_fill_color(*self.LIGHT_BG)
            self.rect(x, y, col_w - 2, 20, "F")
            self.set_text_color(*(color[0] if color else self.DARK))
            self.set_font("Helvetica", "B", 14)
            self.set_xy(x + 2, y + 2)
            self.cell(col_w - 4, 8, str(valeur), align="C")
            self.set_text_color(*self.MUTED)
            self.set_font("Helvetica", "", 8)
            self.set_xy(x + 2, y + 12)
            self.cell(col_w - 4, 6, label, align="C")
            self.set_xy(x + col_w, y)
        self.ln(24)

    def invoice_table(self, df):
        """Table des factures en retard."""
        headers = ["N° Facture", "Client", "Montant €", "Retard (j)", "Priorité"]
        col_widths = [35, 65, 30, 25, 35]

        # En-tête
        self.set_fill_color(*self.DARK)
        self.set_text_color(*self.WHITE)
        self.set_font("Helvetica", "B", 9)
        for h, w in zip(headers, col_widths):
            self.cell(w, 8, h, border=0, fill=True, align="C")
        self.ln()

        # Lignes
        self.set_font("Helvetica", "", 8)
        for i, (_, row) in enumerate(df.iterrows()):
            bg = self.LIGHT_BG if i % 2 == 0 else self.WHITE
            self.set_fill_color(*bg)

            score = row.get("score_risque", 0)
            if score >= 70:
                self.set_text_color(*self.DANGER)
            elif score >= 40:
                self.set_text_color(*self.WARNING)
            else:
                self.set_text_color(*self.DARK)

            self.cell(col_widths[0], 7, str(row.get("numero_facture", ""))[:16], fill=True)
            self.set_text_color(*self.DARK)
            self.cell(col_widths[1], 7, str(row.get("client", ""))[:28], fill=True)
            self.cell(col_widths[2], 7, f"{float(row.get('montant', 0)):,.0f}", fill=True, align="R")
            retard = int(row.get("jours_retard", 0))
            self.set_text_color(*self.DANGER if retard > 60 else (self.WARNING if retard > 30 else self.DARK))
            self.cell(col_widths[3], 7, str(retard), fill=True, align="C")
            self.set_text_color(*self.DARK)
            priorite = str(row.get("priorite", "")).replace("🔴", "").replace("🟠", "").replace("🟡", "").replace("🟢", "").strip()
            self.cell(col_widths[4], 7, priorite, fill=True, align="C")
            self.ln()

        self.ln(4)


def generer_rapport_pdf(df, kpis: dict, analyse_ia: str = "") -> bytes:
    """
    Génère un rapport PDF complet du portefeuille d'impayés.

    Returns:
        bytes du PDF généré
    """
    if not PDF_OK:
        raise ImportError("fpdf2 non installé. Lancez : pip install fpdf2")

    pdf = InvoiceGuardReport()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Titre principal
    pdf.set_text_color(17, 24, 39)
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 12, "Rapport de Recouvrement", ln=True)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(107, 114, 128)
    pdf.cell(0, 7, f"Généré automatiquement par InvoiceGuard AI · {date.today().strftime('%d %B %Y')}", ln=True)
    pdf.ln(8)

    # KPIs
    pdf.section_title("Synthèse du portefeuille")
    pdf.kpi_row([
        ("Total facturé", f"{kpis['montant_total']:,.0f}€"),
        ("Montant en retard", f"{kpis['montant_en_retard']:,.0f}€", (220, 38, 38)),
        ("Factures en retard", f"{kpis['nb_en_retard']} / {kpis['total_factures']}"),
        ("Dossiers critiques", str(kpis["nb_critiques"]), (220, 38, 38)),
        ("DSO", f"{kpis['dso']}j"),
    ])

    # Indicateur taux retard
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(107, 114, 128)
    pdf.cell(0, 6, f"  Taux de retard : {kpis['taux_retard_pct']:.1f}% du portefeuille", ln=True)
    pdf.ln(6)

    # Tableau factures en retard
    en_retard = df[df["jours_retard"] > 0].sort_values("score_risque", ascending=False)
    if len(en_retard) > 0:
        pdf.section_title(f"Factures en retard ({len(en_retard)} dossiers)")
        pdf.invoice_table(en_retard)

    # Analyse IA
    if analyse_ia:
        pdf.section_title("Analyse & Recommandations IA")
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(17, 24, 39)
        # Nettoyage du texte pour PDF (ASCII-safe)
        safe_text = analyse_ia.encode("latin-1", errors="replace").decode("latin-1")
        pdf.multi_cell(0, 5, safe_text)
        pdf.ln(4)

    # Mention légale
    pdf.section_title("Cadre légal de référence")
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(107, 114, 128)
    legal = (
        "Ce rapport est établi conformément à la Loi de Modernisation de l'Economie (LME) du 4 août 2008. "
        "Les délais de paiement entre professionnels sont plafonnés à 60 jours date de facture (ou 45 jours fin de mois). "
        "En cas de retard, des pénalités sont dues de plein droit, sans mise en demeure préalable, "
        "au taux BCE + 10 points. Une indemnité forfaitaire de recouvrement de 40€ est également due."
    )
    pdf.multi_cell(0, 5, legal)

    return bytes(pdf.output())
