# -*- coding: utf-8 -*-
"""
Construction d'une application interactive de visualisation de données
pour les enquêtes électorales françaises faites pour les élections européennes
de juin 2024

PAYS : France
VAGUES : 1 à 6

Auteurs :   Diego Antolinos-Basso
            Nicolas Sormani

Centre : Cevipof (SciencesPo - CNRS)
Année : 2024
"""



# importation des librairies utiles au projet
from shiny import App, ui, reactive
from shinywidgets import render_widget, render_plotly, output_widget
import shinyswatch
import pandas as pd
import numpy as np
import datetime
import orjson
import plotly.graph_objects as go



########
## UI ##
########

# bloc servant à définir les éléments contenus dans l'application
# définir des cadres graphiques personnalisés
def ui_card(title, *args):
    return (
        ui.div(
            {"class": "card mb-4"},
            ui.div(title, class_="card-header"),
            ui.div({"class": "card-body"}, *args),
        ),
    )

# définir la page principale
app_ui = ui.page_fillable(

    # définir le titre de l'application
    ui.h2("Enquête Électorale Française sur les élections européennes du 9 juin 2024"
    ),

    # définir les onglets contenus dans la page principale
    ui.navset_card_pill(

        # onglet 01 : PRESENTATION DE L'APPLICATION
        ui.nav_panel("Présentation",
                    # texte de présentation du projet et des enquêtes
                    ui.markdown(
                        """
                        ### L'Enquête Électorale Française

                        L'Enquête Électorale Française (ENEF) pour les élections européennes du 9 juin 2024
                        est un dispositif d'enquêtes par panel réalisées par l'institut _IPSOS_ pour le
                        _CEVIPOF_, la _Fondation Jean Jaurès_, _Institut Montaigne_ et _Le Monde_.
                        <br>
                        <br>
                        Composé de plus de 10 000 personnes, le panel d'individus est interrogé
                        à 6 reprises de juin 2023 à juin 2024, afin de mieux comprendre les logiques de
                        leurs décisions de vote pour ces élections.
                        <br>
                        Les résultats détaillés de ce dispositif d'enquêtes, accompagnés de décryptages et
                        d'analyses, sont disponibles sur la [page dédiée du Cevipof](https://www.sciencespo.fr/cevipof/fr/content/resultats-et-decrypyages-par-vagues.html).
                        <br>
                        <br>
                        L'attention de l'utilisateur est appelée sur le fait que les opinions mesurées en
                        pourcentage sont sujettes à un _aléa de mesure statistique_, ou _marge d'erreur_,
                        qu'il est important de prendre en compte lors de l'interprétation de ces nombres.
                        L'utilisateur pourra consulter la page 3 des [rapports de résultats détaillés](https://www.sciencespo.fr/cevipof/fr/content/resultats-et-decrypyages-par-vagues.html)
                        pour une évaluation synthétique de ces aléas, et une
                        [note](https://www.sciencespo.fr/cevipof/sites/sciencespo.fr.cevipof/files/Note_Inge%cc%81s1_electionspresidentielles2022_mars2022_V8.pdf)
                        pour une présentation détaillée de cette problématique.
                        <br>
                        ***
                        ### Une application interactive

                        Cette application présente brièvement quelques principaux résultats de cette enquête,
                        afin de les rendre plus accessibles et de contribuer au débat public.
                        <br>
                        <br>
                        Il est rappelé à l'utilisateur que ces résultats graphiques sont _à considérer avec la plus
                        grande prudence d'interprétation_, notamment ceux concernant les graphiques
                        de croisement de variables : un lien entre deux variables suggéré graphiquement doit nécessairement
                        être complété, validé ou infirmé par des analyses et modélisations statistiques approfondies.
                        Or, la présente application a été pensée uniquement à des fins de vulgarisation scientifique,
                        et non pour permettre une exploration approfondie des données, ni une analyse exhaustive et
                        robuste des potentiels liens structurels entre les variables.
                        <br>
                        <br>
                        Il est par conséquent vivement recommandé à l'utilisateur de [contacter le Cevipof](https://www.sciencespo.fr/cevipof/fr/liste-de-contacts.html)
                        et les chercheurs membres du laboratoire en cas de doute, ou pour toute question ou besoin
                        de clarification, de contextualisation ou d'analyse détaillée et commentée de ces
                        principaux résultats graphiques.
                        """
                    )
        ),

        # onglet 02 : TABLEAU DE BORD AVANT L'ELECTION
        ui.nav_panel("Tableau de bord avant l'élection",
            # définir deux colonnes
            ui.layout_columns(
                # colonne 01 : définition et commentaires des indicateurs globaux mis en exergue
                ui.card(
                    ui_card("INTITULES DES QUESTIONS",
                        ui.input_action_button("descript_inteur", "Intérêt pour l'élection"),
                        ui.input_action_button("descript_indcertvot", "Certitude d'aller voter"),
                    ),
                    ui_card("DERNIERES VALEURS ENREGISTREES - Mai 2024",
                        ui.layout_columns(
                            ui_card("Intérêt pour l'élection", "61,9%"),
                            ui_card("Certitude d'aller voter", "61,1%")
                        ),
                    ),
                ),
                # colonne 02 : graphique des indicateurs globaux par vague d'enquête
                ui.card(
                    # afficher une ligne d'indication pour l'utilisateur
                    ui.markdown(
                        """
                        ```
                        Pour afficher les valeurs du graphique, amener la souris sur les barres verticales grises (vagues de l'enquête).
                        Les marges d'erreur sont données dans les rapports de résultats détaillés de chaque vague.
                        ```
                        """
                    ),
                    # afficher le graphique des indicateurs globaux (voir définition dans le bloc 'Server' plus bas)
                    output_widget("Graph_TableauDeBord", width="auto", height="auto")
                ),
                # définir les largeurs des colonnes contenant les cadres graphiques
                col_widths=(3, 9)
            )
        ),

        # onglet 03 : CERTITUDE D'ALLER VOTER CROISEE AVEC DES VARIABLES SOCIO-DEMOGRAPHIQUES
        ui.nav_panel("Intention d'aller voter - Votants",
            # définir deux colonnes
            ui.layout_columns(
                # colonne 01 : informations et choix de l'utilisateur
                ui.card(
                    # cadre 01 : informations sur la variable de l'intention d'aller voter
                    ui_card("CERTITUDE D'ALLER VOTER",
                            # bouton 01 : information sur la question posée dans l'enquête
                            ui.input_action_button("Show_CERT_Vote_Question", # input ID
                                                   "Question posée dans l'enquête" # texte affiché dans le bouton
                            ),
                            # bouton 02 : information sur la variable sélectionnée pour les graphiques
                            ui.input_action_button("Show_CERTST_Vote_Info", # input ID
                                                   "Variable choisie pour les graphiques" # texte affiché dans le bouton
                            ),
                    ),
                    # cadre 02 : choix de la variable socio-démographique à croiser avec l'intention d'aller voter
                    ui_card("CHOISIR UNE VARIABLE SOCIO- DEMOGRAPHIQUE",
                            # groupe de boutons de sélection
                            ui.input_radio_buttons(
                                id="Select_VarSD_Vote",
                                label="",
                                choices={"SEXEST": "Genre",
                                         "AGERST": "Âge",
                                         "REG13ST": "Région",
                                         "AGGLO5ST": "Taille d'agglomération",
                                         "EMPST": "Type d'emploi occupé",
                                         "PCSIST": "Catégorie professionnelle",
                                         "EDUST": "Niveau de scolarité atteint",
                                         "REL1ST": "Religion",
                                         "ECO2ST2": "Revenu mensuel du foyer",
                                         "INTPOLST": "Intérêt pour la politique",
                                         "Q7ST": "Positionnement idéologique",
                                         "PROXST": "Préférence partisane"
                                }
                            ),
                            # bouton 03 : informations détaillées sur la variable socio-démographique (SD) choisie
                            ui.input_action_button("Show_VarSD_Vote_Info", # input ID : identifiant de la variable SD choisie
                                                   "Afficher sa description" # texte affiché dans le bouton
                            )
                    )
                ),
                # colonne 02 : graphique des variables croisées par vagues d'enquête
                ui.card(
                    # afficher une ligne d'indication pour l'utilisateur
                    ui.markdown(
                        """
                        ```
                        Pour afficher les valeurs du graphique, amener la souris sur les barres verticales grises (vagues de l'enquête).
                        Les marges d'erreur sont données dans les rapports de résultats détaillés de chaque vague.
                        ```
                        """
                    ),
                    # afficher le graphique ad hoc (voir définition dans le bloc 'Server' plus bas)
                    output_widget(id="Graph_Croise_Vote", width="auto", height="auto")
                ),
                # définir les largeurs des colonnes contenant les cadres graphiques
                col_widths=(3, 9)
            )
        ),

        # onglet 04 : ABSTENTION CROISEE AVEC DES VARIABLES SOCIO-DEMOGRAPHIQUES
        ui.nav_panel("Intention d'aller voter - Abstentionnistes",
            # définir deux colonnes
            ui.layout_columns(
                # colonne 01 : informations et choix de l'utilisateur
                ui.card(
                    # cadre 01 : informations sur la variable de l'intention d'aller voter
                    ui_card("CERTITUDE DE S'ABSTENIR",
                            # bouton 01 : information sur la question posée dans l'enquête
                            ui.input_action_button("Show_CERT_Abst_Question", # input ID
                                                   "Question posée dans l'enquête" # texte affiché dans le bouton
                            ),
                            # bouton 02 : information sur la variable sélectionnée pour les graphiques
                            ui.input_action_button("Show_CERTST_Abst_Info", # input ID
                                                   "Variable choisie pour les graphiques" # texte affiché dans le bouton
                            ),
                    ),
                    # cadre 02 : choix de la variable socio-démographique à croiser avec l'intention d'aller voter
                    ui_card("CHOISIR UNE VARIABLE SOCIO- DEMOGRAPHIQUE",
                            # groupe de boutons de sélection
                            ui.input_radio_buttons(
                                id="Select_VarSD_Abst",
                                label="",
                                choices={"SEXEST": "Genre",
                                         "AGERST": "Âge",
                                         "REG13ST": "Région",
                                         "AGGLO5ST": "Taille d'agglomération",
                                         "EMPST": "Type d'emploi occupé",
                                         "PCSIST": "Catégorie professionnelle",
                                         "EDUST": "Niveau de scolarité atteint",
                                         "REL1ST": "Religion",
                                         "ECO2ST2": "Revenu mensuel du foyer",
                                         "INTPOLST": "Intérêt pour la politique",
                                         "Q7ST": "Positionnement idéologique",
                                         "PROXST": "Préférence partisane"
                                }
                            ),
                            # bouton 03 : informations détaillées sur la variable socio-démographique choisie
                            ui.input_action_button("Show_VarSD_Abst_Info", # input ID
                                                   "Afficher sa description" # texte affiché dans le bouton
                            )
                    )
                ),

                # colonne 02: graphique des variables croisées par vagues d'enquête
                ui.card(
                        # afficher une ligne d'indication pour l'utilisateur
                        ui.markdown(
                            """
                            ```
                            Pour afficher les valeurs du graphique, amener la souris sur les barres verticales grises (vagues de l'enquête).
                            Les marges d'erreur sont données dans les rapports de résultats détaillés de chaque vague.
                            ```
                            """
                        ),
                        # afficher le graphique ad hoc (voir définition dans le bloc 'Server' plus bas)
                        output_widget(id="Graph_Croise_Abst", width="auto", height="auto")
                ),
                # définir les largeurs des colonnes contenant les cadres graphiques
                col_widths=(3, 9)
            )
        ),

        # onglet 05 : PARTICIPATION AVEC DES VARIABLES SOCIO-DEMO
        ui.nav_panel("Participation",
            # définir deux colonnes
            ui.layout_columns(
                # colonne 01 : informations et choix de l'utilisateur
                ui.card(
                    # cadre 01 : informations sur la variable de l'intention d'aller voter
                    ui_card("Participation au vote",
                            # bouton 01 : information sur la question posée dans l'enquête
                            ui.input_action_button("Show_PART_Question", # input ID
                                                   "Question posée dans l'enquête" # texte affiché dans le bouton
                            ),
                            # bouton 02 : information sur la variable sélectionnée pour les graphiques
                        ui.input_action_button("Show_PARTST_Info", # input ID
                                                   "Variable choisie pour les graphiques" # texte affiché dans le bouton
                            ),
                    ),
                    # cadre 02 : choix de la variable socio-démographique à croiser avec l'intention d'aller voter
                    ui_card("CHOISIR UNE VARIABLE SOCIO- DEMOGRAPHIQUE",
                            # groupe de boutons de sélection
                            ui.input_radio_buttons(
                                id="Select_VarSD_Part",
                                label="",
                                choices={"Y6SEXEST": "Genre",
                                         "Y6AGERST": "Âge",
                                         "Y6REG13ST": "Région",
                                         "Y6AGGLO5ST": "Taille d'agglomération",
                                         "Y6EMPST": "Type d'emploi occupé",
                                         "Y6PCSIST": "Catégorie professionnelle",
                                         "Y6EDUST": "Niveau de scolarité atteint",
                                         "Y6REL1ST": "Religion",
                                         "Y6ECO2ST2": "Revenu mensuel du foyer",
                                         "Y6INTPOLST": "Intérêt pour la politique",
                                         "Y6Q7ST": "Positionnement idéologique",
                                         "Y6PROXST": "Préférence partisane"
                                }
                            ),
                            # bouton 03 : informations détaillées sur la variable socio-démographique choisie
                            ui.input_action_button("Show_VarSD_Part_Info", # input ID
                                                   "Afficher sa description" # texte affiché dans le bouton
                            )
                    )
                ),

                # colonne 02: graphique des variables croisées par vagues d'enquête
                ui.card(
                        # afficher une ligne d'indication pour l'utilisateur
                        ui.markdown(
                            """
                            ```
                            Pour afficher les valeurs du graphique, amener la souris sur les barres verticales grises (vagues de l'enquête).
                            Les marges d'erreur sont données dans les rapports de résultats détaillés de chaque vague.
                            ```
                            """
                        ),
                        # afficher le graphique ad hoc (voir définition dans le bloc 'Server' plus bas)
                        output_widget(id="Graph_Croise_Part", width="auto", height="auto")
                ),
                # définir les largeurs des colonnes contenant les cadres graphiques
                col_widths=(3, 9)
            )
        ),
        id="tab"
    ),
    # définition du theme de couleur de l'application
    theme = shinyswatch.theme.simplex
)



