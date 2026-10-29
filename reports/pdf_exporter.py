"""PDF and HTML Exporter Module for Nilaayam AI.

Renders structured report data into publication-ready HTML using Jinja2
and exports to PDF using WeasyPrint with graceful fallback to styled HTML.
"""

import os
import logging
from typing import Dict, Any

try:
    import jinja2
    HAS_JINJA2 = True
except ImportError:
    jinja2 = None
    HAS_JINJA2 = False

try:
    from weasyprint import HTML
    HAS_WEASYPRINT = True
except (ImportError, OSError):
    HTML = None
    HAS_WEASYPRINT = False

logger = logging.getLogger(__name__)


def _render_template(report_dict: Dict[str, Any]) -> str:
    """Loads the Jinja2 template from reports/templates/report.html and renders it with report data."""
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
    template_file = "report.html"
    template_path = os.path.join(template_dir, template_file)

    if HAS_JINJA2 and os.path.exists(template_path):
        try:
            env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(template_dir),
                autoescape=jinja2.select_autoescape(["html", "xml"])
            )
            template = env.get_template(template_file)
            return template.render(**report_dict)
        except Exception as e:
            logger.warning(f"Error loading Jinja2 template file: {e}. Falling back to inline renderer.")

    # Fallback minimal HTML renderer if Jinja2 or template file is unavailable
    summary = report_dict.get("summary", {})
    title = f"Nilaayam AI Report - {report_dict.get('report_id', '')}"
    html_lines = [
        "<!DOCTYPE html><html><head><meta charset='utf-8'>",
        f"<title>{title}</title>",
        "<style>body{font-family:sans-serif;margin:20px;color:#1e293b;}h1{color:#0369a1;}</style>",
        "</head><body>",
        f"<h1>Nilaayam AI Legal Intelligence Report</h1>",
        f"<p><strong>Report ID:</strong> {report_dict.get('report_id')} | <strong>Date:</strong> {report_dict.get('generated_at')}</p>",
        f"<h3>Status: {summary.get('overall_status')}</h3>",
        f"<p>{summary.get('executive_summary', '')}</p>",
        "<hr>",
        f"<div style='font-size:8pt;color:#991b1b;margin-top:20px;'><strong>DISCLAIMER:</strong> {report_dict.get('disclaimer')}</div>",
        "</body></html>"
    ]
    return "\n".join(html_lines)


def export_report_html(report_dict: Dict[str, Any]) -> str:
    """Renders and returns HTML string for client preview or rendering."""
    return _render_template(report_dict)


def export_report_pdf(report_dict: Dict[str, Any], output_path: str) -> str:
    """Renders HTML template and compiles it into a PDF via WeasyPrint.
    
    If WeasyPrint or native rendering libraries (e.g. Gtk/Pango) are unavailable,
    gracefully saves the rendered HTML to disk and returns the HTML file path.
    """
    html_content = _render_template(report_dict)

    # Ensure parent output directory exists
    parent_dir = os.path.dirname(os.path.abspath(output_path))
    if parent_dir and not os.path.exists(parent_dir):
        os.makedirs(parent_dir, exist_ok=True)

    if HAS_WEASYPRINT and HTML is not None:
        try:
            HTML(string=html_content).write_pdf(output_path)
            logger.info(f"Report exported successfully as PDF: {output_path}")
            return output_path
        except Exception as e:
            logger.warning(f"WeasyPrint PDF rendering failed: {e}. Falling back to saving HTML document.")

    # Fallback to saving HTML file
    fallback_path = output_path
    if fallback_path.lower().endswith(".pdf"):
        fallback_path = fallback_path[:-4] + ".html"

    with open(fallback_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    logger.info(f"Report saved as HTML fallback: {fallback_path}")
    return fallback_path
