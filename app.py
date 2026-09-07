import io
import pandas as pd
import streamlit as st
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

st.set_page_config(
    page_title="Gestion des Cotations", page_icon="📚", layout="wide"
)

st.title("📚 Gestion des Cotations - Complexe Scolaire")

# --- INITIALISATION DE LA MÉMOIRE ---
if "infos_classe" not in st.session_state:
  st.session_state.infos_classe = {
      "province": "Haut-Katanga",
      "ville": "Kasumbalesa",
      "commune": "Kasumbalesa",
      "ecole": "COMPLEXE SCOLAIRE MWANGAZA",
      "option": "TOUTES",
      "classe": "1ère Année",
      "cours_actuel": "COMPTABILITÉ",
      "professeur": "",
      "annee": "2026-2027",
  }

if "eleves" not in st.session_state:
  st.session_state.eleves = pd.DataFrame(
      {"Nom de l'élève": ["LINA LOYA MANDO", "KAPUTU MANINGA", "NGOY ODARI"]}
  )

if "toutes_les_notes" not in st.session_state:
  st.session_state.toutes_les_notes = {}

# --- MENU LATÉRAL ---
st.sidebar.header("Navigation")
menu = st.sidebar.selectbox(
    "Aller vers",
    ["Infos Classe", "Liste des Élèves", "Cotations & Calculs", "Bulletins"],
)

# --- 1. INFOS CLASSE ---
if menu == "Infos Classe":
  st.header("📋 Informations de la Classe")
  with st.form("form_infos"):
    col1, col2 = st.columns(2)
    with col1:
      province = st.text_input(
          "Province", st.session_state.infos_classe["province"]
      )
      ville = st.text_input("Ville", st.session_state.infos_classe["ville"])
      commune = st.text_input(
          "Commune", st.session_state.infos_classe["commune"]
      )
      ecole = st.text_input(
          "Nom de l'École", st.session_state.infos_classe["ecole"]
      )
      option = st.text_input("Option", st.session_state.infos_classe["option"])
    with col2:
      classe = st.text_input("Classe", st.session_state.infos_classe["classe"])
      professeur = st.text_input(
          "Nom du Professeur Principal",
          st.session_state.infos_classe["professeur"],
      )
      annee = st.text_input(
          "Année Scolaire", st.session_state.infos_classe["annee"]
      )

    submitted = st.form_submit_button("Enregistrer les infos de la classe")
    if submitted:
      st.session_state.infos_classe["province"] = province
      st.session_state.infos_classe["ville"] = ville
      st.session_state.infos_classe["commune"] = commune
      st.session_state.infos_classe["ecole"] = ecole
      st.session_state.infos_classe["option"] = option
      st.session_state.infos_classe["classe"] = classe
      st.session_state.infos_classe["professeur"] = professeur
      st.session_state.infos_classe["annee"] = annee
      st.success("Informations de la classe mises à jour avec succès !")

# --- 2. LISTE DES ÉLÈVES ---
elif menu == "Liste des Élèves":
  st.header("👥 Gestion des Élèves")
  edited_eleves = st.data_editor(
      st.session_state.eleves, num_rows="dynamic", use_container_width=True
  )
  if st.button("Mettre à jour la liste"):
    st.session_state.eleves = edited_eleves
    st.success("Liste des élèves mise à jour !")

