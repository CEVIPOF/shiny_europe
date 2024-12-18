# -*- coding: utf-8 -*-
"""
Construction d'une application interactive de visualisation de données
pour les enquêtes électorales françaises faites pour les élections européennes
de juin 2024 et les élections législatives de juillet 2024

PAYS : France
VAGUES : 1 à 7

Auteurs :   Diego Antolinos-Basso
            Nicolas Sormani

Centre : Cevipof (SciencesPo - CNRS)
Année : 2024
"""



#####################
## BLOC LIBRAIRIES ##
#####################

from shiny import App, ui, reactive
from shinywidgets import render_widget, render_plotly, output_widget
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import colorlover as cl
import shinyswatch
import datetime
import orjson



#############
## BLOC UI ##
#############

# définir des cadres graphiques personnalisés
def ui_card(title, *args):
    return (
        ui.div(
            {"class": "card mb-4"},
            ui.div(title, class_="card-header"),
            ui.div({"class": "card-body"}, *args),
        ),
    )



# définir le contenu de la page 01
page_presentation = ui.markdown(
    """
    ### L'Enquête Électorale Française

    L'Enquête Électorale Française (ENEF) pour les élections européennes du 9 juin 2024
    et pour les élections législatives anticipées des 30 juin et 7 juillet 2024,
    est un dispositif d'enquêtes par panel réalisées par l'institut _IPSOS_ pour le
    _CEVIPOF_, la _Fondation Jean Jaurès_, _Institut Montaigne_ et _Le Monde_.
    <br>
    <br>
    Composé de plus de 10 000 personnes, le panel d'individus est interrogé
    à 7 reprises de juin 2023 à juillet 2024, afin de mieux comprendre les logiques de
    leurs décisions de vote pour ces élections.
    <br>
    Les résultats détaillés de ce dispositif d'enquêtes, accompagnés de décryptages et
    d'analyses, sont disponibles sur la [page dédiée du Cevipof](https://www.sciencespo.fr/cevipof/fr/etudes-enquetes/enquete-electorale-francaise-2023-elections-europeennes-2024/).
    <br>
    <br>
    L'attention de l'utilisateur est appelée sur le fait que les opinions mesurées en
    pourcentage sont sujettes à un _aléa de mesure statistique_, ou _marge d'erreur_,
    qu'il est important de prendre en compte lors de l'interprétation de ces nombres.
    L'utilisateur pourra consulter la page 3 des [rapports de résultats détaillés](https://www.sciencespo.fr/cevipof/fr/etudes-enquetes/enquete-electorale-francaise-2023-elections-europeennes-2024/#resultats)
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
    Il est par conséquent vivement recommandé à l'utilisateur de [contacter le Cevipof](https://www.sciencespo.fr/cevipof/fr/centre/contact/)
    et les chercheurs membres du laboratoire en cas de doute, ou pour toute question ou besoin
    de clarification, de contextualisation ou d'analyse détaillée et commentée de ces
    principaux résultats graphiques.
    """
)



# définir un message d'indication pour l'utilisateur concernant les graphiques
message_utilisateur_graph = ui.markdown(
    """
    ```
    Pour afficher les valeurs du graphique, amener la souris sur les barres verticales.
    Les marges d'erreur sont données dans les rapports de résultats détaillés de chaque vague.
    ```
    """
)