#############
## SERVER  ##
#############

# bloc servant à définir les méthodes pour créer les caractéristiques détaillées
# des objets de l'application, ainsi que leur réactivité face aux choix de
# l'utilisateur de l'application
def server(input, output, session):

    #############
    # onglet 02 #
    #############
    # bouton 01 : décrire la variable 'intérêt pour l'élection'
    @reactive.effect
    @reactive.event(input.descript_inteur)
    def _():
        m = ui.modal("La question posée aux répondants est la suivante : 'Sur une échelle de 0 à 10, \
                     où 0 signifie aucun intérêt et 10 signifie énormément d'intérêt, quel est votre \
                     niveau d'intérêt pour les prochaines élections européennes de 2024 ?'. \
                     L'indicateur est alors calculé comme la somme des fréquences obtenues aux \
                     modalités 7 à 10 de cette question.",
                    title="Informations complémentaires sur la question contenue dans l'enquête :",
                    easy_close=False
            )
        ui.modal_show(m)

    # bouton 02 : décrire la variable 'certitude d'aller voter'
    @reactive.effect
    @reactive.event(input.descript_indcertvot)
    def _():
        m = ui.modal("La certitude d'aller voter est calculée à partir de la question suivante : \
                     'Les prochaines élections européennes se tiendront le 9 juin 2024 en France. \
                     Pouvez-vous donner une note de 0 à 10 sur votre intention d’aller voter lors de ces \
                     élections européennes ? 0 signifiant  que vous êtes vraiment tout à fait certain de \
                     ne pas aller voter, et 10 que vous êtes vraiment tout à fait certain d’aller voter.' \
                     L'indicateur est alors calculé comme la somme des fréquences obtenues aux modalités \
                     9 et 10 de cette question.",
                    title="Informations complémentaires sur la question contenue dans l'enquête :",
                    easy_close=False
            )
        ui.modal_show(m)

    # graphique : représenter les deux variables globales du tableau de bord
    @output
    @render_widget
    def Graph_TableauDeBord():

        # importer les données
        df = pd.read_csv("data/indicateurs.csv")

        # calculer les intervalles de confiance à 95% de probabilité (ou 5% de risque)
        # d'après la formule pour les proportions contenue dans l'encadré 3 du document :
        # https://www.sciencespo.fr/cevipof/sites/sciencespo.fr.cevipof/files/Note_Inge%cc%81s1_electionspresidentielles2022_mars2022_V8.pdf
        # calculer la borne BASSE
        df["IC95bb"] = df["pct"] - 1.96*np.sqrt((df["pct"]*(100-df["pct"]))/df["TAILLEECH"])
        # calculer la borne HAUTE
        df["IC95bh"] = df["pct"] + 1.96*np.sqrt((df["pct"]*(100-df["pct"]))/df["TAILLEECH"])

        # créer la figure en mémoire
        fig = go.Figure()

        # créer les couleurs des courbes
        couleurs_mod = ['blue', 'red']

        # ajouter une courbe pour chaque modalité de la variable SD
        # pour chacune des modalités de la variable SD :
        for i, var_modal in enumerate(df['Indicateurs'].unique()):
            # trier les valeurs de la table selon la vague de l'enquête
            df_var = df[df['Indicateurs'] == var_modal].sort_values('VAGUE')
            # ajouter la courbe principale (pourcentage selon la vague)
            fig.add_trace(go.Scatter( # ajouter un objet de type Scatter à la zone de graphique
                x=df_var['VAGUE'],
                y=df_var['pct'],
                mode='lines+markers',
                name=var_modal,
                line=dict(color=couleurs_mod[i]),
                # afficher les valeurs sous le format 'xx.x%' dans la bulle qui s'affiche
                # au survol de la courbe par la souris, et supprimer toutes les autres
                # informations qui pourraient s'afficher en plus (nom de la modalité)
                hovertemplate='%{y:.1f}%<extra></extra>'
            ))
            # ajouter l'intervalle de confiance autour de la courbe principale des données
            fig.add_trace(go.Scatter(
                # définir une zone fermée, en ajoutant la liste des dates inversées
                # à la liste des dates chronologiques des vagues de l'enquête
                x=df_var['VAGUE'].tolist() + df_var['VAGUE'].tolist()[::-1],
                # créer le contour de l'intervalle de confiance, en ajoutant la
                # liste inversée des bornes inférieures à la liste des bornes supérieures
                y=df_var['IC95bh'].tolist() + df_var['IC95bb'].tolist()[::-1],
                # remplir l'espace entre les lignes ainsi définies
                fill='toself',
                # définir la couleur de remplissage des zones de confiance
                # identique à la couleur des courbes principales auxquelles
                # elles correspondent
                fillcolor=couleurs_mod[i],
                # rendre la ligne de contour de la zone de confiance invisible
                # (opacité = 0, soit transparence totale)
                line=dict(color='rgba(255, 255, 255, 0)'),
                # empêcher l'affichage d'informations quand la souris survole
                # la zone de confiance
                hoverinfo="skip",
                # empêcher l'affichage des zones de confiance dans la légende
                showlegend=False,
                # définir l'opacité de la zone de confiance
                # (20% d'opacité correspondent à une transparence de 80%)
                opacity=0.2,
            ))

        # ajouter des lignes verticales pour chaque vague de l'enquête
        for date in df['VAGUE'].unique():
            fig.add_vline(x=date, line_width=2, line_color="grey")

        # mise en forme détaillée et personnalisée du graphique
        fig.update_layout(
            # définir le titre du graphique et son apparence
            title={'text': "Indicateurs généraux",
                   'y':1,
                   'x':0,
                   'xanchor': 'left',
                   'yanchor': 'top'
                    },
            # définir le titre de l'axe des ordonnées et son apparence
            yaxis_title=dict(
                text='Pourcentage de répondants (%)',
                font_size=12
            ),
            # définir l'affichage séparé des valeurs de % affichées sur les
            # courbes quand la souris survole chaque vague (barre verticale)
            hovermode="x",
            # définir le thème général de l'apparence du graphique
            template="plotly_white",
            # définir l'apparence de l'axe des abscisses
            xaxis=dict(
                tickformat='%Y-%m-%d',
                hoverformat='%Y-%m-%d',
            ),
            # définir les sources des données
            annotations=[
                dict(
                    xref='paper',
                    yref='paper',
                    x=0,
                    y=-0.1,
                    xanchor='left',
                    yanchor='top',
                    text=   'Enquête électorale française pour les ' +
                            'élections européennes de juin 2024, ' +
                            'par Ipsos Sopra Steria, Cevipof, ' +
                            'Le Monde, Fondation Jean Jaurès et ' +
                            'Institut Montaigne (2024)',
                    font=dict(size=10, color='grey'),
                    showarrow=False
                )
            ],
            # définir les marges de la zone graphique
            # (augmentées à droite pour la légende)
            margin=dict(b=50, # b = bottom
                        t=30,  # t = top
                        r=200 # r = right
                        ),
            # fixer la position et la taille de la légende
            legend=dict(
                x=1.02, # position horizontale de la légende (1 = à droite du graphique)
                y=1, # position verticale de la légende (1 = en haut)
                xanchor='left', # ancrer la légende à gauche de sa position x
                yanchor='top', # ancrer la légende en haut de sa position y
                bgcolor='rgba(255,255,255,0.8)' # fond légèrement transparent
            )
        )

        # ajuster l'axe des ordonnées en fonction des valeurs observées
        fig.update_yaxes(range=[40, 65])

        # modifier l'apparence des courbes (affinées et "arrondies")
        fig.update_traces(line_shape="spline")

        # retourner le graphique
        return fig

    #############
    # onglet 03 #
    #############

    # bouton 01 : décrire la question posée dans l'enquête
    @reactive.effect
    @reactive.event(input.Show_CERT_Vote_Question)
    def _():
        m = ui.modal("La question posée aux répondants est la suivante : 'Les prochaines élections européennes se tiendront le 9 juin 2024 en France. \
                    Pouvez-vous donner une note de 0 à 10 sur votre intention d’aller voter lors de ces élections européennes ? \
                    0 signifiant que vous êtes vraiment tout à fait certain de ne pas aller voter, \
                    et 10 que vous êtes vraiment tout à fait certain d’aller voter.'",
                    title="Informations complémentaires sur la question contenue dans l'enquête :",
                    easy_close=False
            )
        ui.modal_show(m)

    # bouton 02 : décrire la variable de l'intention d'aller voter choisie
    @reactive.effect
    @reactive.event(input.Show_CERTST_Vote_Info)
    def _():
        m = ui.modal("La variable sur la certitude d'aller voter présentée ici sur les graphiques est une modalité synthétique \
                    de la question posée aux répondants de l'enquête. \
                    Ainsi, parmi les onze modalités de réponse (0 à 10) à la question de l'enquête, \
                    on ne retient que les valeurs 9 et 10, dont on additionne les fréquences respectives.",
                    title="Informations complémentaires sur la variable choisie pour les graphiques :",
                    easy_close=False
            )
        ui.modal_show(m)

    # bouton 03 : afficher la description de la variable socio-démographique choisie
    # avec plusieurs parties de texte qui dépendent de ce choix (via des dictionnaires)
    @reactive.effect
    @reactive.event(input.Show_VarSD_Vote_Info)
    def _():
        # définir le nom de la variable socio-démographique choisie
        dico_nom_var = {
                    "SEXEST": "Genre",
                    "AGERST": "Âge",
                    "REG13ST": "Région",
                    "AGGLO5ST": "Taille d'agglomération",
                    "EMPST": "Type d'emploi occupé",
                    "PCSIST": "Catégorie professionnelle",
                    "EDUST": "Niveau de scolarité atteint",
                    "REL1ST": "Religion",
                    "ECO2ST2": "Revenu mensuel du foyer",
                    "INTPOLST": "Intérêt pour la politique",
                    "Q7ST": "Positionnement idéologique",
                    "PROXST": "Préférence partisane"
        }
        # définir la question de l'enquête associée à la variable socio-démographique choisie
        dico_question_var = {
                    "SEXEST": "Êtes-vous ?",
                    "AGERST": "Quelle est votre date de naissance ?",
                    "REG13ST": "Veuillez indiquer le département et la commune où vous résidez.",
                    "AGGLO5ST": "Veuillez indiquer le département et la commune où vous résidez.",
                    "EMPST": "Quelle est votre situation professionnelle actuelle ?",
                    "PCSIST": "Quelle est votre situation professionnelle actuelle ?",
                    "EDUST": "Choisissez votre niveau de scolarité le plus élevé.",
                    "REL1ST": "Quelle est votre religion, si vous en avez une ?",
                    "ECO2ST2": " Pour finir, nous avons besoin de connaître, à des fins statistiques uniquement, la tranche dans laquelle se situe le revenu MENSUEL NET de votre FOYER après déduction des impôts sur le revenu (veuillez considérer toutes vos sources de revenus: salaires, bourses, prestations retraite et sécurité sociale, dividendes, revenus immobiliers, pensions alimentaires etc.).",
                    "INTPOLST": "De manière générale, diriez-vous que vous vous intéressez à la politique ?",
                    "Q7ST": "Sur une échelle de 0 à 10, où 0 correspond à la gauche et 10 correspond à la droite, où diriez-vous que vous vous situez ?",
                    "PROXST": "De quel parti vous sentez-vous proche ou moins éloigné que les autres ?"
        }
        # définir les modalités de réponse à la question de l'enquête associée à la variable socio-démographique choisie
        dico_modalite_var = {
                    "SEXEST": "1 = 'Homme' ; 2 = 'Femme'",
                    "AGERST": "1 = '18 à 24 ans' ; 2 = '25 à 34 ans' ; 3 = '35 à 49 ans' ; 4 = '50 à 59 ans' ; 5 = '60 ans et plus'",
                    "REG13ST": "1 = 'Ile de France' ; 2 = 'Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)' ; 3 = 'Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)' ; 4 = 'Sud ouest (Nouvelle Aquitaine et Occitanie)' ; 5 = 'Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)'",
                    "AGGLO5ST": "1 = 'Zone rurale (moins de 2 000 habitants)' ; 2 = 'Zone urbaine de 2 000 à 9 999 habitants' ; 3 = 'Zone urbaine de 10 000 à 49 999 habitants' ; 4 = 'Zone urbaine de 50 000 à 199 999 habitants' ; 5 = 'Zone urbaine de 200 000 habitants et plus'",
                    "EMPST": "1 = 'Salarié (salarié à plein temps ou à temps partiel)' ; 2 = 'Indépendant (travaille à mon compte)' ; 3 = 'Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)'",
                    "PCSIST": "1 = 'Agriculteur exploitant, artisan, commerçant, chef d'entreprise' ; 2 = 'Cadre supérieur' ; 3 = 'Profession intermédiaire' ; 4 = 'Employé' ; 5 = 'Ouvrier' ; 6 = 'Retraité, inactif'",
                    "EDUST": "1 = 'Aucun diplôme' ; 2 = 'CAP, BEP' ; 3 = 'Baccalauréat' ; 4 = 'Bac +2' ; 5 = 'Bac +3 et plus'",
                    "REL1ST": "1 = 'Catholique' ; 2 = 'Juive' ; 3 = 'Musulmane' ; 4 = 'Autre religion (protestante, boudhiste ou autre)' ; 5 = 'Sans religion'",
                    "ECO2ST2": "1 = 'Moins de 1 250 euros' ; 2 = 'De 1 250 euros à 1 999 euros' ; 3 = 'De 2 000 à 3 499 euros' ; 4 = 'De 3 500 à 4 999 euros' ; 5 = 'De 3 500 à 4 999 euros'",
                    "INTPOLST": "1 = 'Beaucoup' ; 2 = 'Un peu' ; 3 = 'Pas vraiment' ; 4 = 'Pas du tout'",
                    "Q7ST": "1 = 'Très à gauche' ; 2 = 'Plutôt à gauche' ; 3 = 'Au centre' ; 4 = 'Plutôt à droite' ; 5 = 'Très à droite'",
                    "PROXST": "1 = 'Très à gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)' ; 2 = 'Gauche (Parti Socialiste, Europe Ecologie - Les Verts)' ; 3 = 'Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, L’UDI (Union des Démocrates et Indépendants))' ; 4 = 'Droite (Les Républicains)' ; 5 = 'Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)' ; 6 = 'Autre parti ou aucun parti'"
        }
        # définir le texte complet à afficher (avec parties fixes et variables en fonction du choix effectué)
        m = ui.modal("La variable '%s' correspond à ou est calculée à partir de la question suivante posée aux répondants : \
                     '%s', \
                     et ses modalités de réponse (inchangées par rapport au questionnaire ou regroupées pour les présents graphiques) sont : \
                     %s." % (dico_nom_var.get("%s" % input.Select_VarSD_Vote()),
                             dico_question_var.get("%s" % input.Select_VarSD_Vote()),
                             dico_modalite_var.get("%s" % input.Select_VarSD_Vote())
                     ),
                     title="Informations complémentaires sur la variable socio-démographique choisie :",
                     easy_close=False
            )
        ui.modal_show(m)

    # graphique
    @output
    @render_plotly
    def Graph_Croise_Vote():
        # définir la partie variable du titre
        dico_titre = {
                    "SEXEST": "du genre",
                    "AGERST": "de l'âge",
                    "REG13ST": "de la région de résidence",
                    "AGGLO5ST": "de la taille de l'agglomération de résidence",
                    "EMPST": "du type d'emploi occupé",
                    "PCSIST": "de la catégorie socio-professionnelle",
                    "EDUST": "du niveau de scolarité atteint",
                    "REL1ST": "de la religion",
                    "ECO2ST2": "du revenu mensuel du foyer",
                    "INTPOLST": "de l'intérêt pour la politique",
                    "Q7ST": "du positionnement idéologique",
                    "PROXST": "de la préférence partisane"
        }
        # définir la partie variable du titre de la légende
        dico_legende = {
                    "SEXEST": "Genre",
                    "AGERST": "Âge",
                    "REG13ST": "Région",
                    "AGGLO5ST": "Taille d'agglomération",
                    "EMPST": "Type d'emploi occupé",
                    "PCSIST": "Catégorie professionnelle",
                    "EDUST": "Niveau de scolarité atteint",
                    "REL1ST": "Religion",
                    "ECO2ST2": "Revenu mensuel du foyer",
                    "INTPOLST": "Intérêt pour la politique",
                    "Q7ST": "Positionnement idéologique",
                    "PROXST": "Préférence partisane"
        }
        # définir l'échelle de l'axe des ordonnées en fonction des
        # valeurs prises par la variable socio-démographique choisie
        dico_echelleY = {
                    "SEXEST": [35, 65],
                    "AGERST": [25, 80],
                    "REG13ST": [40, 65],
                    "AGGLO5ST": [40, 65],
                    "EMPST": [35, 70],
                    "PCSIST": [25, 75],
                    "EDUST": [35, 65],
                    "REL1ST": [20, 70],
                    "ECO2ST2": [30, 70],
                    "INTPOLST": [10, 90],
                    "Q7ST": [30, 85],
                    "PROXST": [20, 75],
        }

        # définir une fonction qui affiche les étiquettes
        # des modalités de la variablr SD choisie dans la légende
        # sur plusieurs lignes si leur longueur initiale dépasse la
        # largeur du cadre de la légende
        def wrap_label(label, max_length=20):
            if len(label) <= max_length:
                return label
            words = label.split()
            lines = []
            current_line = []
            current_length = 0
            for word in words:
                if current_length + len(word) > max_length:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = len(word)
                else:
                    current_line.append(word)
                    current_length += len(word) + 1
            if current_line:
                lines.append(' '.join(current_line))
            return '<br>'.join(lines)

        # importer les données
        csvfile = "data/T_certst3_" + "%s" % input.Select_VarSD_Vote().lower() + ".csv"
        data = pd.read_csv(csvfile)

        # supprimer la première colonne (vide) de la base de donnée
        data = data.drop(data.columns[0], axis=1)

        # calculer les intervalles de confiance à 95% de probabilité (ou 5% de risque)
        # d'après la formule pour les proportions contenue dans l'encadré 3 du document :
        # https://www.sciencespo.fr/cevipof/sites/sciencespo.fr.cevipof/files/Note_Inge%cc%81s1_electionspresidentielles2022_mars2022_V8.pdf
        # calculer la borne BASSE
        data["IC95bb"] = data["pct"] - 1.96*np.sqrt((data["pct"]*(100-data["pct"]))/data["TAILLEECH"])
        # calculer la borne HAUTE
        data["IC95bh"] = data["pct"] + 1.96*np.sqrt((data["pct"]*(100-data["pct"]))/data["TAILLEECH"])

        # créer la figure en mémoire
        fig = go.Figure()

        # créer et sélectionner les couleurs des courbes pour les modalités de la variable SD
        couleurs = ['blue', 'red', 'green', 'purple', 'orange', 'magenta']
        nb_mod = len(data["%s" % input.Select_VarSD_Vote()].unique())
        # array : l'indice de position commence à 0, et se termine une valeur
        # avant le nombre indiqué comme limite à droite dans la sélection
        couleurs_mod = couleurs[:nb_mod]

        # ajouter une courbe pour chaque modalité de la variable SD
        # pour chacune des modalités de la variable SD :
        for i, varSD_modal in enumerate(data["%s" % input.Select_VarSD_Vote()].unique()):
            # trier les valeurs de la table selon la vague de l'enquête
            df_varSD = data[data["%s" % input.Select_VarSD_Vote()] == varSD_modal].sort_values('VAGUE')
            # ajouter la courbe principale (pourcentage selon la vague)
            fig.add_trace(go.Scatter( # ajouter un objet de type Scatter à la zone de graphique
                x=df_varSD['VAGUE'],
                y=df_varSD['pct'],
                # afficher les courbes avec des marqueurs (ronds)
                mode='lines+markers',
                # afficher les étiquettes des modalités sur plusieurs lignes dans le cadre
                # de la légende
                name=wrap_label(varSD_modal),
                # afficher les courbes selon le dictionnaire de couleurs
                line=dict(color=couleurs_mod[i]),
                # afficher les valeurs sous le format 'xx.x%' dans la bulle qui s'affiche
                # au survol de la courbe par la souris, et supprimer toutes les autres
                # informations qui pourraient s'afficher en plus (nom de la modalité)
                hovertemplate='%{y:.1f}%<extra></extra>'
            ))
            # ajouter l'intervalle de confiance autour de la courbe principale des données
            fig.add_trace(go.Scatter(
                # définir une zone fermée, en ajoutant la liste des dates inversées
                # à la liste des dates chronologiques des vagues de l'enquête
                x=df_varSD['VAGUE'].tolist() + df_varSD['VAGUE'].tolist()[::-1],
                # créer le contour de l'intervalle de confiance, en ajoutant la
                # liste inversée des bornes inférieures à la liste des bornes supérieures
                y=df_varSD['IC95bh'].tolist() + df_varSD['IC95bb'].tolist()[::-1],
                # remplir l'espace entre les lignes ainsi définies
                fill='toself',
                # définir la couleur de remplissage des zones de confiance
                # identique à la couleur des courbes principales auxquelles
                # elles correspondent
                fillcolor=couleurs_mod[i],
                # rendre la ligne de contour de la zone de confiance invisible
                # (opacité = 0, soit transparence totale)
                line=dict(color='rgba(255, 255, 255, 0)'),
                # empêcher l'affichage d'informations quand la souris survole
                # la zone de confiance
                hoverinfo="skip",
                # empêcher l'affichage des zones de confiance dans la légende
                showlegend=False,
                # définir l'opacité de la zone de confiance
                # (20% d'opacité correspond à une transparence de 80%)
                opacity=0.2,
            ))

        # ajouter des lignes verticales pour chaque vague de l'enquête
        for date in data['VAGUE'].unique():
            fig.add_vline(x=date, line_width=2, line_color="grey")

        # mise en forme détaillée et personnalisée du graphique
        fig.update_layout(
            title={'text': "Certitude d'aller voter en fonction %s" % dico_titre.get("%s" % input.Select_VarSD_Vote()),
                    'y':1,
                    'x':0,
                    'xanchor': 'left',
                    'yanchor': 'top'
            },
            # définir le titre de la légende
            legend_title="%s" % dico_legende.get("%s" % input.Select_VarSD_Vote()),
            # définir l'affichage séparé des valeurs de % affichées sur les
            # courbes quand la souris survole chaque vague (barre verticale)
            hovermode="x",
            # définir le thème général de l'apparence du graphique
            template="plotly_white",
             # définir l'apparence de l'axe des abscisses
            xaxis=dict(
                tickformat='%Y-%m-%d',
                hoverformat='%Y-%m-%d',
                # ajouter un 'rangeslider' sous le graphique
                rangeslider=dict(visible=False), # désactivé actuellement
                # ajouter des boutons au-dessus du graphique pour sélectionner
                # la plage temporelle à observer
                rangeselector=dict(
                    buttons=list([
                        dict(step="all", label="Depuis la 1ère vague de l'enquête"),
                        dict(count=9, label="Depuis 9 mois", step="month", stepmode="backward"),
                        dict(count=6, label="Depuis 6 mois", step="month", stepmode="backward"),
                        dict(count=3, label="Depuis 3 mois", step="month", stepmode="backward")
                    ])
                )
            ),
            # définir le titre de l'axe des ordonnées et son apparence
            yaxis_title=dict(
                text='Pourcentage de répondants (%)',
                font_size=12
            ),
            # définir les sources des données
            annotations=[
                dict(
                    xref='paper',
                    yref='paper',
                    x=0,
                    y=-0.1,
                    xanchor='left',
                    yanchor='top',
                    text=   'Enquête électorale française pour les ' +
                            'élections européennes de juin 2024, ' +
                            'par Ipsos Sopra Steria, Cevipof, ' +
                            'Le Monde, Fondation Jean Jaurès et ' +
                            'Institut Montaigne (2024)',
                    font=dict(size=10, color='grey'),
                    showarrow=False,
                )
            ],
            # définir les marges de la zone graphique
            # (augmentées à droite pour le cadre fixe de la légende)
            margin=dict(b=50, # b = bottom
                        t=50,  # t = top
                        l=50, # l = left
                        r=200 # r = right
                        ),
            # fixer la position de la légende
            legend=dict(
                orientation="v",
                valign='top',  # aligner le texte en haut de chaque marqueur de la légende
                x=1.02, # position horizontale de la légende (1 = à droite du graphique)
                y=1, # position verticale de la légende (1 = en haut)
                xanchor='left', # ancrer la légende à gauche de sa position x
                yanchor='top', # ancrer la légende en haut de sa position y
                bgcolor='rgba(255,255,255,0.8)' # fond légèrement transparent
            )
        )

        # ajuster l'axe des ordonnées en fonction des valeurs observées
        fig.update_yaxes(range=dico_echelleY.get("%s" % input.Select_VarSD_Vote()))

        # modifier l'apparence des courbes (affinées et "arrondies")
        fig.update_traces(line_shape="spline")

        # retourner le graphique
        return fig

    #############
    # onglet 04 #
    #############

    # bouton 01 : décrire la question posée dans l'enquête
    @reactive.effect
    @reactive.event(input.Show_CERT_Abst_Question)
    def _():
        m = ui.modal("La question posée aux répondants est la suivante : 'Les prochaines élections européennes se tiendront le 9 juin 2024 en France. \
                    Pouvez-vous donner une note de 0 à 10 sur votre intention d’aller voter lors de ces élections européennes ? \
                    0 signifiant que vous êtes vraiment tout à fait certain de ne pas aller voter, \
                    et 10 que vous êtes vraiment tout à fait certain d’aller voter.'",
                    title="Informations complémentaires sur la question contenue dans l'enquête :",
                    easy_close=False
            )
        ui.modal_show(m)

    # bouton 02 : décrire la variable de l'intention d'aller voter choisie
    @reactive.effect
    @reactive.event(input.Show_CERTST_Abst_Info)
    def _():
        m = ui.modal("La variable sur la certitude de s'abstenir présentée ici sur les graphiques est une modalité synthétique \
                    de la question posée aux répondants de l'enquête. \
                    Ainsi, parmi les onze modalités de réponse (0 à 10) à la question de l'enquête, \
                    on ne retient que les valeurs 0 à 5, dont on additionne les fréquences respectives.",
                    title="Informations complémentaires sur la variable choisie pour les graphiques :",
                    easy_close=False
            )
        ui.modal_show(m)

    # bouton 03 : afficher la description de la variable socio-démographique choisie
    # avec plusieurs parties de texte qui dépendent de ce choix (via des dictionnaires)
    @reactive.effect
    @reactive.event(input.Show_VarSD_Abst_Info)
    def _():
        # définir le nom de la variable socio-démographique choisie
        dico_nom_var = {
                    "SEXEST": "Genre",
                    "AGERST": "Âge",
                    "REG13ST": "Région",
                    "AGGLO5ST": "Taille d'agglomération",
                    "EMPST": "Type d'emploi occupé",
                    "PCSIST": "Catégorie professionnelle",
                    "EDUST": "Niveau de scolarité atteint",
                    "REL1ST": "Religion",
                    "ECO2ST2": "Revenu mensuel du foyer",
                    "INTPOLST": "Intérêt pour la politique",
                    "Q7ST": "Positionnement idéologique",
                    "PROXST": "Préférence partisane"
        }
        # définir la question de l'enquête associée à la variable socio-démographique choisie
        dico_question_var = {
                    "SEXEST": "Êtes-vous ?",
                    "AGERST": "Quelle est votre date de naissance ?",
                    "REG13ST": "Veuillez indiquer le département et la commune où vous résidez.",
                    "AGGLO5ST": "Veuillez indiquer le département et la commune où vous résidez.",
                    "EMPST": "Quelle est votre situation professionnelle actuelle ?",
                    "PCSIST": "Quelle est votre situation professionnelle actuelle ?",
                    "EDUST": "Choisissez votre niveau de scolarité le plus élevé.",
                    "REL1ST": "Quelle est votre religion, si vous en avez une ?",
                    "ECO2ST2": " Pour finir, nous avons besoin de connaître, à des fins statistiques uniquement, la tranche dans laquelle se situe le revenu MENSUEL NET de votre FOYER après déduction des impôts sur le revenu (veuillez considérer toutes vos sources de revenus: salaires, bourses, prestations retraite et sécurité sociale, dividendes, revenus immobiliers, pensions alimentaires etc.).",
                    "INTPOLST": "De manière générale, diriez-vous que vous vous intéressez à la politique ?",
                    "Q7ST": "Sur une échelle de 0 à 10, où 0 correspond à la gauche et 10 correspond à la droite, où diriez-vous que vous vous situez ?",
                    "PROXST": "De quel parti vous sentez-vous proche ou moins éloigné que les autres ?"
        }
        # définir les modalités de réponse à la question de l'enquête associée à la variable socio-démographique choisie
        dico_modalite_var = {
                    "SEXEST": "1 = 'Homme' ; 2 = 'Femme'",
                    "AGERST": "1 = '18 à 24 ans' ; 2 = '25 à 34 ans' ; 3 = '35 à 49 ans' ; 4 = '50 à 59 ans' ; 5 = '60 ans et plus'",
                    "REG13ST": "1 = 'Ile de France' ; 2 = 'Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)' ; 3 = 'Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)' ; 4 = 'Sud ouest (Nouvelle Aquitaine et Occitanie)' ; 5 = 'Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)'",
                    "AGGLO5ST": "1 = 'Zone rurale (moins de 2 000 habitants)' ; 2 = 'Zone urbaine de 2 000 à 9 999 habitants' ; 3 = 'Zone urbaine de 10 000 à 49 999 habitants' ; 4 = 'Zone urbaine de 50 000 à 199 999 habitants' ; 5 = 'Zone urbaine de 200 000 habitants et plus'",
                    "EMPST": "1 = 'Salarié (salarié à plein temps ou à temps partiel)' ; 2 = 'Indépendant (travaille à mon compte)' ; 3 = 'Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)'",
                    "PCSIST": "1 = 'Agriculteur exploitant, artisan, commerçant, chef d'entreprise' ; 2 = 'Cadre supérieur' ; 3 = 'Profession intermédiaire' ; 4 = 'Employé' ; 5 = 'Ouvrier' ; 6 = 'Retraité, inactif'",
                    "EDUST": "1 = 'Aucun diplôme' ; 2 = 'CAP, BEP' ; 3 = 'Baccalauréat' ; 4 = 'Bac +2' ; 5 = 'Bac +3 et plus'",
                    "REL1ST": "1 = 'Catholique' ; 2 = 'Juive' ; 3 = 'Musulmane' ; 4 = 'Autre religion (protestante, boudhiste ou autre)' ; 5 = 'Sans religion'",
                    "ECO2ST2": "1 = 'Moins de 1 250 euros' ; 2 = 'De 1 250 euros à 1 999 euros' ; 3 = 'De 2 000 à 3 499 euros' ; 4 = 'De 3 500 à 4 999 euros' ; 5 = 'De 3 500 à 4 999 euros'",
                    "INTPOLST": "1 = 'Beaucoup' ; 2 = 'Un peu' ; 3 = 'Pas vraiment' ; 4 = 'Pas du tout'",
                    "Q7ST": "1 = 'Très à gauche' ; 2 = 'Plutôt à gauche' ; 3 = 'Au centre' ; 4 = 'Plutôt à droite' ; 5 = 'Très à droite'",
                    "PROXST": "1 = 'Extême gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)' ; 2 = 'Gauche (Parti Socialiste, Europe Ecologie - Les Verts)' ; 3 = 'Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, L’UDI (Union des Démocrates et Indépendants))' ; 4 = 'Droite (Les Républicains)' ; 5 = 'Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)' ; 6 = 'Autre parti ou aucun parti'"
        }
        # définir le texte complet à afficher (avec parties fixes et variables en fonction du choix effectué)
        m = ui.modal("La variable '%s' correspond à ou est calculée à partir de la question suivante posée aux répondants : \
                     '%s', \
                     et ses modalités de réponse (inchangées par rapport au questionnaire ou regroupées pour les présents graphiques) sont : \
                     %s." % (dico_nom_var.get("%s" % input.Select_VarSD_Abst()),
                             dico_question_var.get("%s" % input.Select_VarSD_Abst()),
                             dico_modalite_var.get("%s" % input.Select_VarSD_Abst())
                     ),
                     title="Informations complémentaires sur la variable socio-démographique choisie :",
                     easy_close=False
            )
        ui.modal_show(m)

    # graphique
    @output
    @render_plotly
    def Graph_Croise_Abst():
        # définir la partie variable du titre
        dico_titre = {
                    "SEXEST": "du genre",
                    "AGERST": "de l'âge",
                    "REG13ST": "de la région de résidence",
                    "AGGLO5ST": "de la taille de l'agglomération de résidence",
                    "EMPST": "du type d'emploi occupé",
                    "PCSIST": "de la catégorie socio-professionnelle",
                    "EDUST": "du niveau de scolarité atteint",
                    "REL1ST": "de la religion",
                    "ECO2ST2": "du revenu mensuel du foyer",
                    "INTPOLST": "de l'intérêt pour la politique",
                    "Q7ST": "du positionnement idéologique",
                    "PROXST": "de la préférence partisane"
        }
        # définir la partie variable du titre de la légende
        dico_legende = {
                    "SEXEST": "Genre",
                    "AGERST": "Âge",
                    "REG13ST": "Région",
                    "AGGLO5ST": "Taille d'agglomération",
                    "EMPST": "Type d'emploi occupé",
                    "PCSIST": "Catégorie professionnelle",
                    "EDUST": "Niveau de scolarité atteint",
                    "REL1ST": "Religion",
                    "ECO2ST2": "Revenu mensuel du foyer",
                    "INTPOLST": "Intérêt pour la politique",
                    "Q7ST": "Positionnement idéologique",
                    "PROXST": "Préférence partisane"
        }
        # définir l'échelle de l'axe des ordonnées en fonction des
        # valeurs prises par la variable socio-démographique choisie
        dico_echelleY = {
                    "SEXEST": [10, 40],
                    "AGERST": [10, 45],
                    "REG13ST": [15, 35],
                    "AGGLO5ST": [15, 35],
                    "EMPST": [15, 40],
                    "PCSIST": [10, 45],
                    "EDUST": [15, 40],
                    "REL1ST": [10, 45],
                    "ECO2ST2": [10, 45],
                    "INTPOLST": [0, 75],
                    "Q7ST": [5, 40],
                    "PROXST": [5, 55],
        }

        # définir une fonction qui affiche les étiquettes
        # des modalités de la variablr SD choisie dans la légende
        # sur plusieurs lignes si leur longueur initiale dépasse la
        # largeur du cadre de la légende
        def wrap_label(label, max_length=20):
            if len(label) <= max_length:
                return label
            words = label.split()
            lines = []
            current_line = []
            current_length = 0
            for word in words:
                if current_length + len(word) > max_length:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = len(word)
                else:
                    current_line.append(word)
                    current_length += len(word) + 1
            if current_line:
                lines.append(' '.join(current_line))
            return '<br>'.join(lines)

        # importer les données
        csvfile = "data/T_certst1_" + "%s" % input.Select_VarSD_Abst().lower() + ".csv"
        data = pd.read_csv(csvfile)

        # supprimer la première colonne (vide) de la base de donnée
        data = data.drop(data.columns[0], axis=1)

        # calculer les intervalles de confiance à 95% de probabilité (ou 5% de risque)
        # d'après la formule pour les proportions contenue dans l'encadré 3 du document :
        # https://www.sciencespo.fr/cevipof/sites/sciencespo.fr.cevipof/files/Note_Inge%cc%81s1_electionspresidentielles2022_mars2022_V8.pdf
        # calculer la borne BASSE
        data["IC95bb"] = data["pct"] - 1.96*np.sqrt((data["pct"]*(100-data["pct"]))/data["TAILLEECH"])
        # calculer la borne HAUTE
        data["IC95bh"] = data["pct"] + 1.96*np.sqrt((data["pct"]*(100-data["pct"]))/data["TAILLEECH"])

        # créer la figure en mémoire
        fig = go.Figure()

        # créer et sélectionner les couleurs des courbes pour les modalités de la variable SD
        couleurs = ['blue', 'red', 'green', 'purple', 'orange', 'magenta']
        nb_mod = len(data["%s" % input.Select_VarSD_Abst()].unique())
        # array : l'indice de position commence à 0, et se termine une valeur
        # avant le nombre indiqué comme limite à droite dans la sélection
        couleurs_mod = couleurs[:nb_mod]

        # ajouter une courbe pour chaque modalité de la variable SD
        # pour chacune des modalités de la variable SD :
        for i, varSD_modal in enumerate(data["%s" % input.Select_VarSD_Abst()].unique()):
            # trier les valeurs de la table selon la vague de l'enquête
            df_varSD = data[data["%s" % input.Select_VarSD_Abst()] == varSD_modal].sort_values('VAGUE')
            # ajouter la courbe principale (pourcentage selon la vague)
            fig.add_trace(go.Scatter( # ajouter un objet de type Scatter à la zone de graphique
                x=df_varSD['VAGUE'],
                y=df_varSD['pct'],
                # afficher les courbes avec des marqueurs (ronds)
                mode='lines+markers',
                # afficher les étiquettes des modalités sur plusieurs lignes dans le cadre
                # de la légende
                name=wrap_label(varSD_modal),
                # afficher les courbes selon le dictionnaire de couleurs
                line=dict(color=couleurs_mod[i]),
                # afficher les valeurs sous le format 'xx.x%' dans la bulle qui s'affiche
                # au survol de la courbe par la souris, et supprimer toutes les autres
                # informations qui pourraient s'afficher en plus (nom de la modalité)
                hovertemplate='%{y:.1f}%<extra></extra>'
            ))
            # ajouter l'intervalle de confiance autour de la courbe principale des données
            fig.add_trace(go.Scatter(
                # définir une zone fermée, en ajoutant la liste des dates inversées
                # à la liste des dates chronologiques des vagues de l'enquête
                x=df_varSD['VAGUE'].tolist() + df_varSD['VAGUE'].tolist()[::-1],
                # créer le contour de l'intervalle de confiance, en ajoutant la
                # liste inversée des bornes inférieures à la liste des bornes supérieures
                y=df_varSD['IC95bh'].tolist() + df_varSD['IC95bb'].tolist()[::-1],
                # remplir l'espace entre les lignes ainsi définies
                fill='toself',
                # définir la couleur de remplissage des zones de confiance
                # identique à la couleur des courbes principales auxquelles
                # elles correspondent
                fillcolor=couleurs_mod[i],
                # rendre la ligne de contour de la zone de confiance invisible
                # (opacité = 0, soit transparence totale)
                line=dict(color='rgba(255, 255, 255, 0)'),
                # empêcher l'affichage d'informations quand la souris survole
                # la zone de confiance
                hoverinfo="skip",
                # empêcher l'affichage des zones de confiance dans la légende
                showlegend=False,
                # définir l'opacité de la zone de confiance
                # (20% d'opacité correspond à une transparence de 80%)
                opacity=0.2,
            ))

        # ajouter des lignes verticales pour chaque vague de l'enquête
        for date in data['VAGUE'].unique():
            fig.add_vline(x=date, line_width=2, line_color="grey")

        # mise en forme détaillée et personnalisée du graphique
        fig.update_layout(
            title={'text': "Certitude d'aller voter en fonction %s" % dico_titre.get("%s" % input.Select_VarSD_Abst()),
                    'y':1,
                    'x':0,
                    'xanchor': 'left',
                    'yanchor': 'top'
            },
            # définir le titre de la légende
            legend_title="%s" % dico_legende.get("%s" % input.Select_VarSD_Abst()),
            # définir l'affichage séparé des valeurs de % affichées sur les
            # courbes quand la souris survole chaque vague (barre verticale)
            hovermode="x",
            # définir le thème général de l'apparence du graphique
            template="plotly_white",
             # définir l'apparence de l'axe des abscisses
            xaxis=dict(
                tickformat='%Y-%m-%d',
                hoverformat='%Y-%m-%d',
                # ajouter un 'rangeslider' sous le graphique
                rangeslider=dict(visible=False), # désactivé actuellement
                # ajouter des boutons au-dessus du graphique pour sélectionner
                # la plage temporelle à observer
                rangeselector=dict(
                    buttons=list([
                        dict(step="all", label="Depuis la 1ère vague de l'enquête"),
                        dict(count=9, label="Depuis 9 mois", step="month", stepmode="backward"),
                        dict(count=6, label="Depuis 6 mois", step="month", stepmode="backward"),
                        dict(count=3, label="Depuis 3 mois", step="month", stepmode="backward")
                    ])
                )
            ),
            # définir le titre de l'axe des ordonnées et son apparence
            yaxis_title=dict(
                text='Pourcentage de répondants (%)',
                font_size=12
            ),
            # définir les sources des données
            annotations=[
                dict(
                    xref='paper',
                    yref='paper',
                    x=0,
                    y=-0.1,
                    xanchor='left',
                    yanchor='top',
                    text=   'Enquête électorale française pour les ' +
                            'élections européennes de juin 2024, ' +
                            'par Ipsos Sopra Steria, Cevipof, ' +
                            'Le Monde, Fondation Jean Jaurès et ' +
                            'Institut Montaigne (2024)',
                    font=dict(size=10, color='grey'),
                    showarrow=False,
                )
            ],
            # définir les marges de la zone graphique
            # (augmentées à droite pour le cadre fixe de la légende)
            margin=dict(b=50, # b = bottom
                        t=50,  # t = top
                        l=50, # l = left
                        r=200 # r = right
                        ),
            # fixer la position de la légende
            legend=dict(
                orientation="v",
                valign='top',  # aligner le texte en haut de chaque marqueur de la légende
                x=1.02, # position horizontale de la légende (1 = à droite du graphique)
                y=1, # position verticale de la légende (1 = en haut)
                xanchor='left', # ancrer la légende à gauche de sa position x
                yanchor='top', # ancrer la légende en haut de sa position y
                bgcolor='rgba(255,255,255,0.8)' # fond légèrement transparent
            )
        )

        # ajuster l'axe des ordonnées en fonction des valeurs observées
        fig.update_yaxes(range=dico_echelleY.get("%s" % input.Select_VarSD_Abst()))

        # modifier l'apparence des courbes (affinées et "arrondies")
        fig.update_traces(line_shape="spline")

        # retourner le graphique
        return fig


    #############
    # onglet 05 #
    #############

    # bouton 01 : décrire la question posée dans l'enquête
    @reactive.effect
    @reactive.event(input.Show_PART_Question)
    def _():
        m = ui.modal("La question posée aux répondants est la suivante : 'QUESTION PARTICIPATION'",
                    title="Informations complémentaires sur la question contenue dans l'enquête :",
                    easy_close=False
            )
        ui.modal_show(m)

    # bouton 02 : décrire la variable de l'intention d'aller voter choisie
    @reactive.effect
    @reactive.event(input.Show_PARTST_Info)
    def _():
        m = ui.modal("La variable sur la participation présentée ici sur les graphiques est une modalité synthétique \
                    de la question posée aux répondants de l'enquête. \
                    Ainsi, parmi les quatre modalités de réponse à la question de l'enquête [...]",
                    title="Informations complémentaires sur la variable choisie pour les graphiques :",
                    easy_close=False
            )
        ui.modal_show(m)

    # bouton 03 : afficher la description de la variable socio-démographique choisie
    # avec plusieurs parties de texte qui dépendent de ce choix (via des dictionnaires)
    @reactive.effect
    @reactive.event(input.Show_VarSD_Part_Info)
    def _():
        # définir le nom de la variable socio-démographique choisie
        dico_nom_var = {
                    "Y6SEXEST": "Genre",
                    "Y6AGERST": "Âge",
                    "Y6REG13ST": "Région",
                    "Y6AGGLO5ST": "Taille d'agglomération",
                    "Y6EMPST": "Type d'emploi occupé",
                    "Y6PCSIST": "Catégorie professionnelle",
                    "Y6EDUST": "Niveau de scolarité atteint",
                    "Y6REL1ST": "Religion",
                    "Y6ECO2ST2": "Revenu mensuel du foyer",
                    "Y6INTPOLST": "Intérêt pour la politique",
                    "Y6Q7ST": "Positionnement idéologique",
                    "Y6PROXST": "Préférence partisane"
        }
        # définir la question de l'enquête associée à la variable socio-démographique choisie
        dico_question_var = {
                    "Y6SEXEST": "Êtes-vous ?",
                    "Y6AGERST": "Quelle est votre date de naissance ?",
                    "Y6REG13ST": "Veuillez indiquer le département et la commune où vous résidez.",
                    "Y6AGGLO5ST": "Veuillez indiquer le département et la commune où vous résidez.",
                    "Y6EMPST": "Quelle est votre situation professionnelle actuelle ?",
                    "Y6PCSIST": "Quelle est votre situation professionnelle actuelle ?",
                    "Y6EDUST": "Choisissez votre niveau de scolarité le plus élevé.",
                    "Y6REL1ST": "Quelle est votre religion, si vous en avez une ?",
                    "Y6ECO2ST2": " Pour finir, nous avons besoin de connaître, à des fins statistiques uniquement, la tranche dans laquelle se situe le revenu MENSUEL NET de votre FOYER après déduction des impôts sur le revenu (veuillez considérer toutes vos sources de revenus: salaires, bourses, prestations retraite et sécurité sociale, dividendes, revenus immobiliers, pensions alimentaires etc.).",
                    "Y6INTPOLST": "De manière générale, diriez-vous que vous vous intéressez à la politique ?",
                    "Y6Q7ST": "Sur une échelle de 0 à 10, où 0 correspond à la gauche et 10 correspond à la droite, où diriez-vous que vous vous situez ?",
                    "Y6PROXST": "De quel parti vous sentez-vous proche ou moins éloigné que les autres ?"
        }
        # définir les modalités de réponse à la question de l'enquête associée à la variable socio-démographique choisie
        dico_modalite_var = {
                    "Y6SEXEST": "1 = 'Homme' ; 2 = 'Femme'",
                    "Y6AGERST": "1 = '18 à 24 ans' ; 2 = '25 à 34 ans' ; 3 = '35 à 49 ans' ; 4 = '50 à 59 ans' ; 5 = '60 ans et plus'",
                    "Y6REG13ST": "1 = 'Ile de France' ; 2 = 'Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)' ; 3 = 'Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)' ; 4 = 'Sud ouest (Nouvelle Aquitaine et Occitanie)' ; 5 = 'Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)'",
                    "Y6AGGLO5ST": "1 = 'Zone rurale (moins de 2 000 habitants)' ; 2 = 'Zone urbaine de 2 000 à 9 999 habitants' ; 3 = 'Zone urbaine de 10 000 à 49 999 habitants' ; 4 = 'Zone urbaine de 50 000 à 199 999 habitants' ; 5 = 'Zone urbaine de 200 000 habitants et plus'",
                    "Y6EMPST": "1 = 'Salarié (salarié à plein temps ou à temps partiel)' ; 2 = 'Indépendant (travaille à mon compte)' ; 3 = 'Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)'",
                    "Y6PCSIST": "1 = 'Agriculteur exploitant, artisan, commerçant, chef d'entreprise' ; 2 = 'Cadre supérieur' ; 3 = 'Profession intermédiaire' ; 4 = 'Employé' ; 5 = 'Ouvrier' ; 6 = 'Retraité, inactif'",
                    "Y6EDUST": "1 = 'Aucun diplôme' ; 2 = 'CAP, BEP' ; 3 = 'Baccalauréat' ; 4 = 'Bac +2' ; 5 = 'Bac +3 et plus'",
                    "Y6REL1ST": "1 = 'Catholique' ; 2 = 'Juive' ; 3 = 'Musulmane' ; 4 = 'Autre religion (protestante, boudhiste ou autre)' ; 5 = 'Sans religion'",
                    "Y6ECO2ST2": "1 = 'Moins de 1 250 euros' ; 2 = 'De 1 250 euros à 1 999 euros' ; 3 = 'De 2 000 à 3 499 euros' ; 4 = 'De 3 500 à 4 999 euros' ; 5 = 'De 3 500 à 4 999 euros'",
                    "Y6INTPOLST": "1 = 'Beaucoup' ; 2 = 'Un peu' ; 3 = 'Pas vraiment' ; 4 = 'Pas du tout'",
                    "Y6Q7ST": "1 = 'Très à gauche' ; 2 = 'Plutôt à gauche' ; 3 = 'Au centre' ; 4 = 'Plutôt à droite' ; 5 = 'Très à droite'",
                    "Y6PROXST": "1 = 'Extême gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)' ; 2 = 'Gauche (Parti Socialiste, Europe Ecologie - Les Verts)' ; 3 = 'Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, L’UDI (Union des Démocrates et Indépendants))' ; 4 = 'Droite (Les Républicains)' ; 5 = 'Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)' ; 6 = 'Autre parti ou aucun parti'"
        }
        # définir le texte complet à afficher (avec parties fixes et variables en fonction du choix effectué)
        m = ui.modal("La variable '%s' correspond à ou est calculée à partir de la question suivante posée aux répondants : \
                     '%s', \
                     et ses modalités de réponse (inchangées par rapport au questionnaire ou regroupées pour les présents graphiques) sont : \
                     %s." % (dico_nom_var.get("%s" % input.Select_VarSD_Part()),
                             dico_question_var.get("%s" % input.Select_VarSD_Part()),
                             dico_modalite_var.get("%s" % input.Select_VarSD_Part())
                     ),
                     title="Informations complémentaires sur la variable socio-démographique choisie :",
                     easy_close=False
            )
        ui.modal_show(m)

    # graphique
    @output
    @render_plotly
    def Graph_Croise_Part():
        # définir la partie variable du titre
        dico_titre = {
                    "Y6SEXEST": "du genre",
                    "Y6AGERST": "de l'âge",
                    "Y6REG13ST": "de la région de résidence",
                    "Y6AGGLO5ST": "de la taille de l'agglomération de résidence",
                    "Y6EMPST": "du type d'emploi occupé",
                    "Y6PCSIST": "de la catégorie socio-professionnelle",
                    "Y6EDUST": "du niveau de scolarité atteint",
                    "Y6REL1ST": "de la religion",
                    "Y6ECO2ST2": "du revenu mensuel du foyer",
                    "Y6INTPOLST": "de l'intérêt pour la politique",
                    "Y6Q7ST": "du positionnement idéologique",
                    "Y6PROXST": "de la préférence partisane"
        }
        # définir la partie variable du titre de la légende
        dico_legende = {
                    "Y6SEXEST": "Genre",
                    "Y6AGERST": "Âge",
                    "Y6REG13ST": "Région",
                    "Y6AGGLO5ST": "Taille d'agglomération",
                    "Y6EMPST": "Type d'emploi occupé",
                    "Y6PCSIST": "Catégorie professionnelle",
                    "Y6EDUST": "Niveau de scolarité atteint",
                    "Y6REL1ST": "Religion",
                    "Y6ECO2ST2": "Revenu mensuel du foyer",
                    "Y6INTPOLST": "Intérêt pour la politique",
                    "Y6Q7ST": "Positionnement idéologique",
                    "Y6PROXST": "Préférence partisane"
        }
        # définir l'échelle de l'axe des ordonnées en fonction des
        # valeurs prises par la variable socio-démographique choisie
        dico_echelleY = {
                    "Y6SEXEST": [10, 40],
                    "Y6AGERST": [10, 45],
                    "Y6REG13ST": [15, 35],
                    "Y6AGGLO5ST": [15, 35],
                    "Y6EMPST": [15, 40],
                    "Y6PCSIST": [10, 45],
                    "Y6EDUST": [15, 40],
                    "Y6REL1ST": [10, 45],
                    "Y6ECO2ST2": [10, 45],
                    "Y6INTPOLST": [0, 75],
                    "Y6Q7ST": [5, 40],
                    "Y6PROXST": [5, 55],
        }

        # définir une fonction qui affiche les étiquettes
        # des modalités de la variable SD choisie dans la légende
        # sur plusieurs lignes si leur longueur initiale dépasse la
        # largeur du cadre de la légende
        def wrap_label(label, max_length=20):
            if len(label) <= max_length:
                return label
            words = label.split()
            lines = []
            current_line = []
            current_length = 0
            for word in words:
                if current_length + len(word) > max_length:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                    current_length = len(word)
                else:
                    current_line.append(word)
                    current_length += len(word) + 1
            if current_line:
                lines.append(' '.join(current_line))
            return '<br>'.join(lines)

        # importer les données
        csvfile = "data/T_w6_parteu24st_" + "%s" % input.Select_VarSD_Part().lower()[2:] + ".csv"
        data = pd.read_csv(csvfile)

        # supprimer la première colonne (vide) de la base de donnée
        data = data.drop(data.columns[0], axis=1)

        # créer la figure en mémoire
        fig = go.Figure()

        for i, varSD_modal in enumerate(data[input.Select_VarSD_Part()].unique()):
            fig.add_trace(go.Bar(
                x=data["Y6PARTEU24ST"],
                y=data[data[input.Select_VarSD_Part()] == varSD_modal]["pct"],
                name=wrap_label(varSD_modal),
                offsetgroup=0
            ))


        # mise en forme détaillée et personnalisée du graphique
        fig.update_layout(
            title={'text': "Participation en fonction %s" % dico_titre.get("%s" % input.Select_VarSD_Part()),
                    'y':1,
                    'x':0,
                    'xanchor': 'left',
                    'yanchor': 'top'
            },
            barmode='stack',
            # définir le titre de la légende
            legend_title="%s" % dico_legende.get("%s" % input.Select_VarSD_Part()),
            # définir l'affichage séparé des valeurs de % affichées sur les
            # courbes quand la souris survole chaque vague (barre verticale)
            hovermode="x",
            # définir le thème général de l'apparence du graphique
            template="plotly_white",
             # définir l'apparence de l'axe des abscisses
            xaxis=dict(
                tickformat='%Y-%m-%d',
                hoverformat='%Y-%m-%d',
                # ajouter un 'rangeslider' sous le graphique
                rangeslider=dict(visible=False), # désactivé actuellement
                # ajouter des boutons au-dessus du graphique pour sélectionner
                # la plage temporelle à observer
                rangeselector=dict(
                    buttons=list([
                        dict(step="all", label="Depuis la 1ère vague de l'enquête"),
                        dict(count=9, label="Depuis 9 mois", step="month", stepmode="backward"),
                        dict(count=6, label="Depuis 6 mois", step="month", stepmode="backward"),
                        dict(count=3, label="Depuis 3 mois", step="month", stepmode="backward")
                    ])
                )
            ),
            # définir le titre de l'axe des ordonnées et son apparence
            yaxis_title=dict(
                text='Pourcentage de répondants (%)',
                font_size=12
            ),
            # définir les sources des données
            annotations=[
                dict(
                    xref='paper',
                    yref='paper',
                    x=0,
                    y=-0.1,
                    xanchor='left',
                    yanchor='top',
                    text=   'Enquête électorale française pour les ' +
                            'élections européennes de juin 2024, ' +
                            'par Ipsos Sopra Steria, Cevipof, ' +
                            'Le Monde, Fondation Jean Jaurès et ' +
                            'Institut Montaigne (2024)',
                    font=dict(size=10, color='grey'),
                    showarrow=False,
                )
            ],
            # définir les marges de la zone graphique
            # (augmentées à droite pour le cadre fixe de la légende)
            margin=dict(b=50, # b = bottom
                        t=50,  # t = top
                        l=50, # l = left
                        r=200 # r = right
                        ),
            # fixer la position de la légende
            legend=dict(
                orientation="v",
                valign='top',  # aligner le texte en haut de chaque marqueur de la légende
                x=1.02, # position horizontale de la légende (1 = à droite du graphique)
                y=1, # position verticale de la légende (1 = en haut)
                xanchor='left', # ancrer la légende à gauche de sa position x
                yanchor='top', # ancrer la légende en haut de sa position y
                bgcolor='rgba(255,255,255,0.8)' # fond légèrement transparent
            )
        )

        # ajuster l'axe des ordonnées en fonction des valeurs observées
        fig.update_yaxes(range=dico_echelleY.get("%s" % input.Select_VarSD_Abst()))

        # retourner le graphique
        return fig

#######
# APP #
#######

# définir une nouvelle instance de l'application
app = App(app_ui, server)