# --- 3. COTATIONS & CALCULS ---
elif menu == "Cotations & Calculs":
  st.header("📝 Saisie et Modification des Cotations par Cours")

  cours_existants = list(st.session_state.toutes_les_notes.keys())
  choix_action = st.radio(
      "Que souhaitez-vous faire ?",
      [
          "Modifier un cours déjà enregistré",
          "Ajouter un tout nouveau cours",
      ],
      horizontal=True,
  )

  if choix_action == "Modifier un cours déjà enregistré":
    if not cours_existants:
      st.warning(
          "Aucun cours n'a encore été enregistré. Veuillez d'abord ajouter un"
          " nouveau cours."
      )
      cours_actif = ""
    else:
      cours_actif = st.selectbox(
          "Sélectionnez le cours à consulter ou modifier", cours_existants
      )
  else:
    saisie_nouveau = st.text_input(
        "Tapez le nom du nouveau cours (ex: ANGLAIS, HISTOIRE...)"
    )
    cours_actif = saisie_nouveau.strip().upper()

  if cours_actif:
    st.info(f"📌 **Cours actuellement actif : {cours_actif}**")

    with st.expander(
        f"⚙️ Configuration des Maxima (Barèmes) pour {cours_actif}",
        expanded=True,
    ):
      col1, col2, col3, col4, col5, col6 = st.columns(6)
      old_max = (
          st.session_state.toutes_les_notes[cours_actif]["maximas"]
          if cours_actif in st.session_state.toutes_les_notes
          else {
              "P1": 60.0,
              "P2": 60.0,
              "EXAM S1": 120.0,
              "P3": 60.0,
              "P4": 60.0,
              "EXAM S2": 120.0,
          }
      )
      max_p1 = col1.number_input(
          "Max P1", value=float(old_max["P1"]), key=f"max_p1_{cours_actif}"
      )
      max_p2 = col2.number_input(
          "Max P2", value=float(old_max["P2"]), key=f"max_p2_{cours_actif}"
      )
      max_ex1 = col3.number_input(
          "Max Exam S1",
          value=float(old_max["EXAM S1"]),
          key=f"max_ex1_{cours_actif}",
      )
      max_p3 = col4.number_input(
          "Max P3", value=float(old_max["P3"]), key=f"max_p3_{cours_actif}"
      )
      max_p4 = col5.number_input(
          "Max P4", value=float(old_max["P4"]), key=f"max_p4_{cours_actif}"
      )
      max_ex2 = col6.number_input(
          "Max Exam S2",
          value=float(old_max["EXAM S2"]),
          key=f"max_ex2_{cours_actif}",
      )

    noms_eleves = st.session_state.eleves["Nom de l'élève"].tolist()

    if cours_actif not in st.session_state.toutes_les_notes:
      df_init = pd.DataFrame(
          {
              "Nom de l'élève": noms_eleves,
              "P1": [0.0] * len(noms_eleves),
              "P2": [0.0] * len(noms_eleves),
              "EXAM S1": [0.0] * len(noms_eleves),
              "P3": [0.0] * len(noms_eleves),
              "P4": [0.0] * len(noms_eleves),
              "EXAM S2": [0.0] * len(noms_eleves),
          }
      )
      st.session_state.toutes_les_notes[cours_actif] = {
          "maximas": {
              "P1": max_p1,
              "P2": max_p2,
              "EXAM S1": max_ex1,
              "P3": max_p3,
              "P4": max_p4,
              "EXAM S2": max_ex2,
          },
          "notes": df_init,
      }
    else:
      st.session_state.toutes_les_notes[cours_actif]["maximas"] = {
          "P1": max_p1,
          "P2": max_p2,
          "EXAM S1": max_ex1,
          "P3": max_p3,
          "P4": max_p4,
          "EXAM S2": max_ex2,
      }
      df_actuel = st.session_state.toutes_les_notes[cours_actif]["notes"]
      for eleve in noms_eleves:
        if eleve not in df_actuel["Nom de l'élève"].values:
          nueva_ligne = pd.DataFrame(
              {
                  "Nom de l'élève": [eleve],
                  "P1": [0.0],
                  "P2": [0.0],
                  "EXAM S1": [0.0],
                  "P3": [0.0],
                  "P4": [0.0],
                  "EXAM S2": [0.0],
              }
          )
          df_actuel = pd.concat([df_actuel, nueva_ligne], ignore_index=True)
      st.session_state.toutes_les_notes[cours_actif]["notes"] = df_actuel

    st.write(
        f"Saisissez ou modifiez les notes des élèves pour le cours de :"
        f" **{cours_actif}**"
    )
    with st.form(key=f"form_notes_{cours_actif}"):
      edited_cotations = st.data_editor(
          st.session_state.toutes_les_notes[cours_actif]["notes"],
          use_container_width=True,
          hide_index=True,
          key=f"editor_{cours_actif}",
      )
      submitted_notes = st.form_submit_button(
          f"💾 Sauvegarder les notes de {cours_actif}"
      )
      if submitted_notes:
        st.session_state.toutes_les_notes[cours_actif]["notes"] = (
            edited_cotations
        )
        st.success(
            f"Les notes du cours de {cours_actif} ont été enregistrées avec"
            " succès !"
        )