# définir le contenu de la page 02 : ELECTIONS EUROPEENNES
page_electionsUE = ui.navset_card_underline(
    
    # onglet 01 : PARTICIPATION
    ui.nav_panel(
        "Participation",
        # définir deux colonnes
        ui.layout_columns(
            # colonne 01 : informations et choix de l'utilisateur
            ui.card(
                # cadre 01 : informations sur la variable
                ui_card(
                    # titre du cadre
                    "PARTICIPATION AU VOTE",
                    # bouton 01 : information sur la question posée dans l'enquête
                    ui.input_action_button(
                        "Show_PART_Question", # input ID
                        "Question posée dans l'enquête" # texte affiché dans le bouton
                    ),
                    # bouton 02 : information sur la variable sélectionnée pour les graphiques
                    ui.input_action_button(
                        "Show_PARTST_Info", # input ID
                        "Variable choisie pour les graphiques" # texte affiché dans le bouton
                    ),
                ),
                # cadre 02 : choix de la variable socio-démographique à croiser avec l'intention d'aller voter
                ui_card(
                    # titre du cadre
                    "CHOISIR UNE VARIABLE SOCIO- DEMOGRAPHIQUE",
                    # groupe de boutons de sélection
                    ui.input_radio_buttons(
                        id="Select_VarSD_Part",
                        label="",
                        choices={
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
                    ),
                    # bouton 03 : informations détaillées sur la variable socio-démographique choisie
                    ui.input_action_button(
                        "Show_VarSD_Part_Info", # input ID
                        "Afficher sa description" # texte affiché dans le bouton
                    )   
                )
            ),
            # colonne 02: graphique
            ui.card(
                # afficher une ligne d'indication pour l'utilisateur
                message_utilisateur_graph,
                # afficher le graphique ad hoc (voir définition dans le bloc 'Server' plus bas)
                output_widget(
                    id="Graph_Croise_Part",
                    width="auto",
                    height="auto"
                )
            ),
            # définir les largeurs des colonnes contenant les cadres graphiques
            col_widths=(3, 9)
        ),
    ),

    # onglet 02 : VOTE EN FAVEUR DES LISTES POLITIQUES
    ui.nav_panel(
        # titre de l'onglet
        "Vote en faveur des listes politiques",
        # définir deux colonnes
        ui.layout_columns(
            # colonne 01 : informations et choix de l'utilisateur
            ui.card(
                # cadre 01 : informations sur la variable
                ui_card(
                    # titre du cadre
                    "VOTE EN FAVEUR DES LISTES",
                    # bouton 01 : information sur la question posée dans l'enquête
                    ui.input_action_button(
                        "Show_LIST_Question", # input ID
                        "Question posée dans l'enquête" # texte affiché dans le bouton
                    ),
                    # bouton 02 : information sur la variable sélectionnée pour les graphiques
                    ui.input_action_button(
                        "Show_LIST_Info", # input ID
                        "Variable choisie pour les graphiques" # texte affiché dans le bouton
                    ),
                )
            ),
            # colonne 02: graphique
            ui.card(
                # afficher une ligne d'indication pour l'utilisateur
                message_utilisateur_graph,
                # afficher le graphique ad hoc (voir définition dans le bloc 'Server' plus bas)
                output_widget(
                    id="Graph_List",
                    width="auto",
                    height="auto"
                )
            ),
            # définir les largeurs des colonnes contenant les cadres graphiques
            col_widths=(3, 9)
        )
    ),

    # onglet 03 : ENJEUX DU VOTE (VUE GLOBALE)
    ui.nav_panel(
        # titre de l'onglet
        "Premier enjeu du vote (vue globale)",
        # définir deux colonnes
        ui.layout_columns(
            # colonne 01 : informations et choix de l'utilisateur
            ui.card(
                # cadre 01 : informations sur la variable
                ui_card(
                    # titre du cadre
                    "PREMIER ENJEU DU VOTE",
                    # bouton 01 : information sur la question posée dans l'enquête
                    ui.input_action_button(
                        "Show_ENJVG_Question", # input ID
                        "Question posée dans l'enquête" # texte affiché dans le bouton
                    ),
                    # bouton 02 : information sur la variable sélectionnée pour les graphiques
                    ui.input_action_button(
                        "Show_ENJVG_Info", # input ID
                        "Variable choisie pour les graphiques" # texte affiché dans le bouton
                    ),
                )
            ),
            # colonne 02: graphique
            ui.card(
                # afficher une ligne d'indication pour l'utilisateur
                message_utilisateur_graph,
                # afficher le graphique ad hoc (voir définition dans le bloc 'Server' plus bas)
                output_widget(
                    id="Graph_EnjVG",
                    width="auto",
                    height="auto"
                )
            ),
            # définir les largeurs des colonnes contenant les cadres graphiques
            col_widths=(3, 9)
        )
    ),

    # onglet 04 : ENJEUX DU VOTE CROISES AVEC DES VARIABLES SOCIO-DEMOGRAPHIQUES
    ui.nav_panel(
        # titre de l'onglet
        "Premier enjeu du vote (vue détaillée)",
        # définir deux colonnes
        ui.layout_columns(
            # colonne 01 : informations et choix de l'utilisateur
            ui.card(
                # cadre 01 : informations sur la variable
                ui_card(
                    # titre du cadre
                    "PREMIER ENJEU DU VOTE",
                    # bouton 01 : information sur la question posée dans l'enquête
                    ui.input_action_button(
                        "Show_ENJ_Question", # input ID
                        "Question posée dans l'enquête" # texte affiché dans le bouton
                    ),
                    # bouton 02 : information sur la variable sélectionnée pour les graphiques
                    ui.input_action_button(
                        "Show_ENJ_Info", # input ID
                        "Variable choisie pour les graphiques" # texte affiché dans le bouton
                    ),
                ),
                # cadre 02 : choix de la variable socio-démographique à croiser avec l'intention d'aller voter
                ui_card(
                    "CHOISIR UNE VARIABLE SOCIO- DEMOGRAPHIQUE",
                    # groupe de boutons de sélection
                    ui.input_radio_buttons(
                        id="Select_VarSD_Enj",
                        label="",
                        choices={
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
                    ),
                    # bouton 03 : informations détaillées sur la variable socio-démographique choisie
                    ui.input_action_button(
                        "Show_VarSD_Enj_Info", # input ID
                        "Afficher sa description" # texte affiché dans le bouton
                    )
                )
            ),
            # colonne 02: graphique
            ui.card(
                # afficher une ligne d'indication pour l'utilisateur
                message_utilisateur_graph,
                # afficher le graphique ad hoc (voir définition dans le bloc 'Server' plus bas)
                output_widget(
                    id="Graph_Croise_Enj",
                    width="auto",
                    height="auto"
                )
            ),
            # définir les largeurs des colonnes contenant les cadres graphiques
            col_widths=(3, 9)
        )
    ),

    # onglet 05 : CONTEXTE DE CHOIX DU VOTE
    ui.nav_panel(
        # titre de l'onglet
        "Contexte de choix du vote",
        # définir deux colonnes
        ui.layout_columns(
            # colonne 01 : informations et choix de l'utilisateur
            ui.card(
                # cadre 01 : informations sur la variable
                ui_card(
                    # titre du cadre
                    "CONTEXTE DE CHOIX DU VOTE",
                    # bouton 01 : choix de la variable
                    # groupe de boutons de sélection
                    ui.input_radio_buttons(
                        id="Select_VarChoixVote",
                        label="",
                        choices={
                            "EUCHOIXST": "Moment du choix du vote",
                            "EUDECST": "Choix fait par adhésion ou par défaut",
                            "EUMOTPRST": "Choix lié au Président ou au Gouvernement en place",
                            "EUELARGST": "Choix lié à l'élargissement de l'UE",
                            "EURNST_0": "Première raison du choix de vote pour la liste du Rassemblement National (RN) conduite par Jordan Bardella"
                        }
                    ),
                    # bouton 02 : information sur la question posée dans l'enquête
                    ui.input_action_button(
                        "Show_ChoixVote_Question", # input ID
                        "Question posée dans l'enquête" # texte affiché dans le bouton
                    )
                )
            ),
            # colonne 02: graphique
            ui.card(
                # afficher une ligne d'indication pour l'utilisateur
                message_utilisateur_graph,
                # afficher le graphique ad hoc (voir définition dans le bloc 'Server' plus bas)
                output_widget(
                    id="Graph_ContextChoixVote",
                    width="auto",
                    height="auto"
                )
            ),
            # définir les largeurs des colonnes contenant les cadres graphiques
            col_widths=(3, 9)
        )
    ),

    # onglet 06 : DECISION D'ORGANISER DES ELECTIONS LEGISLATIVES ANTICIPEES
    ui.nav_panel(
        # titre de l'onglet
        "Dissolution de l'Assemblée nationale",
        # définir deux colonnes
        ui.layout_columns(
            # colonne 01 : informations et choix de l'utilisateur
            ui.card(
                # cadre 01 : informations sur la variable
                ui_card(
                    # titre du cadre
                    "DISSOLUTION DE L'ASSEMBLEE NATIONALE",
                    # bouton 01 : choix de la variable concernant la décision d'organiser des élections législatives
                    # groupe de boutons de sélection
                    ui.input_radio_buttons(
                        id="Select_VarDissolAN",
                        label="",
                        choices={
                            "DISS1ST": "Avis sur la dissolution de l'Assemblée nationale",
                            "DISS2ST": "Impression sur la dissolution de l'Assemblée nationale",
                            "DISS3ST": "Opinion sur la décision du Président de la République"
                        }
                    ),
                    # bouton 02 : information sur la question posée dans l'enquête
                    ui.input_action_button(
                        "Show_DISSOL_Question", # input ID
                        "Question posée dans l'enquête" # texte affiché dans le bouton
                    )
                )
            ),
            # colonne 02: graphique
            ui.card(
                # afficher une ligne d'indication pour l'utilisateur
                message_utilisateur_graph,
                # afficher le graphique ad hoc (voir définition dans le bloc 'Server' plus bas)
                output_widget(
                    id="Graph_DissolAN",
                    width="auto",
                    height="auto"
                )
            ),
            # définir les largeurs des colonnes contenant les cadres graphiques
            col_widths=(3, 9)
        )
    )
)



# définir le contenu de la page 03
page_electionsLEGIS = ui.navset_card_underline(
    
    # onglet 01 : PARTICIPATION (1er tour)
    ui.nav_panel(
        "Participation (1er tour)",
        # définir deux colonnes
        ui.layout_columns(
            # colonne 01 : informations et choix de l'utilisateur
            ui.card(
                # cadre 01 : informations sur la variable
                ui_card(
                    # titre du cadre
                    "PARTICIPATION AU VOTE (1er tour)",
                    # bouton 01 : information sur la question posée dans l'enquête
                    ui.input_action_button(
                        "Show_PART_Question_Legis_T1", # input ID
                        "Question posée dans l'enquête" # texte affiché dans le bouton
                    ),
                    # bouton 02 : information sur la variable sélectionnée pour les graphiques
                    ui.input_action_button(
                        "Show_PARTST_Info_Legis_T1", # input ID
                        "Variable choisie pour les graphiques" # texte affiché dans le bouton
                    ),
                ),
                # cadre 02 : choix de la variable socio-démographique à croiser avec l'intention d'aller voter
                ui_card(
                    # titre du cadre
                    "CHOISIR UNE VARIABLE SOCIO- DEMOGRAPHIQUE",
                    # groupe de boutons de sélection
                    ui.input_radio_buttons(
                        id="Select_VarSD_Part_Legis_T1",
                        label="",
                        choices={
                            "Y7SEXEST": "Genre",
                            "Y7AGERST": "Âge",
                            "Y7REG13ST": "Région",
                            "Y7AGGLO5ST": "Taille d'agglomération",
                            "Y7EMPST": "Type d'emploi occupé",
                            "Y7PCSIST": "Catégorie professionnelle",
                            "Y7EDUST": "Niveau de scolarité atteint",
                            "Y7REL1ST": "Religion",
                            "Y7ECO2ST2": "Revenu mensuel du foyer",
                            "Y7INTPOLST": "Intérêt pour la politique",
                            "Y7Q7ST": "Positionnement idéologique",
                            "Y7PROXST": "Préférence partisane"
                        }
                    ),
                    # bouton 03 : informations détaillées sur la variable socio-démographique choisie
                    ui.input_action_button(
                        "Show_VarSD_Part_Info_Legis_T1", # input ID
                        "Afficher sa description" # texte affiché dans le bouton
                    )   
                )
            ),
            # colonne 02: graphique
            ui.card(
                # afficher une ligne d'indication pour l'utilisateur
                message_utilisateur_graph,
                # afficher le graphique ad hoc (voir définition dans le bloc 'Server' plus bas)
                output_widget(
                    id="Graph_Croise_Part_Legis_T1",
                    width="auto",
                    height="auto"
                )
            ),
            # définir les largeurs des colonnes contenant les cadres graphiques
            col_widths=(3, 9)
        ),
    ),

    # onglet 02 : VOTE EN FAVEUR DES CANDIDATS (couleurs politiques) AU 1er TOUR
    ui.nav_panel(
        # titre de l'onglet
        "Vote en faveur des candidats (1er tour)",
        # définir deux colonnes
        ui.layout_columns(
            # colonne 01 : informations et choix de l'utilisateur
            ui.card(
                # cadre 01 : informations sur la variable
                ui_card(
                    # titre du cadre
                    "VOTE EN FAVEUR DES CANDIDATS",
                    # bouton 01 : information sur la question posée dans l'enquête
                    ui.input_action_button(
                        "Show_CAND_Question_Legis_T1", # input ID
                        "Question posée dans l'enquête" # texte affiché dans le bouton
                    ),
                    # bouton 02 : information sur la variable sélectionnée pour les graphiques
                    ui.input_action_button(
                        "Show_CAND_Info_Legis_T1", # input ID
                        "Variable choisie pour les graphiques" # texte affiché dans le bouton
                    ),
                )
            ),
            # colonne 02: graphique
            ui.card(
                # afficher une ligne d'indication pour l'utilisateur
                message_utilisateur_graph,
                # afficher le graphique ad hoc (voir définition dans le bloc 'Server' plus bas)
                output_widget(
                    id="Graph_Cand_Legis_T1",
                    width="auto",
                    height="auto"
                )
            ),
            # définir les largeurs des colonnes contenant les cadres graphiques
            col_widths=(3, 9)
        )
    ),

    # onglet 03 : PARTICIPATION (2e tour)
    ui.nav_panel(
        "Participation (2e tour)",
        # définir deux colonnes
        ui.layout_columns(
            # colonne 01 : informations et choix de l'utilisateur
            ui.card(
                # cadre 01 : informations sur la variable
                ui_card(
                    # titre du cadre
                    "PARTICIPATION AU VOTE (2e tour)",
                    # bouton 01 : information sur la question posée dans l'enquête
                    ui.input_action_button(
                        "Show_PART_Question_Legis_T2", # input ID
                        "Question posée dans l'enquête" # texte affiché dans le bouton
                    ),
                    # bouton 02 : information sur la variable sélectionnée pour les graphiques
                    ui.input_action_button(
                        "Show_PARTST_Info_Legis_T2", # input ID
                        "Variable choisie pour les graphiques" # texte affiché dans le bouton
                    ),
                ),
                # cadre 02 : choix de la variable socio-démographique à croiser avec l'intention d'aller voter
                ui_card(
                    # titre du cadre
                    "CHOISIR UNE VARIABLE SOCIO- DEMOGRAPHIQUE",
                    # groupe de boutons de sélection
                    ui.input_radio_buttons(
                        id="Select_VarSD_Part_Legis_T2",
                        label="",
                        choices={
                            "Y7SEXEST": "Genre",
                            "Y7AGERST": "Âge",
                            "Y7REG13ST": "Région",
                            "Y7AGGLO5ST": "Taille d'agglomération",
                            "Y7EMPST": "Type d'emploi occupé",
                            "Y7PCSIST": "Catégorie professionnelle",
                            "Y7EDUST": "Niveau de scolarité atteint",
                            "Y7REL1ST": "Religion",
                            "Y7ECO2ST2": "Revenu mensuel du foyer",
                            "Y7INTPOLST": "Intérêt pour la politique",
                            "Y7Q7ST": "Positionnement idéologique",
                            "Y7PROXST": "Préférence partisane"
                        }
                    ),
                    # bouton 03 : informations détaillées sur la variable socio-démographique choisie
                    ui.input_action_button(
                        "Show_VarSD_Part_Info_Legis_T2", # input ID
                        "Afficher sa description" # texte affiché dans le bouton
                    )   
                )
            ),
            # colonne 02: graphique
            ui.card(
                # afficher une ligne d'indication pour l'utilisateur
                message_utilisateur_graph,
                # afficher le graphique ad hoc (voir définition dans le bloc 'Server' plus bas)
                output_widget(
                    id="Graph_Croise_Part_Legis_T2",
                    width="auto",
                    height="auto"
                )
            ),
            # définir les largeurs des colonnes contenant les cadres graphiques
            col_widths=(3, 9)
        ),
    ),

    # onglet 04 : VOTE EN FAVEUR DES CANDIDATS (couleurs politiques) AU 2e TOUR
    ui.nav_panel(
        # titre de l'onglet
        "Vote en faveur des candidats (2e tour)",
        # définir deux colonnes
        ui.layout_columns(
            # colonne 01 : informations et choix de l'utilisateur
            ui.card(
                # cadre 01 : informations sur la variable
                ui_card(
                    # titre du cadre
                    "VOTE EN FAVEUR DES CANDIDATS",
                    # bouton 01 : information sur la question posée dans l'enquête
                    ui.input_action_button(
                        "Show_CAND_Question_Legis_T2", # input ID
                        "Question posée dans l'enquête" # texte affiché dans le bouton
                    ),
                    # bouton 02 : information sur la variable sélectionnée pour les graphiques
                    ui.input_action_button(
                        "Show_CAND_Info_Legis_T2", # input ID
                        "Variable choisie pour les graphiques" # texte affiché dans le bouton
                    ),
                )
            ),
            # colonne 02: graphique
            ui.card(
                # afficher une ligne d'indication pour l'utilisateur
                message_utilisateur_graph,
                # afficher le graphique ad hoc (voir définition dans le bloc 'Server' plus bas)
                output_widget(
                    id="Graph_Cand_Legis_T2",
                    width="auto",
                    height="auto"
                )
            ),
            # définir les largeurs des colonnes contenant les cadres graphiques
            col_widths=(3, 9)
        )
    ),

    # onglet 05 : SENTIMENTS PERSONNELS SUR LES RESULTATS DE L'ELECTION
    ui.nav_panel(
        "Sentiments sur les résultats (2e tour)",
        # définir deux colonnes
        ui.layout_columns(
            # colonne 01 : informations et choix de l'utilisateur
            ui.card(
                # cadre 01 : informations sur la variable
                ui_card(
                    # titre du cadre
                    "SENTIMENTS SUR LES RESULTATS (2e tour)",
                    # bouton 01 : information sur la question posée dans l'enquête
                    ui.input_action_button(
                        "Show_SENTRES_Question_Legis_T2", # input ID
                        "Question posée dans l'enquête" # texte affiché dans le bouton
                    ),
                    # bouton 02 : information sur la variable sélectionnée pour les graphiques
                    ui.input_action_button(
                        "Show_SENTRESST_Info_Legis_T2", # input ID
                        "Variable choisie pour les graphiques" # texte affiché dans le bouton
                    ),
                ),
                # cadre 02 : choix de la variable socio-démographique à croiser avec l'intention d'aller voter
                ui_card(
                    # titre du cadre
                    "CHOISIR UNE VARIABLE SOCIO- DEMOGRAPHIQUE",
                    # groupe de boutons de sélection
                    ui.input_radio_buttons(
                        id="Select_VarSD_SentRes_Legis_T2",
                        label="",
                        choices={
                            "Y7SEXEST": "Genre",
                            "Y7AGERST": "Âge",
                            "Y7REG13ST": "Région",
                            "Y7AGGLO5ST": "Taille d'agglomération",
                            "Y7EMPST": "Type d'emploi occupé",
                            "Y7PCSIST": "Catégorie professionnelle",
                            "Y7EDUST": "Niveau de scolarité atteint",
                            "Y7REL1ST": "Religion",
                            "Y7ECO2ST2": "Revenu mensuel du foyer",
                            "Y7INTPOLST": "Intérêt pour la politique",
                            "Y7Q7ST": "Positionnement idéologique",
                            "Y7PROXST": "Préférence partisane"
                        }
                    ),
                    # bouton 03 : informations détaillées sur la variable socio-démographique choisie
                    ui.input_action_button(
                        "Show_VarSD_SentRes_Info_Legis_T2", # input ID
                        "Afficher sa description" # texte affiché dans le bouton
                    )   
                )
            ),
            # colonne 02: graphique
            ui.card(
                # afficher une ligne d'indication pour l'utilisateur
                message_utilisateur_graph,
                # afficher le graphique ad hoc (voir définition dans le bloc 'Server' plus bas)
                output_widget(
                    id="Graph_Croise_SentRes_Legis_T2",
                    width="auto",
                    height="auto"
                )
            ),
            # définir les largeurs des colonnes contenant les cadres graphiques
            col_widths=(3, 9)
        ),
    ),

    # onglet 06 : AVIS PERSONNEL SUR LE FRONT REPUBLICAIN
    ui.nav_panel(
        "Avis sur le front républicain (2e tour)",
        # définir deux colonnes
        ui.layout_columns(
            # colonne 01 : informations et choix de l'utilisateur
            ui.card(
                # cadre 01 : informations sur la variable
                ui_card(
                    # titre du cadre
                    "AVIS SUR LE FRONT REPUBLICAIN (2e tour)",
                    # bouton 01 : information sur la question posée dans l'enquête
                    ui.input_action_button(
                        "Show_AVFR_Question_Legis_T2", # input ID
                        "Question posée dans l'enquête" # texte affiché dans le bouton
                    ),
                    # bouton 02 : information sur la variable sélectionnée pour les graphiques
                    ui.input_action_button(
                        "Show_AVFRST_Info_Legis_T2", # input ID
                        "Variable choisie pour les graphiques" # texte affiché dans le bouton
                    ),
                ),
                # cadre 02 : choix de la variable socio-démographique à croiser avec l'intention d'aller voter
                ui_card(
                    # titre du cadre
                    "CHOISIR UNE VARIABLE SOCIO- DEMOGRAPHIQUE",
                    # groupe de boutons de sélection
                    ui.input_radio_buttons(
                        id="Select_VarSD_AvFr_Legis_T2",
                        label="",
                        choices={
                            "Y7SEXEST": "Genre",
                            "Y7AGERST": "Âge",
                            "Y7REG13ST": "Région",
                            "Y7AGGLO5ST": "Taille d'agglomération",
                            "Y7EMPST": "Type d'emploi occupé",
                            "Y7PCSIST": "Catégorie professionnelle",
                            "Y7EDUST": "Niveau de scolarité atteint",
                            "Y7REL1ST": "Religion",
                            "Y7ECO2ST2": "Revenu mensuel du foyer",
                            "Y7INTPOLST": "Intérêt pour la politique",
                            "Y7Q7ST": "Positionnement idéologique",
                            "Y7PROXST": "Préférence partisane"
                        }
                    ),
                    # bouton 03 : informations détaillées sur la variable socio-démographique choisie
                    ui.input_action_button(
                        "Show_VarSD_AvFr_Info_Legis_T2", # input ID
                        "Afficher sa description" # texte affiché dans le bouton
                    )   
                )
            ),
            # colonne 02: graphique
            ui.card(
                # afficher une ligne d'indication pour l'utilisateur
                message_utilisateur_graph,
                # afficher le graphique ad hoc (voir définition dans le bloc 'Server' plus bas)
                output_widget(
                    id="Graph_Croise_AvFr_Legis_T2",
                    width="auto",
                    height="auto"
                )
            ),
            # définir les largeurs des colonnes contenant les cadres graphiques
            col_widths=(3, 9)
        ),
    ),

    # onglet 07 : ACCORD DE VUES AVEC L'ENTOURAGE
    ui.nav_panel(
        "Accord de vues avec l'entourage",
        # définir deux colonnes
        ui.layout_columns(
            # colonne 01 : informations et choix de l'utilisateur
            ui.card(
                # cadre 01 : informations sur la variable
                ui_card(
                    # titre du cadre
                    "ACCORD DE VUES AVEC L'ENTOURAGE",
                    # bouton 01 : information sur la question posée dans l'enquête
                    ui.input_action_button(
                        "Show_ACCVUES_Question_Legis_T2", # input ID
                        "Question posée dans l'enquête" # texte affiché dans le bouton
                    ),
                    # bouton 02 : information sur la variable sélectionnée pour les graphiques
                    ui.input_action_button(
                        "Show_ACCVUESST_Info_Legis_T2", # input ID
                        "Variable choisie pour les graphiques" # texte affiché dans le bouton
                    ),
                ),
                # cadre 02 : choix de la variable socio-démographique à croiser avec l'intention d'aller voter
                ui_card(
                    # titre du cadre
                    "CHOISIR UNE VARIABLE SOCIO- DEMOGRAPHIQUE",
                    # groupe de boutons de sélection
                    ui.input_radio_buttons(
                        id="Select_VarSD_AccVues_Legis_T2",
                        label="",
                        choices={
                            "Y7SEXEST": "Genre",
                            "Y7AGERST": "Âge",
                            "Y7REG13ST": "Région",
                            "Y7AGGLO5ST": "Taille d'agglomération",
                            "Y7EMPST": "Type d'emploi occupé",
                            "Y7PCSIST": "Catégorie professionnelle",
                            "Y7EDUST": "Niveau de scolarité atteint",
                            "Y7REL1ST": "Religion",
                            "Y7ECO2ST2": "Revenu mensuel du foyer",
                            "Y7INTPOLST": "Intérêt pour la politique",
                            "Y7Q7ST": "Positionnement idéologique",
                            "Y7PROXST": "Préférence partisane"
                        }
                    ),
                    # bouton 03 : informations détaillées sur la variable socio-démographique choisie
                    ui.input_action_button(
                        "Show_VarSD_AccVues_Info_Legis_T2", # input ID
                        "Afficher sa description" # texte affiché dans le bouton
                    )   
                )
            ),
            # colonne 02: graphique
            ui.card(
                # afficher une ligne d'indication pour l'utilisateur
                message_utilisateur_graph,
                # afficher le graphique ad hoc (voir définition dans le bloc 'Server' plus bas)
                output_widget(
                    id="Graph_Croise_AccVues_Legis_T2",
                    width="auto",
                    height="auto"
                )
            ),
            # définir les largeurs des colonnes contenant les cadres graphiques
            col_widths=(3, 9)
        ),
    ),

    # onglet 08 : AVIS SUR LES CONSEQUENCES DE LA DISSOLUTION
    ui.nav_panel(
        "Avis sur les conséquences de la dissolution de l'Assemblée nationale",
        # définir deux colonnes
        ui.layout_columns(
            # colonne 01 : informations et choix de l'utilisateur
            ui.card(
                # cadre 01 : informations sur la variable
                ui_card(
                    # titre du cadre
                    "AVIS SUR LES CONSEQUENCES DE LA DISSOLUTION",
                    # bouton 01 : information sur la question posée dans l'enquête
                    ui.input_action_button(
                        "Show_AVCONSDISS_Question_Legis_T2", # input ID
                        "Question posée dans l'enquête" # texte affiché dans le bouton
                    ),
                    # bouton 02 : information sur la variable sélectionnée pour les graphiques
                    ui.input_action_button(
                        "Show_AVCONSDISSST_Info_Legis_T2", # input ID
                        "Variable choisie pour les graphiques" # texte affiché dans le bouton
                    ),
                ),
                # cadre 02 : choix de la variable socio-démographique à croiser avec l'intention d'aller voter
                ui_card(
                    # titre du cadre
                    "CHOISIR UNE VARIABLE SOCIO- DEMOGRAPHIQUE",
                    # groupe de boutons de sélection
                    ui.input_radio_buttons(
                        id="Select_VarSD_AvConsDiss_Legis_T2",
                        label="",
                        choices={
                            "Y7SEXEST": "Genre",
                            "Y7AGERST": "Âge",
                            "Y7REG13ST": "Région",
                            "Y7AGGLO5ST": "Taille d'agglomération",
                            "Y7EMPST": "Type d'emploi occupé",
                            "Y7PCSIST": "Catégorie professionnelle",
                            "Y7EDUST": "Niveau de scolarité atteint",
                            "Y7REL1ST": "Religion",
                            "Y7ECO2ST2": "Revenu mensuel du foyer",
                            "Y7INTPOLST": "Intérêt pour la politique",
                            "Y7Q7ST": "Positionnement idéologique",
                            "Y7PROXST": "Préférence partisane"
                        }
                    ),
                    # bouton 03 : informations détaillées sur la variable socio-démographique choisie
                    ui.input_action_button(
                        "Show_VarSD_AvConsDiss_Info_Legis_T2", # input ID
                        "Afficher sa description" # texte affiché dans le bouton
                    )   
                )
            ),
            # colonne 02: graphique
            ui.card(
                # afficher une ligne d'indication pour l'utilisateur
                message_utilisateur_graph,
                # afficher le graphique ad hoc (voir définition dans le bloc 'Server' plus bas)
                output_widget(
                    id="Graph_Croise_AvConsDiss_Legis_T2",
                    width="auto",
                    height="auto"
                )
            ),
            # définir les largeurs des colonnes contenant les cadres graphiques
            col_widths=(3, 9)
        ),
    ),

    # onglet 09 : DEGRE DE CONFIANCE EN LA NOUVELLE ASSEMBLEE NATIONALE
    ui.nav_panel(
        "Degré de confiance en la nouvelle Assemblée nationale",
        # définir deux colonnes
        ui.layout_columns(
            # colonne 01 : informations et choix de l'utilisateur
            ui.card(
                # cadre 01 : informations sur la variable
                ui_card(
                    # titre du cadre
                    "DEGRE DE CONFIANCE EN LA NOUVELLE ASSEMBLEE NATIONALE",
                    # bouton 01 : information sur la question posée dans l'enquête
                    ui.input_action_button(
                        "Show_DEGCONFAN_Question_Legis_T2", # input ID
                        "Question posée dans l'enquête" # texte affiché dans le bouton
                    ),
                    # bouton 02 : information sur la variable sélectionnée pour les graphiques
                    ui.input_action_button(
                        "Show_DEGCONFANST_Info_Legis_T2", # input ID
                        "Variable choisie pour les graphiques" # texte affiché dans le bouton
                    ),
                ),
                # cadre 02 : choix de la variable socio-démographique à croiser avec l'intention d'aller voter
                ui_card(
                    # titre du cadre
                    "CHOISIR UNE VARIABLE SOCIO- DEMOGRAPHIQUE",
                    # groupe de boutons de sélection
                    ui.input_radio_buttons(
                        id="Select_VarSD_DegConfAN_Legis_T2",
                        label="",
                        choices={
                            "Y7SEXEST": "Genre",
                            "Y7AGERST": "Âge",
                            "Y7REG13ST": "Région",
                            "Y7AGGLO5ST": "Taille d'agglomération",
                            "Y7EMPST": "Type d'emploi occupé",
                            "Y7PCSIST": "Catégorie professionnelle",
                            "Y7EDUST": "Niveau de scolarité atteint",
                            "Y7REL1ST": "Religion",
                            "Y7ECO2ST2": "Revenu mensuel du foyer",
                            "Y7INTPOLST": "Intérêt pour la politique",
                            "Y7Q7ST": "Positionnement idéologique",
                            "Y7PROXST": "Préférence partisane"
                        }
                    ),
                    # bouton 03 : informations détaillées sur la variable socio-démographique choisie
                    ui.input_action_button(
                        "Show_VarSD_DegConfAN_Info_Legis_T2", # input ID
                        "Afficher sa description" # texte affiché dans le bouton
                    )   
                )
            ),
            # colonne 02: graphique
            ui.card(
                # afficher une ligne d'indication pour l'utilisateur
                message_utilisateur_graph,
                # afficher le graphique ad hoc (voir définition dans le bloc 'Server' plus bas)
                output_widget(
                    id="Graph_Croise_DegConfAN_Legis_T2",
                    width="auto",
                    height="auto"
                )
            ),
            # définir les largeurs des colonnes contenant les cadres graphiques
            col_widths=(3, 9)
        ),
    ),

    # onglet 10 : SOUHAIT DE DEMISSION DU PRESIDENT DE LA REPUBLIQUE
    ui.nav_panel(
        "Souhait de démission du Président de la République",
        # définir deux colonnes
        ui.layout_columns(
            # colonne 01 : informations et choix de l'utilisateur
            ui.card(
                # cadre 01 : informations sur la variable
                ui_card(
                    # titre du cadre
                    "SOUHAIT DE DEMISSION DU PRESIDENT DE LA REPUBLIQUE",
                    # bouton 01 : information sur la question posée dans l'enquête
                    ui.input_action_button(
                        "Show_SOUHDEMPR_Question_Legis_T2", # input ID
                        "Question posée dans l'enquête" # texte affiché dans le bouton
                    ),
                    # bouton 02 : information sur la variable sélectionnée pour les graphiques
                    ui.input_action_button(
                        "Show_SOUHDEMPRST_Info_Legis_T2", # input ID
                        "Variable choisie pour les graphiques" # texte affiché dans le bouton
                    ),
                ),
                # cadre 02 : choix de la variable socio-démographique à croiser avec l'intention d'aller voter
                ui_card(
                    # titre du cadre
                    "CHOISIR UNE VARIABLE SOCIO- DEMOGRAPHIQUE",
                    # groupe de boutons de sélection
                    ui.input_radio_buttons(
                        id="Select_VarSD_SouhDemPR_Legis_T2",
                        label="",
                        choices={
                            "Y7SEXEST": "Genre",
                            "Y7AGERST": "Âge",
                            "Y7REG13ST": "Région",
                            "Y7AGGLO5ST": "Taille d'agglomération",
                            "Y7EMPST": "Type d'emploi occupé",
                            "Y7PCSIST": "Catégorie professionnelle",
                            "Y7EDUST": "Niveau de scolarité atteint",
                            "Y7REL1ST": "Religion",
                            "Y7ECO2ST2": "Revenu mensuel du foyer",
                            "Y7INTPOLST": "Intérêt pour la politique",
                            "Y7Q7ST": "Positionnement idéologique",
                            "Y7PROXST": "Préférence partisane"
                        }
                    ),
                    # bouton 03 : informations détaillées sur la variable socio-démographique choisie
                    ui.input_action_button(
                        "Show_VarSD_SouhDemPR_Info_Legis_T2", # input ID
                        "Afficher sa description" # texte affiché dans le bouton
                    )   
                )
            ),
            # colonne 02: graphique
            ui.card(
                # afficher une ligne d'indication pour l'utilisateur
                message_utilisateur_graph,
                # afficher le graphique ad hoc (voir définition dans le bloc 'Server' plus bas)
                output_widget(
                    id="Graph_Croise_SouhDemPR_Legis_T2",
                    width="auto",
                    height="auto"
                )
            ),
            # définir les largeurs des colonnes contenant les cadres graphiques
            col_widths=(3, 9)
        ),
    )
)



# définir les pages imbriquées de l'application
app_ui = ui.page_navbar(
    
    # PARTIE 01 : PRESENTATION
    ui.nav_panel(
        "Présentation du projet",
        page_presentation
    ),

    # PARTIE 02 : ELECTIONS EUROPEENNES
    ui.nav_panel(
        "Elections européennes (9 juin 2024)",
        page_electionsUE
    ),

    # PARTIE 03 : ELECTIONS LEGISLATIVES ANTICIPEES
    ui.nav_panel(
        "Elections législatives anticipées (30 juin et 7 juillet 2024)",
        page_electionsLEGIS
    ),

     # choisir l'apparence de l'application
    theme = shinyswatch.theme.simplex
)



#################
## BLOC SERVER ##
#################

def server(input, output, session):

    # REMARQUE :
    # le code pour les onglets 02 à 04 a été retiré de cette version du programme.
    # En effet, ces onglets contiennent les INTENTIONS d'aller voter des répondants
    # que l'on représente uniquement AVANT le scrutin.
    # Cette partie de code est disponible dans le bloc séparé sur la représentation
    # des intentions d'aller voter, utilisable à nouveau pour des élections futures.

    ################################################################################
    ##                          ELECTIONS EUROPEENNES                             ##
    ################################################################################

    #############################
    # onglet 01 : PARTICIPATION #
    #############################

    # bouton 01 : décrire la question posée dans l'enquête
    @reactive.effect
    @reactive.event(input.Show_PART_Question)
    def _():
        m = ui.modal(
            "La question posée aux répondants est la suivante : 'Un électeur sur deux n’a pas voté lors des élections européennes du 9 juin 2024. Dans votre cas personnel, qu’est ce qui correspond le mieux à votre attitude à cette occasion ?'",
            title="Informations complémentaires sur la question contenue dans l'enquête :",
            easy_close=False
        )
        ui.modal_show(m)

    # bouton 02 : décrire la variable de l'intention d'aller voter choisie
    @reactive.effect
    @reactive.event(input.Show_PARTST_Info)
    def _():
        m = ui.modal(
            "La variable sur la participation aux élections européennes présentée ici sur les graphiques est une modalité synthétique de la question posée aux répondants de l'enquête. \
            Ainsi, à partir des quatre modalités de réponse à la question de l'enquête, on en construit 2 : a voté ou n'a pas voté.",
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
            "Y6PCSIST": "1 = 'Agriculteur exploitant, artisan, commerçant, chef d entreprise' ; 2 = 'Cadre supérieur' ; 3 = 'Profession intermédiaire' ; 4 = 'Employé' ; 5 = 'Ouvrier' ; 6 = 'Retraité, inactif'",
            "Y6EDUST": "1 = 'Aucun diplôme' ; 2 = 'CAP, BEP' ; 3 = 'Baccalauréat' ; 4 = 'Bac +2' ; 5 = 'Bac +3 et plus'",
            "Y6REL1ST": "1 = 'Catholique' ; 2 = 'Juive' ; 3 = 'Musulmane' ; 4 = 'Autre religion (protestante, boudhiste ou autre)' ; 5 = 'Sans religion'",
            "Y6ECO2ST2": "1 = 'Moins de 1 250 euros' ; 2 = 'De 1 250 euros à 1 999 euros' ; 3 = 'De 2 000 à 3 499 euros' ; 4 = 'De 3 500 à 4 999 euros' ; 5 = '5 000 euros et plus'",
            "Y6INTPOLST": "1 = 'Beaucoup' ; 2 = 'Un peu' ; 3 = 'Pas vraiment' ; 4 = 'Pas du tout'",
            "Y6Q7ST": "1 = 'Très à gauche' ; 2 = 'Plutôt à gauche' ; 3 = 'Au centre' ; 4 = 'Plutôt à droite' ; 5 = 'Très à droite'",
            "Y6PROXST": "1 = 'Extême gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)' ; 2 = 'Gauche (Parti Socialiste, Europe Ecologie - Les Verts)' ; 3 = 'Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))' ; 4 = 'Droite (Les Républicains)' ; 5 = 'Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)' ; 6 = 'Autre parti ou aucun parti'"
        }
        # définir le texte complet à afficher (avec parties fixes et variables en fonction du choix effectué)
        m = ui.modal(
            "La variable '%s' correspond à ou est calculée à partir de la question suivante posée aux répondants : \
            '%s', \
            et ses modalités de réponse (inchangées par rapport au questionnaire ou regroupées pour les présents graphiques) sont : \
            %s." % (
                dico_nom_var.get(
                    "%s" % input.Select_VarSD_Part()
                ),
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
        # définir les modalités des variables socio-démo et leur ordre
        dico_modalite_var = {
            "Y6SEXEST": "1 = 'Homme' ; 2 = 'Femme'",
            "Y6AGERST": "1 = '18 à 24 ans' ; 2 = '25 à 34 ans' ; 3 = '35 à 49 ans' ; 4 = '50 à 59 ans' ; 5 = '60 ans et plus'",
            "Y6REG13ST": "1 = 'Ile de France' ; 2 = 'Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)' ; 3 = 'Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)' ; 4 = 'Sud ouest (Nouvelle Aquitaine et Occitanie)' ; 5 = 'Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)'",
            "Y6AGGLO5ST": "1 = 'Zone rurale (moins de 2 000 habitants)' ; 2 = 'Zone urbaine de 2 000 à 9 999 habitants' ; 3 = 'Zone urbaine de 10 000 à 49 999 habitants' ; 4 = 'Zone urbaine de 50 000 à 199 999 habitants' ; 5 = 'Zone urbaine de 200 000 habitants et plus'",
            "Y6EMPST": "1 = 'Salarié (salarié à plein temps ou à temps partiel)' ; 2 = 'Indépendant (travaille à mon compte)' ; 3 = 'Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)'",
            "Y6PCSIST": "1 = 'Agriculteur exploitant, artisan, commerçant, chef d entreprise' ; 2 = 'Cadre supérieur' ; 3 = 'Profession intermédiaire' ; 4 = 'Employé' ; 5 = 'Ouvrier' ; 6 = 'Retraité, inactif'",
            "Y6EDUST": "1 = 'Aucun diplôme' ; 2 = 'CAP, BEP' ; 3 = 'Baccalauréat' ; 4 = 'Bac +2' ; 5 = 'Bac +3 et plus'",
            "Y6REL1ST": "1 = 'Catholique' ; 2 = 'Juive' ; 3 = 'Musulmane' ; 4 = 'Autre religion (protestante, boudhiste ou autre)' ; 5 = 'Sans religion'",
            "Y6ECO2ST2": "1 = 'Moins de 1 250 euros' ; 2 = 'De 1 250 euros à 1 999 euros' ; 3 = 'De 2 000 à 3 499 euros' ; 4 = 'De 3 500 à 4 999 euros' ; 5 = '5 000 euros et plus'",
            "Y6INTPOLST": "1 = 'Beaucoup' ; 2 = 'Un peu' ; 3 = 'Pas vraiment' ; 4 = 'Pas du tout'",
            "Y6Q7ST": "1 = 'Très à gauche' ; 2 = 'Plutôt à gauche' ; 3 = 'Au centre' ; 4 = 'Plutôt à droite' ; 5 = 'Très à droite'",
            "Y6PROXST": "1 = 'Très à gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)' ; 2 = 'Gauche (Parti Socialiste, Europe Ecologie - Les Verts)' ; 3 = 'Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))' ; 4 = 'Droite (Les Républicains)' ; 5 = 'Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)' ; 6 = 'Autre parti ou aucun parti'"
        }
        # définir un dictionnaire qui contient l'ordre figé des modalités pour chaque variable socio-démographique
        dico_ordre_modalites = {
            "Y6SEXEST": [
                "Homme",
                "Femme"
            ],
            "Y6AGERST": [
                "18 à 24 ans",
                "25 à 34 ans",
                "35 à 49 ans",
                "50 à 59 ans",
                "60 ans et plus"
            ],
            "Y6REG13ST": [
                "Ile de France",
                "Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)",
                "Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)",
                "Sud ouest (Nouvelle Aquitaine et Occitanie)",
                "Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)"
            ],
            "Y6AGGLO5ST": [
                "Zone rurale (moins de 2 000 habitants)",
                "Zone urbaine de 2 000 à 9 999 habitants",
                "Zone urbaine de 10 000 à 49 999 habitants",
                "Zone urbaine de 50 000 à 199 999 habitants",
                "Zone urbaine de 200 000 habitants et plus"
            ],
            "Y6EMPST": [
                "Salarié (salarié à plein temps ou à temps partiel)",
                "Indépendant (travaille à mon compte)",
                "Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)"
            ],
            "Y6PCSIST": [
                "Agriculteur exploitant, artisan, commerçant, chef d entreprise",
                "Cadre supérieur",
                "Profession intermédiaire",
                "Employé",
                "Ouvrier",
                "Retraité, inactif"
            ],
            "Y6EDUST": [
                "Aucun diplôme",
                "CAP, BEP",
                "Baccalauréat",
                "Bac +2",
                "Bac +3 et plus"
            ],
            "Y6REL1ST": [
                "Catholique",
                "Juive",
                "Musulmane",
                "Autre religion (protestante, boudhiste ou autre)",
                "Sans religion"
            ],
            "Y6ECO2ST2": [
                "Moins de 1 250 euros",
                "De 1 250 euros à 1 999 euros",
                "De 2 000 à 3 499 euros",
                "De 3 500 à 4 999 euros",
                "5 000 euros et plus"
            ],
            "Y6INTPOLST": [
                "Beaucoup",
                "Un peu",
                "Pas vraiment",
                "Pas du tout"
            ],
            "Y6Q7ST": [
                "Très à gauche",
                "Plutôt à gauche",
                "Au centre",
                "Plutôt à droite",
                "Très à droite"
            ],
            "Y6PROXST": [
                "Très à gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)",
                "Gauche (Parti Socialiste, Europe Ecologie - Les Verts)",
                "Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))",
                "Droite (Les Républicains)",
                "Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)",
                "Autre parti ou aucun parti"
            ]
        }
        # définir une fonction qui affiche les étiquettes
        # des modalités de la variablr SD choisie dans la légende
        # sur plusieurs lignes si leur longueur initiale dépasse la
        # largeur du cadre de la légende (version robuste avec gestion des erreurs)
        def wrap_label(label, max_length=20):
            try:
                # Si le label est un float ou NaN
                if pd.isna(label) or isinstance(label, float):
                    return "Non renseigné"
                # Convertir en string si ce n'est pas déjà le cas
                label = str(label).strip()
                # Si la chaîne est vide après nettoyage
                if not label:
                    return "Non renseigné"
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
            except Exception as e:
                print(f"Erreur dans wrap_label avec {label}: {str(e)}")
                return str(label) 
                # retourner le label tel quel en cas d'erreur
        # lire le fichier CSV des données
        csvfile = "data/T_w6_parteu24st_" + "%s" % input.Select_VarSD_Part().lower()[2:] + ".csv"
        df = pd.read_csv(csvfile)
        # nettoyer les données lues
        var_sd = input.Select_VarSD_Part()
        df[var_sd] = df[var_sd].fillna("Non renseigné")  # Gérer les NaN
        df[var_sd] = df[var_sd].astype(str)  # Convertir en string
        df['Y6PARTEU24ST'] = df['Y6PARTEU24ST'].fillna("Non renseigné")
        # s'assurer que toutes les modalités sont des chaînes de caractères dans "dico_ordre_modalites"
        dico_ordre_modalites[var_sd] = [str(modal) for modal in dico_ordre_modalites[var_sd]]
        # filtrer pour ne garder que les modalités définies dans "dico_ordre_modalites"
        df = df[df[var_sd].isin(dico_ordre_modalites[var_sd])]
        # définir l'ordre des modalités pour Y6PARTEU24ST
        ordre_modalites = [
            "Vous avez voté",
            "Vous n'avez pas voté"
        ]
        # créer une colonne catégorielle avec l'ordre souhaité pour la variable socio-démographique
        var_sd = input.Select_VarSD_Part()
        df[var_sd] = pd.Categorical(
            df[var_sd],
            categories=dico_ordre_modalites[var_sd],
            ordered=True
        )
        # filtrer et pivoter les données
        df_pivot = df[df['Y6PARTEU24ST'].isin(ordre_modalites)].pivot(
            index=var_sd,
            columns='Y6PARTEU24ST',
            values='pct'
        )
        df_pivot = df_pivot.reindex(columns=ordre_modalites)
        # créer une palette de couleurs automatique
        nb_couleurs = len(df_pivot.index)
        palette = px.colors.qualitative.Plotly[:nb_couleurs]
        # créer le graphique
        fig = go.Figure()
        # ajouter les données
        for i, VarSD in enumerate(df_pivot.index):
            fig.add_trace(
                go.Bar(
                    x=ordre_modalites,
                    y=df_pivot.loc[VarSD],
                    name=wrap_label(VarSD),
                    marker_color=palette[i],
                    # afficher les valeurs sous le format 'xx.x%' dans la bulle qui s'affiche
                    # au survol de la courbe par la souris, et supprimer toutes les autres
                    # informations qui pourraient s'afficher en plus (nom de la modalité)
                    hovertemplate='%{y:.1f}%<extra></extra>',
                    # n'afficher la bulle contenant la valeur 'y' en % uniquement
                    # au-dessus de la barre verticale survolée par la souris
                    hoverinfo='y',
                    # aligner ce texte 'y' dans la bulle de manière automatique
                    hoverlabel=dict(
                        align='auto'
                    )
                )
            )
         # mettre en forme le graphique
        fig.update_layout(
            barmode='group', # barres séparées et groupées pour les modalités de la VarSD choisie
            title={
                'text': "Participation au vote en fonction %s" % dico_titre.get("%s" % input.Select_VarSD_Part()),
                'y':0.98,
                'x':0.01,
                'xanchor': 'left',
                'yanchor': 'top'
            },
            # définir le titre de la légende
            legend_title="%s" % dico_legende.get("%s" % input.Select_VarSD_Part()),
            # définir l'affichage séparé des valeurs de % affichées au-dessus de
            # chaque barre verticale quand la souris la survole
            hovermode="closest",
            # configuration spécifique pour les bulles d'info :
            # réduire la distance de détection du survol de la souris
            hoverdistance=1,
            # définir le thème général de l'apparence du graphique
            template="plotly_white",
            # définir le titre de l'axe des ordonnées et son apparence
            yaxis_title=dict(
                text='Pourcentage de répondants (%)',
                font_size=12
            ),
            # définir les sources des données
            annotations=[
                dict(
                    xref='paper', # utiliser la largeur totale du graphique comme référence
                    yref='paper', # utiliser la hauteur totale du graphique comme référence
                    x=0.5, # placer le point d'ancrage au milieu de la largeur
                    y=-0.1, # valeur à ajuster pour positionner verticalement le texte sous le graphique
                    xanchor='center', # centrer le texte par rapport au point d'ancrage
                    yanchor='top',
                    text=
                        'Enquête électorale française pour les ' +
                        'élections européennes de juin 2024, ' +
                        'par Ipsos Sopra Steria, Cevipof, ' +
                        'Le Monde, Fondation Jean Jaurès et ' +
                        'Institut Montaigne (2024)',
                    font=dict(
                        size=10,
                        color='grey'
                    ),
                    showarrow=False
                )
            ],
            # définir les marges de la zone graphique
            # (augmentées à droite pour le cadre fixe de la légende)
            margin=dict(
                b=50, # b = bottom
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
            ),
        )
        # retourner le graphique
        return fig



    ##################################
    # onglet 02 : LISTES POLITIQUES  #
    ##################################

    # bouton 01 : décrire la question posée dans l'enquête
    @reactive.effect
    @reactive.event(input.Show_LIST_Question)
    def _():
        m = ui.modal(
            "La question posée aux répondants est la suivante : 'Voici les listes qui se présentaient lors des élections européennes du 9 juin 2024. Pouvez-vous dire celle pour laquelle vous avez voté ?'",
            title="Informations complémentaires sur la question contenue dans l'enquête :",
            easy_close=False
        )
        ui.modal_show(m)

    # bouton 02 : décrire la variable
    @reactive.effect
    @reactive.event(input.Show_LIST_Info)
    def _():
        m = ui.modal(
            "La variable sur la liste politique ayant reçu le vote du répondant contient à l'origine 40 modalités. \
            La variable du vote en faveur des listes politiques présentée ici sur les graphiques est simplifiée, \
            certaines listes politiques étant regroupées par proximité politique. \
            Ainsi, les modalités de réponse synthétiques retenues pour cette variable sont les suivantes : \
            1 = 'Très à gauche (Lutte ouvrière, Nouveau parti anti-capitaliste, Parti communiste français, La France insoumise)', \
            2 = 'Gauche (Parti socialiste, Europe ecologie - Les Verts)', \
            3 = 'Centre (Renaissance, MoDem, Horizons, UDI)', \
            4 = 'Droite (Les Républicains)', \
            5 = 'Très à droite (Rassemblement national, Reconquête)', \
            6 = 'Autre liste'.",
            title="Informations complémentaires sur la variable choisie pour les graphiques :",
            easy_close=False
        )
        ui.modal_show(m)

    # graphique
    @output
    @render_plotly
    def Graph_List():
        # importer les données
        csvfile = "data/T_w6_eu24dxst.csv"
        data = pd.read_csv(csvfile)
        # supprimer la première colonne (vide) de la base de donnée
        data = data.drop(
            data.columns[0],
            axis=1
        )
        # identifier les étiquettes courtes (chiffres démarrant à 1)
        data['ETIQCOURTE'] = data.index + 1
        etiquettes_courtes = data["ETIQCOURTE"]
        # identifier les étiquettes longues (modalités de la variable dans la table lue)
        etiquettes_longues = data["EU24DXST"]
        # créer la figure en mémoire
        fig = go.Figure()
        # créer la liste des couleurs en fonction du nombre de modalités
        couleurs_cl = cl.scales[str(max(3, len(data["EU24DXST"])))]['qual']['Set1']
        # ajouter les données
        fig.add_trace(
            go.Bar(
                # on représente la colonne des étiquettes courtes (et non la variable elle-même, car
                # cette colonne correspond aux étiquettes longues de la légende)
                x=data["ETIQCOURTE"],
                y=data["pct"],
                # changer de couleur en fonction de la modalité de réponse
                marker_color=couleurs_cl,
                # afficher les valeurs sous le format 'xx.x%' dans la bulle qui s'affiche
                # au survol de la courbe par la souris, et supprimer toutes les autres
                # informations qui pourraient s'afficher en plus (nom de la modalité)
                hovertemplate='%{y:.1f}%<extra></extra>',
                # n'afficher la bulle contenant la valeur 'y' en % uniquement
                # au-dessus de la barre verticale survolée par la souris
                hoverinfo='y',
                # centrer ce texte 'y' dans la bulle
                hoverlabel=dict(
                   align='auto'
                )
            )
        )
        # créer le texte de la légende (correspondance entre les étiquettes courtes et les étiquettes longues)
        legende_text = "<br>".join([f"{lettre}: {etiquette}" for lettre, etiquette in zip(etiquettes_courtes, etiquettes_longues)])
        # mettre en forme le graphique
        fig.update_layout(
            # définir le titre du graphique et son apparence
            title={
                'text': "Vote en faveur des listes politiques",
                'y':0.98,
                'x':0.01,
                'xanchor': 'left',
                'yanchor': 'top'
            },
            # définir le titre de l'axe des ordonnées et son apparence
            yaxis_title=dict(
                text='Pourcentage de répondants (%)',
                font_size=12
            ),
            # définir l'affichage séparé des valeurs de % affichées au-dessus de
            # chaque barre verticale quand la souris la survole
            hovermode="closest",
            # définir le thème général de l'apparence du graphique
            template="plotly_white",
            # définir deux annotations
            annotations=[
                # sources des données
                dict(
                    xref='paper', # utiliser la largeur totale du graphique comme référence
                    yref='paper', # utiliser la hauteur totale du graphique comme référence
                    x=0.5, # placer le point d'ancrage au milieu de la largeur
                    y=-0.1, # valeur à ajuster pour positionner verticalement le texte sous le graphique
                    xanchor='center', # centrer le texte par rapport au point d'ancrage
                    yanchor='top',
                    text=
                        'Enquête électorale française pour les ' +
                        'élections européennes de juin 2024, ' +
                        'par Ipsos Sopra Steria, Cevipof, ' +
                        'Le Monde, Fondation Jean Jaurès et ' +
                        'Institut Montaigne (2024)',
                    font=dict(
                        size=10,
                        color='grey'
                    ),
                    showarrow=False
                ),
                # légende personnalisée
                dict(
                    valign="top", # aligner le texte en haut de chaque marqueur de la légende
                    x=0.05, # position horizontale de la légende (1 = à droite du graphique)
                    y=1.00, # position verticale de la légende (1 = en haut)
                    xref='paper',
                    yref='paper',
                    xanchor='left', # ancrer la légende à gauche de sa position x
                    yanchor='top', # ancrer la légende en haut de sa position y
                    text=f"<b>Légende :</b><br>{legende_text}",
                    showarrow=False,
                    font=dict(size=12),
                    align='left',
                    bgcolor='rgba(255,255,255,0.8)', # fond légèrement transparent
                )
            ],
            # définir les marges de la zone graphique
            # (augmentées à droite pour le cadre fixe de la légende)
            margin=dict(
                b=50, # b = bottom
                t=50,  # t = top
                l=50, # l = left
                r=200 # r = right
            )
        )
        # configurer l'axe des abscisses pour n'afficher que des nombres entiers
        fig.update_xaxes(
            tickmode='linear',
            tick0=1,
            dtick=1,
            tickfont=dict(size=12),
            tickangle=0
        )

        # retourner le graphique
        return fig



    ###################################################
    # onglet 03 : PREMIER ENJEU DU VOTE (vue globale) #
    ###################################################

    # bouton 01 : décrire la question posée dans l'enquête
    @reactive.effect
    @reactive.event(input.Show_ENJVG_Question)
    def _():
        m = ui.modal(
            "La question posée aux répondants est la suivante : 'Parmi les sujets suivants, \
            quels sont les trois dont vous avez tenu le plus compte dans votre choix de vote \
            pour les élections européennes du dimanche 9 juin ? (en 1er)' \
            et ses modalités de réponse sont : \
            1 = 'Le chômage', 2 = 'La menace terroriste', 3 = 'Le pouvoir d’achat', \
            4 = 'Système scolaire et éducation', 5 = 'Le système de santé', \
            6 = 'La fiscalité', 7 = 'L’avenir du système de retraite', \
            8 = 'La protection de l’environnement', 9 = 'L’immigration', \
            10 = 'La sécurité des biens et des personnes', 11 = 'Le niveau des inégalités sociales', \
            12 = 'La place de la France en Europe et dans le monde', \
            13 = 'Le montant des déficits publics', 14 = 'La guerre en Ukraine', \
            15 = 'L’avenir de l’agriculture', 16 = 'La situation à Gaza'.",
            title="Informations complémentaires sur la question contenue dans l'enquête :",
            easy_close=False
        )
        ui.modal_show(m)

    # bouton 02 : décrire la variable des enjeux du vote
    @reactive.effect
    @reactive.event(input.Show_ENJVG_Info)
    def _():
        m = ui.modal(
            "La variable sur le premier enjeu du vote présentée ici est une version simplifiée. \
            Ainsi, sur les 16 propositions de réponse soumises au choix des répondants, seules \
            les 4 propositions ayant reccueilli le plus de suffrages sont présentées en détail. \
            Les 12 autres propositions sont agrégées dans la modalité 'Autres réponses'.",
            title="Informations complémentaires sur la variable choisie pour les graphiques :",
            easy_close=False
        )
        ui.modal_show(m)

    # graphique
    @output
    @render_plotly
    def Graph_EnjVG():
        # importer les données
        csvfile = "data/T_w6_enjeurst_0.csv"
        data = pd.read_csv(csvfile)
        # supprimer la première colonne (vide) de la base de donnée
        data = data.drop(
            data.columns[0],
            axis=1
        )
        # créer la figure en mémoire
        fig = go.Figure()
        # créer la liste des couleurs en fonction du nombre de modalités
        couleurs_cl = cl.scales[str(max(3, len(data["ENJEURST_0"])))]['qual']['Set1']
        # ajouter les données
        fig.add_trace(
            go.Bar(
                x=data["ENJEURST_0"],
                y=data["pct"],
                # changer de couleur en fonction de la modalité de réponse
                marker_color=couleurs_cl,
                # afficher les valeurs sous le format 'xx.x%' dans la bulle qui s'affiche
                # au survol de la courbe par la souris, et supprimer toutes les autres
                # informations qui pourraient s'afficher en plus (nom de la modalité)
                hovertemplate='%{y:.1f}%<extra></extra>'
            )
        )
        # mettre en forme le graphique
        fig.update_layout(
            # définir le titre du graphique et son apparence
            title={
                'text': "Premier enjeu du vote",
                'y':0.98,
                'x':0.01,
                'xanchor': 'left',
                'yanchor': 'top'
            },
            # définir le titre de l'axe des ordonnées et son apparence
            yaxis_title=dict(
                text='Pourcentage de répondants (%)',
                font_size=12
            ),
            # définir l'affichage séparé des valeurs de % affichées au-dessus de
            # chaque barre verticale quand la souris la survole
            hovermode="x",
            # définir le thème général de l'apparence du graphique
            template="plotly_white",
            # définir les sources des données
            annotations=[
                dict(
                    xref='paper', # utiliser la largeur totale du graphique comme référence
                    yref='paper', # utiliser la hauteur totale du graphique comme référence
                    x=0.5, # placer le point d'ancrage au milieu de la largeur
                    y=-0.1, # valeur à ajuster pour positionner verticalement le texte sous le graphique
                    xanchor='center', # centrer le texte par rapport au point d'ancrage
                    yanchor='top',
                    text=
                        'Enquête électorale française pour les ' +
                        'élections européennes de juin 2024, ' +
                        'par Ipsos Sopra Steria, Cevipof, ' +
                        'Le Monde, Fondation Jean Jaurès et ' +
                        'Institut Montaigne (2024)',
                    font=dict(
                        size=10,
                        color='grey'
                    ),
                    showarrow=False
                )
            ],
            # définir les marges de la zone graphique
            # (augmentées à droite pour le cadre fixe de la légende)
            margin=dict(
                b=50, # b = bottom
                t=50,  # t = top
                l=50, # l = left
                r=200 # r = right
            )
        )
        # retourner le graphique
        return fig



    #####################################################
    # onglet 04 : PREMIER ENJEU DU VOTE (vue détaillée) #
    #####################################################

    # bouton 01 : décrire la question posée dans l'enquête
    @reactive.effect
    @reactive.event(input.Show_ENJ_Question)
    def _():
        m = ui.modal(
            "La question posée aux répondants est la suivante : 'Parmi les sujets suivants, \
            quels sont les trois dont vous avez tenu le plus compte dans votre choix de vote \
            pour les élections européennes du dimanche 9 juin ? (en 1er)' \
            et ses modalités de réponse sont : \
            1 = 'Le chômage', 2 = 'La menace terroriste', 3 = 'Le pouvoir d’achat', \
            4 = 'Système scolaire et éducation', 5 = 'Le système de santé', \
            6 = 'La fiscalité', 7 = 'L’avenir du système de retraite', \
            8 = 'La protection de l’environnement', 9 = 'L’immigration', \
            10 = 'La sécurité des biens et des personnes', 11 = 'Le niveau des inégalités sociales', \
            12 = 'La place de la France en Europe et dans le monde', \
            13 = 'Le montant des déficits publics', 14 = 'La guerre en Ukraine', \
            15 = 'L’avenir de l’agriculture', 16 = 'La situation à Gaza'.",
            title="Informations complémentaires sur la question contenue dans l'enquête :",
            easy_close=False
        )
        ui.modal_show(m)

    # bouton 02 : décrire la variable des enjeux du vote
    @reactive.effect
    @reactive.event(input.Show_ENJ_Info)
    def _():
        m = ui.modal(
            "La variable sur le premier enjeu du vote présentée ici est une version simplifiée. \
            Ainsi, sur les 16 propositions de réponse soumises au choix des répondants, seules \
            les 4 propositions ayant reccueilli le plus de suffrages sont présentées en détail. \
            Les 12 autres propositions sont agrégées dans la modalité 'Autres réponses'.",
            title="Informations complémentaires sur la variable choisie pour les graphiques :",
            easy_close=False
        )
        ui.modal_show(m)


    # bouton 03 : afficher la description de la variable socio-démographique choisie
    # avec plusieurs parties de texte qui dépendent de ce choix (via des dictionnaires)
    @reactive.effect
    @reactive.event(input.Show_VarSD_Enj_Info)
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
            "Y6PCSIST": "1 = 'Agriculteur exploitant, artisan, commerçant, chef d entreprise' ; 2 = 'Cadre supérieur' ; 3 = 'Profession intermédiaire' ; 4 = 'Employé' ; 5 = 'Ouvrier' ; 6 = 'Retraité, inactif'",
            "Y6EDUST": "1 = 'Aucun diplôme' ; 2 = 'CAP, BEP' ; 3 = 'Baccalauréat' ; 4 = 'Bac +2' ; 5 = 'Bac +3 et plus'",
            "Y6REL1ST": "1 = 'Catholique' ; 2 = 'Juive' ; 3 = 'Musulmane' ; 4 = 'Autre religion (protestante, boudhiste ou autre)' ; 5 = 'Sans religion'",
            "Y6ECO2ST2": "1 = 'Moins de 1 250 euros' ; 2 = 'De 1 250 euros à 1 999 euros' ; 3 = 'De 2 000 à 3 499 euros' ; 4 = 'De 3 500 à 4 999 euros' ; 5 = '5 000 euros et plus'",
            "Y6INTPOLST": "1 = 'Beaucoup' ; 2 = 'Un peu' ; 3 = 'Pas vraiment' ; 4 = 'Pas du tout'",
            "Y6Q7ST": "1 = 'Très à gauche' ; 2 = 'Plutôt à gauche' ; 3 = 'Au centre' ; 4 = 'Plutôt à droite' ; 5 = 'Très à droite'",
            "Y6PROXST": "1 = 'Très à gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)' ; 2 = 'Gauche (Parti Socialiste, Europe Ecologie - Les Verts)' ; 3 = 'Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))' ; 4 = 'Droite (Les Républicains)' ; 5 = 'Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)' ; 6 = 'Autre parti ou aucun parti'"
        }
        # définir le texte complet à afficher (avec parties fixes et variables en fonction du choix effectué)
        m = ui.modal(
            "La variable '%s' correspond à ou est calculée à partir de la question suivante posée aux répondants : \
            '%s', \
            et ses modalités de réponse (inchangées par rapport au questionnaire ou regroupées pour les présents graphiques) sont : \
            %s." % (
                dico_nom_var.get("%s" % input.Select_VarSD_Enj()),
                dico_question_var.get("%s" % input.Select_VarSD_Enj()),
                dico_modalite_var.get("%s" % input.Select_VarSD_Enj())
            ),
            title="Informations complémentaires sur la variable socio-démographique choisie :",
            easy_close=False
        )
        ui.modal_show(m)

    # graphique
    @output
    @render_plotly
    def Graph_Croise_Enj():
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
        # définir les modalités des variables socio-démo et leur ordre
        dico_modalite_var = {
            "Y6SEXEST": "1 = 'Homme' ; 2 = 'Femme'",
            "Y6AGERST": "1 = '18 à 24 ans' ; 2 = '25 à 34 ans' ; 3 = '35 à 49 ans' ; 4 = '50 à 59 ans' ; 5 = '60 ans et plus'",
            "Y6REG13ST": "1 = 'Ile de France' ; 2 = 'Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)' ; 3 = 'Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)' ; 4 = 'Sud ouest (Nouvelle Aquitaine et Occitanie)' ; 5 = 'Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)'",
            "Y6AGGLO5ST": "1 = 'Zone rurale (moins de 2 000 habitants)' ; 2 = 'Zone urbaine de 2 000 à 9 999 habitants' ; 3 = 'Zone urbaine de 10 000 à 49 999 habitants' ; 4 = 'Zone urbaine de 50 000 à 199 999 habitants' ; 5 = 'Zone urbaine de 200 000 habitants et plus'",
            "Y6EMPST": "1 = 'Salarié (salarié à plein temps ou à temps partiel)' ; 2 = 'Indépendant (travaille à mon compte)' ; 3 = 'Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)'",
            "Y6PCSIST": "1 = 'Agriculteur exploitant, artisan, commerçant, chef d entreprise' ; 2 = 'Cadre supérieur' ; 3 = 'Profession intermédiaire' ; 4 = 'Employé' ; 5 = 'Ouvrier' ; 6 = 'Retraité, inactif'",
            "Y6EDUST": "1 = 'Aucun diplôme' ; 2 = 'CAP, BEP' ; 3 = 'Baccalauréat' ; 4 = 'Bac +2' ; 5 = 'Bac +3 et plus'",
            "Y6REL1ST": "1 = 'Catholique' ; 2 = 'Juive' ; 3 = 'Musulmane' ; 4 = 'Autre religion (protestante, boudhiste ou autre)' ; 5 = 'Sans religion'",
            "Y6ECO2ST2": "1 = 'Moins de 1 250 euros' ; 2 = 'De 1 250 euros à 1 999 euros' ; 3 = 'De 2 000 à 3 499 euros' ; 4 = 'De 3 500 à 4 999 euros' ; 5 = '5 000 euros et plus'",
            "Y6INTPOLST": "1 = 'Beaucoup' ; 2 = 'Un peu' ; 3 = 'Pas vraiment' ; 4 = 'Pas du tout'",
            "Y6Q7ST": "1 = 'Très à gauche' ; 2 = 'Plutôt à gauche' ; 3 = 'Au centre' ; 4 = 'Plutôt à droite' ; 5 = 'Très à droite'",
            "Y6PROXST": "1 = 'Très à gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)' ; 2 = 'Gauche (Parti Socialiste, Europe Ecologie - Les Verts)' ; 3 = 'Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))' ; 4 = 'Droite (Les Républicains)' ; 5 = 'Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)' ; 6 = 'Autre parti ou aucun parti'"
        }
        # définir un dictionnaire qui contient l'ordre figé des modalités pour chaque variable socio-démographique
        dico_ordre_modalites = {
            "Y6SEXEST": [
                "Homme",
                "Femme"
            ],
            "Y6AGERST": [
                "18 à 24 ans",
                "25 à 34 ans",
                "35 à 49 ans",
                "50 à 59 ans",
                "60 ans et plus"
            ],
            "Y6REG13ST": [
                "Ile de France",
                "Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)",
                "Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)",
                "Sud ouest (Nouvelle Aquitaine et Occitanie)",
                "Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)"
            ],
            "Y6AGGLO5ST": [
                "Zone rurale (moins de 2 000 habitants)",
                "Zone urbaine de 2 000 à 9 999 habitants",
                "Zone urbaine de 10 000 à 49 999 habitants",
                "Zone urbaine de 50 000 à 199 999 habitants",
                "Zone urbaine de 200 000 habitants et plus"
            ],
            "Y6EMPST": [
                "Salarié (salarié à plein temps ou à temps partiel)",
                "Indépendant (travaille à mon compte)",
                "Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)"
            ],
            "Y6PCSIST": [
                "Agriculteur exploitant, artisan, commerçant, chef d entreprise",
                "Cadre supérieur",
                "Profession intermédiaire",
                "Employé",
                "Ouvrier",
                "Retraité, inactif"
            ],
            "Y6EDUST": [
                "Aucun diplôme",
                "CAP, BEP",
                "Baccalauréat",
                "Bac +2",
                "Bac +3 et plus"
            ],
            "Y6REL1ST": [
                "Catholique",
                "Juive",
                "Musulmane",
                "Autre religion (protestante, boudhiste ou autre)",
                "Sans religion"
            ],
            "Y6ECO2ST2": [
                "Moins de 1 250 euros",
                "De 1 250 euros à 1 999 euros",
                "De 2 000 à 3 499 euros",
                "De 3 500 à 4 999 euros",
                "5 000 euros et plus"
            ],
            "Y6INTPOLST": [
                "Beaucoup",
                "Un peu",
                "Pas vraiment",
                "Pas du tout"
            ],
            "Y6Q7ST": [
                "Très à gauche",
                "Plutôt à gauche",
                "Au centre",
                "Plutôt à droite",
                "Très à droite"
            ],
            "Y6PROXST": [
                "Très à gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)",
                "Gauche (Parti Socialiste, Europe Ecologie - Les Verts)",
                "Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))",
                "Droite (Les Républicains)",
                "Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)",
                "Autre parti ou aucun parti"
            ]
        }
        # définir une fonction qui affiche les étiquettes
        # des modalités de la variablr SD choisie dans la légende
        # sur plusieurs lignes si leur longueur initiale dépasse la
        # largeur du cadre de la légende (version robuste avec gestion des erreurs)
        def wrap_label(label, max_length=20):
            try:
                # Si le label est un float ou NaN
                if pd.isna(label) or isinstance(label, float):
                    return "Non renseigné"
                # Convertir en string si ce n'est pas déjà le cas
                label = str(label).strip()
                # Si la chaîne est vide après nettoyage
                if not label:
                    return "Non renseigné"
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
            except Exception as e:
                print(f"Erreur dans wrap_label avec {label}: {str(e)}")
                return str(label) 
                # retourner le label tel quel en cas d'erreur
        # lire le fichier CSV des données
        csvfile = "data/T_w6_enjeurst_0_" + "%s" % input.Select_VarSD_Enj().lower()[2:] + ".csv"
        df = pd.read_csv(csvfile)
        # nettoyer les données lues
        var_sd = input.Select_VarSD_Enj()
        df[var_sd] = df[var_sd].fillna("Non renseigné")  # Gérer les NaN
        df[var_sd] = df[var_sd].astype(str)  # Convertir en string
        df['Y6ENJEURST_0'] = df['Y6ENJEURST_0'].fillna("Non renseigné")
        # s'assurer que toutes les modalités sont des chaînes de caractères dans "dico_ordre_modalites"
        dico_ordre_modalites[var_sd] = [str(modal) for modal in dico_ordre_modalites[var_sd]]
        # filtrer pour ne garder que les modalités définies dans "dico_ordre_modalites"
        df = df[df[var_sd].isin(dico_ordre_modalites[var_sd])]
        # définir l'ordre des modalités pour Y6ENJEURST_0
        ordre_modalites = [
            "Le chômage",
            "Système scolaire et éducation",
            "La sécurité des biens et des personnes",
            "Le montant des déficits publics"
        ]
        # créer une colonne catégorielle avec l'ordre souhaité pour la variable socio-démographique
        var_sd = input.Select_VarSD_Enj()
        df[var_sd] = pd.Categorical(
            df[var_sd],
            categories=dico_ordre_modalites[var_sd],
            ordered=True
        )
        # filtrer et pivoter les données
        df_pivot = df[df['Y6ENJEURST_0'].isin(ordre_modalites)].pivot(
            index=var_sd,
            columns='Y6ENJEURST_0',
            values='pct'
        )
        df_pivot = df_pivot.reindex(columns=ordre_modalites)
        # créer une palette de couleurs automatique
        nb_couleurs = len(df_pivot.index)
        palette = px.colors.qualitative.Plotly[:nb_couleurs]
        # créer le graphique
        fig = go.Figure()
        # ajouter les données 
        for i, VarSD in enumerate(df_pivot.index):
            fig.add_trace(
                go.Bar(
                    x=ordre_modalites,
                    y=df_pivot.loc[VarSD],
                    name=wrap_label(VarSD),
                    marker_color=palette[i],
                    # afficher les valeurs sous le format 'xx.x%' dans la bulle qui s'affiche
                    # au survol de la courbe par la souris, et supprimer toutes les autres
                    # informations qui pourraient s'afficher en plus (nom de la modalité)
                    hovertemplate='%{y:.1f}%<extra></extra>',
                    # n'afficher la bulle contenant la valeur 'y' en % uniquement
                    # au-dessus de la barre verticale survolée par la souris
                    hoverinfo='y',
                    # centrer ce texte 'y' dans la bulle
                    hoverlabel=dict(
                        align='auto'
                    )
                )
            )
        # mettre en forme le graphique
        fig.update_layout(
            barmode='group', # barres séparées et groupées pour les modalités de la VarSD choisie
            title={
                'text': "Premier enjeu du vote en fonction %s" % dico_titre.get("%s" % input.Select_VarSD_Enj()),
                'y':0.98,
                'x':0.01,
                'xanchor': 'left',
                'yanchor': 'top'
            },
            # définir le titre de la légende
            legend_title="%s" % dico_legende.get("%s" % input.Select_VarSD_Enj()),
            # définir l'affichage séparé des valeurs de % affichées au-dessus de
            # chaque barre verticale quand la souris la survole
            hovermode="closest",
            # définir le thème général de l'apparence du graphique
            template="plotly_white",
            # définir le titre de l'axe des ordonnées et son apparence
            yaxis_title=dict(
                text='Pourcentage de répondants (%)',
                font_size=12
            ),
            # définir les sources des données
            annotations=[
                dict(
                    xref='paper', # utiliser la largeur totale du graphique comme référence
                    yref='paper', # utiliser la hauteur totale du graphique comme référence
                    x=0.5, # placer le point d'ancrage au milieu de la largeur
                    y=-0.1, # valeur à ajuster pour positionner verticalement le texte sous le graphique
                    xanchor='center', # centrer le texte par rapport au point d'ancrage
                    yanchor='top',
                    text=
                        'Enquête électorale française pour les ' +
                        'élections européennes de juin 2024, ' +
                        'par Ipsos Sopra Steria, Cevipof, ' +
                        'Le Monde, Fondation Jean Jaurès et ' +
                        'Institut Montaigne (2024)',
                    font=dict(
                        size=10,
                        color='grey'
                    ),
                    showarrow=False
                )
            ],
            # définir les marges de la zone graphique
            # (augmentées à droite pour le cadre fixe de la légende)
            margin=dict(
                b=50, # b = bottom
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
            ),
        )
        # retourner le graphique
        return fig



    #########################################
    # onglet 05 : CONTEXTE DE CHOIX DU VOTE #
    #########################################

    # bouton 02 : décrire la question posée dans l'enquête
    @reactive.effect
    @reactive.event(input.Show_ChoixVote_Question)
    def _():
        # définir le nom de la variable choisie
        dico_nom_var = {
            "EUCHOIXST": "Moment du choix du vote",
            "EUDECST": "Choix du vote fait par adhésion ou par défaut",
            "EUMOTPRST": "Choix du vote lié au Président ou au Gouvernement en place",
            "EUELARGST": "Choix du vote lié à l'élargissement de l'UE",
            "EURNST_0": "Première raison du choix de vote pour la liste du Rassemblement National (RN) conduite par Jordan Bardella"
        }
        # définir la question de l'enquête associée à la variable choisie
        dico_question_var = {
            "EUCHOIXST": "A quel moment avez-vous décidé de la liste pour laquelle vous avez voté ?",
            "EUDECST": "Avez-vous voté pour cette liste... ?",
            "EUMOTPRST": "Lors des élections européennes, avez-vous voté...",
            "EUELARGST": "Pour certains, il faut continuer l’élargissement de l’Union européenne et accueillir de nouveaux pays membres. Pour d'autres, il faut arrêter l’élargissement de l’Union européenne et ne plus accueillir de nouveaux pays membres. Sur une échelle de 0 à 10, dites-moi quelle est votre opinion ? (0 signifie qu’il faut arrêter l’élargissement de l’Union européenne, 10 signifie qu’il faut continuer l’élargissement de l’Union européenne)",
            "EURNST_0": "Pour quelles raisons avez-vous voté pour la liste du Rassemblement National conduite par Jordan Bardella ? (en premier)"
        }
        # définir les modalités de réponse à la question de l'enquête associée à la variable choisie
        dico_modalite_var = {
            "EUCHOIXST": "1 = 'Il y a au moins un mois' ; 2 = 'Les dernières semaines avant le scrutin' ; 3 = 'Les derniers jours avant le scrutin' ; 4 = 'Juste avant le week-end des élections' ; 5 = 'Au dernier moment, le jour du scrutin ou la veille'",
            "EUDECST": "1 = 'Avant tout par adhésion' ; 2 = 'Avant tout par défaut'",
            "EUMOTPRST": "1 = 'Avant tout pour manifester votre soutien au Président de la République et au Gouvernement' ; 2 = 'Avant tout pour manifester votre opposition au Président de la République et au Gouvernement' ; 3 = 'Ni l'un, ni l'autre'",
            "EUELARGST": "1 = 'Arrêter l'élargissement' ; 2 = 'Ni l'un, ni l'autre' ; 3 = 'Continuer l'élargissement'",
            "EURNST_0": "'1' = 'Par adhésion à son programme sur l'Europe' ; '2' = 'Par envie de soutenir Marine Le Pen' ; '3' = 'Par volonté de sanctionner le pouvoir en place et les autres partis politiques' ; '4' = 'Par envie de soutenir Jordan Bardella' ; '5' = 'Par adhésion aux valeurs et aux idées que défend le RN'"
        }
        # afficher le texte de décrivant la question (avec parties fixes et variables en fonction du choix)
        m = ui.modal(
            "La variable '%s' correspond à la question suivante posée aux répondants : \
            '%s', \
            et ses modalités de réponse (inchangées par rapport au questionnaire ou regroupées pour les présents graphiques) sont : \
            %s." % (
                dico_nom_var.get(
                    "%s" % input.Select_VarChoixVote()
                ),
                dico_question_var.get("%s" % input.Select_VarChoixVote()),
                dico_modalite_var.get("%s" % input.Select_VarChoixVote())
                ),
                title="Informations complémentaires sur la question contenue dans l'enquête :",
                easy_close=False
        )
        ui.modal_show(m)

    # graphique
    @output
    @render_plotly
    def Graph_ContextChoixVote():
        # définir la partie variable du titre
        dico_titre = {
            "EUCHOIXST": "Moment du choix du vote",
            "EUDECST": "Choix du vote fait par adhésion ou par défaut",
            "EUMOTPRST": "Choix du vote lié au Président ou au Gouvernement en place",
            "EUELARGST": "Choix du vote lié à l'élargissement de l'UE",
            "EURNST_0": "Première raison du choix de vote pour la liste du RN"
        }
        # définir l'échelle de l'axe des ordonnées en fonction des
        # valeurs prises par la variable choisie
        dico_echelleY = {
            "EUCHOIXST": [0, 60],
            "EUDECST": [0, 60],
            "EUMOTPRST": [0, 60],
            "EUELARGST": [0, 50],
            "EURNST_0": [0, 60]
        }
        # importer les données
        csvfile = "data/T_w6_" + "%s" % input.Select_VarChoixVote().lower() + ".csv"
        data = pd.read_csv(csvfile)
        # supprimer la première colonne (vide) de la base de donnée
        data = data.drop(
            data.columns[0],
            axis=1
        )
        # identifier les étiquettes courtes (chiffres démarrant à 1)
        data['ETIQCOURTE'] = data.index + 1
        etiquettes_courtes = data["ETIQCOURTE"]
        # identifier les étiquettes longues (modalités de la variable dans la table lue)
        etiquettes_longues = data["%s" % input.Select_VarChoixVote()]
        # créer la figure en mémoire
        fig = go.Figure()
        # créer la liste des couleurs en fonction du nombre de modalités
        couleurs_cl = cl.scales[str(max(3, len(data["%s" % input.Select_VarChoixVote()])))]['qual']['Set1']
        # ajouter les données
        fig.add_trace(
            go.Bar(
                # on représente la colonne des étiquettes courtes (et non la variable elle-même, car
                # cette colonne correspond aux étiquettes longues de la légende)
                x=data["ETIQCOURTE"],
                y=data["pct"],
                # changer de couleur en fonction de la modalité de réponse
                marker_color=couleurs_cl,
                # afficher les valeurs sous le format 'xx.x%' dans la bulle qui s'affiche
                # au survol de la courbe par la souris, et supprimer toutes les autres
                # informations qui pourraient s'afficher en plus (nom de la modalité)
                hovertemplate='%{y:.1f}%<extra></extra>',
                # n'afficher la bulle contenant la valeur 'y' en % uniquement
                # au-dessus de la barre verticale survolée par la souris
                hoverinfo='y',
                # centrer ce texte 'y' dans la bulle
                hoverlabel=dict(
                    align='auto'
                )
            )
        )
        # créer le texte de la légende (correspondance entre les étiquettes courtes et les étiquettes longues)
        legende_text = "<br>".join([f"{lettre}: {etiquette}" for lettre, etiquette in zip(etiquettes_courtes, etiquettes_longues)])
        # mettre en forme le graphique
        fig.update_layout(
            # définir le titre du graphique et son apparence
            title={
                'text': "%s" % (
                    dico_titre.get("%s" % input.Select_VarChoixVote())
                ),
                'y':0.98,
                'x':0.01,
                'xanchor': 'left',
                'yanchor': 'top'
            },
            # définir le titre de l'axe des ordonnées et son apparence
            yaxis_title=dict(
                text='Pourcentage de répondants (%)',
                font_size=12
            ),
            # définir l'affichage séparé des valeurs de % affichées au-dessus de
            # chaque barre verticale quand la souris la survole
            hovermode="closest",
            # définir le thème général de l'apparence du graphique
            template="plotly_white",
            # définir deux annotations
            annotations=[
                # sources des données
                dict(
                    xref='paper', # utiliser la largeur totale du graphique comme référence
                    yref='paper', # utiliser la hauteur totale du graphique comme référence
                    x=0.5, # placer le point d'ancrage au milieu de la largeur
                    y=-0.1, # valeur à ajuster pour positionner verticalement le texte sous le graphique
                    xanchor='center', # centrer le texte par rapport au point d'ancrage
                    yanchor='top',
                    text=
                        'Enquête électorale française pour les ' +
                        'élections européennes de juin 2024, ' +
                        'par Ipsos Sopra Steria, Cevipof, ' +
                        'Le Monde, Fondation Jean Jaurès et ' +
                        'Institut Montaigne (2024)',
                    font=dict(
                        size=10,
                        color='grey'
                    ),
                    showarrow=False
                ),
                # légende personnalisée
                dict(
                    valign="top", # aligner le texte en haut de chaque marqueur de la légende
                    x=0.67, # position horizontale de la légende (1 = à droite du graphique)
                    y=1.10, # position verticale de la légende (1 = en haut)
                    xref='paper',
                    yref='paper',
                    xanchor='left', # ancrer la légende à gauche de sa position x
                    yanchor='top', # ancrer la légende en haut de sa position y
                    text=f"<b>Légende :</b><br>{legende_text}",
                    showarrow=False,
                    font=dict(size=12),
                    align='left',
                    bgcolor='rgba(255,255,255,0.8)', # fond légèrement transparent
                )
            ],
            # définir les marges de la zone graphique
            # (augmentées à droite pour le cadre fixe de la légende)
            margin=dict(
                b=50, # b = bottom
                t=50,  # t = top
                l=50, # l = left
                r=200 # r = right
            )
        )
        # configurer l'axe des abscisses pour n'afficher que des nombres entiers
        fig.update_xaxes(
            tickmode='linear',
            tick0=1,
            dtick=1,
            tickfont=dict(size=12),
            tickangle=0
        )
        # ajuster l'axe des ordonnées en fonction des valeurs observées
        fig.update_yaxes(range=dico_echelleY.get("%s" % input.Select_VarChoixVote()))
        # retourner le graphique
        return fig



    ####################################################
    # onglet 06 : DISSOLUTION DE L'ASSEMBLÉE NATIONALE #
    ####################################################

    # bouton 02 : décrire la question posée dans l'enquête
    @reactive.effect
    @reactive.event(input.Show_DISSOL_Question)
    def _():
        # définir le nom de la variable choisie
        dico_nom_var = {
            "DISS1ST": "Avis sur la dissolution de l'Assemblée nationale",
            "DISS2ST": "Impression sur la dissolution de l'Assemblée nationale",
            "DISS3ST": "Opinion sur la décision du Président de la République"
        }
        # définir la question de l'enquête associée à la variable choisie
        dico_question_var = {
            "DISS1ST": "A l’issue des élections européennes, le président de la République Emmanuel Macron a décidé de dissoudre l’Assemblée nationale. Ainsi, de nouvelles élections législatives auront lieu les 30 juin et 7 juillet prochain. Diriez-vous que vous êtes favorable ou opposé à la dissolution de l’Assemblée nationale ?",
            "DISS2ST": "Et plus précisément, quand vous pensez à la dissolution de l’Assemblée nationale et à la perspective de nouvelles élections législatives, lequel des sentiments suivants est le plus proche de ce que vous ressentez ?",
            "DISS3ST": "Diriez-vous que la décision d’Emmanuel Macron de dissoudre l’Assemblée nationale est..."
        }
        # définir les modalités de réponse à la question de l'enquête associée à la variable choisie
        dico_modalite_var = {
            "DISS1ST": "1 = 'Favorable' ; 2 = 'Opposé'",
            "DISS2ST": "1 = 'Sentiment positif' ; 2 = 'Indifférence' ; '3' = 'Sentiment négatif'",
            "DISS3ST": "1 = 'Audacieuse ou courageuse' ; 2 = 'Dangeureuse ou irresponsable'"
        }
        # afficher le texte de décrivant la question (avec parties fixes et variables en fonction du choix)
        m = ui.modal(
            "La variable '%s' correspond à la question suivante posée aux répondants : \
            '%s', \
            et ses modalités de réponse sont : \
            %s." % (
                dico_nom_var.get(
                    "%s" % input.Select_VarDissolAN()
                ),
                dico_question_var.get("%s" % input.Select_VarDissolAN()),
                dico_modalite_var.get("%s" % input.Select_VarDissolAN())
            ),
            title="Informations complémentaires sur la question contenue dans l'enquête :",
            easy_close=False
        )
        ui.modal_show(m)

    # graphique
    @output
    @render_plotly
    def Graph_DissolAN():
        # définir la partie variable du titre
        dico_titre = {
            "DISS1ST": "Avis sur la dissolution de l'Assemblée nationale",
            "DISS2ST": "Impression sur la dissolution de l'Assemblée nationale",
            "DISS3ST": "Opinion sur la décision du Président de la République"
        }
        # définir l'échelle de l'axe des ordonnées en fonction des
        # valeurs prises par la variable choisie
        dico_echelleY = {
            "DISS1ST": [0, 60],
            "DISS2ST": [0, 60],
            "DISS3ST": [0, 70]
        }
        # importer les données
        csvfile = "data/T_w6_" + "%s" % input.Select_VarDissolAN().lower() + ".csv"
        data = pd.read_csv(csvfile)
        # supprimer la première colonne (vide) de la base de donnée
        data = data.drop(data.columns[0], axis=1)
        # créer la figure en mémoire
        fig = go.Figure()
        # créer la liste des couleurs en fonction du nombre de modalités
        couleurs_cl = cl.scales[str(max(3, len(data["%s" % input.Select_VarDissolAN()])))]['qual']['Set1']
        # ajouter les données
        fig.add_trace(
            go.Bar(
                x=data["%s" % input.Select_VarDissolAN()],
                y=data["pct"],
                # changer de couleur en fonction de la modalité de réponse
                marker_color=couleurs_cl,
                # afficher les valeurs sous le format 'xx.x%' dans la bulle qui s'affiche
                # au survol de la courbe par la souris, et supprimer toutes les autres
                # informations qui pourraient s'afficher en plus (nom de la modalité)
                hovertemplate='%{y:.1f}%<extra></extra>',
                # n'afficher la bulle contenant la valeur 'y' en % uniquement
                # au-dessus de la barre verticale survolée par la souris
                hoverinfo='y',
                # centrer ce texte 'y' dans la bulle
                hoverlabel=dict(
                    align='auto'
                )
            )
        )
        # mettre en forme le graphique
        fig.update_layout(
            # définir le titre du graphique et son apparence
            title={
                'text': "%s" % (
                    dico_titre.get("%s" % input.Select_VarDissolAN())
                ),
                'y':0.98,
                'x':0.01,
                'xanchor': 'left',
                'yanchor': 'top'
             },
            # définir le titre de l'axe des ordonnées et son apparence
            yaxis_title=dict(
                text='Pourcentage de répondants (%)',
                font_size=12
            ),
            # définir l'affichage séparé des valeurs de % affichées au-dessus de
            # chaque barre verticale quand la souris la survole
            hovermode="closest",
            # définir le thème général de l'apparence du graphique
            template="plotly_white",
            # définir les sources des données
            annotations=[
                dict(
                    xref='paper', # utiliser la largeur totale du graphique comme référence
                    yref='paper', # utiliser la hauteur totale du graphique comme référence
                    x=0.5, # placer le point d'ancrage au milieu de la largeur
                    y=-0.1, # valeur à ajuster pour positionner verticalement le texte sous le graphique
                    xanchor='center', # centrer le texte par rapport au point d'ancrage
                    yanchor='top',
                    text=
                        'Enquête électorale française pour les ' +
                        'élections européennes de juin 2024, ' +
                        'par Ipsos Sopra Steria, Cevipof, ' +
                        'Le Monde, Fondation Jean Jaurès et ' +
                        'Institut Montaigne (2024)',
                    font=dict(size=10, color='grey'),
                    showarrow=False
                )
            ],
            # définir les marges de la zone graphique
            # (augmentées à droite pour le cadre fixe de la légende)
            margin=dict(
                b=50, # b = bottom
                t=50,  # t = top
                l=50, # l = left
                r=200 # r = right
            )
        )
        # ajuster l'axe des ordonnées en fonction des valeurs observées
        fig.update_yaxes(range=dico_echelleY.get("%s" % input.Select_VarDissolAN()))
        # retourner le graphique
        return fig


    ################################################################################
    ##                          ELECTIONS LEGISLATIVES                            ##
    ################################################################################

    ########################################
    # onglet 01 : PARTICIPATION (1er tour) #
    ########################################

    # bouton 01 : décrire la question posée dans l'enquête
    @reactive.effect
    @reactive.event(input.Show_PART_Question_Legis_T1)
    def _():
        m = ui.modal(
            "La question posée aux répondants est la suivante : 'Un électeur sur trois n’a pas voté au premier tour des élections législatives le 30 juin 2024. Dans votre cas personnel, qu’est ce qui correspond le mieux à votre attitude à cette occasion ?'",
            title="Informations complémentaires sur la question contenue dans l'enquête :",
            easy_close=False
        )
        ui.modal_show(m)

    # bouton 02 : décrire la variable de l'intention d'aller voter choisie
    @reactive.effect
    @reactive.event(input.Show_PARTST_Info_Legis_T1)
    def _():
        m = ui.modal(
            "La variable sur la participation aux élections législatives présentée ici sur les graphiques est une modalité synthétique de la question posée aux répondants de l'enquête. \
            Ainsi, à partir des quatre modalités de réponse à la question de l'enquête, on en construit deux : 'Vous avez voté' ou 'Vous n'avez pas voté'.",
            title="Informations complémentaires sur la variable choisie pour les graphiques :",
            easy_close=False
        )
        ui.modal_show(m)

    # bouton 03 : afficher la description de la variable socio-démographique choisie
    # avec plusieurs parties de texte qui dépendent de ce choix (via des dictionnaires)
    @reactive.effect
    @reactive.event(input.Show_VarSD_Part_Info_Legis_T1)
    def _():
        # définir le nom de la variable socio-démographique choisie
        dico_nom_var = {
            "Y7SEXEST": "Genre",
            "Y7AGERST": "Âge",
            "Y7REG13ST": "Région",
            "Y7AGGLO5ST": "Taille d'agglomération",
            "Y7EMPST": "Type d'emploi occupé",
            "Y7PCSIST": "Catégorie professionnelle",
            "Y7EDUST": "Niveau de scolarité atteint",
            "Y7REL1ST": "Religion",
            "Y7ECO2ST2": "Revenu mensuel du foyer",
            "Y7INTPOLST": "Intérêt pour la politique",
            "Y7Q7ST": "Positionnement idéologique",
            "Y7PROXST": "Préférence partisane"
        }
        # définir la question de l'enquête associée à la variable socio-démographique choisie
        dico_question_var = {
            "Y7SEXEST": "Êtes-vous ?",
            "Y7AGERST": "Quelle est votre date de naissance ?",
            "Y7REG13ST": "Veuillez indiquer le département et la commune où vous résidez.",
            "Y7AGGLO5ST": "Veuillez indiquer le département et la commune où vous résidez.",
            "Y7EMPST": "Quelle est votre situation professionnelle actuelle ?",
            "Y7PCSIST": "Quelle est votre situation professionnelle actuelle ?",
            "Y7EDUST": "Choisissez votre niveau de scolarité le plus élevé.",
            "Y7REL1ST": "Quelle est votre religion, si vous en avez une ?",
            "Y7ECO2ST2": " Pour finir, nous avons besoin de connaître, à des fins statistiques uniquement, la tranche dans laquelle se situe le revenu MENSUEL NET de votre FOYER après déduction des impôts sur le revenu (veuillez considérer toutes vos sources de revenus: salaires, bourses, prestations retraite et sécurité sociale, dividendes, revenus immobiliers, pensions alimentaires etc.).",
            "Y7INTPOLST": "De manière générale, diriez-vous que vous vous intéressez à la politique ?",
            "Y7Q7ST": "Sur une échelle de 0 à 10, où 0 correspond à la gauche et 10 correspond à la droite, où diriez-vous que vous vous situez ?",
            "Y7PROXST": "De quel parti vous sentez-vous proche ou moins éloigné que les autres ?"
        }
        # définir les modalités de réponse à la question de l'enquête associée à la variable socio-démographique choisie
        dico_modalite_var = {
            "Y7SEXEST": "1 = 'Homme' ; 2 = 'Femme'",
            "Y7AGERST": "1 = '18 à 24 ans' ; 2 = '25 à 34 ans' ; 3 = '35 à 49 ans' ; 4 = '50 à 59 ans' ; 5 = '60 ans et plus'",
            "Y7REG13ST": "1 = 'Ile de France' ; 2 = 'Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)' ; 3 = 'Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)' ; 4 = 'Sud ouest (Nouvelle Aquitaine et Occitanie)' ; 5 = 'Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)'",
            "Y7AGGLO5ST": "1 = 'Zone rurale (moins de 2 000 habitants)' ; 2 = 'Zone urbaine de 2 000 à 9 999 habitants' ; 3 = 'Zone urbaine de 10 000 à 49 999 habitants' ; 4 = 'Zone urbaine de 50 000 à 199 999 habitants' ; 5 = 'Zone urbaine de 200 000 habitants et plus'",
            "Y7EMPST": "1 = 'Salarié (salarié à plein temps ou à temps partiel)' ; 2 = 'Indépendant (travaille à mon compte)' ; 3 = 'Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)'",
            "Y7PCSIST": "1 = 'Agriculteur exploitant, artisan, commerçant, chef d entreprise' ; 2 = 'Cadre supérieur' ; 3 = 'Profession intermédiaire' ; 4 = 'Employé' ; 5 = 'Ouvrier' ; 6 = 'Retraité, inactif'",
            "Y7EDUST": "1 = 'Aucun diplôme' ; 2 = 'CAP, BEP' ; 3 = 'Baccalauréat' ; 4 = 'Bac +2' ; 5 = 'Bac +3 et plus'",
            "Y7REL1ST": "1 = 'Catholique' ; 2 = 'Juive' ; 3 = 'Musulmane' ; 4 = 'Autre religion (protestante, boudhiste ou autre)' ; 5 = 'Sans religion'",
            "Y7ECO2ST2": "1 = 'Moins de 1 250 euros' ; 2 = 'De 1 250 euros à 1 999 euros' ; 3 = 'De 2 000 à 3 499 euros' ; 4 = 'De 3 500 à 4 999 euros' ; 5 = '5 000 euros et plus'",
            "Y7INTPOLST": "1 = 'Beaucoup' ; 2 = 'Un peu' ; 3 = 'Pas vraiment' ; 4 = 'Pas du tout'",
            "Y7Q7ST": "1 = 'Très à gauche' ; 2 = 'Plutôt à gauche' ; 3 = 'Au centre' ; 4 = 'Plutôt à droite' ; 5 = 'Très à droite'",
            "Y7PROXST": "1 = 'Extême gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)' ; 2 = 'Gauche (Parti Socialiste, Europe Ecologie - Les Verts)' ; 3 = 'Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))' ; 4 = 'Droite (Les Républicains)' ; 5 = 'Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)' ; 6 = 'Autre parti ou aucun parti'"
        }
        # définir le texte complet à afficher (avec parties fixes et variables en fonction du choix effectué)
        m = ui.modal(
            "La variable '%s' correspond à ou est calculée à partir de la question suivante posée aux répondants : \
            '%s', \
            et ses modalités de réponse (inchangées par rapport au questionnaire ou regroupées pour les présents graphiques) sont : \
            %s." % (
                dico_nom_var.get(
                    "%s" % input.Select_VarSD_Part_Legis_T1()
                ),
                dico_question_var.get("%s" % input.Select_VarSD_Part_Legis_T1()),
                dico_modalite_var.get("%s" % input.Select_VarSD_Part_Legis_T1())
            ),
            title="Informations complémentaires sur la variable socio-démographique choisie :",
            easy_close=False
        )
        ui.modal_show(m)

    # graphique
    @output
    @render_plotly
    def Graph_Croise_Part_Legis_T1():
        # définir la partie variable du titre
        dico_titre = {
            "Y7SEXEST": "du genre",
            "Y7AGERST": "de l'âge",
            "Y7REG13ST": "de la région de résidence",
            "Y7AGGLO5ST": "de la taille de l'agglomération de résidence",
            "Y7EMPST": "du type d'emploi occupé",
            "Y7PCSIST": "de la catégorie socio-professionnelle",
            "Y7EDUST": "du niveau de scolarité atteint",
            "Y7REL1ST": "de la religion",
            "Y7ECO2ST2": "du revenu mensuel du foyer",
            "Y7INTPOLST": "de l'intérêt pour la politique",
            "Y7Q7ST": "du positionnement idéologique",
            "Y7PROXST": "de la préférence partisane"
        }
        # définir la partie variable du titre de la légende
        dico_legende = {
            "Y7SEXEST": "Genre",
            "Y7AGERST": "Âge",
            "Y7REG13ST": "Région",
            "Y7AGGLO5ST": "Taille d'agglomération",
            "Y7EMPST": "Type d'emploi occupé",
            "Y7PCSIST": "Catégorie professionnelle",
            "Y7EDUST": "Niveau de scolarité atteint",
            "Y7REL1ST": "Religion",
            "Y7ECO2ST2": "Revenu mensuel du foyer",
            "Y7INTPOLST": "Intérêt pour la politique",
            "Y7Q7ST": "Positionnement idéologique",
            "Y7PROXST": "Préférence partisane"
        }
        # définir l'échelle de l'axe des ordonnées en fonction des
        # valeurs prises par la variable socio-démographique choisie
        dico_echelleY = {
            "Y7SEXEST": [10, 40],
            "Y7AGERST": [10, 45],
            "Y7REG13ST": [15, 35],
            "Y7AGGLO5ST": [15, 35],
            "Y7EMPST": [15, 40],
            "Y7PCSIST": [10, 45],
            "Y7EDUST": [15, 40],
            "Y7REL1ST": [10, 45],
            "Y7ECO2ST2": [10, 45],
            "Y7INTPOLST": [0, 75],
            "Y7Q7ST": [5, 40],
            "Y7PROXST": [5, 55],
        }
        # définir les modalités des variables socio-démo et leur ordre
        dico_modalite_var = {
            "Y7SEXEST": "1 = 'Homme' ; 2 = 'Femme'",
            "Y7AGERST": "1 = '18 à 24 ans' ; 2 = '25 à 34 ans' ; 3 = '35 à 49 ans' ; 4 = '50 à 59 ans' ; 5 = '60 ans et plus'",
            "Y7REG13ST": "1 = 'Ile de France' ; 2 = 'Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)' ; 3 = 'Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)' ; 4 = 'Sud ouest (Nouvelle Aquitaine et Occitanie)' ; 5 = 'Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)'",
            "Y7AGGLO5ST": "1 = 'Zone rurale (moins de 2 000 habitants)' ; 2 = 'Zone urbaine de 2 000 à 9 999 habitants' ; 3 = 'Zone urbaine de 10 000 à 49 999 habitants' ; 4 = 'Zone urbaine de 50 000 à 199 999 habitants' ; 5 = 'Zone urbaine de 200 000 habitants et plus'",
            "Y7EMPST": "1 = 'Salarié (salarié à plein temps ou à temps partiel)' ; 2 = 'Indépendant (travaille à mon compte)' ; 3 = 'Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)'",
            "Y7PCSIST": "1 = 'Agriculteur exploitant, artisan, commerçant, chef d entreprise' ; 2 = 'Cadre supérieur' ; 3 = 'Profession intermédiaire' ; 4 = 'Employé' ; 5 = 'Ouvrier' ; 6 = 'Retraité, inactif'",
            "Y7EDUST": "1 = 'Aucun diplôme' ; 2 = 'CAP, BEP' ; 3 = 'Baccalauréat' ; 4 = 'Bac +2' ; 5 = 'Bac +3 et plus'",
            "Y7REL1ST": "1 = 'Catholique' ; 2 = 'Juive' ; 3 = 'Musulmane' ; 4 = 'Autre religion (protestante, boudhiste ou autre)' ; 5 = 'Sans religion'",
            "Y7ECO2ST2": "1 = 'Moins de 1 250 euros' ; 2 = 'De 1 250 euros à 1 999 euros' ; 3 = 'De 2 000 à 3 499 euros' ; 4 = 'De 3 500 à 4 999 euros' ; 5 = '5 000 euros et plus'",
            "Y7INTPOLST": "1 = 'Beaucoup' ; 2 = 'Un peu' ; 3 = 'Pas vraiment' ; 4 = 'Pas du tout'",
            "Y7Q7ST": "1 = 'Très à gauche' ; 2 = 'Plutôt à gauche' ; 3 = 'Au centre' ; 4 = 'Plutôt à droite' ; 5 = 'Très à droite'",
            "Y7PROXST": "1 = 'Très à gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)' ; 2 = 'Gauche (Parti Socialiste, Europe Ecologie - Les Verts)' ; 3 = 'Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))' ; 4 = 'Droite (Les Républicains)' ; 5 = 'Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)' ; 6 = 'Autre parti ou aucun parti'"
        }
        # définir un dictionnaire qui contient l'ordre figé des modalités pour chaque variable socio-démographique
        dico_ordre_modalites = {
            "Y7SEXEST": [
                "Homme",
                "Femme"
            ],
            "Y7AGERST": [
                "18 à 24 ans",
                "25 à 34 ans",
                "35 à 49 ans",
                "50 à 59 ans",
                "60 ans et plus"
            ],
            "Y7REG13ST": [
                "Ile de France",
                "Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)",
                "Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)",
                "Sud ouest (Nouvelle Aquitaine et Occitanie)",
                "Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)"
            ],
            "Y7AGGLO5ST": [
                "Zone rurale (moins de 2 000 habitants)",
                "Zone urbaine de 2 000 à 9 999 habitants",
                "Zone urbaine de 10 000 à 49 999 habitants",
                "Zone urbaine de 50 000 à 199 999 habitants",
                "Zone urbaine de 200 000 habitants et plus"
            ],
            "Y7EMPST": [
                "Salarié (salarié à plein temps ou à temps partiel)",
                "Indépendant (travaille à mon compte)",
                "Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)"
            ],
            "Y7PCSIST": [
                "Agriculteur exploitant, artisan, commerçant, chef d entreprise",
                "Cadre supérieur",
                "Profession intermédiaire",
                "Employé",
                "Ouvrier",
                "Retraité, inactif"
            ],
            "Y7EDUST": [
                "Aucun diplôme",
                "CAP, BEP",
                "Baccalauréat",
                "Bac +2",
                "Bac +3 et plus"
            ],
            "Y7REL1ST": [
                "Catholique",
                "Juive",
                "Musulmane",
                "Autre religion (protestante, boudhiste ou autre)",
                "Sans religion"
            ],
            "Y7ECO2ST2": [
                "Moins de 1 250 euros",
                "De 1 250 euros à 1 999 euros",
                "De 2 000 à 3 499 euros",
                "De 3 500 à 4 999 euros",
                "5 000 euros et plus"
            ],
            "Y7INTPOLST": [
                "Beaucoup",
                "Un peu",
                "Pas vraiment",
                "Pas du tout"
            ],
            "Y7Q7ST": [
                "Très à gauche",
                "Plutôt à gauche",
                "Au centre",
                "Plutôt à droite",
                "Très à droite"
            ],
            "Y7PROXST": [
                "Très à gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)",
                "Gauche (Parti Socialiste, Europe Ecologie - Les Verts)",
                "Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))",
                "Droite (Les Républicains)",
                "Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)",
                "Autre parti ou aucun parti"
            ]
        }
        # définir une fonction qui affiche les étiquettes
        # des modalités de la variablr SD choisie dans la légende
        # sur plusieurs lignes si leur longueur initiale dépasse la
        # largeur du cadre de la légende (version robuste avec gestion des erreurs)
        def wrap_label(label, max_length=20):
            try:
                # Si le label est un float ou NaN
                if pd.isna(label) or isinstance(label, float):
                    return "Non renseigné"
                # Convertir en string si ce n'est pas déjà le cas
                label = str(label).strip()
                # Si la chaîne est vide après nettoyage
                if not label:
                    return "Non renseigné"
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
            except Exception as e:
                print(f"Erreur dans wrap_label avec {label}: {str(e)}")
                return str(label) 
                # retourner le label tel quel en cas d'erreur
        # lire le fichier CSV des données
        csvfile = "data/T_w7_partl24ast_" + "%s" % input.Select_VarSD_Part_Legis_T1().lower()[2:] + ".csv"
        df = pd.read_csv(csvfile)
        # nettoyer les données lues
        var_sd = input.Select_VarSD_Part_Legis_T1()
        df[var_sd] = df[var_sd].fillna("Non renseigné")  # Gérer les NaN
        df[var_sd] = df[var_sd].astype(str)  # Convertir en string
        df['Y7PARTL24AST'] = df['Y7PARTL24AST'].fillna("Non renseigné")
        # s'assurer que toutes les modalités sont des chaînes de caractères dans "dico_ordre_modalites"
        dico_ordre_modalites[var_sd] = [str(modal) for modal in dico_ordre_modalites[var_sd]]
        # filtrer pour ne garder que les modalités définies dans "dico_ordre_modalites"
        df = df[df[var_sd].isin(dico_ordre_modalites[var_sd])]
        # définir l'ordre des modalités pour Y7PARTL24AST
        ordre_modalites = [
            "Vous avez voté",
            "Vous n'avez pas voté"
        ]
        # créer une colonne catégorielle avec l'ordre souhaité pour la variable socio-démographique
        var_sd = input.Select_VarSD_Part_Legis_T1()
        df[var_sd] = pd.Categorical(
            df[var_sd],
            categories=dico_ordre_modalites[var_sd],
            ordered=True
        )
        # filtrer et pivoter les données
        df_pivot = df[df['Y7PARTL24AST'].isin(ordre_modalites)].pivot(
            index=var_sd,
            columns='Y7PARTL24AST',
            values='pct'
        )
        df_pivot = df_pivot.reindex(columns=ordre_modalites)
        # créer une palette de couleurs automatique
        nb_couleurs = len(df_pivot.index)
        palette = px.colors.qualitative.Plotly[:nb_couleurs]
        # créer le graphique
        fig = go.Figure()
        # ajouter les données
        for i, VarSD in enumerate(df_pivot.index):
            fig.add_trace(
                go.Bar(
                    x=ordre_modalites,
                    y=df_pivot.loc[VarSD],
                    name=wrap_label(VarSD),
                    marker_color=palette[i],
                    # afficher les valeurs sous le format 'xx.x%' dans la bulle qui s'affiche
                    # au survol de la courbe par la souris, et supprimer toutes les autres
                    # informations qui pourraient s'afficher en plus (nom de la modalité)
                    hovertemplate='%{y:.1f}%<extra></extra>',
                    # n'afficher la bulle contenant la valeur 'y' en % uniquement
                    # au-dessus de la barre verticale survolée par la souris
                    hoverinfo='y',
                    # centrer ce texte 'y' dans la bulle
                    hoverlabel=dict(
                        align='auto'
                    )
                )
            )
         # mettre en forme le graphique
        fig.update_layout(
            barmode='group', # barres séparées et groupées pour les modalités de la VarSD choisie
            title={
                'text': "Participation au vote en fonction %s" % dico_titre.get("%s" % input.Select_VarSD_Part_Legis_T1()),
                'y':0.98,
                'x':0.01,
                'xanchor': 'left',
                'yanchor': 'top'
            },
            # définir le titre de la légende
            legend_title="%s" % dico_legende.get("%s" % input.Select_VarSD_Part_Legis_T1()),
            # définir l'affichage séparé des valeurs de % affichées au-dessus de
            # chaque barre verticale quand la souris la survole
            hovermode="closest",
            # définir le thème général de l'apparence du graphique
            template="plotly_white",
            # définir le titre de l'axe des ordonnées et son apparence
            yaxis_title=dict(
                text='Pourcentage de répondants (%)',
                font_size=12
            ),
            # définir les sources des données
            annotations=[
                dict(
                    xref='paper', # utiliser la largeur totale du graphique comme référence
                    yref='paper', # utiliser la hauteur totale du graphique comme référence
                    x=0.5, # placer le point d'ancrage au milieu de la largeur
                    y=-0.1, # valeur à ajuster pour positionner verticalement le texte sous le graphique
                    xanchor='center', # centrer le texte par rapport au point d'ancrage
                    yanchor='top',
                    text=
                        'Enquête électorale française pour les ' +
                        'élections européennes de juin 2024, ' +
                        'par Ipsos Sopra Steria, Cevipof, ' +
                        'Le Monde, Fondation Jean Jaurès et ' +
                        'Institut Montaigne (2024)',
                    font=dict(
                        size=10,
                        color='grey'
                    ),
                    showarrow=False
                )
            ],
            # définir les marges de la zone graphique
            # (augmentées à droite pour le cadre fixe de la légende)
            margin=dict(
                b=50, # b = bottom
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
            ),
        )
        # retourner le graphique
        return fig



    ########################################################################
    # onglet 02 : VOTE POUR LES CANDIDATS (couleurs politiques) (1er tour) #
    ########################################################################

    # bouton 01 : décrire la question posée dans l'enquête
    @reactive.effect
    @reactive.event(input.Show_CAND_Question_Legis_T1)
    def _():
        m = ui.modal(
            "La question posée aux répondants est la suivante : 'Pour quel candidat avez-vous voté au premier tour des élections législatives dans votre circonscription ?'",
            title="Informations complémentaires sur la question contenue dans l'enquête :",
            easy_close=False
        )
        ui.modal_show(m)

    # bouton 02 : décrire la variable
    @reactive.effect
    @reactive.event(input.Show_CAND_Info_Legis_T1)
    def _():
        m = ui.modal(
            "La variable sur la couleur politique du candidat ayant reçu le vote du répondant contient à l'origine 12 modalités. \
            La variable du vote en faveur de la couleur politique du candidat présentée ici sur les graphiques est simplifiée : \
            seules les 4 couleurs politiques ayant récolté le plus de suffrages sont retenues. \
            Ainsi, les modalités de réponse synthétiques retenues pour cette variable sont les suivantes : \
            1 = 'Rassemblement national (RN)', \
            2 = 'Nouveau Front Populaire (NFP)', \
            3 = 'Ensemble', \
            4 = 'Les Républicains (LR) / Divers Droite (DVD)'.",
            title="Informations complémentaires sur la variable choisie pour les graphiques :",
            easy_close=False
        )
        ui.modal_show(m)

    # graphique
    @output
    @render_plotly
    def Graph_Cand_Legis_T1():
        # importer les données
        csvfile = "data/T_w7_leg24axst.csv"
        data = pd.read_csv(csvfile)
        # supprimer la première colonne (vide) de la base de donnée
        data = data.drop(
            data.columns[0],
            axis=1
        )
        # identifier les étiquettes courtes (chiffres démarrant à 1)
        data['ETIQCOURTE'] = data.index + 1
        etiquettes_courtes = data["ETIQCOURTE"]
        # identifier les étiquettes longues (modalités de la variable dans la table lue)
        etiquettes_longues = data["LEG24AXST"]
        # créer la figure en mémoire
        fig = go.Figure()
        # créer la liste des couleurs en fonction du nombre de modalités
        couleurs_cl = cl.scales[str(max(3, len(data["LEG24AXST"])))]['qual']['Set1']
        # ajouter les données
        fig.add_trace(
            go.Bar(
                # on représente la colonne des étiquettes courtes (et non la variable elle-même, car
                # cette colonne correspond aux étiquettes longues de la légende)
                x=data["ETIQCOURTE"],
                y=data["pct"],
                # changer de couleur en fonction de la modalité de réponse
                marker_color=couleurs_cl,
                # afficher les valeurs sous le format 'xx.x%' dans la bulle qui s'affiche
                # au survol de la courbe par la souris, et supprimer toutes les autres
                # informations qui pourraient s'afficher en plus (nom de la modalité)
                hovertemplate='%{y:.1f}%<extra></extra>',
                # n'afficher la bulle contenant la valeur 'y' en % uniquement
                # au-dessus de la barre verticale survolée par la souris
                hoverinfo='y',
                # centrer ce texte 'y' dans la bulle
                hoverlabel=dict(
                    align='auto'
                )
            )
        )
        # créer le texte de la légende (correspondance entre les étiquettes courtes et les étiquettes longues)
        legende_text = "<br>".join([f"{lettre}: {etiquette}" for lettre, etiquette in zip(etiquettes_courtes, etiquettes_longues)])
        # mettre en forme le graphique
        fig.update_layout(
            # définir le titre du graphique et son apparence
            title={
                'text': "Vote en faveur des candidats (couleurs politiques)",
                'y':0.98,
                'x':0.01,
                'xanchor': 'left',
                'yanchor': 'top'
            },
            # définir le titre de l'axe des ordonnées et son apparence
            yaxis_title=dict(
                text='Pourcentage de répondants (%)',
                font_size=12
            ),
            # définir l'affichage séparé des valeurs de % affichées au-dessus de
            # chaque barre verticale quand la souris la survole
            hovermode="closest",
            # définir le thème général de l'apparence du graphique
            template="plotly_white",
            # définir deux annotations
            annotations=[
                # sources des données
                dict(
                    xref='paper', # utiliser la largeur totale du graphique comme référence
                    yref='paper', # utiliser la hauteur totale du graphique comme référence
                    x=0.5, # placer le point d'ancrage au milieu de la largeur
                    y=-0.1, # valeur à ajuster pour positionner verticalement le texte sous le graphique
                    xanchor='center', # centrer le texte par rapport au point d'ancrage
                    yanchor='top',
                    text=
                        'Enquête électorale française pour les ' +
                        'élections européennes de juin 2024, ' +
                        'par Ipsos Sopra Steria, Cevipof, ' +
                        'Le Monde, Fondation Jean Jaurès et ' +
                        'Institut Montaigne (2024)',
                    font=dict(
                        size=10,
                        color='grey'
                    ),
                    showarrow=False
                ),
                # légende personnalisée
                dict(
                    valign="top", # aligner le texte en haut de chaque marqueur de la légende
                    x=0.75, # position horizontale de la légende (1 = à droite du graphique)
                    y=1.00, # position verticale de la légende (1 = en haut)
                    xref='paper',
                    yref='paper',
                    xanchor='left', # ancrer la légende à gauche de sa position x
                    yanchor='top', # ancrer la légende en haut de sa position y
                    text=f"<b>Légende :</b><br>{legende_text}",
                    showarrow=False,
                    font=dict(size=12),
                    align='left',
                    bgcolor='rgba(255,255,255,0.8)', # fond légèrement transparent
                )
            ],
            # définir les marges de la zone graphique
            # (augmentées à droite pour le cadre fixe de la légende)
            margin=dict(
                b=50, # b = bottom
                t=50,  # t = top
                l=50, # l = left
                r=200 # r = right
            )
        )
        # configurer l'axe des abscisses pour n'afficher que des nombres entiers
        fig.update_xaxes(
            tickmode='linear',
            tick0=1,
            dtick=1,
            tickfont=dict(size=12),
            tickangle=0
        )

        # retourner le graphique
        return fig


    ########################################
    # onglet 03 : PARTICIPATION (2e tour)  #
    ########################################

    # bouton 01 : décrire la question posée dans l'enquête
    @reactive.effect
    @reactive.event(input.Show_PART_Question_Legis_T2)
    def _():
        m = ui.modal(
            "La question posée aux répondants est la suivante : 'Un électeur sur trois n’a pas voté au second tour des élections législatives le 7 juillet 2024. Dans votre cas personnel, qu’est ce qui correspond le mieux à votre attitude à cette occasion ?'",
            title="Informations complémentaires sur la question contenue dans l'enquête :",
            easy_close=False
        )
        ui.modal_show(m)

    # bouton 02 : décrire la variable de l'intention d'aller voter choisie
    @reactive.effect
    @reactive.event(input.Show_PARTST_Info_Legis_T2)
    def _():
        m = ui.modal(
            "La variable sur la participation aux élections législatives présentée ici sur les graphiques est une modalité synthétique de la question posée aux répondants de l'enquête. \
            Ainsi, à partir des quatre modalités de réponse à la question de l'enquête, on en construit deux : 'Vous avez voté' ou 'Vous n'avez pas voté'.",
            title="Informations complémentaires sur la variable choisie pour les graphiques :",
            easy_close=False
        )
        ui.modal_show(m)

    # bouton 03 : afficher la description de la variable socio-démographique choisie
    # avec plusieurs parties de texte qui dépendent de ce choix (via des dictionnaires)
    @reactive.effect
    @reactive.event(input.Show_VarSD_Part_Info_Legis_T2)
    def _():
        # définir le nom de la variable socio-démographique choisie
        dico_nom_var = {
            "Y7SEXEST": "Genre",
            "Y7AGERST": "Âge",
            "Y7REG13ST": "Région",
            "Y7AGGLO5ST": "Taille d'agglomération",
            "Y7EMPST": "Type d'emploi occupé",
            "Y7PCSIST": "Catégorie professionnelle",
            "Y7EDUST": "Niveau de scolarité atteint",
            "Y7REL1ST": "Religion",
            "Y7ECO2ST2": "Revenu mensuel du foyer",
            "Y7INTPOLST": "Intérêt pour la politique",
            "Y7Q7ST": "Positionnement idéologique",
            "Y7PROXST": "Préférence partisane"
        }
        # définir la question de l'enquête associée à la variable socio-démographique choisie
        dico_question_var = {
            "Y7SEXEST": "Êtes-vous ?",
            "Y7AGERST": "Quelle est votre date de naissance ?",
            "Y7REG13ST": "Veuillez indiquer le département et la commune où vous résidez.",
            "Y7AGGLO5ST": "Veuillez indiquer le département et la commune où vous résidez.",
            "Y7EMPST": "Quelle est votre situation professionnelle actuelle ?",
            "Y7PCSIST": "Quelle est votre situation professionnelle actuelle ?",
            "Y7EDUST": "Choisissez votre niveau de scolarité le plus élevé.",
            "Y7REL1ST": "Quelle est votre religion, si vous en avez une ?",
            "Y7ECO2ST2": " Pour finir, nous avons besoin de connaître, à des fins statistiques uniquement, la tranche dans laquelle se situe le revenu MENSUEL NET de votre FOYER après déduction des impôts sur le revenu (veuillez considérer toutes vos sources de revenus: salaires, bourses, prestations retraite et sécurité sociale, dividendes, revenus immobiliers, pensions alimentaires etc.).",
            "Y7INTPOLST": "De manière générale, diriez-vous que vous vous intéressez à la politique ?",
            "Y7Q7ST": "Sur une échelle de 0 à 10, où 0 correspond à la gauche et 10 correspond à la droite, où diriez-vous que vous vous situez ?",
            "Y7PROXST": "De quel parti vous sentez-vous proche ou moins éloigné que les autres ?"
        }
        # définir les modalités de réponse à la question de l'enquête associée à la variable socio-démographique choisie
        dico_modalite_var = {
            "Y7SEXEST": "1 = 'Homme' ; 2 = 'Femme'",
            "Y7AGERST": "1 = '18 à 24 ans' ; 2 = '25 à 34 ans' ; 3 = '35 à 49 ans' ; 4 = '50 à 59 ans' ; 5 = '60 ans et plus'",
            "Y7REG13ST": "1 = 'Ile de France' ; 2 = 'Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)' ; 3 = 'Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)' ; 4 = 'Sud ouest (Nouvelle Aquitaine et Occitanie)' ; 5 = 'Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)'",
            "Y7AGGLO5ST": "1 = 'Zone rurale (moins de 2 000 habitants)' ; 2 = 'Zone urbaine de 2 000 à 9 999 habitants' ; 3 = 'Zone urbaine de 10 000 à 49 999 habitants' ; 4 = 'Zone urbaine de 50 000 à 199 999 habitants' ; 5 = 'Zone urbaine de 200 000 habitants et plus'",
            "Y7EMPST": "1 = 'Salarié (salarié à plein temps ou à temps partiel)' ; 2 = 'Indépendant (travaille à mon compte)' ; 3 = 'Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)'",
            "Y7PCSIST": "1 = 'Agriculteur exploitant, artisan, commerçant, chef d entreprise' ; 2 = 'Cadre supérieur' ; 3 = 'Profession intermédiaire' ; 4 = 'Employé' ; 5 = 'Ouvrier' ; 6 = 'Retraité, inactif'",
            "Y7EDUST": "1 = 'Aucun diplôme' ; 2 = 'CAP, BEP' ; 3 = 'Baccalauréat' ; 4 = 'Bac +2' ; 5 = 'Bac +3 et plus'",
            "Y7REL1ST": "1 = 'Catholique' ; 2 = 'Juive' ; 3 = 'Musulmane' ; 4 = 'Autre religion (protestante, boudhiste ou autre)' ; 5 = 'Sans religion'",
            "Y7ECO2ST2": "1 = 'Moins de 1 250 euros' ; 2 = 'De 1 250 euros à 1 999 euros' ; 3 = 'De 2 000 à 3 499 euros' ; 4 = 'De 3 500 à 4 999 euros' ; 5 = '5 000 euros et plus'",
            "Y7INTPOLST": "1 = 'Beaucoup' ; 2 = 'Un peu' ; 3 = 'Pas vraiment' ; 4 = 'Pas du tout'",
            "Y7Q7ST": "1 = 'Très à gauche' ; 2 = 'Plutôt à gauche' ; 3 = 'Au centre' ; 4 = 'Plutôt à droite' ; 5 = 'Très à droite'",
            "Y7PROXST": "1 = 'Extême gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)' ; 2 = 'Gauche (Parti Socialiste, Europe Ecologie - Les Verts)' ; 3 = 'Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))' ; 4 = 'Droite (Les Républicains)' ; 5 = 'Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)' ; 6 = 'Autre parti ou aucun parti'"
        }
        # définir le texte complet à afficher (avec parties fixes et variables en fonction du choix effectué)
        m = ui.modal(
            "La variable '%s' correspond à ou est calculée à partir de la question suivante posée aux répondants : \
            '%s', \
            et ses modalités de réponse (inchangées par rapport au questionnaire ou regroupées pour les présents graphiques) sont : \
            %s." % (
                dico_nom_var.get(
                    "%s" % input.Select_VarSD_Part_Legis_T2()
                ),
                dico_question_var.get("%s" % input.Select_VarSD_Part_Legis_T2()),
                dico_modalite_var.get("%s" % input.Select_VarSD_Part_Legis_T2())
            ),
            title="Informations complémentaires sur la variable socio-démographique choisie :",
            easy_close=False
        )
        ui.modal_show(m)

    # graphique
    @output
    @render_plotly
    def Graph_Croise_Part_Legis_T2():
        # définir la partie variable du titre
        dico_titre = {
            "Y7SEXEST": "du genre",
            "Y7AGERST": "de l'âge",
            "Y7REG13ST": "de la région de résidence",
            "Y7AGGLO5ST": "de la taille de l'agglomération de résidence",
            "Y7EMPST": "du type d'emploi occupé",
            "Y7PCSIST": "de la catégorie socio-professionnelle",
            "Y7EDUST": "du niveau de scolarité atteint",
            "Y7REL1ST": "de la religion",
            "Y7ECO2ST2": "du revenu mensuel du foyer",
            "Y7INTPOLST": "de l'intérêt pour la politique",
            "Y7Q7ST": "du positionnement idéologique",
            "Y7PROXST": "de la préférence partisane"
        }
        # définir la partie variable du titre de la légende
        dico_legende = {
            "Y7SEXEST": "Genre",
            "Y7AGERST": "Âge",
            "Y7REG13ST": "Région",
            "Y7AGGLO5ST": "Taille d'agglomération",
            "Y7EMPST": "Type d'emploi occupé",
            "Y7PCSIST": "Catégorie professionnelle",
            "Y7EDUST": "Niveau de scolarité atteint",
            "Y7REL1ST": "Religion",
            "Y7ECO2ST2": "Revenu mensuel du foyer",
            "Y7INTPOLST": "Intérêt pour la politique",
            "Y7Q7ST": "Positionnement idéologique",
            "Y7PROXST": "Préférence partisane"
        }
        # définir l'échelle de l'axe des ordonnées en fonction des
        # valeurs prises par la variable socio-démographique choisie
        dico_echelleY = {
            "Y7SEXEST": [10, 40],
            "Y7AGERST": [10, 45],
            "Y7REG13ST": [15, 35],
            "Y7AGGLO5ST": [15, 35],
            "Y7EMPST": [15, 40],
            "Y7PCSIST": [10, 45],
            "Y7EDUST": [15, 40],
            "Y7REL1ST": [10, 45],
            "Y7ECO2ST2": [10, 45],
            "Y7INTPOLST": [0, 75],
            "Y7Q7ST": [5, 40],
            "Y7PROXST": [5, 55],
        }
        # définir les modalités des variables socio-démo et leur ordre
        dico_modalite_var = {
            "Y7SEXEST": "1 = 'Homme' ; 2 = 'Femme'",
            "Y7AGERST": "1 = '18 à 24 ans' ; 2 = '25 à 34 ans' ; 3 = '35 à 49 ans' ; 4 = '50 à 59 ans' ; 5 = '60 ans et plus'",
            "Y7REG13ST": "1 = 'Ile de France' ; 2 = 'Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)' ; 3 = 'Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)' ; 4 = 'Sud ouest (Nouvelle Aquitaine et Occitanie)' ; 5 = 'Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)'",
            "Y7AGGLO5ST": "1 = 'Zone rurale (moins de 2 000 habitants)' ; 2 = 'Zone urbaine de 2 000 à 9 999 habitants' ; 3 = 'Zone urbaine de 10 000 à 49 999 habitants' ; 4 = 'Zone urbaine de 50 000 à 199 999 habitants' ; 5 = 'Zone urbaine de 200 000 habitants et plus'",
            "Y7EMPST": "1 = 'Salarié (salarié à plein temps ou à temps partiel)' ; 2 = 'Indépendant (travaille à mon compte)' ; 3 = 'Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)'",
            "Y7PCSIST": "1 = 'Agriculteur exploitant, artisan, commerçant, chef d entreprise' ; 2 = 'Cadre supérieur' ; 3 = 'Profession intermédiaire' ; 4 = 'Employé' ; 5 = 'Ouvrier' ; 6 = 'Retraité, inactif'",
            "Y7EDUST": "1 = 'Aucun diplôme' ; 2 = 'CAP, BEP' ; 3 = 'Baccalauréat' ; 4 = 'Bac +2' ; 5 = 'Bac +3 et plus'",
            "Y7REL1ST": "1 = 'Catholique' ; 2 = 'Juive' ; 3 = 'Musulmane' ; 4 = 'Autre religion (protestante, boudhiste ou autre)' ; 5 = 'Sans religion'",
            "Y7ECO2ST2": "1 = 'Moins de 1 250 euros' ; 2 = 'De 1 250 euros à 1 999 euros' ; 3 = 'De 2 000 à 3 499 euros' ; 4 = 'De 3 500 à 4 999 euros' ; 5 = '5 000 euros et plus'",
            "Y7INTPOLST": "1 = 'Beaucoup' ; 2 = 'Un peu' ; 3 = 'Pas vraiment' ; 4 = 'Pas du tout'",
            "Y7Q7ST": "1 = 'Très à gauche' ; 2 = 'Plutôt à gauche' ; 3 = 'Au centre' ; 4 = 'Plutôt à droite' ; 5 = 'Très à droite'",
            "Y7PROXST": "1 = 'Très à gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)' ; 2 = 'Gauche (Parti Socialiste, Europe Ecologie - Les Verts)' ; 3 = 'Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))' ; 4 = 'Droite (Les Républicains)' ; 5 = 'Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)' ; 6 = 'Autre parti ou aucun parti'"
        }
        # définir un dictionnaire qui contient l'ordre figé des modalités pour chaque variable socio-démographique
        dico_ordre_modalites = {
            "Y7SEXEST": [
                "Homme",
                "Femme"
            ],
            "Y7AGERST": [
                "18 à 24 ans",
                "25 à 34 ans",
                "35 à 49 ans",
                "50 à 59 ans",
                "60 ans et plus"
            ],
            "Y7REG13ST": [
                "Ile de France",
                "Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)",
                "Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)",
                "Sud ouest (Nouvelle Aquitaine et Occitanie)",
                "Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)"
            ],
            "Y7AGGLO5ST": [
                "Zone rurale (moins de 2 000 habitants)",
                "Zone urbaine de 2 000 à 9 999 habitants",
                "Zone urbaine de 10 000 à 49 999 habitants",
                "Zone urbaine de 50 000 à 199 999 habitants",
                "Zone urbaine de 200 000 habitants et plus"
            ],
            "Y7EMPST": [
                "Salarié (salarié à plein temps ou à temps partiel)",
                "Indépendant (travaille à mon compte)",
                "Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)"
            ],
            "Y7PCSIST": [
                "Agriculteur exploitant, artisan, commerçant, chef d entreprise",
                "Cadre supérieur",
                "Profession intermédiaire",
                "Employé",
                "Ouvrier",
                "Retraité, inactif"
            ],
            "Y7EDUST": [
                "Aucun diplôme",
                "CAP, BEP",
                "Baccalauréat",
                "Bac +2",
                "Bac +3 et plus"
            ],
            "Y7REL1ST": [
                "Catholique",
                "Juive",
                "Musulmane",
                "Autre religion (protestante, boudhiste ou autre)",
                "Sans religion"
            ],
            "Y7ECO2ST2": [
                "Moins de 1 250 euros",
                "De 1 250 euros à 1 999 euros",
                "De 2 000 à 3 499 euros",
                "De 3 500 à 4 999 euros",
                "5 000 euros et plus"
            ],
            "Y7INTPOLST": [
                "Beaucoup",
                "Un peu",
                "Pas vraiment",
                "Pas du tout"
            ],
            "Y7Q7ST": [
                "Très à gauche",
                "Plutôt à gauche",
                "Au centre",
                "Plutôt à droite",
                "Très à droite"
            ],
            "Y7PROXST": [
                "Très à gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)",
                "Gauche (Parti Socialiste, Europe Ecologie - Les Verts)",
                "Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))",
                "Droite (Les Républicains)",
                "Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)",
                "Autre parti ou aucun parti"
            ]
        }
        # définir une fonction qui affiche les étiquettes
        # des modalités de la variablr SD choisie dans la légende
        # sur plusieurs lignes si leur longueur initiale dépasse la
        # largeur du cadre de la légende (version robuste avec gestion des erreurs)
        def wrap_label(label, max_length=20):
            try:
                # Si le label est un float ou NaN
                if pd.isna(label) or isinstance(label, float):
                    return "Non renseigné"
                # Convertir en string si ce n'est pas déjà le cas
                label = str(label).strip()
                # Si la chaîne est vide après nettoyage
                if not label:
                    return "Non renseigné"
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
            except Exception as e:
                print(f"Erreur dans wrap_label avec {label}: {str(e)}")
                return str(label) 
                # retourner le label tel quel en cas d'erreur
        # lire le fichier CSV des données
        csvfile = "data/T_w7_partl24bst_" + "%s" % input.Select_VarSD_Part_Legis_T2().lower()[2:] + ".csv"
        df = pd.read_csv(csvfile)
        # nettoyer les données lues
        var_sd = input.Select_VarSD_Part_Legis_T2()
        df[var_sd] = df[var_sd].fillna("Non renseigné")  # Gérer les NaN
        df[var_sd] = df[var_sd].astype(str)  # Convertir en string
        df['Y7PARTL24BST'] = df['Y7PARTL24BST'].fillna("Non renseigné")
        # s'assurer que toutes les modalités sont des chaînes de caractères dans "dico_ordre_modalites"
        dico_ordre_modalites[var_sd] = [str(modal) for modal in dico_ordre_modalites[var_sd]]
        # filtrer pour ne garder que les modalités définies dans "dico_ordre_modalites"
        df = df[df[var_sd].isin(dico_ordre_modalites[var_sd])]
        # définir l'ordre des modalités pour Y7PARTL24BST
        ordre_modalites = [
            "Vous avez voté",
            "Vous n'avez pas voté"
        ]
        # créer une colonne catégorielle avec l'ordre souhaité pour la variable socio-démographique
        var_sd = input.Select_VarSD_Part_Legis_T2()
        df[var_sd] = pd.Categorical(
            df[var_sd],
            categories=dico_ordre_modalites[var_sd],
            ordered=True
        )
        # filtrer et pivoter les données
        df_pivot = df[df['Y7PARTL24BST'].isin(ordre_modalites)].pivot(
            index=var_sd,
            columns='Y7PARTL24BST',
            values='pct'
        )
        df_pivot = df_pivot.reindex(columns=ordre_modalites)
        # créer une palette de couleurs automatique
        nb_couleurs = len(df_pivot.index)
        palette = px.colors.qualitative.Plotly[:nb_couleurs]
        # créer le graphique
        fig = go.Figure()
        # ajouter les données
        for i, VarSD in enumerate(df_pivot.index):
            fig.add_trace(
                go.Bar(
                    x=ordre_modalites,
                    y=df_pivot.loc[VarSD],
                    name=wrap_label(VarSD),
                    marker_color=palette[i],
                    # afficher les valeurs sous le format 'xx.x%' dans la bulle qui s'affiche
                    # au survol de la courbe par la souris, et supprimer toutes les autres
                    # informations qui pourraient s'afficher en plus (nom de la modalité)
                    hovertemplate='%{y:.1f}%<extra></extra>',
                    # n'afficher la bulle contenant la valeur 'y' en % uniquement
                    # au-dessus de la barre verticale survolée par la souris
                    hoverinfo='y',
                    # centrer ce texte 'y' dans la bulle
                    hoverlabel=dict(
                        align='auto'
                    )
                )
            )
         # mettre en forme le graphique
        fig.update_layout(
            barmode='group', # barres séparées et groupées pour les modalités de la VarSD choisie
            title={
                'text': "Participation au vote en fonction %s" % dico_titre.get("%s" % input.Select_VarSD_Part_Legis_T2()),
                'y':0.98,
                'x':0.01,
                'xanchor': 'left',
                'yanchor': 'top'
            },
            # définir le titre de la légende
            legend_title="%s" % dico_legende.get("%s" % input.Select_VarSD_Part_Legis_T2()),
            # définir l'affichage séparé des valeurs de % affichées au-dessus de
            # chaque barre verticale quand la souris la survole
            hovermode="closest",
            # définir le thème général de l'apparence du graphique
            template="plotly_white",
            # définir le titre de l'axe des ordonnées et son apparence
            yaxis_title=dict(
                text='Pourcentage de répondants (%)',
                font_size=12
            ),
            # définir les sources des données
            annotations=[
                dict(
                    xref='paper', # utiliser la largeur totale du graphique comme référence
                    yref='paper', # utiliser la hauteur totale du graphique comme référence
                    x=0.5, # placer le point d'ancrage au milieu de la largeur
                    y=-0.1, # valeur à ajuster pour positionner verticalement le texte sous le graphique
                    xanchor='center', # centrer le texte par rapport au point d'ancrage
                    yanchor='top',
                    text=
                        'Enquête électorale française pour les ' +
                        'élections européennes de juin 2024, ' +
                        'par Ipsos Sopra Steria, Cevipof, ' +
                        'Le Monde, Fondation Jean Jaurès et ' +
                        'Institut Montaigne (2024)',
                    font=dict(
                        size=10,
                        color='grey'
                    ),
                    showarrow=False
                )
            ],
            # définir les marges de la zone graphique
            # (augmentées à droite pour le cadre fixe de la légende)
            margin=dict(
                b=50, # b = bottom
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
            ),
        )
        # retourner le graphique
        return fig


    ########################################################################
    # onglet 04 : VOTE POUR LES CANDIDATS (couleurs politiques) (2e tour)  #
    ########################################################################

    # bouton 01 : décrire la question posée dans l'enquête
    @reactive.effect
    @reactive.event(input.Show_CAND_Question_Legis_T2)
    def _():
        m = ui.modal(
            "La question posée aux répondants est la suivante : 'Voici les candidats qui se présentaient au second tour des élections législatives dans votre circonscription. Pouvez-vous dire celui pour lequel vous avez voté ?'",
            title="Informations complémentaires sur la question contenue dans l'enquête :",
            easy_close=False
        )
        ui.modal_show(m)

    # bouton 02 : décrire la variable
    @reactive.effect
    @reactive.event(input.Show_CAND_Info_Legis_T2)
    def _():
        m = ui.modal(
            "La variable sur la couleur politique du candidat ayant reçu le vote du répondant contient à l'origine 7 modalités. \
            La variable du vote en faveur de la couleur politique du candidat présentée ici sur les graphiques est simplifiée : \
            seules les 4 couleurs politiques ayant récolté le plus de suffrages sont retenues. \
            Ainsi, les modalités de réponse synthétiques retenues pour cette variable sont les suivantes : \
            1 = 'Rassemblement national (RN) et alliés', \
            2 = 'Ensemble', \
            3 = 'Nouveau Front Populaire (NFP)', \
            4 = 'Les Républicains (LR) / Divers Droite (DVD)'.",
            title="Informations complémentaires sur la variable choisie pour les graphiques :",
            easy_close=False
        )
        ui.modal_show(m)

    # graphique
    @output
    @render_plotly
    def Graph_Cand_Legis_T2():
        # importer les données
        csvfile = "data/T_w7_leg24bxst.csv"
        data = pd.read_csv(csvfile)
        # supprimer la première colonne (vide) de la base de donnée
        data = data.drop(
            data.columns[0],
            axis=1
        )
        # identifier les étiquettes courtes (chiffres démarrant à 1)
        data['ETIQCOURTE'] = data.index + 1
        etiquettes_courtes = data["ETIQCOURTE"]
        # identifier les étiquettes longues (modalités de la variable dans la table lue)
        etiquettes_longues = data["LEG24BXST"]
        # créer la figure en mémoire
        fig = go.Figure()
        # créer la liste des couleurs en fonction du nombre de modalités
        couleurs_cl = cl.scales[str(max(3, len(data["LEG24BXST"])))]['qual']['Set1']
        # ajouter les données
        fig.add_trace(
            go.Bar(
                # on représente la colonne des étiquettes courtes (et non la variable elle-même, car
                # cette colonne correspond aux étiquettes longues de la légende)
                x=data["ETIQCOURTE"],
                y=data["pct"],
                # changer de couleur en fonction de la modalité de réponse
                marker_color=couleurs_cl,
                # afficher les valeurs sous le format 'xx.x%' dans la bulle qui s'affiche
                # au survol de la courbe par la souris, et supprimer toutes les autres
                # informations qui pourraient s'afficher en plus (nom de la modalité)
                hovertemplate='%{y:.1f}%<extra></extra>',
                # n'afficher la bulle contenant la valeur 'y' en % uniquement
                # au-dessus de la barre verticale survolée par la souris
                hoverinfo='y',
                # centrer ce texte 'y' dans la bulle
                hoverlabel=dict(
                   align='auto'
                )
            )
        )
        # créer le texte de la légende (correspondance entre les étiquettes courtes et les étiquettes longues)
        legende_text = "<br>".join([f"{lettre}: {etiquette}" for lettre, etiquette in zip(etiquettes_courtes, etiquettes_longues)])
        # mettre en forme le graphique
        fig.update_layout(
            # définir le titre du graphique et son apparence
            title={
                'text': "Vote en faveur des candidats (couleurs politiques)",
                'y':0.98,
                'x':0.01,
                'xanchor': 'left',
                'yanchor': 'top'
            },
            # définir le titre de l'axe des ordonnées et son apparence
            yaxis_title=dict(
                text='Pourcentage de répondants (%)',
                font_size=12
            ),
            # définir l'affichage séparé des valeurs de % affichées au-dessus de
            # chaque barre verticale quand la souris la survole
            hovermode="closest",
            # définir le thème général de l'apparence du graphique
            template="plotly_white",
            # définir deux annotations
            annotations=[
                # sources des données
                dict(
                    xref='paper', # utiliser la largeur totale du graphique comme référence
                    yref='paper', # utiliser la hauteur totale du graphique comme référence
                    x=0.5, # placer le point d'ancrage au milieu de la largeur
                    y=-0.1, # valeur à ajuster pour positionner verticalement le texte sous le graphique
                    xanchor='center', # centrer le texte par rapport au point d'ancrage
                    yanchor='top',
                    text=
                        'Enquête électorale française pour les ' +
                        'élections européennes de juin 2024, ' +
                        'par Ipsos Sopra Steria, Cevipof, ' +
                        'Le Monde, Fondation Jean Jaurès et ' +
                        'Institut Montaigne (2024)',
                    font=dict(
                        size=10,
                        color='grey'
                    ),
                    showarrow=False
                ),
                # légende personnalisée
                dict(
                    valign="top", # aligner le texte en haut de chaque marqueur de la légende
                    x=0.75, # position horizontale de la légende (1 = à droite du graphique)
                    y=1.00, # position verticale de la légende (1 = en haut)
                    xref='paper',
                    yref='paper',
                    xanchor='left', # ancrer la légende à gauche de sa position x
                    yanchor='top', # ancrer la légende en haut de sa position y
                    text=f"<b>Légende :</b><br>{legende_text}",
                    showarrow=False,
                    font=dict(size=12),
                    align='left',
                    bgcolor='rgba(255,255,255,0.8)', # fond légèrement transparent
                )
            ],
            # définir les marges de la zone graphique
            # (augmentées à droite pour le cadre fixe de la légende)
            margin=dict(
                b=50, # b = bottom
                t=50,  # t = top
                l=50, # l = left
                r=200 # r = right
            )
        )
        # configurer l'axe des abscisses pour n'afficher que des nombres entiers
        fig.update_xaxes(
            tickmode='linear',
            tick0=1,
            dtick=1,
            tickfont=dict(size=12),
            tickangle=0
        )

        # retourner le graphique
        return fig


    #####################################################################
    # onglet 05 : SENTIMENTS PERSONNELS SUR LES RESULTATS DE L'ELECTION #
    #####################################################################

    # bouton 01 : décrire la question posée dans l'enquête
    @reactive.effect
    @reactive.event(input.Show_SENTRES_Question_Legis_T2)
    def _():
        m = ui.modal(
            "La question posée aux répondants est la suivante : 'Et quand vous pensez aux résultats des élections législatives des 30 juin et 7 juillet dernier, lequel des sentiments suivants est le plus proche de ce que vous ressentez ?'",
            title="Informations complémentaires sur la question contenue dans l'enquête :",
            easy_close=False
        )
        ui.modal_show(m)

    # bouton 02 : décrire la variable de l'intention d'aller voter choisie
    @reactive.effect
    @reactive.event(input.Show_SENTRESST_Info_Legis_T2)
    def _():
        m = ui.modal(
            "La variable sur le sentiment personnel des répondants concernant les résultats des élections législatives (2e tour) présentée ici sur les graphiques est une modalité synthétique de la question posée aux répondants de l'enquête. \
            Ainsi, à partir des sept modalités de réponse à la question de l'enquête, on en construit deux : 'Sentiment positif (joie, espoir ou soulagement)' ou 'Sentiment négatif (déception, colère ou peur)'.",
            title="Informations complémentaires sur la variable choisie pour les graphiques :",
            easy_close=False
        )
        ui.modal_show(m)

    # bouton 03 : afficher la description de la variable socio-démographique choisie
    # avec plusieurs parties de texte qui dépendent de ce choix (via des dictionnaires)
    @reactive.effect
    @reactive.event(input.Show_VarSD_SentRes_Info_Legis_T2)
    def _():
        # définir le nom de la variable socio-démographique choisie
        dico_nom_var = {
            "Y7SEXEST": "Genre",
            "Y7AGERST": "Âge",
            "Y7REG13ST": "Région",
            "Y7AGGLO5ST": "Taille d'agglomération",
            "Y7EMPST": "Type d'emploi occupé",
            "Y7PCSIST": "Catégorie professionnelle",
            "Y7EDUST": "Niveau de scolarité atteint",
            "Y7REL1ST": "Religion",
            "Y7ECO2ST2": "Revenu mensuel du foyer",
            "Y7INTPOLST": "Intérêt pour la politique",
            "Y7Q7ST": "Positionnement idéologique",
            "Y7PROXST": "Préférence partisane"
        }
        # définir la question de l'enquête associée à la variable socio-démographique choisie
        dico_question_var = {
            "Y7SEXEST": "Êtes-vous ?",
            "Y7AGERST": "Quelle est votre date de naissance ?",
            "Y7REG13ST": "Veuillez indiquer le département et la commune où vous résidez.",
            "Y7AGGLO5ST": "Veuillez indiquer le département et la commune où vous résidez.",
            "Y7EMPST": "Quelle est votre situation professionnelle actuelle ?",
            "Y7PCSIST": "Quelle est votre situation professionnelle actuelle ?",
            "Y7EDUST": "Choisissez votre niveau de scolarité le plus élevé.",
            "Y7REL1ST": "Quelle est votre religion, si vous en avez une ?",
            "Y7ECO2ST2": " Pour finir, nous avons besoin de connaître, à des fins statistiques uniquement, la tranche dans laquelle se situe le revenu MENSUEL NET de votre FOYER après déduction des impôts sur le revenu (veuillez considérer toutes vos sources de revenus: salaires, bourses, prestations retraite et sécurité sociale, dividendes, revenus immobiliers, pensions alimentaires etc.).",
            "Y7INTPOLST": "De manière générale, diriez-vous que vous vous intéressez à la politique ?",
            "Y7Q7ST": "Sur une échelle de 0 à 10, où 0 correspond à la gauche et 10 correspond à la droite, où diriez-vous que vous vous situez ?",
            "Y7PROXST": "De quel parti vous sentez-vous proche ou moins éloigné que les autres ?"
        }
        # définir les modalités de réponse à la question de l'enquête associée à la variable socio-démographique choisie
        dico_modalite_var = {
            "Y7SEXEST": "1 = 'Homme' ; 2 = 'Femme'",
            "Y7AGERST": "1 = '18 à 24 ans' ; 2 = '25 à 34 ans' ; 3 = '35 à 49 ans' ; 4 = '50 à 59 ans' ; 5 = '60 ans et plus'",
            "Y7REG13ST": "1 = 'Ile de France' ; 2 = 'Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)' ; 3 = 'Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)' ; 4 = 'Sud ouest (Nouvelle Aquitaine et Occitanie)' ; 5 = 'Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)'",
            "Y7AGGLO5ST": "1 = 'Zone rurale (moins de 2 000 habitants)' ; 2 = 'Zone urbaine de 2 000 à 9 999 habitants' ; 3 = 'Zone urbaine de 10 000 à 49 999 habitants' ; 4 = 'Zone urbaine de 50 000 à 199 999 habitants' ; 5 = 'Zone urbaine de 200 000 habitants et plus'",
            "Y7EMPST": "1 = 'Salarié (salarié à plein temps ou à temps partiel)' ; 2 = 'Indépendant (travaille à mon compte)' ; 3 = 'Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)'",
            "Y7PCSIST": "1 = 'Agriculteur exploitant, artisan, commerçant, chef d entreprise' ; 2 = 'Cadre supérieur' ; 3 = 'Profession intermédiaire' ; 4 = 'Employé' ; 5 = 'Ouvrier' ; 6 = 'Retraité, inactif'",
            "Y7EDUST": "1 = 'Aucun diplôme' ; 2 = 'CAP, BEP' ; 3 = 'Baccalauréat' ; 4 = 'Bac +2' ; 5 = 'Bac +3 et plus'",
            "Y7REL1ST": "1 = 'Catholique' ; 2 = 'Juive' ; 3 = 'Musulmane' ; 4 = 'Autre religion (protestante, boudhiste ou autre)' ; 5 = 'Sans religion'",
            "Y7ECO2ST2": "1 = 'Moins de 1 250 euros' ; 2 = 'De 1 250 euros à 1 999 euros' ; 3 = 'De 2 000 à 3 499 euros' ; 4 = 'De 3 500 à 4 999 euros' ; 5 = '5 000 euros et plus'",
            "Y7INTPOLST": "1 = 'Beaucoup' ; 2 = 'Un peu' ; 3 = 'Pas vraiment' ; 4 = 'Pas du tout'",
            "Y7Q7ST": "1 = 'Très à gauche' ; 2 = 'Plutôt à gauche' ; 3 = 'Au centre' ; 4 = 'Plutôt à droite' ; 5 = 'Très à droite'",
            "Y7PROXST": "1 = 'Extême gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)' ; 2 = 'Gauche (Parti Socialiste, Europe Ecologie - Les Verts)' ; 3 = 'Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))' ; 4 = 'Droite (Les Républicains)' ; 5 = 'Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)' ; 6 = 'Autre parti ou aucun parti'"
        }
        # définir le texte complet à afficher (avec parties fixes et variables en fonction du choix effectué)
        m = ui.modal(
            "La variable '%s' correspond à ou est calculée à partir de la question suivante posée aux répondants : \
            '%s', \
            et ses modalités de réponse (inchangées par rapport au questionnaire ou regroupées pour les présents graphiques) sont : \
            %s." % (
                dico_nom_var.get(
                    "%s" % input.Select_VarSD_SentRes_Legis_T2()
                ),
                dico_question_var.get("%s" % input.Select_VarSD_SentRes_Legis_T2()),
                dico_modalite_var.get("%s" % input.Select_VarSD_SentRes_Legis_T2())
            ),
            title="Informations complémentaires sur la variable socio-démographique choisie :",
            easy_close=False
        )
        ui.modal_show(m)

    # graphique
    @output
    @render_plotly
    def Graph_Croise_SentRes_Legis_T2():
        # définir la partie variable du titre
        dico_titre = {
            "Y7SEXEST": "du genre",
            "Y7AGERST": "de l'âge",
            "Y7REG13ST": "de la région de résidence",
            "Y7AGGLO5ST": "de la taille de l'agglomération de résidence",
            "Y7EMPST": "du type d'emploi occupé",
            "Y7PCSIST": "de la catégorie socio-professionnelle",
            "Y7EDUST": "du niveau de scolarité atteint",
            "Y7REL1ST": "de la religion",
            "Y7ECO2ST2": "du revenu mensuel du foyer",
            "Y7INTPOLST": "de l'intérêt pour la politique",
            "Y7Q7ST": "du positionnement idéologique",
            "Y7PROXST": "de la préférence partisane"
        }
        # définir la partie variable du titre de la légende
        dico_legende = {
            "Y7SEXEST": "Genre",
            "Y7AGERST": "Âge",
            "Y7REG13ST": "Région",
            "Y7AGGLO5ST": "Taille d'agglomération",
            "Y7EMPST": "Type d'emploi occupé",
            "Y7PCSIST": "Catégorie professionnelle",
            "Y7EDUST": "Niveau de scolarité atteint",
            "Y7REL1ST": "Religion",
            "Y7ECO2ST2": "Revenu mensuel du foyer",
            "Y7INTPOLST": "Intérêt pour la politique",
            "Y7Q7ST": "Positionnement idéologique",
            "Y7PROXST": "Préférence partisane"
        }
        # définir l'échelle de l'axe des ordonnées en fonction des
        # valeurs prises par la variable socio-démographique choisie
        dico_echelleY = {
            "Y7SEXEST": [10, 40],
            "Y7AGERST": [10, 45],
            "Y7REG13ST": [15, 35],
            "Y7AGGLO5ST": [15, 35],
            "Y7EMPST": [15, 40],
            "Y7PCSIST": [10, 45],
            "Y7EDUST": [15, 40],
            "Y7REL1ST": [10, 45],
            "Y7ECO2ST2": [10, 45],
            "Y7INTPOLST": [0, 75],
            "Y7Q7ST": [5, 40],
            "Y7PROXST": [5, 55],
        }
        # définir les modalités des variables socio-démo et leur ordre
        dico_modalite_var = {
            "Y7SEXEST": "1 = 'Homme' ; 2 = 'Femme'",
            "Y7AGERST": "1 = '18 à 24 ans' ; 2 = '25 à 34 ans' ; 3 = '35 à 49 ans' ; 4 = '50 à 59 ans' ; 5 = '60 ans et plus'",
            "Y7REG13ST": "1 = 'Ile de France' ; 2 = 'Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)' ; 3 = 'Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)' ; 4 = 'Sud ouest (Nouvelle Aquitaine et Occitanie)' ; 5 = 'Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)'",
            "Y7AGGLO5ST": "1 = 'Zone rurale (moins de 2 000 habitants)' ; 2 = 'Zone urbaine de 2 000 à 9 999 habitants' ; 3 = 'Zone urbaine de 10 000 à 49 999 habitants' ; 4 = 'Zone urbaine de 50 000 à 199 999 habitants' ; 5 = 'Zone urbaine de 200 000 habitants et plus'",
            "Y7EMPST": "1 = 'Salarié (salarié à plein temps ou à temps partiel)' ; 2 = 'Indépendant (travaille à mon compte)' ; 3 = 'Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)'",
            "Y7PCSIST": "1 = 'Agriculteur exploitant, artisan, commerçant, chef d entreprise' ; 2 = 'Cadre supérieur' ; 3 = 'Profession intermédiaire' ; 4 = 'Employé' ; 5 = 'Ouvrier' ; 6 = 'Retraité, inactif'",
            "Y7EDUST": "1 = 'Aucun diplôme' ; 2 = 'CAP, BEP' ; 3 = 'Baccalauréat' ; 4 = 'Bac +2' ; 5 = 'Bac +3 et plus'",
            "Y7REL1ST": "1 = 'Catholique' ; 2 = 'Juive' ; 3 = 'Musulmane' ; 4 = 'Autre religion (protestante, boudhiste ou autre)' ; 5 = 'Sans religion'",
            "Y7ECO2ST2": "1 = 'Moins de 1 250 euros' ; 2 = 'De 1 250 euros à 1 999 euros' ; 3 = 'De 2 000 à 3 499 euros' ; 4 = 'De 3 500 à 4 999 euros' ; 5 = '5 000 euros et plus'",
            "Y7INTPOLST": "1 = 'Beaucoup' ; 2 = 'Un peu' ; 3 = 'Pas vraiment' ; 4 = 'Pas du tout'",
            "Y7Q7ST": "1 = 'Très à gauche' ; 2 = 'Plutôt à gauche' ; 3 = 'Au centre' ; 4 = 'Plutôt à droite' ; 5 = 'Très à droite'",
            "Y7PROXST": "1 = 'Très à gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)' ; 2 = 'Gauche (Parti Socialiste, Europe Ecologie - Les Verts)' ; 3 = 'Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))' ; 4 = 'Droite (Les Républicains)' ; 5 = 'Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)' ; 6 = 'Autre parti ou aucun parti'"
        }
        # définir un dictionnaire qui contient l'ordre figé des modalités pour chaque variable socio-démographique
        dico_ordre_modalites = {
            "Y7SEXEST": [
                "Homme",
                "Femme"
            ],
            "Y7AGERST": [
                "18 à 24 ans",
                "25 à 34 ans",
                "35 à 49 ans",
                "50 à 59 ans",
                "60 ans et plus"
            ],
            "Y7REG13ST": [
                "Ile de France",
                "Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)",
                "Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)",
                "Sud ouest (Nouvelle Aquitaine et Occitanie)",
                "Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)"
            ],
            "Y7AGGLO5ST": [
                "Zone rurale (moins de 2 000 habitants)",
                "Zone urbaine de 2 000 à 9 999 habitants",
                "Zone urbaine de 10 000 à 49 999 habitants",
                "Zone urbaine de 50 000 à 199 999 habitants",
                "Zone urbaine de 200 000 habitants et plus"
            ],
            "Y7EMPST": [
                "Salarié (salarié à plein temps ou à temps partiel)",
                "Indépendant (travaille à mon compte)",
                "Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)"
            ],
            "Y7PCSIST": [
                "Agriculteur exploitant, artisan, commerçant, chef d entreprise",
                "Cadre supérieur",
                "Profession intermédiaire",
                "Employé",
                "Ouvrier",
                "Retraité, inactif"
            ],
            "Y7EDUST": [
                "Aucun diplôme",
                "CAP, BEP",
                "Baccalauréat",
                "Bac +2",
                "Bac +3 et plus"
            ],
            "Y7REL1ST": [
                "Catholique",
                "Juive",
                "Musulmane",
                "Autre religion (protestante, boudhiste ou autre)",
                "Sans religion"
            ],
            "Y7ECO2ST2": [
                "Moins de 1 250 euros",
                "De 1 250 euros à 1 999 euros",
                "De 2 000 à 3 499 euros",
                "De 3 500 à 4 999 euros",
                "5 000 euros et plus"
            ],
            "Y7INTPOLST": [
                "Beaucoup",
                "Un peu",
                "Pas vraiment",
                "Pas du tout"
            ],
            "Y7Q7ST": [
                "Très à gauche",
                "Plutôt à gauche",
                "Au centre",
                "Plutôt à droite",
                "Très à droite"
            ],
            "Y7PROXST": [
                "Très à gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)",
                "Gauche (Parti Socialiste, Europe Ecologie - Les Verts)",
                "Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))",
                "Droite (Les Républicains)",
                "Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)",
                "Autre parti ou aucun parti"
            ]
        }
        # définir une fonction qui affiche les étiquettes
        # des modalités de la variablr SD choisie dans la légende
        # sur plusieurs lignes si leur longueur initiale dépasse la
        # largeur du cadre de la légende (version robuste avec gestion des erreurs)
        def wrap_label(label, max_length=20):
            try:
                # Si le label est un float ou NaN
                if pd.isna(label) or isinstance(label, float):
                    return "Non renseigné"
                # Convertir en string si ce n'est pas déjà le cas
                label = str(label).strip()
                # Si la chaîne est vide après nettoyage
                if not label:
                    return "Non renseigné"
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
            except Exception as e:
                print(f"Erreur dans wrap_label avec {label}: {str(e)}")
                return str(label) 
                # retourner le label tel quel en cas d'erreur
        # lire le fichier CSV des données
        csvfile = "data/T_w7_pl4st_" + "%s" % input.Select_VarSD_SentRes_Legis_T2().lower()[2:] + ".csv"
        df = pd.read_csv(csvfile)
        # nettoyer les données lues
        var_sd = input.Select_VarSD_SentRes_Legis_T2()
        df[var_sd] = df[var_sd].fillna("Non renseigné")  # Gérer les NaN
        df[var_sd] = df[var_sd].astype(str)  # Convertir en string
        df['Y7PL4ST'] = df['Y7PL4ST'].fillna("Non renseigné")
        # s'assurer que toutes les modalités sont des chaînes de caractères dans "dico_ordre_modalites"
        dico_ordre_modalites[var_sd] = [str(modal) for modal in dico_ordre_modalites[var_sd]]
        # filtrer pour ne garder que les modalités définies dans "dico_ordre_modalites"
        df = df[df[var_sd].isin(dico_ordre_modalites[var_sd])]
        # définir l'ordre des modalités pour Y7PL4ST
        ordre_modalites = [
            "Sentiment positif (joie, espoir ou soulagement)",
            "Sentiment négatif (déception, colère ou peur)"
        ]
        # créer une colonne catégorielle avec l'ordre souhaité pour la variable socio-démographique
        var_sd = input.Select_VarSD_SentRes_Legis_T2()
        df[var_sd] = pd.Categorical(
            df[var_sd],
            categories=dico_ordre_modalites[var_sd],
            ordered=True
        )
        # filtrer et pivoter les données
        df_pivot = df[df['Y7PL4ST'].isin(ordre_modalites)].pivot(
            index=var_sd,
            columns='Y7PL4ST',
            values='pct'
        )
        df_pivot = df_pivot.reindex(columns=ordre_modalites)
        # créer une palette de couleurs automatique
        nb_couleurs = len(df_pivot.index)
        palette = px.colors.qualitative.Plotly[:nb_couleurs]
        # créer le graphique
        fig = go.Figure()
        # ajouter les données
        for i, VarSD in enumerate(df_pivot.index):
            fig.add_trace(
                go.Bar(
                    x=ordre_modalites,
                    y=df_pivot.loc[VarSD],
                    name=wrap_label(VarSD),
                    marker_color=palette[i],
                    # afficher les valeurs sous le format 'xx.x%' dans la bulle qui s'affiche
                    # au survol de la courbe par la souris, et supprimer toutes les autres
                    # informations qui pourraient s'afficher en plus (nom de la modalité)
                    hovertemplate='%{y:.1f}%<extra></extra>',
                    # n'afficher la bulle contenant la valeur 'y' en % uniquement
                    # au-dessus de la barre verticale survolée par la souris
                    hoverinfo='y',
                    # centrer ce texte 'y' dans la bulle
                    hoverlabel=dict(
                        align='auto'
                    )
                )
            )
         # mettre en forme le graphique
        fig.update_layout(
            barmode='group', # barres séparées et groupées pour les modalités de la VarSD choisie
            title={
                'text': "Sentiment personnel sur les résultats des élections en fonction %s" % dico_titre.get("%s" % input.Select_VarSD_SentRes_Legis_T2()),
                'y':0.98,
                'x':0.01,
                'xanchor': 'left',
                'yanchor': 'top'
            },
            # définir le titre de la légende
            legend_title="%s" % dico_legende.get("%s" % input.Select_VarSD_SentRes_Legis_T2()),
            # définir l'affichage séparé des valeurs de % affichées au-dessus de
            # chaque barre verticale quand la souris la survole
            hovermode="closest",
            # définir le thème général de l'apparence du graphique
            template="plotly_white",
            # définir le titre de l'axe des ordonnées et son apparence
            yaxis_title=dict(
                text='Pourcentage de répondants (%)',
                font_size=12
            ),
            # définir les sources des données
            annotations=[
                dict(
                    xref='paper', # utiliser la largeur totale du graphique comme référence
                    yref='paper', # utiliser la hauteur totale du graphique comme référence
                    x=0.5, # placer le point d'ancrage au milieu de la largeur
                    y=-0.1, # valeur à ajuster pour positionner verticalement le texte sous le graphique
                    xanchor='center', # centrer le texte par rapport au point d'ancrage
                    yanchor='top',
                    text=
                        'Enquête électorale française pour les ' +
                        'élections européennes de juin 2024, ' +
                        'par Ipsos Sopra Steria, Cevipof, ' +
                        'Le Monde, Fondation Jean Jaurès et ' +
                        'Institut Montaigne (2024)',
                    font=dict(
                        size=10,
                        color='grey'
                    ),
                    showarrow=False
                )
            ],
            # définir les marges de la zone graphique
            # (augmentées à droite pour le cadre fixe de la légende)
            margin=dict(
                b=50, # b = bottom
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
            ),
        )
        # retourner le graphique
        return fig


    #######################################################
    # onglet 06 : AVIS SUR LE FRONT REPUBLICAIN (2e tour) #
    #######################################################

    # bouton 01 : décrire la question posée dans l'enquête
    @reactive.effect
    @reactive.event(input.Show_AVFR_Question_Legis_T2)
    def _():
        m = ui.modal(
            "La question posée aux répondants est la suivante : 'Le Front Républicain est le fait d’appeler les électeurs de gauche et de droite à voter au second tour d’une élection pour un même candidat, afin d’empêcher l’élection d’un candidat du Rassemblement National. De laquelle des deux opinions suivantes vous sentez-vous le plus proche ?'",
            title="Informations complémentaires sur la question contenue dans l'enquête :",
            easy_close=False
        )
        ui.modal_show(m)

    # bouton 02 : décrire la variable de l'intention d'aller voter choisie
    @reactive.effect
    @reactive.event(input.Show_AVFRST_Info_Legis_T2)
    def _():
        m = ui.modal(
            "La variable sur l'avis des répondants concernant le front républicain aux élections législatives (2e tour) \
            présentée ici sur les graphiques contient deux modalités de réponse : \
            'L’appel au Front Républicain exprime l’inquiétude de ceux qui pensent que le Rassemblement National est une menace pour la démocratie' \
            et 'Le Front Républicain est une tactique permettant aux partis traditionnels de conserver le pouvoir'.",
            title="Informations complémentaires sur la variable choisie pour les graphiques :",
            easy_close=False
        )
        ui.modal_show(m)

    # bouton 03 : afficher la description de la variable socio-démographique choisie
    # avec plusieurs parties de texte qui dépendent de ce choix (via des dictionnaires)
    @reactive.effect
    @reactive.event(input.Show_VarSD_AvFr_Info_Legis_T2)
    def _():
        # définir le nom de la variable socio-démographique choisie
        dico_nom_var = {
            "Y7SEXEST": "Genre",
            "Y7AGERST": "Âge",
            "Y7REG13ST": "Région",
            "Y7AGGLO5ST": "Taille d'agglomération",
            "Y7EMPST": "Type d'emploi occupé",
            "Y7PCSIST": "Catégorie professionnelle",
            "Y7EDUST": "Niveau de scolarité atteint",
            "Y7REL1ST": "Religion",
            "Y7ECO2ST2": "Revenu mensuel du foyer",
            "Y7INTPOLST": "Intérêt pour la politique",
            "Y7Q7ST": "Positionnement idéologique",
            "Y7PROXST": "Préférence partisane"
        }
        # définir la question de l'enquête associée à la variable socio-démographique choisie
        dico_question_var = {
            "Y7SEXEST": "Êtes-vous ?",
            "Y7AGERST": "Quelle est votre date de naissance ?",
            "Y7REG13ST": "Veuillez indiquer le département et la commune où vous résidez.",
            "Y7AGGLO5ST": "Veuillez indiquer le département et la commune où vous résidez.",
            "Y7EMPST": "Quelle est votre situation professionnelle actuelle ?",
            "Y7PCSIST": "Quelle est votre situation professionnelle actuelle ?",
            "Y7EDUST": "Choisissez votre niveau de scolarité le plus élevé.",
            "Y7REL1ST": "Quelle est votre religion, si vous en avez une ?",
            "Y7ECO2ST2": " Pour finir, nous avons besoin de connaître, à des fins statistiques uniquement, la tranche dans laquelle se situe le revenu MENSUEL NET de votre FOYER après déduction des impôts sur le revenu (veuillez considérer toutes vos sources de revenus: salaires, bourses, prestations retraite et sécurité sociale, dividendes, revenus immobiliers, pensions alimentaires etc.).",
            "Y7INTPOLST": "De manière générale, diriez-vous que vous vous intéressez à la politique ?",
            "Y7Q7ST": "Sur une échelle de 0 à 10, où 0 correspond à la gauche et 10 correspond à la droite, où diriez-vous que vous vous situez ?",
            "Y7PROXST": "De quel parti vous sentez-vous proche ou moins éloigné que les autres ?"
        }
        # définir les modalités de réponse à la question de l'enquête associée à la variable socio-démographique choisie
        dico_modalite_var = {
            "Y7SEXEST": "1 = 'Homme' ; 2 = 'Femme'",
            "Y7AGERST": "1 = '18 à 24 ans' ; 2 = '25 à 34 ans' ; 3 = '35 à 49 ans' ; 4 = '50 à 59 ans' ; 5 = '60 ans et plus'",
            "Y7REG13ST": "1 = 'Ile de France' ; 2 = 'Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)' ; 3 = 'Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)' ; 4 = 'Sud ouest (Nouvelle Aquitaine et Occitanie)' ; 5 = 'Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)'",
            "Y7AGGLO5ST": "1 = 'Zone rurale (moins de 2 000 habitants)' ; 2 = 'Zone urbaine de 2 000 à 9 999 habitants' ; 3 = 'Zone urbaine de 10 000 à 49 999 habitants' ; 4 = 'Zone urbaine de 50 000 à 199 999 habitants' ; 5 = 'Zone urbaine de 200 000 habitants et plus'",
            "Y7EMPST": "1 = 'Salarié (salarié à plein temps ou à temps partiel)' ; 2 = 'Indépendant (travaille à mon compte)' ; 3 = 'Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)'",
            "Y7PCSIST": "1 = 'Agriculteur exploitant, artisan, commerçant, chef d entreprise' ; 2 = 'Cadre supérieur' ; 3 = 'Profession intermédiaire' ; 4 = 'Employé' ; 5 = 'Ouvrier' ; 6 = 'Retraité, inactif'",
            "Y7EDUST": "1 = 'Aucun diplôme' ; 2 = 'CAP, BEP' ; 3 = 'Baccalauréat' ; 4 = 'Bac +2' ; 5 = 'Bac +3 et plus'",
            "Y7REL1ST": "1 = 'Catholique' ; 2 = 'Juive' ; 3 = 'Musulmane' ; 4 = 'Autre religion (protestante, boudhiste ou autre)' ; 5 = 'Sans religion'",
            "Y7ECO2ST2": "1 = 'Moins de 1 250 euros' ; 2 = 'De 1 250 euros à 1 999 euros' ; 3 = 'De 2 000 à 3 499 euros' ; 4 = 'De 3 500 à 4 999 euros' ; 5 = '5 000 euros et plus'",
            "Y7INTPOLST": "1 = 'Beaucoup' ; 2 = 'Un peu' ; 3 = 'Pas vraiment' ; 4 = 'Pas du tout'",
            "Y7Q7ST": "1 = 'Très à gauche' ; 2 = 'Plutôt à gauche' ; 3 = 'Au centre' ; 4 = 'Plutôt à droite' ; 5 = 'Très à droite'",
            "Y7PROXST": "1 = 'Extême gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)' ; 2 = 'Gauche (Parti Socialiste, Europe Ecologie - Les Verts)' ; 3 = 'Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))' ; 4 = 'Droite (Les Républicains)' ; 5 = 'Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)' ; 6 = 'Autre parti ou aucun parti'"
        }
        # définir le texte complet à afficher (avec parties fixes et variables en fonction du choix effectué)
        m = ui.modal(
            "La variable '%s' correspond à ou est calculée à partir de la question suivante posée aux répondants : \
            '%s', \
            et ses modalités de réponse (inchangées par rapport au questionnaire ou regroupées pour les présents graphiques) sont : \
            %s." % (
                dico_nom_var.get(
                    "%s" % input.Select_VarSD_AvFr_Legis_T2()
                ),
                dico_question_var.get("%s" % input.Select_VarSD_AvFr_Legis_T2()),
                dico_modalite_var.get("%s" % input.Select_VarSD_AvFr_Legis_T2())
            ),
            title="Informations complémentaires sur la variable socio-démographique choisie :",
            easy_close=False
        )
        ui.modal_show(m)

    # graphique
    @output
    @render_plotly
    def Graph_Croise_AvFr_Legis_T2():
        # définir la partie variable du titre
        dico_titre = {
            "Y7SEXEST": "du genre",
            "Y7AGERST": "de l'âge",
            "Y7REG13ST": "de la région de résidence",
            "Y7AGGLO5ST": "de la taille de l'agglomération de résidence",
            "Y7EMPST": "du type d'emploi occupé",
            "Y7PCSIST": "de la catégorie socio-professionnelle",
            "Y7EDUST": "du niveau de scolarité atteint",
            "Y7REL1ST": "de la religion",
            "Y7ECO2ST2": "du revenu mensuel du foyer",
            "Y7INTPOLST": "de l'intérêt pour la politique",
            "Y7Q7ST": "du positionnement idéologique",
            "Y7PROXST": "de la préférence partisane"
        }
        # définir la partie variable du titre de la légende
        dico_legende = {
            "Y7SEXEST": "Genre",
            "Y7AGERST": "Âge",
            "Y7REG13ST": "Région",
            "Y7AGGLO5ST": "Taille d'agglomération",
            "Y7EMPST": "Type d'emploi occupé",
            "Y7PCSIST": "Catégorie professionnelle",
            "Y7EDUST": "Niveau de scolarité atteint",
            "Y7REL1ST": "Religion",
            "Y7ECO2ST2": "Revenu mensuel du foyer",
            "Y7INTPOLST": "Intérêt pour la politique",
            "Y7Q7ST": "Positionnement idéologique",
            "Y7PROXST": "Préférence partisane"
        }
        # définir l'échelle de l'axe des ordonnées en fonction des
        # valeurs prises par la variable socio-démographique choisie
        dico_echelleY = {
            "Y7SEXEST": [10, 40],
            "Y7AGERST": [10, 45],
            "Y7REG13ST": [15, 35],
            "Y7AGGLO5ST": [15, 35],
            "Y7EMPST": [15, 40],
            "Y7PCSIST": [10, 45],
            "Y7EDUST": [15, 40],
            "Y7REL1ST": [10, 45],
            "Y7ECO2ST2": [10, 45],
            "Y7INTPOLST": [0, 75],
            "Y7Q7ST": [5, 40],
            "Y7PROXST": [5, 55],
        }
        # définir les modalités des variables socio-démo et leur ordre
        dico_modalite_var = {
            "Y7SEXEST": "1 = 'Homme' ; 2 = 'Femme'",
            "Y7AGERST": "1 = '18 à 24 ans' ; 2 = '25 à 34 ans' ; 3 = '35 à 49 ans' ; 4 = '50 à 59 ans' ; 5 = '60 ans et plus'",
            "Y7REG13ST": "1 = 'Ile de France' ; 2 = 'Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)' ; 3 = 'Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)' ; 4 = 'Sud ouest (Nouvelle Aquitaine et Occitanie)' ; 5 = 'Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)'",
            "Y7AGGLO5ST": "1 = 'Zone rurale (moins de 2 000 habitants)' ; 2 = 'Zone urbaine de 2 000 à 9 999 habitants' ; 3 = 'Zone urbaine de 10 000 à 49 999 habitants' ; 4 = 'Zone urbaine de 50 000 à 199 999 habitants' ; 5 = 'Zone urbaine de 200 000 habitants et plus'",
            "Y7EMPST": "1 = 'Salarié (salarié à plein temps ou à temps partiel)' ; 2 = 'Indépendant (travaille à mon compte)' ; 3 = 'Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)'",
            "Y7PCSIST": "1 = 'Agriculteur exploitant, artisan, commerçant, chef d entreprise' ; 2 = 'Cadre supérieur' ; 3 = 'Profession intermédiaire' ; 4 = 'Employé' ; 5 = 'Ouvrier' ; 6 = 'Retraité, inactif'",
            "Y7EDUST": "1 = 'Aucun diplôme' ; 2 = 'CAP, BEP' ; 3 = 'Baccalauréat' ; 4 = 'Bac +2' ; 5 = 'Bac +3 et plus'",
            "Y7REL1ST": "1 = 'Catholique' ; 2 = 'Juive' ; 3 = 'Musulmane' ; 4 = 'Autre religion (protestante, boudhiste ou autre)' ; 5 = 'Sans religion'",
            "Y7ECO2ST2": "1 = 'Moins de 1 250 euros' ; 2 = 'De 1 250 euros à 1 999 euros' ; 3 = 'De 2 000 à 3 499 euros' ; 4 = 'De 3 500 à 4 999 euros' ; 5 = '5 000 euros et plus'",
            "Y7INTPOLST": "1 = 'Beaucoup' ; 2 = 'Un peu' ; 3 = 'Pas vraiment' ; 4 = 'Pas du tout'",
            "Y7Q7ST": "1 = 'Très à gauche' ; 2 = 'Plutôt à gauche' ; 3 = 'Au centre' ; 4 = 'Plutôt à droite' ; 5 = 'Très à droite'",
            "Y7PROXST": "1 = 'Très à gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)' ; 2 = 'Gauche (Parti Socialiste, Europe Ecologie - Les Verts)' ; 3 = 'Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))' ; 4 = 'Droite (Les Républicains)' ; 5 = 'Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)' ; 6 = 'Autre parti ou aucun parti'"
        }
        # définir un dictionnaire qui contient l'ordre figé des modalités pour chaque variable socio-démographique
        dico_ordre_modalites = {
            "Y7SEXEST": [
                "Homme",
                "Femme"
            ],
            "Y7AGERST": [
                "18 à 24 ans",
                "25 à 34 ans",
                "35 à 49 ans",
                "50 à 59 ans",
                "60 ans et plus"
            ],
            "Y7REG13ST": [
                "Ile de France",
                "Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)",
                "Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)",
                "Sud ouest (Nouvelle Aquitaine et Occitanie)",
                "Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)"
            ],
            "Y7AGGLO5ST": [
                "Zone rurale (moins de 2 000 habitants)",
                "Zone urbaine de 2 000 à 9 999 habitants",
                "Zone urbaine de 10 000 à 49 999 habitants",
                "Zone urbaine de 50 000 à 199 999 habitants",
                "Zone urbaine de 200 000 habitants et plus"
            ],
            "Y7EMPST": [
                "Salarié (salarié à plein temps ou à temps partiel)",
                "Indépendant (travaille à mon compte)",
                "Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)"
            ],
            "Y7PCSIST": [
                "Agriculteur exploitant, artisan, commerçant, chef d entreprise",
                "Cadre supérieur",
                "Profession intermédiaire",
                "Employé",
                "Ouvrier",
                "Retraité, inactif"
            ],
            "Y7EDUST": [
                "Aucun diplôme",
                "CAP, BEP",
                "Baccalauréat",
                "Bac +2",
                "Bac +3 et plus"
            ],
            "Y7REL1ST": [
                "Catholique",
                "Juive",
                "Musulmane",
                "Autre religion (protestante, boudhiste ou autre)",
                "Sans religion"
            ],
            "Y7ECO2ST2": [
                "Moins de 1 250 euros",
                "De 1 250 euros à 1 999 euros",
                "De 2 000 à 3 499 euros",
                "De 3 500 à 4 999 euros",
                "5 000 euros et plus"
            ],
            "Y7INTPOLST": [
                "Beaucoup",
                "Un peu",
                "Pas vraiment",
                "Pas du tout"
            ],
            "Y7Q7ST": [
                "Très à gauche",
                "Plutôt à gauche",
                "Au centre",
                "Plutôt à droite",
                "Très à droite"
            ],
            "Y7PROXST": [
                "Très à gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)",
                "Gauche (Parti Socialiste, Europe Ecologie - Les Verts)",
                "Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))",
                "Droite (Les Républicains)",
                "Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)",
                "Autre parti ou aucun parti"
            ]
        }
        # définir une fonction qui affiche les étiquettes
        # des modalités de la variablr SD choisie dans la légende
        # sur plusieurs lignes si leur longueur initiale dépasse la
        # largeur du cadre de la légende (version robuste avec gestion des erreurs)
        def wrap_label(label, max_length=20):
            try:
                # Si le label est un float ou NaN
                if pd.isna(label) or isinstance(label, float):
                    return "Non renseigné"
                # Convertir en string si ce n'est pas déjà le cas
                label = str(label).strip()
                # Si la chaîne est vide après nettoyage
                if not label:
                    return "Non renseigné"
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
            except Exception as e:
                print(f"Erreur dans wrap_label avec {label}: {str(e)}")
                return str(label) 
                # retourner le label tel quel en cas d'erreur
        # lire le fichier CSV des données
        csvfile = "data/T_w7_pl5st_" + "%s" % input.Select_VarSD_AvFr_Legis_T2().lower()[2:] + ".csv"
        df = pd.read_csv(csvfile)
        # nettoyer les données lues
        var_sd = input.Select_VarSD_AvFr_Legis_T2()
        df[var_sd] = df[var_sd].fillna("Non renseigné")  # Gérer les NaN
        df[var_sd] = df[var_sd].astype(str)  # Convertir en string
        df['Y7PL5ST'] = df['Y7PL5ST'].fillna("Non renseigné")
        # s'assurer que toutes les modalités sont des chaînes de caractères dans "dico_ordre_modalites"
        dico_ordre_modalites[var_sd] = [str(modal) for modal in dico_ordre_modalites[var_sd]]
        # filtrer pour ne garder que les modalités définies dans "dico_ordre_modalites"
        df = df[df[var_sd].isin(dico_ordre_modalites[var_sd])]
        # définir l'ordre des modalités pour Y7PL5ST
        ordre_modalites = [
            "Le RN est une menace pour la démocratie",
            "Tactique des partis traditionnels pour garder le pouvoir"
        ]
        # créer une colonne catégorielle avec l'ordre souhaité pour la variable socio-démographique
        var_sd = input.Select_VarSD_AvFr_Legis_T2()
        df[var_sd] = pd.Categorical(
            df[var_sd],
            categories=dico_ordre_modalites[var_sd],
            ordered=True
        )
        # filtrer et pivoter les données
        df_pivot = df[df['Y7PL5ST'].isin(ordre_modalites)].pivot(
            index=var_sd,
            columns='Y7PL5ST',
            values='pct'
        )
        df_pivot = df_pivot.reindex(columns=ordre_modalites)
        # créer une palette de couleurs automatique
        nb_couleurs = len(df_pivot.index)
        palette = px.colors.qualitative.Plotly[:nb_couleurs]
        # créer le graphique
        fig = go.Figure()
        # ajouter les données
        for i, VarSD in enumerate(df_pivot.index):
            fig.add_trace(
                go.Bar(
                    x=ordre_modalites,
                    y=df_pivot.loc[VarSD],
                    name=wrap_label(VarSD),
                    marker_color=palette[i],
                    # afficher les valeurs sous le format 'xx.x%' dans la bulle qui s'affiche
                    # au survol de la courbe par la souris, et supprimer toutes les autres
                    # informations qui pourraient s'afficher en plus (nom de la modalité)
                    hovertemplate='%{y:.1f}%<extra></extra>',
                    # n'afficher la bulle contenant la valeur 'y' en % uniquement
                    # au-dessus de la barre verticale survolée par la souris
                    hoverinfo='y',
                    # centrer ce texte 'y' dans la bulle
                    hoverlabel=dict(
                        align='auto'
                    )
                )
            )
         # mettre en forme le graphique
        fig.update_layout(
            barmode='group', # barres séparées et groupées pour les modalités de la VarSD choisie
            title={
                'text': "Avis sur le front républicain en fonction %s" % dico_titre.get("%s" % input.Select_VarSD_AvFr_Legis_T2()),
                'y':0.98,
                'x':0.01,
                'xanchor': 'left',
                'yanchor': 'top'
            },
            # définir le titre de la légende
            legend_title="%s" % dico_legende.get("%s" % input.Select_VarSD_AvFr_Legis_T2()),
            # définir l'affichage séparé des valeurs de % affichées au-dessus de
            # chaque barre verticale quand la souris la survole
            hovermode="closest",
            # définir le thème général de l'apparence du graphique
            template="plotly_white",
            # définir le titre de l'axe des ordonnées et son apparence
            yaxis_title=dict(
                text='Pourcentage de répondants (%)',
                font_size=12
            ),
            # définir les sources des données
            annotations=[
                dict(
                    xref='paper', # utiliser la largeur totale du graphique comme référence
                    yref='paper', # utiliser la hauteur totale du graphique comme référence
                    x=0.5, # placer le point d'ancrage au milieu de la largeur
                    y=-0.1, # valeur à ajuster pour positionner verticalement le texte sous le graphique
                    xanchor='center', # centrer le texte par rapport au point d'ancrage
                    yanchor='top',
                    text=
                        'Enquête électorale française pour les ' +
                        'élections européennes de juin 2024, ' +
                        'par Ipsos Sopra Steria, Cevipof, ' +
                        'Le Monde, Fondation Jean Jaurès et ' +
                        'Institut Montaigne (2024)',
                    font=dict(
                        size=10,
                        color='grey'
                    ),
                    showarrow=False
                )
            ],
            # définir les marges de la zone graphique
            # (augmentées à droite pour le cadre fixe de la légende)
            margin=dict(
                b=50, # b = bottom
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
            ),
        )
        # retourner le graphique
        return fig


    ###############################################
    # onglet 07 : ACCORD DE VUES AVEC L'ENTOURAGE #
    ###############################################

    # bouton 01 : décrire la question posée dans l'enquête
    @reactive.effect
    @reactive.event(input.Show_ACCVUES_Question_Legis_T2)
    def _():
        m = ui.modal(
            "La question posée aux répondants est la suivante : 'À l’occasion de ces élections législatives, avez-vous eu de profonds désaccords ou des discussions animées avec des gens de votre entourage ?'",
            title="Informations complémentaires sur la question contenue dans l'enquête :",
            easy_close=False
        )
        ui.modal_show(m)

    # bouton 02 : décrire la variable de l'intention d'aller voter choisie
    @reactive.effect
    @reactive.event(input.Show_ACCVUESST_Info_Legis_T2)
    def _():
        m = ui.modal(
            "La variable sur l'accord des points de vue des répondants avec leur entourage à l'occasion des élections législatives présentée ici sur les graphiques est une modalité synthétique de la question posée aux répondants de l'enquête. \
            Ainsi, à partir des quatre modalités de réponse à la question de l'enquête, on en construit deux : 'Souvent (très souvent ou assez souvent)' ou 'Rarement ou jamais'.",
            title="Informations complémentaires sur la variable choisie pour les graphiques :",
            easy_close=False
        )
        ui.modal_show(m)

    # bouton 03 : afficher la description de la variable socio-démographique choisie
    # avec plusieurs parties de texte qui dépendent de ce choix (via des dictionnaires)
    @reactive.effect
    @reactive.event(input.Show_VarSD_AccVues_Info_Legis_T2)
    def _():
        # définir le nom de la variable socio-démographique choisie
        dico_nom_var = {
            "Y7SEXEST": "Genre",
            "Y7AGERST": "Âge",
            "Y7REG13ST": "Région",
            "Y7AGGLO5ST": "Taille d'agglomération",
            "Y7EMPST": "Type d'emploi occupé",
            "Y7PCSIST": "Catégorie professionnelle",
            "Y7EDUST": "Niveau de scolarité atteint",
            "Y7REL1ST": "Religion",
            "Y7ECO2ST2": "Revenu mensuel du foyer",
            "Y7INTPOLST": "Intérêt pour la politique",
            "Y7Q7ST": "Positionnement idéologique",
            "Y7PROXST": "Préférence partisane"
        }
        # définir la question de l'enquête associée à la variable socio-démographique choisie
        dico_question_var = {
            "Y7SEXEST": "Êtes-vous ?",
            "Y7AGERST": "Quelle est votre date de naissance ?",
            "Y7REG13ST": "Veuillez indiquer le département et la commune où vous résidez.",
            "Y7AGGLO5ST": "Veuillez indiquer le département et la commune où vous résidez.",
            "Y7EMPST": "Quelle est votre situation professionnelle actuelle ?",
            "Y7PCSIST": "Quelle est votre situation professionnelle actuelle ?",
            "Y7EDUST": "Choisissez votre niveau de scolarité le plus élevé.",
            "Y7REL1ST": "Quelle est votre religion, si vous en avez une ?",
            "Y7ECO2ST2": " Pour finir, nous avons besoin de connaître, à des fins statistiques uniquement, la tranche dans laquelle se situe le revenu MENSUEL NET de votre FOYER après déduction des impôts sur le revenu (veuillez considérer toutes vos sources de revenus: salaires, bourses, prestations retraite et sécurité sociale, dividendes, revenus immobiliers, pensions alimentaires etc.).",
            "Y7INTPOLST": "De manière générale, diriez-vous que vous vous intéressez à la politique ?",
            "Y7Q7ST": "Sur une échelle de 0 à 10, où 0 correspond à la gauche et 10 correspond à la droite, où diriez-vous que vous vous situez ?",
            "Y7PROXST": "De quel parti vous sentez-vous proche ou moins éloigné que les autres ?"
        }
        # définir les modalités de réponse à la question de l'enquête associée à la variable socio-démographique choisie
        dico_modalite_var = {
            "Y7SEXEST": "1 = 'Homme' ; 2 = 'Femme'",
            "Y7AGERST": "1 = '18 à 24 ans' ; 2 = '25 à 34 ans' ; 3 = '35 à 49 ans' ; 4 = '50 à 59 ans' ; 5 = '60 ans et plus'",
            "Y7REG13ST": "1 = 'Ile de France' ; 2 = 'Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)' ; 3 = 'Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)' ; 4 = 'Sud ouest (Nouvelle Aquitaine et Occitanie)' ; 5 = 'Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)'",
            "Y7AGGLO5ST": "1 = 'Zone rurale (moins de 2 000 habitants)' ; 2 = 'Zone urbaine de 2 000 à 9 999 habitants' ; 3 = 'Zone urbaine de 10 000 à 49 999 habitants' ; 4 = 'Zone urbaine de 50 000 à 199 999 habitants' ; 5 = 'Zone urbaine de 200 000 habitants et plus'",
            "Y7EMPST": "1 = 'Salarié (salarié à plein temps ou à temps partiel)' ; 2 = 'Indépendant (travaille à mon compte)' ; 3 = 'Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)'",
            "Y7PCSIST": "1 = 'Agriculteur exploitant, artisan, commerçant, chef d entreprise' ; 2 = 'Cadre supérieur' ; 3 = 'Profession intermédiaire' ; 4 = 'Employé' ; 5 = 'Ouvrier' ; 6 = 'Retraité, inactif'",
            "Y7EDUST": "1 = 'Aucun diplôme' ; 2 = 'CAP, BEP' ; 3 = 'Baccalauréat' ; 4 = 'Bac +2' ; 5 = 'Bac +3 et plus'",
            "Y7REL1ST": "1 = 'Catholique' ; 2 = 'Juive' ; 3 = 'Musulmane' ; 4 = 'Autre religion (protestante, boudhiste ou autre)' ; 5 = 'Sans religion'",
            "Y7ECO2ST2": "1 = 'Moins de 1 250 euros' ; 2 = 'De 1 250 euros à 1 999 euros' ; 3 = 'De 2 000 à 3 499 euros' ; 4 = 'De 3 500 à 4 999 euros' ; 5 = '5 000 euros et plus'",
            "Y7INTPOLST": "1 = 'Beaucoup' ; 2 = 'Un peu' ; 3 = 'Pas vraiment' ; 4 = 'Pas du tout'",
            "Y7Q7ST": "1 = 'Très à gauche' ; 2 = 'Plutôt à gauche' ; 3 = 'Au centre' ; 4 = 'Plutôt à droite' ; 5 = 'Très à droite'",
            "Y7PROXST": "1 = 'Extême gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)' ; 2 = 'Gauche (Parti Socialiste, Europe Ecologie - Les Verts)' ; 3 = 'Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))' ; 4 = 'Droite (Les Républicains)' ; 5 = 'Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)' ; 6 = 'Autre parti ou aucun parti'"
        }
        # définir le texte complet à afficher (avec parties fixes et variables en fonction du choix effectué)
        m = ui.modal(
            "La variable '%s' correspond à ou est calculée à partir de la question suivante posée aux répondants : \
            '%s', \
            et ses modalités de réponse (inchangées par rapport au questionnaire ou regroupées pour les présents graphiques) sont : \
            %s." % (
                dico_nom_var.get(
                    "%s" % input.Select_VarSD_AccVues_Legis_T2()
                ),
                dico_question_var.get("%s" % input.Select_VarSD_AccVues_Legis_T2()),
                dico_modalite_var.get("%s" % input.Select_VarSD_AccVues_Legis_T2())
            ),
            title="Informations complémentaires sur la variable socio-démographique choisie :",
            easy_close=False
        )
        ui.modal_show(m)

    # graphique
    @output
    @render_plotly
    def Graph_Croise_AccVues_Legis_T2():
        # définir la partie variable du titre
        dico_titre = {
            "Y7SEXEST": "du genre",
            "Y7AGERST": "de l'âge",
            "Y7REG13ST": "de la région de résidence",
            "Y7AGGLO5ST": "de la taille de l'agglomération de résidence",
            "Y7EMPST": "du type d'emploi occupé",
            "Y7PCSIST": "de la catégorie socio-professionnelle",
            "Y7EDUST": "du niveau de scolarité atteint",
            "Y7REL1ST": "de la religion",
            "Y7ECO2ST2": "du revenu mensuel du foyer",
            "Y7INTPOLST": "de l'intérêt pour la politique",
            "Y7Q7ST": "du positionnement idéologique",
            "Y7PROXST": "de la préférence partisane"
        }
        # définir la partie variable du titre de la légende
        dico_legende = {
            "Y7SEXEST": "Genre",
            "Y7AGERST": "Âge",
            "Y7REG13ST": "Région",
            "Y7AGGLO5ST": "Taille d'agglomération",
            "Y7EMPST": "Type d'emploi occupé",
            "Y7PCSIST": "Catégorie professionnelle",
            "Y7EDUST": "Niveau de scolarité atteint",
            "Y7REL1ST": "Religion",
            "Y7ECO2ST2": "Revenu mensuel du foyer",
            "Y7INTPOLST": "Intérêt pour la politique",
            "Y7Q7ST": "Positionnement idéologique",
            "Y7PROXST": "Préférence partisane"
        }
        # définir l'échelle de l'axe des ordonnées en fonction des
        # valeurs prises par la variable socio-démographique choisie
        dico_echelleY = {
            "Y7SEXEST": [10, 40],
            "Y7AGERST": [10, 45],
            "Y7REG13ST": [15, 35],
            "Y7AGGLO5ST": [15, 35],
            "Y7EMPST": [15, 40],
            "Y7PCSIST": [10, 45],
            "Y7EDUST": [15, 40],
            "Y7REL1ST": [10, 45],
            "Y7ECO2ST2": [10, 45],
            "Y7INTPOLST": [0, 75],
            "Y7Q7ST": [5, 40],
            "Y7PROXST": [5, 55],
        }
        # définir les modalités des variables socio-démo et leur ordre
        dico_modalite_var = {
            "Y7SEXEST": "1 = 'Homme' ; 2 = 'Femme'",
            "Y7AGERST": "1 = '18 à 24 ans' ; 2 = '25 à 34 ans' ; 3 = '35 à 49 ans' ; 4 = '50 à 59 ans' ; 5 = '60 ans et plus'",
            "Y7REG13ST": "1 = 'Ile de France' ; 2 = 'Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)' ; 3 = 'Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)' ; 4 = 'Sud ouest (Nouvelle Aquitaine et Occitanie)' ; 5 = 'Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)'",
            "Y7AGGLO5ST": "1 = 'Zone rurale (moins de 2 000 habitants)' ; 2 = 'Zone urbaine de 2 000 à 9 999 habitants' ; 3 = 'Zone urbaine de 10 000 à 49 999 habitants' ; 4 = 'Zone urbaine de 50 000 à 199 999 habitants' ; 5 = 'Zone urbaine de 200 000 habitants et plus'",
            "Y7EMPST": "1 = 'Salarié (salarié à plein temps ou à temps partiel)' ; 2 = 'Indépendant (travaille à mon compte)' ; 3 = 'Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)'",
            "Y7PCSIST": "1 = 'Agriculteur exploitant, artisan, commerçant, chef d entreprise' ; 2 = 'Cadre supérieur' ; 3 = 'Profession intermédiaire' ; 4 = 'Employé' ; 5 = 'Ouvrier' ; 6 = 'Retraité, inactif'",
            "Y7EDUST": "1 = 'Aucun diplôme' ; 2 = 'CAP, BEP' ; 3 = 'Baccalauréat' ; 4 = 'Bac +2' ; 5 = 'Bac +3 et plus'",
            "Y7REL1ST": "1 = 'Catholique' ; 2 = 'Juive' ; 3 = 'Musulmane' ; 4 = 'Autre religion (protestante, boudhiste ou autre)' ; 5 = 'Sans religion'",
            "Y7ECO2ST2": "1 = 'Moins de 1 250 euros' ; 2 = 'De 1 250 euros à 1 999 euros' ; 3 = 'De 2 000 à 3 499 euros' ; 4 = 'De 3 500 à 4 999 euros' ; 5 = '5 000 euros et plus'",
            "Y7INTPOLST": "1 = 'Beaucoup' ; 2 = 'Un peu' ; 3 = 'Pas vraiment' ; 4 = 'Pas du tout'",
            "Y7Q7ST": "1 = 'Très à gauche' ; 2 = 'Plutôt à gauche' ; 3 = 'Au centre' ; 4 = 'Plutôt à droite' ; 5 = 'Très à droite'",
            "Y7PROXST": "1 = 'Très à gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)' ; 2 = 'Gauche (Parti Socialiste, Europe Ecologie - Les Verts)' ; 3 = 'Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))' ; 4 = 'Droite (Les Républicains)' ; 5 = 'Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)' ; 6 = 'Autre parti ou aucun parti'"
        }
        # définir un dictionnaire qui contient l'ordre figé des modalités pour chaque variable socio-démographique
        dico_ordre_modalites = {
            "Y7SEXEST": [
                "Homme",
                "Femme"
            ],
            "Y7AGERST": [
                "18 à 24 ans",
                "25 à 34 ans",
                "35 à 49 ans",
                "50 à 59 ans",
                "60 ans et plus"
            ],
            "Y7REG13ST": [
                "Ile de France",
                "Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)",
                "Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)",
                "Sud ouest (Nouvelle Aquitaine et Occitanie)",
                "Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)"
            ],
            "Y7AGGLO5ST": [
                "Zone rurale (moins de 2 000 habitants)",
                "Zone urbaine de 2 000 à 9 999 habitants",
                "Zone urbaine de 10 000 à 49 999 habitants",
                "Zone urbaine de 50 000 à 199 999 habitants",
                "Zone urbaine de 200 000 habitants et plus"
            ],
            "Y7EMPST": [
                "Salarié (salarié à plein temps ou à temps partiel)",
                "Indépendant (travaille à mon compte)",
                "Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)"
            ],
            "Y7PCSIST": [
                "Agriculteur exploitant, artisan, commerçant, chef d entreprise",
                "Cadre supérieur",
                "Profession intermédiaire",
                "Employé",
                "Ouvrier",
                "Retraité, inactif"
            ],
            "Y7EDUST": [
                "Aucun diplôme",
                "CAP, BEP",
                "Baccalauréat",
                "Bac +2",
                "Bac +3 et plus"
            ],
            "Y7REL1ST": [
                "Catholique",
                "Juive",
                "Musulmane",
                "Autre religion (protestante, boudhiste ou autre)",
                "Sans religion"
            ],
            "Y7ECO2ST2": [
                "Moins de 1 250 euros",
                "De 1 250 euros à 1 999 euros",
                "De 2 000 à 3 499 euros",
                "De 3 500 à 4 999 euros",
                "5 000 euros et plus"
            ],
            "Y7INTPOLST": [
                "Beaucoup",
                "Un peu",
                "Pas vraiment",
                "Pas du tout"
            ],
            "Y7Q7ST": [
                "Très à gauche",
                "Plutôt à gauche",
                "Au centre",
                "Plutôt à droite",
                "Très à droite"
            ],
            "Y7PROXST": [
                "Très à gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)",
                "Gauche (Parti Socialiste, Europe Ecologie - Les Verts)",
                "Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))",
                "Droite (Les Républicains)",
                "Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)",
                "Autre parti ou aucun parti"
            ]
        }
        # définir une fonction qui affiche les étiquettes
        # des modalités de la variablr SD choisie dans la légende
        # sur plusieurs lignes si leur longueur initiale dépasse la
        # largeur du cadre de la légende (version robuste avec gestion des erreurs)
        def wrap_label(label, max_length=20):
            try:
                # Si le label est un float ou NaN
                if pd.isna(label) or isinstance(label, float):
                    return "Non renseigné"
                # Convertir en string si ce n'est pas déjà le cas
                label = str(label).strip()
                # Si la chaîne est vide après nettoyage
                if not label:
                    return "Non renseigné"
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
            except Exception as e:
                print(f"Erreur dans wrap_label avec {label}: {str(e)}")
                return str(label) 
                # retourner le label tel quel en cas d'erreur
        # lire le fichier CSV des données
        csvfile = "data/T_w7_pl6st_" + "%s" % input.Select_VarSD_AccVues_Legis_T2().lower()[2:] + ".csv"
        df = pd.read_csv(csvfile)
        # nettoyer les données lues
        var_sd = input.Select_VarSD_AccVues_Legis_T2()
        df[var_sd] = df[var_sd].fillna("Non renseigné")  # Gérer les NaN
        df[var_sd] = df[var_sd].astype(str)  # Convertir en string
        df['Y7PL6ST'] = df['Y7PL6ST'].fillna("Non renseigné")
        # s'assurer que toutes les modalités sont des chaînes de caractères dans "dico_ordre_modalites"
        dico_ordre_modalites[var_sd] = [str(modal) for modal in dico_ordre_modalites[var_sd]]
        # filtrer pour ne garder que les modalités définies dans "dico_ordre_modalites"
        df = df[df[var_sd].isin(dico_ordre_modalites[var_sd])]
        # définir l'ordre des modalités pour Y7PL6ST
        ordre_modalites = [
            "Souvent",
            "Rarement ou jamais"
        ]
        # créer une colonne catégorielle avec l'ordre souhaité pour la variable socio-démographique
        var_sd = input.Select_VarSD_AccVues_Legis_T2()
        df[var_sd] = pd.Categorical(
            df[var_sd],
            categories=dico_ordre_modalites[var_sd],
            ordered=True
        )
        # filtrer et pivoter les données
        df_pivot = df[df['Y7PL6ST'].isin(ordre_modalites)].pivot(
            index=var_sd,
            columns='Y7PL6ST',
            values='pct'
        )
        df_pivot = df_pivot.reindex(columns=ordre_modalites)
        # créer une palette de couleurs automatique
        nb_couleurs = len(df_pivot.index)
        palette = px.colors.qualitative.Plotly[:nb_couleurs]
        # créer le graphique
        fig = go.Figure()
        # ajouter les données
        for i, VarSD in enumerate(df_pivot.index):
            fig.add_trace(
                go.Bar(
                    x=ordre_modalites,
                    y=df_pivot.loc[VarSD],
                    name=wrap_label(VarSD),
                    marker_color=palette[i],
                    # afficher les valeurs sous le format 'xx.x%' dans la bulle qui s'affiche
                    # au survol de la courbe par la souris, et supprimer toutes les autres
                    # informations qui pourraient s'afficher en plus (nom de la modalité)
                    hovertemplate='%{y:.1f}%<extra></extra>',
                    # n'afficher la bulle contenant la valeur 'y' en % uniquement
                    # au-dessus de la barre verticale survolée par la souris
                    hoverinfo='y',
                    # centrer ce texte 'y' dans la bulle
                    hoverlabel=dict(
                        align='auto'
                    )
                )
            )
         # mettre en forme le graphique
        fig.update_layout(
            barmode='group', # barres séparées et groupées pour les modalités de la VarSD choisie
            title={
                'text': "Accord de vues avec l'entourage en fonction %s" % dico_titre.get("%s" % input.Select_VarSD_AccVues_Legis_T2()),
                'y':0.98,
                'x':0.01,
                'xanchor': 'left',
                'yanchor': 'top'
            },
            # définir le titre de la légende
            legend_title="%s" % dico_legende.get("%s" % input.Select_VarSD_AccVues_Legis_T2()),
            # définir l'affichage séparé des valeurs de % affichées au-dessus de
            # chaque barre verticale quand la souris la survole
            hovermode="closest",
            # définir le thème général de l'apparence du graphique
            template="plotly_white",
            # définir le titre de l'axe des ordonnées et son apparence
            yaxis_title=dict(
                text='Pourcentage de répondants (%)',
                font_size=12
            ),
            # définir les sources des données
            annotations=[
                dict(
                    xref='paper', # utiliser la largeur totale du graphique comme référence
                    yref='paper', # utiliser la hauteur totale du graphique comme référence
                    x=0.5, # placer le point d'ancrage au milieu de la largeur
                    y=-0.1, # valeur à ajuster pour positionner verticalement le texte sous le graphique
                    xanchor='center', # centrer le texte par rapport au point d'ancrage
                    yanchor='top',
                    text=
                        'Enquête électorale française pour les ' +
                        'élections européennes de juin 2024, ' +
                        'par Ipsos Sopra Steria, Cevipof, ' +
                        'Le Monde, Fondation Jean Jaurès et ' +
                        'Institut Montaigne (2024)',
                    font=dict(
                        size=10,
                        color='grey'
                    ),
                    showarrow=False
                )
            ],
            # définir les marges de la zone graphique
            # (augmentées à droite pour le cadre fixe de la légende)
            margin=dict(
                b=50, # b = bottom
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
            ),
        )
        # retourner le graphique
        return fig


    ###########################################################
    # onglet 08 : AVIS SUR LES CONSEQUENCES DE LA DISSOLUTION #
    ###########################################################

    # bouton 01 : décrire la question posée dans l'enquête
    @reactive.effect
    @reactive.event(input.Show_AVCONSDISS_Question_Legis_T2)
    def _():
        m = ui.modal(
            "La question posée aux répondants est la suivante : 'Diriez-vous que la décision d’Emmanuel Macron de dissoudre l’Assemblée nationale, et les résultats des élections législatives qui ont suivi cette décision, ont eu des conséquences positives ou négatives pour la France ?'",
            title="Informations complémentaires sur la question contenue dans l'enquête :",
            easy_close=False
        )
        ui.modal_show(m)

    # bouton 02 : décrire la variable de l'intention d'aller voter choisie
    @reactive.effect
    @reactive.event(input.Show_AVCONSDISSST_Info_Legis_T2)
    def _():
        m = ui.modal(
            "La variable sur l'avis sur les conséquences de la dissolution de l'Assemblée nationale de la part des répondants présentée ici sur les graphiques est une modalité synthétique de la question posée aux répondants de l'enquête. \
            Ainsi, à partir des quatre modalités de réponse à la question de l'enquête, on en construit deux : 'Des conséquences positives (très positives ou plutôt positives)' ou 'Des conséquences négatives (très négatives ou plutôt négatives)'.",
            title="Informations complémentaires sur la variable choisie pour les graphiques :",
            easy_close=False
        )
        ui.modal_show(m)

    # bouton 03 : afficher la description de la variable socio-démographique choisie
    # avec plusieurs parties de texte qui dépendent de ce choix (via des dictionnaires)
    @reactive.effect
    @reactive.event(input.Show_VarSD_AvConsDiss_Info_Legis_T2)
    def _():
        # définir le nom de la variable socio-démographique choisie
        dico_nom_var = {
            "Y7SEXEST": "Genre",
            "Y7AGERST": "Âge",
            "Y7REG13ST": "Région",
            "Y7AGGLO5ST": "Taille d'agglomération",
            "Y7EMPST": "Type d'emploi occupé",
            "Y7PCSIST": "Catégorie professionnelle",
            "Y7EDUST": "Niveau de scolarité atteint",
            "Y7REL1ST": "Religion",
            "Y7ECO2ST2": "Revenu mensuel du foyer",
            "Y7INTPOLST": "Intérêt pour la politique",
            "Y7Q7ST": "Positionnement idéologique",
            "Y7PROXST": "Préférence partisane"
        }
        # définir la question de l'enquête associée à la variable socio-démographique choisie
        dico_question_var = {
            "Y7SEXEST": "Êtes-vous ?",
            "Y7AGERST": "Quelle est votre date de naissance ?",
            "Y7REG13ST": "Veuillez indiquer le département et la commune où vous résidez.",
            "Y7AGGLO5ST": "Veuillez indiquer le département et la commune où vous résidez.",
            "Y7EMPST": "Quelle est votre situation professionnelle actuelle ?",
            "Y7PCSIST": "Quelle est votre situation professionnelle actuelle ?",
            "Y7EDUST": "Choisissez votre niveau de scolarité le plus élevé.",
            "Y7REL1ST": "Quelle est votre religion, si vous en avez une ?",
            "Y7ECO2ST2": " Pour finir, nous avons besoin de connaître, à des fins statistiques uniquement, la tranche dans laquelle se situe le revenu MENSUEL NET de votre FOYER après déduction des impôts sur le revenu (veuillez considérer toutes vos sources de revenus: salaires, bourses, prestations retraite et sécurité sociale, dividendes, revenus immobiliers, pensions alimentaires etc.).",
            "Y7INTPOLST": "De manière générale, diriez-vous que vous vous intéressez à la politique ?",
            "Y7Q7ST": "Sur une échelle de 0 à 10, où 0 correspond à la gauche et 10 correspond à la droite, où diriez-vous que vous vous situez ?",
            "Y7PROXST": "De quel parti vous sentez-vous proche ou moins éloigné que les autres ?"
        }
        # définir les modalités de réponse à la question de l'enquête associée à la variable socio-démographique choisie
        dico_modalite_var = {
            "Y7SEXEST": "1 = 'Homme' ; 2 = 'Femme'",
            "Y7AGERST": "1 = '18 à 24 ans' ; 2 = '25 à 34 ans' ; 3 = '35 à 49 ans' ; 4 = '50 à 59 ans' ; 5 = '60 ans et plus'",
            "Y7REG13ST": "1 = 'Ile de France' ; 2 = 'Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)' ; 3 = 'Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)' ; 4 = 'Sud ouest (Nouvelle Aquitaine et Occitanie)' ; 5 = 'Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)'",
            "Y7AGGLO5ST": "1 = 'Zone rurale (moins de 2 000 habitants)' ; 2 = 'Zone urbaine de 2 000 à 9 999 habitants' ; 3 = 'Zone urbaine de 10 000 à 49 999 habitants' ; 4 = 'Zone urbaine de 50 000 à 199 999 habitants' ; 5 = 'Zone urbaine de 200 000 habitants et plus'",
            "Y7EMPST": "1 = 'Salarié (salarié à plein temps ou à temps partiel)' ; 2 = 'Indépendant (travaille à mon compte)' ; 3 = 'Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)'",
            "Y7PCSIST": "1 = 'Agriculteur exploitant, artisan, commerçant, chef d entreprise' ; 2 = 'Cadre supérieur' ; 3 = 'Profession intermédiaire' ; 4 = 'Employé' ; 5 = 'Ouvrier' ; 6 = 'Retraité, inactif'",
            "Y7EDUST": "1 = 'Aucun diplôme' ; 2 = 'CAP, BEP' ; 3 = 'Baccalauréat' ; 4 = 'Bac +2' ; 5 = 'Bac +3 et plus'",
            "Y7REL1ST": "1 = 'Catholique' ; 2 = 'Juive' ; 3 = 'Musulmane' ; 4 = 'Autre religion (protestante, boudhiste ou autre)' ; 5 = 'Sans religion'",
            "Y7ECO2ST2": "1 = 'Moins de 1 250 euros' ; 2 = 'De 1 250 euros à 1 999 euros' ; 3 = 'De 2 000 à 3 499 euros' ; 4 = 'De 3 500 à 4 999 euros' ; 5 = '5 000 euros et plus'",
            "Y7INTPOLST": "1 = 'Beaucoup' ; 2 = 'Un peu' ; 3 = 'Pas vraiment' ; 4 = 'Pas du tout'",
            "Y7Q7ST": "1 = 'Très à gauche' ; 2 = 'Plutôt à gauche' ; 3 = 'Au centre' ; 4 = 'Plutôt à droite' ; 5 = 'Très à droite'",
            "Y7PROXST": "1 = 'Extême gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)' ; 2 = 'Gauche (Parti Socialiste, Europe Ecologie - Les Verts)' ; 3 = 'Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))' ; 4 = 'Droite (Les Républicains)' ; 5 = 'Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)' ; 6 = 'Autre parti ou aucun parti'"
        }
        # définir le texte complet à afficher (avec parties fixes et variables en fonction du choix effectué)
        m = ui.modal(
            "La variable '%s' correspond à ou est calculée à partir de la question suivante posée aux répondants : \
            '%s', \
            et ses modalités de réponse (inchangées par rapport au questionnaire ou regroupées pour les présents graphiques) sont : \
            %s." % (
                dico_nom_var.get(
                    "%s" % input.Select_VarSD_AvConsDiss_Legis_T2()
                ),
                dico_question_var.get("%s" % input.Select_VarSD_AvConsDiss_Legis_T2()),
                dico_modalite_var.get("%s" % input.Select_VarSD_AvConsDiss_Legis_T2())
            ),
            title="Informations complémentaires sur la variable socio-démographique choisie :",
            easy_close=False
        )
        ui.modal_show(m)

    # graphique
    @output
    @render_plotly
    def Graph_Croise_AvConsDiss_Legis_T2():
        # définir la partie variable du titre
        dico_titre = {
            "Y7SEXEST": "du genre",
            "Y7AGERST": "de l'âge",
            "Y7REG13ST": "de la région de résidence",
            "Y7AGGLO5ST": "de la taille de l'agglomération de résidence",
            "Y7EMPST": "du type d'emploi occupé",
            "Y7PCSIST": "de la catégorie socio-professionnelle",
            "Y7EDUST": "du niveau de scolarité atteint",
            "Y7REL1ST": "de la religion",
            "Y7ECO2ST2": "du revenu mensuel du foyer",
            "Y7INTPOLST": "de l'intérêt pour la politique",
            "Y7Q7ST": "du positionnement idéologique",
            "Y7PROXST": "de la préférence partisane"
        }
        # définir la partie variable du titre de la légende
        dico_legende = {
            "Y7SEXEST": "Genre",
            "Y7AGERST": "Âge",
            "Y7REG13ST": "Région",
            "Y7AGGLO5ST": "Taille d'agglomération",
            "Y7EMPST": "Type d'emploi occupé",
            "Y7PCSIST": "Catégorie professionnelle",
            "Y7EDUST": "Niveau de scolarité atteint",
            "Y7REL1ST": "Religion",
            "Y7ECO2ST2": "Revenu mensuel du foyer",
            "Y7INTPOLST": "Intérêt pour la politique",
            "Y7Q7ST": "Positionnement idéologique",
            "Y7PROXST": "Préférence partisane"
        }
        # définir l'échelle de l'axe des ordonnées en fonction des
        # valeurs prises par la variable socio-démographique choisie
        dico_echelleY = {
            "Y7SEXEST": [10, 40],
            "Y7AGERST": [10, 45],
            "Y7REG13ST": [15, 35],
            "Y7AGGLO5ST": [15, 35],
            "Y7EMPST": [15, 40],
            "Y7PCSIST": [10, 45],
            "Y7EDUST": [15, 40],
            "Y7REL1ST": [10, 45],
            "Y7ECO2ST2": [10, 45],
            "Y7INTPOLST": [0, 75],
            "Y7Q7ST": [5, 40],
            "Y7PROXST": [5, 55],
        }
        # définir les modalités des variables socio-démo et leur ordre
        dico_modalite_var = {
            "Y7SEXEST": "1 = 'Homme' ; 2 = 'Femme'",
            "Y7AGERST": "1 = '18 à 24 ans' ; 2 = '25 à 34 ans' ; 3 = '35 à 49 ans' ; 4 = '50 à 59 ans' ; 5 = '60 ans et plus'",
            "Y7REG13ST": "1 = 'Ile de France' ; 2 = 'Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)' ; 3 = 'Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)' ; 4 = 'Sud ouest (Nouvelle Aquitaine et Occitanie)' ; 5 = 'Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)'",
            "Y7AGGLO5ST": "1 = 'Zone rurale (moins de 2 000 habitants)' ; 2 = 'Zone urbaine de 2 000 à 9 999 habitants' ; 3 = 'Zone urbaine de 10 000 à 49 999 habitants' ; 4 = 'Zone urbaine de 50 000 à 199 999 habitants' ; 5 = 'Zone urbaine de 200 000 habitants et plus'",
            "Y7EMPST": "1 = 'Salarié (salarié à plein temps ou à temps partiel)' ; 2 = 'Indépendant (travaille à mon compte)' ; 3 = 'Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)'",
            "Y7PCSIST": "1 = 'Agriculteur exploitant, artisan, commerçant, chef d entreprise' ; 2 = 'Cadre supérieur' ; 3 = 'Profession intermédiaire' ; 4 = 'Employé' ; 5 = 'Ouvrier' ; 6 = 'Retraité, inactif'",
            "Y7EDUST": "1 = 'Aucun diplôme' ; 2 = 'CAP, BEP' ; 3 = 'Baccalauréat' ; 4 = 'Bac +2' ; 5 = 'Bac +3 et plus'",
            "Y7REL1ST": "1 = 'Catholique' ; 2 = 'Juive' ; 3 = 'Musulmane' ; 4 = 'Autre religion (protestante, boudhiste ou autre)' ; 5 = 'Sans religion'",
            "Y7ECO2ST2": "1 = 'Moins de 1 250 euros' ; 2 = 'De 1 250 euros à 1 999 euros' ; 3 = 'De 2 000 à 3 499 euros' ; 4 = 'De 3 500 à 4 999 euros' ; 5 = '5 000 euros et plus'",
            "Y7INTPOLST": "1 = 'Beaucoup' ; 2 = 'Un peu' ; 3 = 'Pas vraiment' ; 4 = 'Pas du tout'",
            "Y7Q7ST": "1 = 'Très à gauche' ; 2 = 'Plutôt à gauche' ; 3 = 'Au centre' ; 4 = 'Plutôt à droite' ; 5 = 'Très à droite'",
            "Y7PROXST": "1 = 'Très à gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)' ; 2 = 'Gauche (Parti Socialiste, Europe Ecologie - Les Verts)' ; 3 = 'Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))' ; 4 = 'Droite (Les Républicains)' ; 5 = 'Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)' ; 6 = 'Autre parti ou aucun parti'"
        }
        # définir un dictionnaire qui contient l'ordre figé des modalités pour chaque variable socio-démographique
        dico_ordre_modalites = {
            "Y7SEXEST": [
                "Homme",
                "Femme"
            ],
            "Y7AGERST": [
                "18 à 24 ans",
                "25 à 34 ans",
                "35 à 49 ans",
                "50 à 59 ans",
                "60 ans et plus"
            ],
            "Y7REG13ST": [
                "Ile de France",
                "Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)",
                "Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)",
                "Sud ouest (Nouvelle Aquitaine et Occitanie)",
                "Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)"
            ],
            "Y7AGGLO5ST": [
                "Zone rurale (moins de 2 000 habitants)",
                "Zone urbaine de 2 000 à 9 999 habitants",
                "Zone urbaine de 10 000 à 49 999 habitants",
                "Zone urbaine de 50 000 à 199 999 habitants",
                "Zone urbaine de 200 000 habitants et plus"
            ],
            "Y7EMPST": [
                "Salarié (salarié à plein temps ou à temps partiel)",
                "Indépendant (travaille à mon compte)",
                "Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)"
            ],
            "Y7PCSIST": [
                "Agriculteur exploitant, artisan, commerçant, chef d entreprise",
                "Cadre supérieur",
                "Profession intermédiaire",
                "Employé",
                "Ouvrier",
                "Retraité, inactif"
            ],
            "Y7EDUST": [
                "Aucun diplôme",
                "CAP, BEP",
                "Baccalauréat",
                "Bac +2",
                "Bac +3 et plus"
            ],
            "Y7REL1ST": [
                "Catholique",
                "Juive",
                "Musulmane",
                "Autre religion (protestante, boudhiste ou autre)",
                "Sans religion"
            ],
            "Y7ECO2ST2": [
                "Moins de 1 250 euros",
                "De 1 250 euros à 1 999 euros",
                "De 2 000 à 3 499 euros",
                "De 3 500 à 4 999 euros",
                "5 000 euros et plus"
            ],
            "Y7INTPOLST": [
                "Beaucoup",
                "Un peu",
                "Pas vraiment",
                "Pas du tout"
            ],
            "Y7Q7ST": [
                "Très à gauche",
                "Plutôt à gauche",
                "Au centre",
                "Plutôt à droite",
                "Très à droite"
            ],
            "Y7PROXST": [
                "Très à gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)",
                "Gauche (Parti Socialiste, Europe Ecologie - Les Verts)",
                "Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))",
                "Droite (Les Républicains)",
                "Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)",
                "Autre parti ou aucun parti"
            ]
        }
        # définir une fonction qui affiche les étiquettes
        # des modalités de la variablr SD choisie dans la légende
        # sur plusieurs lignes si leur longueur initiale dépasse la
        # largeur du cadre de la légende (version robuste avec gestion des erreurs)
        def wrap_label(label, max_length=20):
            try:
                # Si le label est un float ou NaN
                if pd.isna(label) or isinstance(label, float):
                    return "Non renseigné"
                # Convertir en string si ce n'est pas déjà le cas
                label = str(label).strip()
                # Si la chaîne est vide après nettoyage
                if not label:
                    return "Non renseigné"
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
            except Exception as e:
                print(f"Erreur dans wrap_label avec {label}: {str(e)}")
                return str(label) 
                # retourner le label tel quel en cas d'erreur
        # lire le fichier CSV des données
        csvfile = "data/T_w7_pl13st_" + "%s" % input.Select_VarSD_AvConsDiss_Legis_T2().lower()[2:] + ".csv"
        df = pd.read_csv(csvfile)
        # nettoyer les données lues
        var_sd = input.Select_VarSD_AvConsDiss_Legis_T2()
        df[var_sd] = df[var_sd].fillna("Non renseigné")  # Gérer les NaN
        df[var_sd] = df[var_sd].astype(str)  # Convertir en string
        df['Y7PL13ST'] = df['Y7PL13ST'].fillna("Non renseigné")
        # s'assurer que toutes les modalités sont des chaînes de caractères dans "dico_ordre_modalites"
        dico_ordre_modalites[var_sd] = [str(modal) for modal in dico_ordre_modalites[var_sd]]
        # filtrer pour ne garder que les modalités définies dans "dico_ordre_modalites"
        df = df[df[var_sd].isin(dico_ordre_modalites[var_sd])]
        # définir l'ordre des modalités pour Y7PL13ST
        ordre_modalites = [
            "Des conséquences positives",
            "Des conséquences négatives"
        ]
        # créer une colonne catégorielle avec l'ordre souhaité pour la variable socio-démographique
        var_sd = input.Select_VarSD_AvConsDiss_Legis_T2()
        df[var_sd] = pd.Categorical(
            df[var_sd],
            categories=dico_ordre_modalites[var_sd],
            ordered=True
        )
        # filtrer et pivoter les données
        df_pivot = df[df['Y7PL13ST'].isin(ordre_modalites)].pivot(
            index=var_sd,
            columns='Y7PL13ST',
            values='pct'
        )
        df_pivot = df_pivot.reindex(columns=ordre_modalites)
        # créer une palette de couleurs automatique
        nb_couleurs = len(df_pivot.index)
        palette = px.colors.qualitative.Plotly[:nb_couleurs]
        # créer le graphique
        fig = go.Figure()
        # ajouter les données
        for i, VarSD in enumerate(df_pivot.index):
            fig.add_trace(
                go.Bar(
                    x=ordre_modalites,
                    y=df_pivot.loc[VarSD],
                    name=wrap_label(VarSD),
                    marker_color=palette[i],
                    # afficher les valeurs sous le format 'xx.x%' dans la bulle qui s'affiche
                    # au survol de la courbe par la souris, et supprimer toutes les autres
                    # informations qui pourraient s'afficher en plus (nom de la modalité)
                    hovertemplate='%{y:.1f}%<extra></extra>',
                    # n'afficher la bulle contenant la valeur 'y' en % uniquement
                    # au-dessus de la barre verticale survolée par la souris
                    hoverinfo='y',
                    # centrer ce texte 'y' dans la bulle
                    hoverlabel=dict(
                        align='auto'
                    )
                )
            )
         # mettre en forme le graphique
        fig.update_layout(
            barmode='group', # barres séparées et groupées pour les modalités de la VarSD choisie
            title={
                'text': "Avis sur les conséquences de la dissolution en fonction %s" % dico_titre.get("%s" % input.Select_VarSD_AvConsDiss_Legis_T2()),
                'y':0.98,
                'x':0.01,
                'xanchor': 'left',
                'yanchor': 'top'
            },
            # définir le titre de la légende
            legend_title="%s" % dico_legende.get("%s" % input.Select_VarSD_AvConsDiss_Legis_T2()),
            # définir l'affichage séparé des valeurs de % affichées au-dessus de
            # chaque barre verticale quand la souris la survole
            hovermode="closest",
            # définir le thème général de l'apparence du graphique
            template="plotly_white",
            # définir le titre de l'axe des ordonnées et son apparence
            yaxis_title=dict(
                text='Pourcentage de répondants (%)',
                font_size=12
            ),
            # définir les sources des données
            annotations=[
                dict(
                    xref='paper', # utiliser la largeur totale du graphique comme référence
                    yref='paper', # utiliser la hauteur totale du graphique comme référence
                    x=0.5, # placer le point d'ancrage au milieu de la largeur
                    y=-0.1, # valeur à ajuster pour positionner verticalement le texte sous le graphique
                    xanchor='center', # centrer le texte par rapport au point d'ancrage
                    yanchor='top',
                    text=
                        'Enquête électorale française pour les ' +
                        'élections européennes de juin 2024, ' +
                        'par Ipsos Sopra Steria, Cevipof, ' +
                        'Le Monde, Fondation Jean Jaurès et ' +
                        'Institut Montaigne (2024)',
                    font=dict(
                        size=10,
                        color='grey'
                    ),
                    showarrow=False
                )
            ],
            # définir les marges de la zone graphique
            # (augmentées à droite pour le cadre fixe de la légende)
            margin=dict(
                b=50, # b = bottom
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
            ),
        )
        # retourner le graphique
        return fig


    #####################################################################
    # onglet 09 : DEGRE DE CONFIANCE EN LA NOUVELLE ASSEMBLEE NATIONALE #
    #####################################################################

    # bouton 01 : décrire la question posée dans l'enquête
    @reactive.effect
    @reactive.event(input.Show_DEGCONFAN_Question_Legis_T2)
    def _():
        m = ui.modal(
            "La question posée aux répondants est la suivante : 'Diriez-vous que vous avez confiance ou non dans la nouvelle Assemblée nationale, issue des élections législatives des 30 juin et 7 juillet dernier ?'",
            title="Informations complémentaires sur la question contenue dans l'enquête :",
            easy_close=False
        )
        ui.modal_show(m)

    # bouton 02 : décrire la variable de l'intention d'aller voter choisie
    @reactive.effect
    @reactive.event(input.Show_DEGCONFANST_Info_Legis_T2)
    def _():
        m = ui.modal(
            "La variable sur le degré de confiance des répondants envers la nouvelle Assemblée nationale présentée ici sur les graphiques est une modalité synthétique de la question posée aux répondants de l'enquête. \
            Ainsi, à partir des quatre modalités de réponse à la question de l'enquête, on en construit deux : 'Confiance (tout à fait confiance ou plutôt confiance)' ou 'Pas confiance (pas du tout confiance ou plutôt pas confiance)'.",
            title="Informations complémentaires sur la variable choisie pour les graphiques :",
            easy_close=False
        )
        ui.modal_show(m)

    # bouton 03 : afficher la description de la variable socio-démographique choisie
    # avec plusieurs parties de texte qui dépendent de ce choix (via des dictionnaires)
    @reactive.effect
    @reactive.event(input.Show_VarSD_DegConfAN_Info_Legis_T2)
    def _():
        # définir le nom de la variable socio-démographique choisie
        dico_nom_var = {
            "Y7SEXEST": "Genre",
            "Y7AGERST": "Âge",
            "Y7REG13ST": "Région",
            "Y7AGGLO5ST": "Taille d'agglomération",
            "Y7EMPST": "Type d'emploi occupé",
            "Y7PCSIST": "Catégorie professionnelle",
            "Y7EDUST": "Niveau de scolarité atteint",
            "Y7REL1ST": "Religion",
            "Y7ECO2ST2": "Revenu mensuel du foyer",
            "Y7INTPOLST": "Intérêt pour la politique",
            "Y7Q7ST": "Positionnement idéologique",
            "Y7PROXST": "Préférence partisane"
        }
        # définir la question de l'enquête associée à la variable socio-démographique choisie
        dico_question_var = {
            "Y7SEXEST": "Êtes-vous ?",
            "Y7AGERST": "Quelle est votre date de naissance ?",
            "Y7REG13ST": "Veuillez indiquer le département et la commune où vous résidez.",
            "Y7AGGLO5ST": "Veuillez indiquer le département et la commune où vous résidez.",
            "Y7EMPST": "Quelle est votre situation professionnelle actuelle ?",
            "Y7PCSIST": "Quelle est votre situation professionnelle actuelle ?",
            "Y7EDUST": "Choisissez votre niveau de scolarité le plus élevé.",
            "Y7REL1ST": "Quelle est votre religion, si vous en avez une ?",
            "Y7ECO2ST2": " Pour finir, nous avons besoin de connaître, à des fins statistiques uniquement, la tranche dans laquelle se situe le revenu MENSUEL NET de votre FOYER après déduction des impôts sur le revenu (veuillez considérer toutes vos sources de revenus: salaires, bourses, prestations retraite et sécurité sociale, dividendes, revenus immobiliers, pensions alimentaires etc.).",
            "Y7INTPOLST": "De manière générale, diriez-vous que vous vous intéressez à la politique ?",
            "Y7Q7ST": "Sur une échelle de 0 à 10, où 0 correspond à la gauche et 10 correspond à la droite, où diriez-vous que vous vous situez ?",
            "Y7PROXST": "De quel parti vous sentez-vous proche ou moins éloigné que les autres ?"
        }
        # définir les modalités de réponse à la question de l'enquête associée à la variable socio-démographique choisie
        dico_modalite_var = {
            "Y7SEXEST": "1 = 'Homme' ; 2 = 'Femme'",
            "Y7AGERST": "1 = '18 à 24 ans' ; 2 = '25 à 34 ans' ; 3 = '35 à 49 ans' ; 4 = '50 à 59 ans' ; 5 = '60 ans et plus'",
            "Y7REG13ST": "1 = 'Ile de France' ; 2 = 'Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)' ; 3 = 'Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)' ; 4 = 'Sud ouest (Nouvelle Aquitaine et Occitanie)' ; 5 = 'Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)'",
            "Y7AGGLO5ST": "1 = 'Zone rurale (moins de 2 000 habitants)' ; 2 = 'Zone urbaine de 2 000 à 9 999 habitants' ; 3 = 'Zone urbaine de 10 000 à 49 999 habitants' ; 4 = 'Zone urbaine de 50 000 à 199 999 habitants' ; 5 = 'Zone urbaine de 200 000 habitants et plus'",
            "Y7EMPST": "1 = 'Salarié (salarié à plein temps ou à temps partiel)' ; 2 = 'Indépendant (travaille à mon compte)' ; 3 = 'Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)'",
            "Y7PCSIST": "1 = 'Agriculteur exploitant, artisan, commerçant, chef d entreprise' ; 2 = 'Cadre supérieur' ; 3 = 'Profession intermédiaire' ; 4 = 'Employé' ; 5 = 'Ouvrier' ; 6 = 'Retraité, inactif'",
            "Y7EDUST": "1 = 'Aucun diplôme' ; 2 = 'CAP, BEP' ; 3 = 'Baccalauréat' ; 4 = 'Bac +2' ; 5 = 'Bac +3 et plus'",
            "Y7REL1ST": "1 = 'Catholique' ; 2 = 'Juive' ; 3 = 'Musulmane' ; 4 = 'Autre religion (protestante, boudhiste ou autre)' ; 5 = 'Sans religion'",
            "Y7ECO2ST2": "1 = 'Moins de 1 250 euros' ; 2 = 'De 1 250 euros à 1 999 euros' ; 3 = 'De 2 000 à 3 499 euros' ; 4 = 'De 3 500 à 4 999 euros' ; 5 = '5 000 euros et plus'",
            "Y7INTPOLST": "1 = 'Beaucoup' ; 2 = 'Un peu' ; 3 = 'Pas vraiment' ; 4 = 'Pas du tout'",
            "Y7Q7ST": "1 = 'Très à gauche' ; 2 = 'Plutôt à gauche' ; 3 = 'Au centre' ; 4 = 'Plutôt à droite' ; 5 = 'Très à droite'",
            "Y7PROXST": "1 = 'Extême gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)' ; 2 = 'Gauche (Parti Socialiste, Europe Ecologie - Les Verts)' ; 3 = 'Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))' ; 4 = 'Droite (Les Républicains)' ; 5 = 'Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)' ; 6 = 'Autre parti ou aucun parti'"
        }
        # définir le texte complet à afficher (avec parties fixes et variables en fonction du choix effectué)
        m = ui.modal(
            "La variable '%s' correspond à ou est calculée à partir de la question suivante posée aux répondants : \
            '%s', \
            et ses modalités de réponse (inchangées par rapport au questionnaire ou regroupées pour les présents graphiques) sont : \
            %s." % (
                dico_nom_var.get(
                    "%s" % input.Select_VarSD_DegConfAN_Legis_T2()
                ),
                dico_question_var.get("%s" % input.Select_VarSD_DegConfAN_Legis_T2()),
                dico_modalite_var.get("%s" % input.Select_VarSD_DegConfAN_Legis_T2())
            ),
            title="Informations complémentaires sur la variable socio-démographique choisie :",
            easy_close=False
        )
        ui.modal_show(m)

    # graphique
    @output
    @render_plotly
    def Graph_Croise_DegConfAN_Legis_T2():
        # définir la partie variable du titre
        dico_titre = {
            "Y7SEXEST": "du genre",
            "Y7AGERST": "de l'âge",
            "Y7REG13ST": "de la région de résidence",
            "Y7AGGLO5ST": "de la taille de l'agglomération de résidence",
            "Y7EMPST": "du type d'emploi occupé",
            "Y7PCSIST": "de la catégorie socio-professionnelle",
            "Y7EDUST": "du niveau de scolarité atteint",
            "Y7REL1ST": "de la religion",
            "Y7ECO2ST2": "du revenu mensuel du foyer",
            "Y7INTPOLST": "de l'intérêt pour la politique",
            "Y7Q7ST": "du positionnement idéologique",
            "Y7PROXST": "de la préférence partisane"
        }
        # définir la partie variable du titre de la légende
        dico_legende = {
            "Y7SEXEST": "Genre",
            "Y7AGERST": "Âge",
            "Y7REG13ST": "Région",
            "Y7AGGLO5ST": "Taille d'agglomération",
            "Y7EMPST": "Type d'emploi occupé",
            "Y7PCSIST": "Catégorie professionnelle",
            "Y7EDUST": "Niveau de scolarité atteint",
            "Y7REL1ST": "Religion",
            "Y7ECO2ST2": "Revenu mensuel du foyer",
            "Y7INTPOLST": "Intérêt pour la politique",
            "Y7Q7ST": "Positionnement idéologique",
            "Y7PROXST": "Préférence partisane"
        }
        # définir l'échelle de l'axe des ordonnées en fonction des
        # valeurs prises par la variable socio-démographique choisie
        dico_echelleY = {
            "Y7SEXEST": [10, 40],
            "Y7AGERST": [10, 45],
            "Y7REG13ST": [15, 35],
            "Y7AGGLO5ST": [15, 35],
            "Y7EMPST": [15, 40],
            "Y7PCSIST": [10, 45],
            "Y7EDUST": [15, 40],
            "Y7REL1ST": [10, 45],
            "Y7ECO2ST2": [10, 45],
            "Y7INTPOLST": [0, 75],
            "Y7Q7ST": [5, 40],
            "Y7PROXST": [5, 55],
        }
        # définir les modalités des variables socio-démo et leur ordre
        dico_modalite_var = {
            "Y7SEXEST": "1 = 'Homme' ; 2 = 'Femme'",
            "Y7AGERST": "1 = '18 à 24 ans' ; 2 = '25 à 34 ans' ; 3 = '35 à 49 ans' ; 4 = '50 à 59 ans' ; 5 = '60 ans et plus'",
            "Y7REG13ST": "1 = 'Ile de France' ; 2 = 'Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)' ; 3 = 'Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)' ; 4 = 'Sud ouest (Nouvelle Aquitaine et Occitanie)' ; 5 = 'Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)'",
            "Y7AGGLO5ST": "1 = 'Zone rurale (moins de 2 000 habitants)' ; 2 = 'Zone urbaine de 2 000 à 9 999 habitants' ; 3 = 'Zone urbaine de 10 000 à 49 999 habitants' ; 4 = 'Zone urbaine de 50 000 à 199 999 habitants' ; 5 = 'Zone urbaine de 200 000 habitants et plus'",
            "Y7EMPST": "1 = 'Salarié (salarié à plein temps ou à temps partiel)' ; 2 = 'Indépendant (travaille à mon compte)' ; 3 = 'Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)'",
            "Y7PCSIST": "1 = 'Agriculteur exploitant, artisan, commerçant, chef d entreprise' ; 2 = 'Cadre supérieur' ; 3 = 'Profession intermédiaire' ; 4 = 'Employé' ; 5 = 'Ouvrier' ; 6 = 'Retraité, inactif'",
            "Y7EDUST": "1 = 'Aucun diplôme' ; 2 = 'CAP, BEP' ; 3 = 'Baccalauréat' ; 4 = 'Bac +2' ; 5 = 'Bac +3 et plus'",
            "Y7REL1ST": "1 = 'Catholique' ; 2 = 'Juive' ; 3 = 'Musulmane' ; 4 = 'Autre religion (protestante, boudhiste ou autre)' ; 5 = 'Sans religion'",
            "Y7ECO2ST2": "1 = 'Moins de 1 250 euros' ; 2 = 'De 1 250 euros à 1 999 euros' ; 3 = 'De 2 000 à 3 499 euros' ; 4 = 'De 3 500 à 4 999 euros' ; 5 = '5 000 euros et plus'",
            "Y7INTPOLST": "1 = 'Beaucoup' ; 2 = 'Un peu' ; 3 = 'Pas vraiment' ; 4 = 'Pas du tout'",
            "Y7Q7ST": "1 = 'Très à gauche' ; 2 = 'Plutôt à gauche' ; 3 = 'Au centre' ; 4 = 'Plutôt à droite' ; 5 = 'Très à droite'",
            "Y7PROXST": "1 = 'Très à gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)' ; 2 = 'Gauche (Parti Socialiste, Europe Ecologie - Les Verts)' ; 3 = 'Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))' ; 4 = 'Droite (Les Républicains)' ; 5 = 'Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)' ; 6 = 'Autre parti ou aucun parti'"
        }
        # définir un dictionnaire qui contient l'ordre figé des modalités pour chaque variable socio-démographique
        dico_ordre_modalites = {
            "Y7SEXEST": [
                "Homme",
                "Femme"
            ],
            "Y7AGERST": [
                "18 à 24 ans",
                "25 à 34 ans",
                "35 à 49 ans",
                "50 à 59 ans",
                "60 ans et plus"
            ],
            "Y7REG13ST": [
                "Ile de France",
                "Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)",
                "Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)",
                "Sud ouest (Nouvelle Aquitaine et Occitanie)",
                "Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)"
            ],
            "Y7AGGLO5ST": [
                "Zone rurale (moins de 2 000 habitants)",
                "Zone urbaine de 2 000 à 9 999 habitants",
                "Zone urbaine de 10 000 à 49 999 habitants",
                "Zone urbaine de 50 000 à 199 999 habitants",
                "Zone urbaine de 200 000 habitants et plus"
            ],
            "Y7EMPST": [
                "Salarié (salarié à plein temps ou à temps partiel)",
                "Indépendant (travaille à mon compte)",
                "Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)"
            ],
            "Y7PCSIST": [
                "Agriculteur exploitant, artisan, commerçant, chef d entreprise",
                "Cadre supérieur",
                "Profession intermédiaire",
                "Employé",
                "Ouvrier",
                "Retraité, inactif"
            ],
            "Y7EDUST": [
                "Aucun diplôme",
                "CAP, BEP",
                "Baccalauréat",
                "Bac +2",
                "Bac +3 et plus"
            ],
            "Y7REL1ST": [
                "Catholique",
                "Juive",
                "Musulmane",
                "Autre religion (protestante, boudhiste ou autre)",
                "Sans religion"
            ],
            "Y7ECO2ST2": [
                "Moins de 1 250 euros",
                "De 1 250 euros à 1 999 euros",
                "De 2 000 à 3 499 euros",
                "De 3 500 à 4 999 euros",
                "5 000 euros et plus"
            ],
            "Y7INTPOLST": [
                "Beaucoup",
                "Un peu",
                "Pas vraiment",
                "Pas du tout"
            ],
            "Y7Q7ST": [
                "Très à gauche",
                "Plutôt à gauche",
                "Au centre",
                "Plutôt à droite",
                "Très à droite"
            ],
            "Y7PROXST": [
                "Très à gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)",
                "Gauche (Parti Socialiste, Europe Ecologie - Les Verts)",
                "Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))",
                "Droite (Les Républicains)",
                "Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)",
                "Autre parti ou aucun parti"
            ]
        }
       # définir une fonction qui affiche les étiquettes
        # des modalités de la variablr SD choisie dans la légende
        # sur plusieurs lignes si leur longueur initiale dépasse la
        # largeur du cadre de la légende (version robuste avec gestion des erreurs)
        def wrap_label(label, max_length=20):
            try:
                # Si le label est un float ou NaN
                if pd.isna(label) or isinstance(label, float):
                    return "Non renseigné"
                # Convertir en string si ce n'est pas déjà le cas
                label = str(label).strip()
                # Si la chaîne est vide après nettoyage
                if not label:
                    return "Non renseigné"
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
            except Exception as e:
                print(f"Erreur dans wrap_label avec {label}: {str(e)}")
                return str(label) 
                # retourner le label tel quel en cas d'erreur
        # lire le fichier CSV des données
        csvfile = "data/T_w7_pl15st_" + "%s" % input.Select_VarSD_DegConfAN_Legis_T2().lower()[2:] + ".csv"
        df = pd.read_csv(csvfile)
        # nettoyer les données lues
        var_sd = input.Select_VarSD_DegConfAN_Legis_T2()
        df[var_sd] = df[var_sd].fillna("Non renseigné")  # Gérer les NaN
        df[var_sd] = df[var_sd].astype(str)  # Convertir en string
        df['Y7PL15ST'] = df['Y7PL15ST'].fillna("Non renseigné")
        # s'assurer que toutes les modalités sont des chaînes de caractères dans "dico_ordre_modalites"
        dico_ordre_modalites[var_sd] = [str(modal) for modal in dico_ordre_modalites[var_sd]]
        # filtrer pour ne garder que les modalités définies dans "dico_ordre_modalites"
        df = df[df[var_sd].isin(dico_ordre_modalites[var_sd])]
        # définir l'ordre des modalités pour Y7PL15ST
        ordre_modalites = [
            "Confiance",
            "Pas confiance"
        ]
        # créer une colonne catégorielle avec l'ordre souhaité pour la variable socio-démographique
        var_sd = input.Select_VarSD_DegConfAN_Legis_T2()
        df[var_sd] = pd.Categorical(
            df[var_sd],
            categories=dico_ordre_modalites[var_sd],
            ordered=True
        )
        # filtrer et pivoter les données
        df_pivot = df[df['Y7PL15ST'].isin(ordre_modalites)].pivot(
            index=var_sd,
            columns='Y7PL15ST',
            values='pct'
        )
        df_pivot = df_pivot.reindex(columns=ordre_modalites)
        # créer une palette de couleurs automatique
        nb_couleurs = len(df_pivot.index)
        palette = px.colors.qualitative.Plotly[:nb_couleurs]
        # créer le graphique
        fig = go.Figure()
        # ajouter les données
        for i, VarSD in enumerate(df_pivot.index):
            fig.add_trace(
                go.Bar(
                    x=ordre_modalites,
                    y=df_pivot.loc[VarSD],
                    name=wrap_label(VarSD),
                    marker_color=palette[i],
                    # afficher les valeurs sous le format 'xx.x%' dans la bulle qui s'affiche
                    # au survol de la courbe par la souris, et supprimer toutes les autres
                    # informations qui pourraient s'afficher en plus (nom de la modalité)
                    hovertemplate='%{y:.1f}%<extra></extra>',
                    # n'afficher la bulle contenant la valeur 'y' en % uniquement
                    # au-dessus de la barre verticale survolée par la souris
                    hoverinfo='y',
                    # centrer ce texte 'y' dans la bulle
                    hoverlabel=dict(
                        align='auto'
                    )
                )
            )
         # mettre en forme le graphique
        fig.update_layout(
            barmode='group', # barres séparées et groupées pour les modalités de la VarSD choisie
            title={
                'text': "Degré de confiance envers la nouvelle Assemblée nationale en fonction %s" % dico_titre.get("%s" % input.Select_VarSD_DegConfAN_Legis_T2()),
                'y':0.98,
                'x':0.01,
                'xanchor': 'left',
                'yanchor': 'top'
            },
            # définir le titre de la légende
            legend_title="%s" % dico_legende.get("%s" % input.Select_VarSD_DegConfAN_Legis_T2()),
            # définir l'affichage séparé des valeurs de % affichées au-dessus de
            # chaque barre verticale quand la souris la survole
            hovermode="closest",
            # définir le thème général de l'apparence du graphique
            template="plotly_white",
            # définir le titre de l'axe des ordonnées et son apparence
            yaxis_title=dict(
                text='Pourcentage de répondants (%)',
                font_size=12
            ),
            # définir les sources des données
            annotations=[
                dict(
                    xref='paper', # utiliser la largeur totale du graphique comme référence
                    yref='paper', # utiliser la hauteur totale du graphique comme référence
                    x=0.5, # placer le point d'ancrage au milieu de la largeur
                    y=-0.1, # valeur à ajuster pour positionner verticalement le texte sous le graphique
                    xanchor='center', # centrer le texte par rapport au point d'ancrage
                    yanchor='top',
                    text=
                        'Enquête électorale française pour les ' +
                        'élections européennes de juin 2024, ' +
                        'par Ipsos Sopra Steria, Cevipof, ' +
                        'Le Monde, Fondation Jean Jaurès et ' +
                        'Institut Montaigne (2024)',
                    font=dict(
                        size=10,
                        color='grey'
                    ),
                    showarrow=False
                )
            ],
            # définir les marges de la zone graphique
            # (augmentées à droite pour le cadre fixe de la légende)
            margin=dict(
                b=50, # b = bottom
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
            ),
        )
        # retourner le graphique
        return fig


    #####################################################################
    # onglet 09 : SOUHAIT DE DEMISSION DU PRESIDENT DE LA REPUBLIQUE    #
    #####################################################################

    # bouton 01 : décrire la question posée dans l'enquête
    @reactive.effect
    @reactive.event(input.Show_SOUHDEMPR_Question_Legis_T2)
    def _():
        m = ui.modal(
            "La question posée aux répondants est la suivante : 'À l’issue de ces élections législatives, seriez-vous favorable ou non à la démission d’Emmanuel Macron et à ce qu’une nouvelle élection présidentielle ait lieu dans les prochains mois ?'",
            title="Informations complémentaires sur la question contenue dans l'enquête :",
            easy_close=False
        )
        ui.modal_show(m)

    # bouton 02 : décrire la variable de l'intention d'aller voter choisie
    @reactive.effect
    @reactive.event(input.Show_SOUHDEMPRST_Info_Legis_T2)
    def _():
        m = ui.modal(
            "La variable sur le souhait de démission du Président de la République émis par les répondants présentée ici sur les graphiques est une modalité synthétique de la question posée aux répondants de l'enquête. \
            Ainsi, à partir des quatre modalités de réponse à la question de l'enquête, on en construit deux : 'Favorable (tout à fait favorable ou plutôt favorable)' ou 'Pas favorable (pas du tout favorable ou pas vraiment favorable)'.",
            title="Informations complémentaires sur la variable choisie pour les graphiques :",
            easy_close=False
        )
        ui.modal_show(m)

    # bouton 03 : afficher la description de la variable socio-démographique choisie
    # avec plusieurs parties de texte qui dépendent de ce choix (via des dictionnaires)
    @reactive.effect
    @reactive.event(input.Show_VarSD_SouhDemPR_Info_Legis_T2)
    def _():
        # définir le nom de la variable socio-démographique choisie
        dico_nom_var = {
            "Y7SEXEST": "Genre",
            "Y7AGERST": "Âge",
            "Y7REG13ST": "Région",
            "Y7AGGLO5ST": "Taille d'agglomération",
            "Y7EMPST": "Type d'emploi occupé",
            "Y7PCSIST": "Catégorie professionnelle",
            "Y7EDUST": "Niveau de scolarité atteint",
            "Y7REL1ST": "Religion",
            "Y7ECO2ST2": "Revenu mensuel du foyer",
            "Y7INTPOLST": "Intérêt pour la politique",
            "Y7Q7ST": "Positionnement idéologique",
            "Y7PROXST": "Préférence partisane"
        }
        # définir la question de l'enquête associée à la variable socio-démographique choisie
        dico_question_var = {
            "Y7SEXEST": "Êtes-vous ?",
            "Y7AGERST": "Quelle est votre date de naissance ?",
            "Y7REG13ST": "Veuillez indiquer le département et la commune où vous résidez.",
            "Y7AGGLO5ST": "Veuillez indiquer le département et la commune où vous résidez.",
            "Y7EMPST": "Quelle est votre situation professionnelle actuelle ?",
            "Y7PCSIST": "Quelle est votre situation professionnelle actuelle ?",
            "Y7EDUST": "Choisissez votre niveau de scolarité le plus élevé.",
            "Y7REL1ST": "Quelle est votre religion, si vous en avez une ?",
            "Y7ECO2ST2": " Pour finir, nous avons besoin de connaître, à des fins statistiques uniquement, la tranche dans laquelle se situe le revenu MENSUEL NET de votre FOYER après déduction des impôts sur le revenu (veuillez considérer toutes vos sources de revenus: salaires, bourses, prestations retraite et sécurité sociale, dividendes, revenus immobiliers, pensions alimentaires etc.).",
            "Y7INTPOLST": "De manière générale, diriez-vous que vous vous intéressez à la politique ?",
            "Y7Q7ST": "Sur une échelle de 0 à 10, où 0 correspond à la gauche et 10 correspond à la droite, où diriez-vous que vous vous situez ?",
            "Y7PROXST": "De quel parti vous sentez-vous proche ou moins éloigné que les autres ?"
        }
        # définir les modalités de réponse à la question de l'enquête associée à la variable socio-démographique choisie
        dico_modalite_var = {
            "Y7SEXEST": "1 = 'Homme' ; 2 = 'Femme'",
            "Y7AGERST": "1 = '18 à 24 ans' ; 2 = '25 à 34 ans' ; 3 = '35 à 49 ans' ; 4 = '50 à 59 ans' ; 5 = '60 ans et plus'",
            "Y7REG13ST": "1 = 'Ile de France' ; 2 = 'Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)' ; 3 = 'Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)' ; 4 = 'Sud ouest (Nouvelle Aquitaine et Occitanie)' ; 5 = 'Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)'",
            "Y7AGGLO5ST": "1 = 'Zone rurale (moins de 2 000 habitants)' ; 2 = 'Zone urbaine de 2 000 à 9 999 habitants' ; 3 = 'Zone urbaine de 10 000 à 49 999 habitants' ; 4 = 'Zone urbaine de 50 000 à 199 999 habitants' ; 5 = 'Zone urbaine de 200 000 habitants et plus'",
            "Y7EMPST": "1 = 'Salarié (salarié à plein temps ou à temps partiel)' ; 2 = 'Indépendant (travaille à mon compte)' ; 3 = 'Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)'",
            "Y7PCSIST": "1 = 'Agriculteur exploitant, artisan, commerçant, chef d entreprise' ; 2 = 'Cadre supérieur' ; 3 = 'Profession intermédiaire' ; 4 = 'Employé' ; 5 = 'Ouvrier' ; 6 = 'Retraité, inactif'",
            "Y7EDUST": "1 = 'Aucun diplôme' ; 2 = 'CAP, BEP' ; 3 = 'Baccalauréat' ; 4 = 'Bac +2' ; 5 = 'Bac +3 et plus'",
            "Y7REL1ST": "1 = 'Catholique' ; 2 = 'Juive' ; 3 = 'Musulmane' ; 4 = 'Autre religion (protestante, boudhiste ou autre)' ; 5 = 'Sans religion'",
            "Y7ECO2ST2": "1 = 'Moins de 1 250 euros' ; 2 = 'De 1 250 euros à 1 999 euros' ; 3 = 'De 2 000 à 3 499 euros' ; 4 = 'De 3 500 à 4 999 euros' ; 5 = '5 000 euros et plus'",
            "Y7INTPOLST": "1 = 'Beaucoup' ; 2 = 'Un peu' ; 3 = 'Pas vraiment' ; 4 = 'Pas du tout'",
            "Y7Q7ST": "1 = 'Très à gauche' ; 2 = 'Plutôt à gauche' ; 3 = 'Au centre' ; 4 = 'Plutôt à droite' ; 5 = 'Très à droite'",
            "Y7PROXST": "1 = 'Extême gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)' ; 2 = 'Gauche (Parti Socialiste, Europe Ecologie - Les Verts)' ; 3 = 'Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))' ; 4 = 'Droite (Les Républicains)' ; 5 = 'Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)' ; 6 = 'Autre parti ou aucun parti'"
        }
        # définir le texte complet à afficher (avec parties fixes et variables en fonction du choix effectué)
        m = ui.modal(
            "La variable '%s' correspond à ou est calculée à partir de la question suivante posée aux répondants : \
            '%s', \
            et ses modalités de réponse (inchangées par rapport au questionnaire ou regroupées pour les présents graphiques) sont : \
            %s." % (
                dico_nom_var.get(
                    "%s" % input.Select_VarSD_SouhDemPR_Legis_T2()
                ),
                dico_question_var.get("%s" % input.Select_VarSD_SouhDemPR_Legis_T2()),
                dico_modalite_var.get("%s" % input.Select_VarSD_SouhDemPR_Legis_T2())
            ),
            title="Informations complémentaires sur la variable socio-démographique choisie :",
            easy_close=False
        )
        ui.modal_show(m)

    # graphique
    @output
    @render_plotly
    def Graph_Croise_SouhDemPR_Legis_T2():
        # définir la partie variable du titre
        dico_titre = {
            "Y7SEXEST": "du genre",
            "Y7AGERST": "de l'âge",
            "Y7REG13ST": "de la région de résidence",
            "Y7AGGLO5ST": "de la taille de l'agglomération de résidence",
            "Y7EMPST": "du type d'emploi occupé",
            "Y7PCSIST": "de la catégorie socio-professionnelle",
            "Y7EDUST": "du niveau de scolarité atteint",
            "Y7REL1ST": "de la religion",
            "Y7ECO2ST2": "du revenu mensuel du foyer",
            "Y7INTPOLST": "de l'intérêt pour la politique",
            "Y7Q7ST": "du positionnement idéologique",
            "Y7PROXST": "de la préférence partisane"
        }
        # définir la partie variable du titre de la légende
        dico_legende = {
            "Y7SEXEST": "Genre",
            "Y7AGERST": "Âge",
            "Y7REG13ST": "Région",
            "Y7AGGLO5ST": "Taille d'agglomération",
            "Y7EMPST": "Type d'emploi occupé",
            "Y7PCSIST": "Catégorie professionnelle",
            "Y7EDUST": "Niveau de scolarité atteint",
            "Y7REL1ST": "Religion",
            "Y7ECO2ST2": "Revenu mensuel du foyer",
            "Y7INTPOLST": "Intérêt pour la politique",
            "Y7Q7ST": "Positionnement idéologique",
            "Y7PROXST": "Préférence partisane"
        }
        # définir l'échelle de l'axe des ordonnées en fonction des
        # valeurs prises par la variable socio-démographique choisie
        dico_echelleY = {
            "Y7SEXEST": [10, 40],
            "Y7AGERST": [10, 45],
            "Y7REG13ST": [15, 35],
            "Y7AGGLO5ST": [15, 35],
            "Y7EMPST": [15, 40],
            "Y7PCSIST": [10, 45],
            "Y7EDUST": [15, 40],
            "Y7REL1ST": [10, 45],
            "Y7ECO2ST2": [10, 45],
            "Y7INTPOLST": [0, 75],
            "Y7Q7ST": [5, 40],
            "Y7PROXST": [5, 55],
        }
        # définir les modalités des variables socio-démo et leur ordre
        dico_modalite_var = {
            "Y7SEXEST": "1 = 'Homme' ; 2 = 'Femme'",
            "Y7AGERST": "1 = '18 à 24 ans' ; 2 = '25 à 34 ans' ; 3 = '35 à 49 ans' ; 4 = '50 à 59 ans' ; 5 = '60 ans et plus'",
            "Y7REG13ST": "1 = 'Ile de France' ; 2 = 'Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)' ; 3 = 'Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)' ; 4 = 'Sud ouest (Nouvelle Aquitaine et Occitanie)' ; 5 = 'Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)'",
            "Y7AGGLO5ST": "1 = 'Zone rurale (moins de 2 000 habitants)' ; 2 = 'Zone urbaine de 2 000 à 9 999 habitants' ; 3 = 'Zone urbaine de 10 000 à 49 999 habitants' ; 4 = 'Zone urbaine de 50 000 à 199 999 habitants' ; 5 = 'Zone urbaine de 200 000 habitants et plus'",
            "Y7EMPST": "1 = 'Salarié (salarié à plein temps ou à temps partiel)' ; 2 = 'Indépendant (travaille à mon compte)' ; 3 = 'Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)'",
            "Y7PCSIST": "1 = 'Agriculteur exploitant, artisan, commerçant, chef d entreprise' ; 2 = 'Cadre supérieur' ; 3 = 'Profession intermédiaire' ; 4 = 'Employé' ; 5 = 'Ouvrier' ; 6 = 'Retraité, inactif'",
            "Y7EDUST": "1 = 'Aucun diplôme' ; 2 = 'CAP, BEP' ; 3 = 'Baccalauréat' ; 4 = 'Bac +2' ; 5 = 'Bac +3 et plus'",
            "Y7REL1ST": "1 = 'Catholique' ; 2 = 'Juive' ; 3 = 'Musulmane' ; 4 = 'Autre religion (protestante, boudhiste ou autre)' ; 5 = 'Sans religion'",
            "Y7ECO2ST2": "1 = 'Moins de 1 250 euros' ; 2 = 'De 1 250 euros à 1 999 euros' ; 3 = 'De 2 000 à 3 499 euros' ; 4 = 'De 3 500 à 4 999 euros' ; 5 = '5 000 euros et plus'",
            "Y7INTPOLST": "1 = 'Beaucoup' ; 2 = 'Un peu' ; 3 = 'Pas vraiment' ; 4 = 'Pas du tout'",
            "Y7Q7ST": "1 = 'Très à gauche' ; 2 = 'Plutôt à gauche' ; 3 = 'Au centre' ; 4 = 'Plutôt à droite' ; 5 = 'Très à droite'",
            "Y7PROXST": "1 = 'Très à gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)' ; 2 = 'Gauche (Parti Socialiste, Europe Ecologie - Les Verts)' ; 3 = 'Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))' ; 4 = 'Droite (Les Républicains)' ; 5 = 'Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)' ; 6 = 'Autre parti ou aucun parti'"
        }
        # définir un dictionnaire qui contient l'ordre figé des modalités pour chaque variable socio-démographique
        dico_ordre_modalites = {
            "Y7SEXEST": [
                "Homme",
                "Femme"
            ],
            "Y7AGERST": [
                "18 à 24 ans",
                "25 à 34 ans",
                "35 à 49 ans",
                "50 à 59 ans",
                "60 ans et plus"
            ],
            "Y7REG13ST": [
                "Ile de France",
                "Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)",
                "Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)",
                "Sud ouest (Nouvelle Aquitaine et Occitanie)",
                "Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)"
            ],
            "Y7AGGLO5ST": [
                "Zone rurale (moins de 2 000 habitants)",
                "Zone urbaine de 2 000 à 9 999 habitants",
                "Zone urbaine de 10 000 à 49 999 habitants",
                "Zone urbaine de 50 000 à 199 999 habitants",
                "Zone urbaine de 200 000 habitants et plus"
            ],
            "Y7EMPST": [
                "Salarié (salarié à plein temps ou à temps partiel)",
                "Indépendant (travaille à mon compte)",
                "Sans emploi (ne travaille pas actuellement tout en recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)"
            ],
            "Y7PCSIST": [
                "Agriculteur exploitant, artisan, commerçant, chef d entreprise",
                "Cadre supérieur",
                "Profession intermédiaire",
                "Employé",
                "Ouvrier",
                "Retraité, inactif"
            ],
            "Y7EDUST": [
                "Aucun diplôme",
                "CAP, BEP",
                "Baccalauréat",
                "Bac +2",
                "Bac +3 et plus"
            ],
            "Y7REL1ST": [
                "Catholique",
                "Juive",
                "Musulmane",
                "Autre religion (protestante, boudhiste ou autre)",
                "Sans religion"
            ],
            "Y7ECO2ST2": [
                "Moins de 1 250 euros",
                "De 1 250 euros à 1 999 euros",
                "De 2 000 à 3 499 euros",
                "De 3 500 à 4 999 euros",
                "5 000 euros et plus"
            ],
            "Y7INTPOLST": [
                "Beaucoup",
                "Un peu",
                "Pas vraiment",
                "Pas du tout"
            ],
            "Y7Q7ST": [
                "Très à gauche",
                "Plutôt à gauche",
                "Au centre",
                "Plutôt à droite",
                "Très à droite"
            ],
            "Y7PROXST": [
                "Très à gauche (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise)",
                "Gauche (Parti Socialiste, Europe Ecologie - Les Verts)",
                "Centre (Renaissance, Le MoDem (Mouvement Démocrate), Horizons, UDI (Union des Démocrates et Indépendants))",
                "Droite (Les Républicains)",
                "Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)",
                "Autre parti ou aucun parti"
            ]
        }
        # définir une fonction qui affiche les étiquettes
        # des modalités de la variablr SD choisie dans la légende
        # sur plusieurs lignes si leur longueur initiale dépasse la
        # largeur du cadre de la légende (version robuste avec gestion des erreurs)
        def wrap_label(label, max_length=20):
            try:
                # Si le label est un float ou NaN
                if pd.isna(label) or isinstance(label, float):
                    return "Non renseigné"
                # Convertir en string si ce n'est pas déjà le cas
                label = str(label).strip()
                # Si la chaîne est vide après nettoyage
                if not label:
                    return "Non renseigné"
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
            except Exception as e:
                print(f"Erreur dans wrap_label avec {label}: {str(e)}")
                return str(label) 
                # retourner le label tel quel en cas d'erreur
        # lire le fichier CSV des données
        csvfile = "data/T_w7_pl16st_" + "%s" % input.Select_VarSD_SouhDemPR_Legis_T2().lower()[2:] + ".csv"
        df = pd.read_csv(csvfile)
        # nettoyer les données lues
        var_sd = input.Select_VarSD_SouhDemPR_Legis_T2()
        df[var_sd] = df[var_sd].fillna("Non renseigné")  # Gérer les NaN
        df[var_sd] = df[var_sd].astype(str)  # Convertir en string
        df['Y7PL16ST'] = df['Y7PL16ST'].fillna("Non renseigné")
        # s'assurer que toutes les modalités sont des chaînes de caractères dans "dico_ordre_modalites"
        dico_ordre_modalites[var_sd] = [str(modal) for modal in dico_ordre_modalites[var_sd]]
        # filtrer pour ne garder que les modalités définies dans "dico_ordre_modalites"
        df = df[df[var_sd].isin(dico_ordre_modalites[var_sd])]
        # définir l'ordre des modalités pour Y7PL16ST
        ordre_modalites = [
            "Favorable",
            "Pas favorable"
        ]
        # créer une colonne catégorielle avec l'ordre souhaité pour la variable socio-démographique
        var_sd = input.Select_VarSD_SouhDemPR_Legis_T2()
        df[var_sd] = pd.Categorical(
            df[var_sd],
            categories=dico_ordre_modalites[var_sd],
            ordered=True
        )
        # filtrer et pivoter les données
        df_pivot = df[df['Y7PL16ST'].isin(ordre_modalites)].pivot(
            index=var_sd,
            columns='Y7PL16ST',
            values='pct'
        )
        df_pivot = df_pivot.reindex(columns=ordre_modalites)
        # créer une palette de couleurs automatique
        nb_couleurs = len(df_pivot.index)
        palette = px.colors.qualitative.Plotly[:nb_couleurs]
        # créer le graphique
        fig = go.Figure()
        # ajouter les données
        for i, VarSD in enumerate(df_pivot.index):
            fig.add_trace(
                go.Bar(
                    x=ordre_modalites,
                    y=df_pivot.loc[VarSD],
                    name=wrap_label(VarSD),
                    marker_color=palette[i],
                    # afficher les valeurs sous le format 'xx.x%' dans la bulle qui s'affiche
                    # au survol de la courbe par la souris, et supprimer toutes les autres
                    # informations qui pourraient s'afficher en plus (nom de la modalité)
                    hovertemplate='%{y:.1f}%<extra></extra>',
                    # n'afficher la bulle contenant la valeur 'y' en % uniquement
                    # au-dessus de la barre verticale survolée par la souris
                    hoverinfo='y',
                    # centrer ce texte 'y' dans la bulle
                    hoverlabel=dict(
                        align='auto'
                    )
                )
            )
         # mettre en forme le graphique
        fig.update_layout(
            barmode='group', # barres séparées et groupées pour les modalités de la VarSD choisie
            title={
                'text': "Souhait de démission du Président de la République en fonction %s" % dico_titre.get("%s" % input.Select_VarSD_SouhDemPR_Legis_T2()),
                'y':0.98,
                'x':0.01,
                'xanchor': 'left',
                'yanchor': 'top'
            },
            # définir le titre de la légende
            legend_title="%s" % dico_legende.get("%s" % input.Select_VarSD_SouhDemPR_Legis_T2()),
            # définir l'affichage séparé des valeurs de % affichées au-dessus de
            # chaque barre verticale quand la souris la survole
            hovermode="closest",
            # définir le thème général de l'apparence du graphique
            template="plotly_white",
            # définir le titre de l'axe des ordonnées et son apparence
            yaxis_title=dict(
                text='Pourcentage de répondants (%)',
                font_size=12
            ),
            # définir les sources des données
            annotations=[
                dict(
                    xref='paper', # utiliser la largeur totale du graphique comme référence
                    yref='paper', # utiliser la hauteur totale du graphique comme référence
                    x=0.5, # placer le point d'ancrage au milieu de la largeur
                    y=-0.1, # valeur à ajuster pour positionner verticalement le texte sous le graphique
                    xanchor='center', # centrer le texte par rapport au point d'ancrage
                    yanchor='top',
                    text=
                        'Enquête électorale française pour les ' +
                        'élections européennes de juin 2024, ' +
                        'par Ipsos Sopra Steria, Cevipof, ' +
                        'Le Monde, Fondation Jean Jaurès et ' +
                        'Institut Montaigne (2024)',
                    font=dict(
                        size=10,
                        color='grey'
                    ),
                    showarrow=False
                )
            ],
            # définir les marges de la zone graphique
            # (augmentées à droite pour le cadre fixe de la légende)
            margin=dict(
                b=50, # b = bottom
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
            ),
        )
        # retourner le graphique
        return fig



##############
## BLOC APP ##
##############

# définir une nouvelle instance de l'application
app = App(app_ui, server)
