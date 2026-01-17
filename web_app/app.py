from flask import Flask, render_template, jsonify, send_file
from engine_v2 import get_cis_data
import os

app = Flask(__name__)

# Path to the CIS Excel file
CIS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), '3540_avance.xlsx')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def api_data():
    """
    API endpoint to fetch the analysis data.
    """
    data = get_cis_data(CIS_FILE)
    return jsonify(data)

@app.route('/report/download')
def download_report():
    """
    Generates and downloads a PDF report explaining the methodology.
    For this MVP, we serve a generated HTML report or the Excel.
    Let's serve the Audit Excel for now as the 'Report'.
    """
    # Regenerate the Excel just in case
    # In a real app we'd generate a beautiful PDF here.
    # For now, let's point to the Excel located in root.
    excel_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'analisis_auditado_3540.xlsx')
    if os.path.exists(excel_path):
        return send_file(excel_path, as_attachment=True)
    else:
        return "Informe no generado. Ejecute el análisis primero.", 404

if __name__ == '__main__':
    print(f" * Servidor CIS Aldabón-Gemini iniciado")
    print(f" * Archivo de Datos: {CIS_FILE}")
    app.run(debug=True, port=5000)
