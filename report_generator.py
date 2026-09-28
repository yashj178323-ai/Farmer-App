"""
Generates an official-looking PDF summary of PACS kiosk activity for
download from the Admin Portal's Analytics tab.

Requires: pip install fpdf2
"""
from datetime import datetime
from fpdf import FPDF

MAROON = (122, 35, 49)     # #7A2331
GOLD = (176, 141, 87)      # #B08D57
INK = (30, 41, 59)         # #1E293B
MUTED = (85, 99, 122)      # #55637A


class GovReportPDF(FPDF):
    def header(self):
        # Tricolor strip
        self.set_fill_color(255, 153, 51)
        self.rect(0, 0, 70, 4, "F")
        self.set_fill_color(255, 255, 255)
        self.rect(70, 0, 70, 4, "F")
        self.set_fill_color(19, 136, 8)
        self.rect(140, 0, 70, 4, "F")

        self.set_y(10)
        self.set_font("Helvetica", "B", 15)
        self.set_text_color(*MAROON)
        self.cell(0, 8, "Ministry of Cooperation, Government of India", ln=True, align="C")

        self.set_font("Helvetica", "", 10)
        self.set_text_color(*MUTED)
        self.cell(0, 6, "PACS Central Governance & Telemetry Portal — Official Summary Report", ln=True, align="C")

        self.set_draw_color(*GOLD)
        self.set_line_width(0.5)
        self.line(15, 26, 195, 26)
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*MUTED)
        self.cell(0, 10, f"Generated {datetime.now().strftime('%d %b %Y, %H:%M')} | Page {self.page_no()}", align="C")

    def section_title(self, text):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(*MAROON)
        self.ln(4)
        self.cell(0, 8, text, ln=True)
        self.set_draw_color(*GOLD)
        self.line(self.get_x(), self.get_y(), self.get_x() + 180, self.get_y())
        self.ln(3)

    def kv_row(self, label, value):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(*INK)
        self.cell(70, 7, label, border=0)
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 7, str(value), ln=True)

    def data_table(self, headers, rows, col_widths):
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(246, 244, 239)
        self.set_text_color(*MAROON)
        for h, w in zip(headers, col_widths):
            self.cell(w, 8, h, border=1, fill=True)
        self.ln()

        self.set_font("Helvetica", "", 9)
        self.set_text_color(*INK)
        for row in rows:
            for val, w in zip(row, col_widths):
                self.cell(w, 7, str(val), border=1)
            self.ln()


def generate_weekly_report_pdf(total_queries, open_tickets, domain_rows, language_rows, kiosk_status_rows):
    """
    domain_rows: list of (policy_scheme_name, query_count)
    language_rows: list of (language_name, usage_count)
    kiosk_status_rows: list of dicts with kiosk_id/state/district/last_seen/online
    Returns: PDF file as bytes, ready for st.download_button.
    """
    pdf = GovReportPDF()
    pdf.add_page()

    pdf.section_title("Network Summary")
    pdf.kv_row("Report Period", datetime.now().strftime("Week ending %d %b %Y"))
    pdf.kv_row("Total Kiosk Queries Logged", total_queries)
    pdf.kv_row("Open Grievance Tickets", open_tickets)
    pdf.kv_row("Registered Kiosks Reporting", len(kiosk_status_rows))
    online_count = sum(1 for k in kiosk_status_rows if k.get("online"))
    pdf.kv_row("Kiosks Currently Online", f"{online_count} / {len(kiosk_status_rows)}" if kiosk_status_rows else "0 / 0")

    pdf.section_title("Query Volume by Policy Domain")
    pdf.data_table(
        ["Policy Scheme", "Queries Handled"],
        domain_rows,
        [130, 50]
    )

    pdf.section_title("Regional Language Distribution")
    pdf.data_table(
        ["Language", "Usage Count"],
        language_rows,
        [130, 50]
    )

    if kiosk_status_rows:
        pdf.section_title("Kiosk Health Status")
        table_rows = [
            (k["kiosk_id"], k["district"], "Online" if k["online"] else "Offline", k["last_seen"])
            for k in kiosk_status_rows
        ]
        pdf.data_table(
            ["Kiosk ID", "District", "Status", "Last Seen"],
            table_rows,
            [40, 50, 30, 60]
        )

    return bytes(pdf.output())