# --- 4. BULLETINS ---
elif menu == "Bulletins":
  st.header("📄 Aperçu et Impression des Bulletins")

  eleve_selectionne = st.selectbox(
      "Sélectionner un élève", st.session_state.eleves["Nom de l'élève"]
  )

  if eleve_selectionne:
    infos = st.session_state.infos_classe

    st.markdown(f"### {infos['ecole']}")
    st.write(f"**GESTION DE SCOLARITÉ - Année {infos['annee']}**")
    st.markdown("---")

    col_a, col_b = st.columns(2)
    with col_a:
      st.write(f"**ÉLÈVE :** {eleve_selectionne}")
      st.write(f"**CLASSE :** {infos['classe']}")
    with col_b:
      st.write(f"**OPTION :** {infos['option']}")
      st.write(
          f"**NOMBRE DE MATIÈRES :** {len(st.session_state.toutes_les_notes)}"
      )

    st.markdown("#### EXTRAIT DU BULLETIN")

    if not st.session_state.toutes_les_notes:
      st.warning(
          "Aucune matière enregistrée pour le moment. Veuillez saisir des notes"
          " dans l'onglet 'Cotations & Calculs'."
      )
    else:
      lignes_bulletin = []
      tot_max_p1, tot_max_p2, tot_max_ex1, tot_max_s1 = 0, 0, 0, 0
      tot_max_p3, tot_max_p4, tot_max_ex2, tot_max_s2, tot_max_gen = (
          0,
          0,
          0,
          0,
          0,
      )
      tot_p1, tot_p2, tot_ex1, tot_s1 = 0.0, 0.0, 0.0, 0.0
      tot_p3, tot_p4, tot_ex2, tot_s2, tot_general = 0.0, 0.0, 0.0, 0.0, 0.0

      for nom_cours, donnees in st.session_state.toutes_les_notes.items():
        mx = donnees["maximas"]
        df_n = donnees["notes"]
        ligne_eleve = df_n[df_n["Nom de l'élève"] == eleve_selectionne]

        p1 = (
            float(ligne_eleve["P1"].values[0])
            if not ligne_eleve.empty
            else 0.0
        )
        p2 = (
            float(ligne_eleve["P2"].values[0])
            if not ligne_eleve.empty
            else 0.0
        )
        ex1 = (
            float(ligne_eleve["EXAM S1"].values[0])
            if not ligne_eleve.empty
            else 0.0
        )
        s1 = p1 + p2 + ex1

        p3 = (
            float(ligne_eleve["P3"].values[0])
            if not ligne_eleve.empty
            else 0.0
        )
        p4 = (
            float(ligne_eleve["P4"].values[0])
            if not ligne_eleve.empty
            else 0.0
        )
        ex2 = (
            float(ligne_eleve["EXAM S2"].values[0])
            if not ligne_eleve.empty
            else 0.0
        )
        s2 = p3 + p4 + ex2
        total_m = s1 + s2

        mx_s1 = mx["P1"] + mx["P2"] + mx["EXAM S1"]
        mx_s2 = mx["P3"] + mx["P4"] + mx["EXAM S2"]
        mx_gen = mx_s1 + mx_s2

        lignes_bulletin.append({
            "MATIÈRE": f"MAX ( {nom_cours} )",
            "P1": mx["P1"],
            "P2": mx["P2"],
            "EXAM S1": mx["EXAM S1"],
            "TOT S1": mx_s1,
            "P3": mx["P3"],
            "P4": mx["P4"],
            "EXAM S2": mx["EXAM S2"],
            "TOT S2": mx_s2,
            "TOTAL": mx_gen,
        })

        lignes_bulletin.append({
            "MATIÈRE": nom_cours,
            "P1": p1,
            "P2": p2,
            "EXAM S1": ex1,
            "TOT S1": s1,
            "P3": p3,
            "P4": p4,
            "EXAM S2": ex2,
            "TOT S2": s2,
            "TOTAL": total_m,
        })

        tot_max_p1 += mx["P1"]
        tot_max_p2 += mx["P2"]
        tot_max_ex1 += mx["EXAM S1"]
        tot_max_s1 += mx_s1
        tot_max_p3 += mx["P3"]
        tot_max_p4 += mx["P4"]
        tot_max_ex2 += mx["EXAM S2"]
        tot_max_s2 += mx_s2
        tot_max_gen += mx_gen

        tot_p1 += p1
        tot_p2 += p2
        tot_ex1 += ex1
        tot_s1 += s1
        tot_p3 += p3
        tot_p4 += p4
        tot_ex2 += ex2
        tot_s2 += s2
        tot_general += total_m

      lignes_bulletin.append({
          "MATIÈRE": "POINTS TOTAUX",
          "P1": tot_p1,
          "P2": tot_p2,
          "EXAM S1": tot_ex1,
          "TOT S1": tot_s1,
          "P3": tot_p3,
          "P4": tot_p4,
          "EXAM S2": tot_ex2,
          "TOT S2": tot_s2,
          "TOTAL": tot_general,
      })

      lignes_bulletin.append({
          "MATIÈRE": "MAXIMA GÉNÉRAUX",
          "P1": tot_max_p1,
          "P2": tot_max_p2,
          "EXAM S1": tot_max_ex1,
          "TOT S1": tot_max_s1,
          "P3": tot_max_p3,
          "P4": tot_max_p4,
          "EXAM S2": tot_max_ex2,
          "TOT S2": tot_max_s2,
          "TOTAL": tot_max_gen,
      })

      df_final_bulletin = pd.DataFrame(lignes_bulletin)
      st.dataframe(df_final_bulletin, use_container_width=True, hide_index=True)

      # --- GÉNÉRATION DU PDF PROFESSIONNEL ---
      def generer_pdf_bulletin():
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30
        )
        elements = []
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            'TitleStyle',
            parent=styles['Heading1'],
            fontSize=14,
            alignment=1,
            textColor=colors.HexColor('#1f385c'),
        )
        subtitle_style = ParagraphStyle(
            'SubTitleStyle',
            parent=styles['Normal'],
            fontSize=10,
            alignment=1,
            textColor=colors.HexColor('#555555'),
        )
        bold_style = ParagraphStyle(
            'BoldStyle', parent=styles['Normal'], fontSize=9, fontName='Helvetica-Bold'
        )
        normal_style = ParagraphStyle(
            'NormalStyle', parent=styles['Normal'], fontSize=9
        )

        elements.append(
            Paragraph(infos["ecole"].upper(), title_style)
        )
        elements.append(
            Paragraph(
                f"GESTION DE SCOLARITÉ - Année {infos['annee']}", subtitle_style
            )
        )
        elements.append(Spacer(1, 15))

        # En-tête des infos de l'élève
        info_data = [
            [
                Paragraph(f"<b>ÉLÈVE :</b> {eleve_selectionne}", normal_style),
                Paragraph(f"<b>OPTION :</b> {infos['option']}", normal_style),
            ],
            [
                Paragraph(f"<b>CLASSE :</b> {infos['classe']}", normal_style),
                Paragraph(
                    f"<b>NOMBRE DE MATIÈRES :</b> {len(st.session_state.toutes_les_notes)}",
                    normal_style,
                ),
            ],
        ]
        t_info = Table(info_data, colWidths=[270, 270])
        t_info.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f2f2f2")),
                ("PADDING", (0, 0), (-1, -1), 6),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
            ])
        )
        elements.append(t_info)
        elements.append(Spacer(1, 15))

        elements.append(Paragraph("<b>EXTRAIT DU BULLETIN</b>", bold_style))
        elements.append(Spacer(1, 8))

        # Conversion du DataFrame en tableau ReportLab
        table_data = [[
            Paragraph(f"<b>{col}</b>", bold_style)
            for col in df_final_bulletin.columns
        ]]
        for _, row in df_final_bulletin.iterrows():
          row_cells = []
          for col in df_final_bulletin.columns:
            val = str(row[col])
            row_cells.append(Paragraph(val, normal_style))
          table_data.append(row_cells)

        t_bulletin = Table(table_data, colWidths=[110, 45, 45, 55, 55, 45, 45, 55, 55, 50])
        t_bulletin.setStyle(
            TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#d9d9d9")),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#999999")),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ])
        )
        elements.append(t_bulletin)
        doc.build(elements)
        buffer.seek(0)
        return buffer

        # Bouton de téléchargement PDF

      st.markdown("---")
      pdf_file = generer_pdf_bulletin()
      st.download_button(
          label="📥 Télécharger l'extrait en PDF",
          data=pdf_file,
          file_name=(
              f"Bulletin_{eleve_selectionne.replace(' ', '_')}_{infos['classe']}.pdf"
          ),
          mime="application/pdf",
      )