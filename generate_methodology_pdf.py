from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER

def create_report():
    file_name = "Informe_Metodologico_Cocina_Electoral.pdf"
    doc = SimpleDocTemplate(file_name, pagesize=A4,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Justify', alignment=TA_JUSTIFY, fontSize=11, leading=14))
    styles.add(ParagraphStyle(name='CenterTitle', alignment=TA_CENTER, fontSize=18, spaceAfter=20, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle(name='SubTitle', fontSize=14, spaceAfter=10, spaceBefore=20, fontName="Helvetica-Bold", color=colors.darkblue))
    styles.add(ParagraphStyle(name='Explanation', fontSize=10, leading=12, textColor=colors.dimgrey, leftIndent=20))

    Story = []

    # Title
    Story.append(Paragraph("Informe Didáctico: La 'Cocina' Electoral", styles['CenterTitle']))
    Story.append(Paragraph("Comparativa: Método CIS (Tezanos) vs. Método Rectificado (Aldabón-Gemini)", styles['Normal']))
    Story.append(Spacer(1, 12))
    Story.append(Paragraph("Enero 2026", styles['Normal']))
    Story.append(Spacer(1, 30))

    # Introduction
    Story.append(Paragraph("1. ¿Qué es la 'Cocina' y por qué es necesaria?", styles['SubTitle']))
    Story.append(Paragraph("""
    Imagina que quieres saber qué va a cenar tu clase, pero solo puedes preguntar a 10 personas.
    Si de esas 10 personas, 5 te dicen "Pizza", 2 "Hamburguesa" y 3 te dicen "No sé" o "No te lo quiero decir",
    tienes un problema. Esos 3 indecisos acabarán cenando algo, y si no averiguas qué, tu predicción fallará.
    """, styles['Justify']))
    Story.append(Spacer(1, 6))
    Story.append(Paragraph("""
    En las encuestas políticas pasa lo mismo. La **"Cocina"** es el conjunto de fórmulas matemáticas que usamos para:
    a) Asignar un voto probable a los que dicen "No sé".
    b) Corregir a los que mienten (sí, la gente miente en las encuestas).
    """, styles['Justify']))

    # Method 1: Tezanos
    Story.append(Paragraph("2. El Método Oficial (Alaminos-Tezanos)", styles['SubTitle']))
    Story.append(Paragraph("Filosofía: \"El voto es un estado emocional\"", styles['Heading4']))
    
    Story.append(Paragraph("""
    El método actual del CIS asume que el votante es fluido. Para adivinar el voto de un indeciso, 
    le hace preguntas sobre sus sentimientos actuales:
    """, styles['Justify']))
    
    list_tezanos = [
        "¿Qué partido le despierta más SIMPATÍA?",
        "¿Qué líder político valora mejor (del 1 al 10)?",
        "¿Quién preferiría que fuese el Presidente ahora mismo?"
    ]
    for item in list_tezanos:
        Story.append(Paragraph(f"• {item}", styles['Explanation']))
        
    Story.append(Paragraph("""
    <br/><b>El Fallo del Método: El "Voto Vergonzante"</b><br/>
    En España, sociológicamente, el votante de izquierdas suele estar orgulloso de serlo y lo dice abiertamente.
    Sin embargo, el votante de derechas (PP/VOX) es más reservado o crítico. A veces, un votante del PP
    está enfadado con su líder y le pone un 3 de nota, pero <b>le acabará votando igual</b> por lealtad ideológica.
    <br/><br/>
    Como el método de Tezanos solo mira la "simpatía actual", confunde ese enfado temporal con un cambio de voto,
    y asigna a casi todos los indecisos a la izquierda. Esto provoca que el CIS siempre infle al PSOE.
    """, styles['Justify']))

    # Method 2: Aldabón-Gemini
    Story.append(Paragraph("3. El Método Rectificado (Aldabón-Gemini)", styles['SubTitle']))
    Story.append(Paragraph("Filosofía: \"Dime qué hiciste ayer y te diré qué harás mañana\"", styles['Heading4']))
    
    Story.append(Paragraph("""
    Nuestro método desconfía de los sentimientos momentáneos. Nosotros usamos un <b>\"Detector de Mentiras\"</b> 
    matemático basado en el RECUERDO DE VOTO.
    """, styles['Justify']))

    Story.append(Paragraph("""
    <b>Paso A: El Factor de Corrección (K)</b><br/>
    Comparamos lo que la gente dice en la encuesta con la REALIDAD verificada (las elecciones del 23J).
    """, styles['Justify']))
    
    Story.append(Spacer(1, 6))
    
    # K-Factor Example Table
    data = [
        ['Partido', 'Voto Real (23J)', 'Encuestados que\ndicen haberle votado', 'Conclusión', 'Acción Matemática'],
        ['PSOE', '31.7%', '40.0%', 'La gente exagera\n(Efecto "Caballo Ganador")', 'Bajamos peso (x0.8)'],
        ['PP', '33.1%', '20.0%', 'La gente se oculta\n("Voto Vergonzante")', 'Subimos peso (x1.6)'],
    ]
    t = Table(data, colWidths=[50, 80, 100, 120, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    Story.append(t)
    
    Story.append(Spacer(1, 12))
    
    Story.append(Paragraph("""
    <b>Paso B: La Matriz de Fugas</b><br/>
    Si Juan nos dice: <i>"Voté al PP en 2023, pero ahora no sé a quién votar"</i>, nosotros no adivinamos.
    Miramos estadísticas: "El 90% de los que votaron al PP siguen siendo fieles".
    Por tanto, asignamos a Juan un 90% de probabilidad de volver al PP, aunque ahora esté enfadado.
    """, styles['Justify']))

    # Conclusion
    Story.append(Paragraph("4. Conclusión Final", styles['SubTitle']))
    Story.append(Paragraph("""
    Mientras que el CIS hace una "foto del estado de ánimo" (que cambia con las noticias de la semana),
    el método Aldabón-Gemini hace una "radiografía estructural" (que mide la lealtad de fondo).
    y menos a la izquierda (corrigiendo la sobre-declaración), acertando más en el resultado final de las urnas.
    """, styles['Justify']))
    
    # Technical Annex
    Story.append(Paragraph("5. Anexo Técnico: Fórmulas y Algoritmos", styles['SubTitle']))
    Story.append(Paragraph("""
    Este anexo detalla la formulación matemática exacta utilizada en el algoritmo <b>Aldabón-Gemini v2.1</b>.
    """, styles['Justify']))
    
    # 1. Variables Base
    Story.append(Paragraph("A. Definición de Variables Base", styles['Heading4']))
    list_vars = [
        "<b>V_real:</b> % Voto Real obtenido por el partido P en las elecciones del 23J.",
        "<b>R_bruto:</b> % de encuestados que declaran haber votado a P en 2023.",
        "<b>R_norm:</b> Recuerdo de voto normalizado (eliminando NS/NC).",
        "<b>S_p:</b> Intención directa de voto + Simpatía declarada (Dato bruto del CIS)."
    ]
    for v in list_vars:
        Story.append(Paragraph(f"• {v}", styles['Explanation']))
    Story.append(Spacer(1, 6))

    # 2. Formulas
    Story.append(Paragraph("B. Algoritmo de Rectificación", styles['Heading4']))
    
    Story.append(Paragraph("<b>1. Normalización del Recuerdo:</b><br/>Primero obtenemos el recuerdo válido equivalente.", styles['Justify']))
    Story.append(Paragraph("<i>R_norm = (R_bruto / Suma_Recuerdo_Validos) x 100</i>", styles['Explanation']))
    
    Story.append(Spacer(1, 6))
    Story.append(Paragraph("<b>2. Cálculo del Factor K (Corrector de Sesgo):</b><br/>Este coeficiente detecta la autocomplacencia o el ocultamiento.", styles['Justify']))
    Story.append(Paragraph("<i>K = V_real / R_norm</i>", styles['Explanation']))
    Story.append(Paragraph("• Si K > 1: Existe voto oculto (infra-representación).", styles['Explanation']))
    Story.append(Paragraph("• Si K < 1: Existe sobre-representación (efecto 'caballo ganador').", styles['Explanation']))
    
    Story.append(Spacer(1, 6))
    Story.append(Paragraph("<b>3. Matriz de Ajuste Fino (Fidelidad y Liderazgo):</b><br/>Aplicamos coeficientes de segunda derivada.", styles['Justify']))
    Story.append(Paragraph("• <b>Fidelidad (F):</b> Retención histórica. (Ej. PSOE=0.93, PP=0.92, VOX=0.82)", styles['Explanation']))
    Story.append(Paragraph("• <b>Liderazgo (L):</b> Factor de tendencia actual. (Ej. SALF=1.20 por viralidad)", styles['Explanation']))
    
    Story.append(Spacer(1, 6))
    Story.append(Paragraph("<b>4. Fórmula Final de Estimación:</b><br/>La intención directa (S_p) se proyecta corregida por los tres factores:", styles['Justify']))
    Story.append(Paragraph("<i>Estimacion_Final = S_p  x  K  x  F  x  L</i>", styles['CenterTitle']))
    Story.append(Paragraph("(El resultado final se re-normaliza para sumar 100%)", styles['Explanation']))
    
    Story.append(Spacer(1, 30))
    Story.append(Paragraph("Documento generado automáticamente por el sistema de análisis.", styles['Explanation']))

    doc.build(Story)
    print(f"PDF generado exitosamente: {file_name}")

if __name__ == "__main__":
    create_report()
