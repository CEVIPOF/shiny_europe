# -*- coding: utf-8 -*-
"""
Construction d'une application interactive de visualisation de données
pour les enquêtes électorales françaises faites pour les élections européennes
de juin 2024

PAYS : France
VAGUES : 1 à 6

Auteurs :   Diego Antolinos-Basso
            Nicolas Sormani

Centre : Cevipof (SciencesPo)
Année : 2024
"""

from shiny import App, render, ui, reactive
from shinywidgets import output_widget, render_widget, render_plotly
import shinyswatch
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import datetime

########
## UI ##
########

# définir des ui-card maison
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

    shinyswatch.theme.simplex,

    # définir le titre de l'application
    ui.h2("Enquête Électorale Française sur les élections européennes du 9 juin 2024"
    ),

    # définir les onglets contenus dans la page principale de l'application
    ui.navset_card_pill(

        # onglet 01
        ui.nav_panel("Présentation",
                    # texte de présentation du projet et des enquêtes
                    ui.markdown(
                        """
                        ### L'Enquête Électorale Française

                        Dans la perspective des élections européennes du 9 juin 2024, _Ipsos Sopra Steria_,
                        le _Cevipof_ et _Le Monde_ ont mis en place en juin 2023 un dispositif d'enquêtes
                        par panel intitulé Enquête Électorale Française pour les élections européennes du 9 juin 2024 - ENEF
                        <br>
                        <br>
                        Composé de plus de 10 000 personnes, le panel d'individus est interrogé
                        à 6 reprises de juin 2023 à juin 2024, afin de mieux comprendre les logiques de
                        leurs décisions de vote pour ces élections.
                        <br>
                        <br>
                        Les résultats détaillés de ce dispositif d'enquête, accompagnés de décryptages et
                        d'analyses, sont disponibles sur la [page dédiée du Cevipof](https://www.sciencespo.fr/cevipof/fr/content/resultats-et-decrypyages-par-vagues.html).
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

        # onglet 02
        ui.nav_panel("Tableau de bord général",
            ui.layout_columns(
                # indicateurs globaux en exergues
                ui.card(
                    ui_card("Intitulés des questions",
                        ui.input_action_button("descript_inteur", "Intérêt pour l'élection"),
                        ui.input_action_button("descript_indpart", "Indice de participation"),
                    ),
                    ui_card("Derniers indicateurs enregistrés - Juin 2024",
                        ui.layout_columns(
                            ui_card("Intérêt pour l'élection", "61,9%"),
                            ui_card("Indice de participation", "47,1%")
                        ),
                    ),
                ),
                # dataviz temporelle par vagues des indicateurs
                ui_card("Évolution des variables principales d'intérêt pour l'élection",
                    output_widget("graph_interet", width="auto", height="auto")),
                col_widths=(3, 9)
            )
        ),

        # onglet 03
        ui.nav_panel("Intention d'aller voter - Votants",
            # définir deux colonnes sur cet onglet
            ui.layout_columns(
                # colonne 1 de l'onglet : informations et choix de l'utilisateur
                ui.card(
                    # cadre 01 : informations sur la variable de l'intention d'aller voter
                    ui_card("CERTITUDE D'ALLER VOTER",
                            # bouton 01 : information sur la question posée dans l'enquête
                            ui.input_action_button("Show_CERT_Question", # input ID
                                                   "Question posée dans l'enquête" # texte affiché dans le bouton
                            ),
                            # bouton 02 : information sur la variable sélectionnée pour les graphiques
                            ui.input_action_button("Show_CERTST_Info", # input ID
                                                   "Variable choisie pour les graphiques" # texte affiché dans le bouton
                            ),
                    ),
                    # cadre 02 : choix de la variable socio-démographique à croiser avec l'intention d'aller voter
                    ui_card("CHOISIR UNE VARIABLE SOCIO- DEMOGRAPHIQUE",
                            # groupe de boutons de sélection
                            ui.input_radio_buttons(
                                id="select_VarSD",
                                label="",
                                choices={"SEXEST": "Genre",
                                         "AGERST": "Âge",
                                         "REG13ST": "Région",
                                         "AGGLO5ST": "Taille d'agglomération",
                                         "EMPST": "Type d'emploi occupé",
                                         "PCSIST": "Catégorie professionnelle",
                                         "EDUR4ST": "Niveau de scolarité atteint",
                                         "REL1ST": "Religion",
                                         "ECO2ST2": "Revenu mensuel du foyer",
                                         "INTPOLST": "Intérêt pour la politique",
                                         "Q7ST": "Positionnement idéologique",
                                         "PROXST": "Préférence partisane"
                                }
                            ),
                            # bouton 03 : informations détaillées sur la variable socio-démographique choisie
                            ui.input_action_button("Show_VarSD_Info", # input ID
                                                   "Afficher sa description" # texte affiché dans le bouton
                            )
                    )
                ),
                # colonne 2 de l'onglet : graphique des variables
                ui_card("CERTITUDE D'ALLER VOTER EN FONCTION D'UNE VARIABLE SOCIO-DEMOGRAPHIQUE",
                        # afficher le graphique ad hoc
                        output_widget(id="graph_croise")
                ),
                # largeurs respectives des deux cadres sur cet onglet 03
                col_widths=(3, 9)
            )
        ),

        # TODO
        # onglet 04
        # ui.nav_panel("Exploration thématique",
        #             # barre de navigation contenant les sous-onglets thématiques
        #             ui.navset_card_pill(
        #                 # sous-onglet 01
        #                 ui.nav_panel("Les raisons de l'abstention", # titre du sous-onglet
        #                              "Raisons de l'abstention (vague 03)" # contenu du sous-onglet
        #                 ),
        #                 # sous-onglet 02
        #                 ui.nav_panel("Le conflit israelo-palestinien", # titre du sous-onglet
        #                              "Conflit israelo-palestinien (vague 02)" # contenu du sous-onglet
        #                 ),
        #                 # sous-onglet 03
        #                 ui.nav_panel("Les enjeux de ces élections", # titre du sous-onglet
        #                              "Les enjeux de ces élections (vague XX)" # contenu du sous-onglet
        #                 ),
        #                 # sous-onglet 04
        #                 ui.nav_panel("La perception de l'Union européenne et de ses valeurs", # titre du sous-onglet
        #                              "La perception de l'Union européenne et de ses valeurs (vague 04)" # contenu du sous-onglet
        #                 )
        #             )
        # ),

        # onglet 05
        ui.nav_panel("Intention d'aller voter - Abstentionnistes",
            # définir deux colonnes sur cet onglet (une pour les informations, une pour le graphique)
            ui.layout_columns(
                # colonne 1 de l'onglet : informations et choix de l'utilisateur
                ui.card(
                    # cadre 01 : informations sur la variable de l'intention d'aller voter
                    ui_card("CERTITUDE DE S'ABSTENIR",
                            # bouton 01 : information sur la question posée dans l'enquête
                            ui.input_action_button("Show_CERT_Question_Abst", # input ID
                                                   "Question posée dans l'enquête" # texte affiché dans le bouton
                            ),
                            # bouton 02 : information sur la variable sélectionnée pour les graphiques
                            ui.input_action_button("Show_CERTST_Info_Abst", # input ID
                                                   "Variable choisie pour les graphiques" # texte affiché dans le bouton
                            ),
                    ),
                    # cadre 02 : choix de la variable socio-démographique à croiser avec l'intention d'aller voter
                    ui_card("CHOISIR UNE VARIABLE SOCIO- DEMOGRAPHIQUE",
                            # groupe de boutons de sélection
                            ui.input_radio_buttons(
                                id="select_VarSD_Abst",
                                label="",
                                choices={"SEXEST": "Genre",
                                         "AGERST": "Âge",
                                         "REG13ST": "Région",
                                         "AGGLO5ST": "Taille d'agglomération",
                                         "EMPST": "Type d'emploi occupé",
                                         "PCSIST": "Catégorie professionnelle",
                                         "EDUR4ST": "Niveau de scolarité atteint",
                                         "REL1ST": "Religion",
                                         "ECO2ST2": "Revenu mensuel du foyer",
                                         "INTPOLST": "Intérêt pour la politique",
                                         "Q7ST": "Positionnement idéologique",
                                         "PROXST": "Préférence partisane"
                                }
                            ),
                            # bouton 03 : informations détaillées sur la variable socio-démographique choisie
                            ui.input_action_button("Show_VarSD_Info_Abst", # input ID
                                                   "Afficher sa description" # texte affiché dans le bouton
                            )
                    )
                ),

                # colonne 2 de l'onglet : graphique des variables
                ui_card("CERTITUDE DE S'ABSTENIR EN FONCTION D'UNE VARIABLE SOCIO-DEMOGRAPHIQUE",
                        # afficher le graphique ad hoc
                        output_widget(id="graph_croise_Abst")
                ),

                # largeurs respectives des deux cadres
                col_widths=(3, 9)
            )
        ),

        id="tab"
        ),
    )

#############
## SERVEUR ##
#############

# bloc définissant les méthodes mises en oeuvre pour la réactivité des objets
def server(input, output, session):

    # onglet 2

    # bouton onglet 2 : intérêt pour l'élection
    @reactive.effect
    @reactive.event(input.descript_inteur)
    def _():
        m = ui.modal("La question posée aux répondants était : sur une échelle de 0 à 10, où 0 signifie aucun intérêt et 10 signifie énormément d'intérêt, quel est votre niveau d'intérêt pour les prochaines élections européennes de 2024 ?",
                    title="Informations complémentaires sur la question contenue dans l'enquête :",
                    easy_close=False
            )
        ui.modal_show(m)

    # bouton onglet 2 : indice de participation
    @reactive.effect
    @reactive.event(input.descript_indpart)
    def _():
        m = ui.modal("L'indice de participation aux élections européennes de juin 2024 INDPART est calculé à partir de la question : les prochaines élections européennes se tiendront le 9 juin 2024 en France. Pouvez-vous donner une note de 0 à 10 sur votre intention d’aller voter lors de ces élections européennes ? 0 signifiant que vous êtes vraiment tout à fait certain de ne pas aller voter, et 10 que vous êtes vraiment tout à fait certain d’aller voter.",
                    title="Informations complémentaires sur la question contenue dans l'enquête :",
                    easy_close=False
            )
        ui.modal_show(m)

    # graphique onglet 2
    @output
    @render_widget
    def graph_interet():

        # charge les données spécifiquement préparées pour ce graphique
        indicateurs = pd.read_csv("data/indicateurs.csv")

        # construit le graphique avec autant de courbe que "d'Indicateurs"
        fig = px.line(indicateurs,
            x="Date",
            y="Valeur",
            color="Indicateurs",
            markers=True,
            template="plotly_white",
            hover_data={"Valeur": False,
                        "Indicateurs": False,
                        "Date": False
                      },
            labels={'Valeur':"Pourcentage de répondants (%)",
                  'Date': "Vague de l'enquête"},
        )

        # améliorations graphiques variées
        fig.update_layout(yaxis_range=[30, 70])
        fig.update_traces(textposition="top right", line=dict(width=2), line_shape="spline")
        fig.update_traces(marker=dict(size=8, line=dict(width=2, color='dimgrey')))
        fig.update_traces(hovertemplate=None)
        fig.update_layout(hovermode="x")

        # source
        annotations = []
        annotations.append(dict(xref='paper',
                                yref='paper',
                                x=0.9,
                                y=-0.22,
                                text='Enquête électorale française pour les ' +
                                    'élections européennes de juin 2024, ' +
                                    'par Ipsos Sopra Steria, Cevipof, ' +
                                    'Le Monde, Fondation Jean Jaurès et ' +
                                    'Institut Montaigne (2024)',
                                font=dict(family='Arial',
                                        size=12,
                                        color='rgb(153, 122, 144)'),
                                showarrow=False
                                )
        )
        fig.update_layout(annotations=annotations)

        # affiche des lignes verticales grise à chaque vagues avec une annotation de la date
        for date in list(indicateurs.Date):
            fig.add_vline(
                x=datetime.datetime.strptime(date, "%Y-%m-%d").timestamp() * 1000,
                line_width=2,
                line_color="grey",
                # annotation_text=datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%B %Y"),
                # annotation_position="top left",
                # annotation_borderpad=10,
            )
        return fig

    # onglet 3

    # bouton onglet 3 : question posée dans l'enquête
    @reactive.effect
    @reactive.event(input.Show_CERT_Question)
    def _():
        m = ui.modal("Les prochaines élections européennes se tiendront le 9 juin 2024 en France. \
                    Pouvez-vous donner une note de 0 à 10 sur votre intention d’aller voter lors de ces élections européennes ? \
                    0 signifiant que vous êtes vraiment tout à fait certain de ne pas aller voter, \
                    et 10 que vous êtes vraiment tout à fait certain d’aller voter.",
                    title="Informations complémentaires sur la question contenue dans l'enquête :",
                    easy_close=False
            )
        ui.modal_show(m)

    # bouton onglet 3 : variable choisie pour les graphiques
    @reactive.effect
    @reactive.event(input.Show_CERTST_Info)
    def _():
        m = ui.modal("La variable sur la certitude d'aller voter présentée ici sur les graphiques est une modalité synthétique \
                    de la question posée aux répondants de l'enquête. \
                    Ainsi, parmi les onze modalités de réponse (0 à 10) à la question de l'enquête, \
                    on ne retient que les valeurs 9 et 10, dont on additionne les fréquences respectives.",
                    title="Informations complémentaires sur la variable choisie pour les graphiques :",
                    easy_close=True
            )
        ui.modal_show(m)

    # bouton onglet 3 : afficher sa description (variable socio-démographique)
    @reactive.effect
    @reactive.event(input.Show_VarSD_Info)
    def _():
        # définir la description de la variable socio-démographique choisie
        # avec plusieurs parties de texte variables
        # nom de la variable socio-démographique choisie
        dico_nom_var = {
                    "SEXEST": "Genre",
                    "AGERST": "Âge",
                    "REG13ST": "Région",
                    "AGGLO5ST": "Taille d'agglomération",
                    "EMPST": "Type d'emploi occupé",
                    "PCSIST": "Catégorie professionnelle",
                    "EDUR4ST": "Niveau de scolarité atteint",
                    "REL1ST": "Religion",
                    "ECO2ST2": "Revenu mensuel du foyer",
                    "INTPOLST": "Intérêt pour la politique",
                    "Q7ST": "Positionnement idéologique",
                    "PROXST": "Préférence partisane"
        }
        # question de l'enquête associée à la variable socio-démographique choisie
        dico_question_var = {
                    "SEXEST": "Êtes-vous ?",
                    "AGERST": "Quelle est votre date de naissance ?",
                    "REG13ST": "Veuillez indiquer le département et la commune où vous résidez.",
                    "AGGLO5ST": "Veuillez indiquer le département et la commune où vous résidez.",
                    "EMPST": "Quelle est votre situation professionnelle actuelle ?",
                    "PCSIST": "Quelle est votre situation professionnelle actuelle ?",
                    "EDUR4ST": "Choisissez votre niveau de scolarité le plus élevé.",
                    "REL1ST": "Quelle est votre religion, si vous en avez une ?",
                    "ECO2ST2": " Pour finir, nous avons besoin de connaître, à des fins statistiques uniquement, la tranche dans laquelle se situe le revenu MENSUEL NET de votre FOYER après déduction des impôts sur le revenu (veuillez considérer toutes vos sources de revenus: salaires, bourses, prestations retraite et sécurité sociale, dividendes, revenus immobiliers, pensions alimentaires etc.).",
                    "INTPOLST": "De manière générale, diriez-vous que vous vous intéressez à la politique ?",
                    "Q7ST": "Sur une échelle de 0 à 10, où 0 correspond à la gauche et 10 correspond à la droite, où diriez-vous que vous vous situez ?",
                    "PROXST": "De quel parti vous sentez-vous proche ou moins éloigné que les autres ?"
        }
        # modalités de réponse à la question de l'enquête associée à la variable socio-démographique choisie
        dico_modalite_var = {
                    "SEXEST": "1 = 'Homme' ; 2 = 'Femme'",
                    "AGERST": "1 = '18 à 24 ans' ; 2 = '25 à 34 ans' ; 3 = '35 à 49 ans' ; 4 = '50 à 59 ans' ; 5 = '60 ans et plus'",
                    "REG13ST": "1 = 'Ile de France' ; 2 = 'Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)' ; 3 = 'Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)' ; 4 = 'Sud ouest (Nouvelle Aquitaine et Occitanie)' ; 5 = 'Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)'",
                    "AGGLO5ST": "1 = 'Zone rurale (moins de 2 000 habitants)' ; 2 = 'Zone urbaine de 2 000 à 9 999 habitants' ; 3 = 'Zone urbaine de 10 000 à 49 999 habitants' ; 4 = 'Zone urbaine de 50 000 à 199 999 habitants' ; 5 = 'Zone urbaine de 200 000 habitants et plus'",
                    "EMPST": "1 = 'Salarié (salarié à plein temps ou à temps partiel)' ; 2 = 'Indépendant (travaille à mon compte)' ; 3 = 'Sans emploi (ne travaille pas actuellement tout recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)'",
                    "PCSIST": "1 = 'Agriculteur exploitant, artisan, commerçant, chef d'entreprise' ; 2 = 'Cadre supérieur' ; 3 = 'Profession intermédiaire' ; 4 = 'Employé' ; 5 = 'Ouvrier' ; 6 = 'Retraité, inactif'",
                    "EDUR4ST": "1 = 'Aucun diplôme, CEP' ; 2 = 'BEPC, CAP, BEP' ; 3 = 'Baccalauréat ' ; 4 = 'Diplôme de l'enseignement supérieur'",
                    "REL1ST": "1 = 'Catholique' ; 2 = 'Juive' ; 3 = 'Musulmane' ; 4 = 'Autre religion (protestante, boudhiste ou autre)' ; 5 = 'Sans religion'",
                    "ECO2ST2": "1 = 'Moins de 1 250 euros' ; 2 = 'De 1 250 euros à 1 999 euros' ; 3 = 'De 2 000 à 3 499 euros' ; 4 = 'De 3 500 à 4 999 euros' ; 5 = 'De 3 500 à 4 999 euros'",
                    "INTPOLST": "1 = 'Beaucoup' ; 2 = 'Un peu' ; 3 = 'Pas vraiment' ; 4 = 'Pas du tout'",
                    "Q7ST": "1 = 'Très à gauche' ; 2 = 'Plutôt à gauche' ; 3 = 'Au centre' ; 4 = 'Plutôt à droite' ; 5 = 'Très à droite'",
                    "PROXST": "1 = 'Gauche et écologistes (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise, Parti Socialiste, Europe Ecologie - Les Verts)' ; 2 = 'Centre (La République En Marche !, désormais Renaissance, Le MoDem (Mouvement Démocrate), Horizons, L’UDI (Union des Démocrates et Indépendants))' ; 3 = 'Droite (Les Républicains)' ; 4 = 'Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)' ; 5 = 'Autre parti ou aucun parti'"
        }
        # définir le texte complet à afficher (parties fixes et variables)
        m = ui.modal("La variable '%s' correspond à ou est calculée à partir de la question suivante posée aux répondants : \
                     '%s', \
                     et ses modalités de réponse (inchangées par rapport au questionnaire ou regroupées pour les présents graphiques) sont : \
                     %s." % (dico_nom_var.get("%s" % input.select_VarSD()),
                             dico_question_var.get("%s" % input.select_VarSD()),
                             dico_modalite_var.get("%s" % input.select_VarSD())
                     ),
                     title="Informations complémentaires sur la variable socio-démographique choisie :",
                     easy_close=True
            )
        ui.modal_show(m)

    # graphique onglet 3
    @output
    @render_plotly
    def graph_croise():

        # importer la base de données au format CSV avec Panda
        csvfile = "data/T_certst3_" + "%s" % input.select_VarSD().lower() + ".csv"
        data = pd.read_csv(csvfile)

        # supprimer la première colonne (vide) de la base de donnée
        data = data.drop(data.columns[0], axis=1)

        # définir la partie variable du titre
        dico_titre = {
                    "SEXEST": "du genre",
                    "AGERST": "de l'âge",
                    "REG13ST": "de la région de résidence",
                    "AGGLO5ST": "de la taille de l'agglomération de résidence",
                    "EMPST": "du type d'emploi occupé",
                    "PCSIST": "de la catégorie socio-professionnelle",
                    "EDUR4ST": "du niveau de scolarité atteint",
                    "REL1ST": "de la religion",
                    "ECO2ST2": "du revenu mensuel du foyer",
                    "INTPOLST": "de l'intérêt pour la politique",
                    "Q7ST": "du positionnement idéologique",
                    "PROXST": "de la préférence partisane"
        }
        # définir la partie variable de la légende
        dico_legende = {
                    "SEXEST": "Genre",
                    "AGERST": "Âge",
                    "REG13ST": "Région",
                    "AGGLO5ST": "Taille d'agglomération",
                    "EMPST": "Type d'emploi occupé",
                    "PCSIST": "Catégorie professionnelle",
                    "EDUR4ST": "Niveau de scolarité atteint",
                    "REL1ST": "Religion",
                    "ECO2ST2": "Revenu mensuel du foyer",
                    "INTPOLST": "Intérêt pour la politique",
                    "Q7ST": "Positionnement idéologique",
                    "PROXST": "Préférence partisane"
        }
        # définir l'échelle variable de l'axe des ordonnées
        dico_echelleY = {
                    "SEXEST": [35, 65],
                    "AGERST": [20, 80],
                    "REG13ST": [35, 65],
                    "AGGLO5ST": [40, 60],
                    "EMPST": [30, 70],
                    "PCSIST": [25, 75],
                    "EDUR4ST": [35, 65],
                    "REL1ST": [20, 70],
                    "ECO2ST2": [30, 70],
                    "INTPOLST": [10, 90],
                    "Q7ST": [30, 80],
                    "PROXST": [20, 80],
        }

        # arrondir les fréquences croisées pondérées (besoin des étiquettes)
        data["pct"] = round(data["pct"], 2)

        # créer un graphique de courbes
        fig = px.line(data,
                      x="VAGUE",
                      y="pct",
                      # chaque modalité de la variable a une couleur de courbe différente
                      color="%s" % input.select_VarSD(),
                      # chaque modalité de la variable a un marqueur de valeur différent
                      markers=True,
                      # données à afficher au survol des points
                      hover_data={"%s" % input.select_VarSD():False,
                                  "CERTST3":False,
                                  "pct":True,
                                  "n":False,
                                  "unweighted_n":False,
                                  "VAGUE":False
                                },
                      # définir les titres des axes et celui de la légende
                      labels={'pct':"Pourcentage de répondants (%)",
                              'CERTST3':"Certitude d'aller voter",
                              '%s' % input.select_VarSD(): '%s' % dico_legende.get("%s" % input.select_VarSD()),
                              'VAGUE': ""},
                      # définir l'apparence du graphique
                      template="plotly_white"
                    )

        # améliorations graphiques variées
        fig.update_traces(hovertemplate=None)
        fig.update_layout(hovermode="x")
        fig.update_layout(yaxis_range=dico_echelleY.get("%s" % input.select_VarSD())),
        fig.update_traces(textposition="top right", line=dict(width=2), line_shape="spline")
        fig.update_traces(marker=dict(size=8, line=dict(width=2, color='dimgrey')))

        # définir le titre du graphique
        fig.update_layout(
            title="Certitude d'aller voter en fonction %s" % dico_titre.get("%s" % input.select_VarSD()),
            xaxis_tickfont_size=12,
            yaxis=dict(
                title='Pourcentage de répondants (%)',
                titlefont_size=12,
                tickfont_size=12,
            )
        )

        # source
        annotations = []
        annotations.append(dict(xref='paper',
                                yref='paper',
                                x=0.925,
                                y=-0.09,
                                text='Enquête électorale française pour les ' +
                                    'élections européennes de juin 2024, ' +
                                    'par Ipsos Sopra Steria, Cevipof, ' +
                                    'Le Monde, Fondation Jean Jaurès et ' +
                                    'Institut Montaigne (2024)',
                                font=dict(family='Arial',
                                        size=12,
                                        color='rgb(153, 122, 144)'),
                                showarrow=False
                                )
        )
        fig.update_layout(annotations=annotations)

        # affiche des lignes verticales grise à chaque vagues avec une annotation de la date
        for date in list(data.VAGUE):
            fig.add_vline(
                x=datetime.datetime.strptime(date, "%Y-%m-%d").timestamp() * 1000,
                line_width=2,
                line_color="grey",
                # annotation_text=datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%B %Y"),
                # annotation_position="top left",
                # annotation_borderpad=10
            )

        return fig

    # onglet 5

    # boutons onglet 5
    @reactive.effect
    @reactive.event(input.Show_CERT_Question_Abst)
    def _():
        m = ui.modal("Les prochaines élections européennes se tiendront le 9 juin 2024 en France. \
                    Pouvez-vous donner une note de 0 à 10 sur votre intention d’aller voter lors de ces élections européennes ? \
                    0 signifiant que vous êtes vraiment tout à fait certain de ne pas aller voter, \
                    et 10 que vous êtes vraiment tout à fait certain d’aller voter.",
                    title="Informations complémentaires sur la question contenue dans l'enquête :",
                    easy_close=False
            )
        ui.modal_show(m)

    @reactive.effect
    @reactive.event(input.Show_CERTST_Info_Abst)
    def _():
        m = ui.modal("La variable sur la certitude de s'abstenir présentée ici sur les graphiques est une modalité synthétique \
                    de la question posée aux répondants de l'enquête. \
                    Ainsi, parmi les onze modalités de réponse (0 à 10) à la question de l'enquête, \
                    on ne retient que les valeurs 0 à 5, dont on additionne les fréquences respectives.",
                    title="Informations complémentaires sur la variable choisie pour les graphiques :",
                    easy_close=True
            )
        ui.modal_show(m)

    @reactive.effect
    @reactive.event(input.Show_VarSD_Info_Abst)
    def _():
        # définir la description de la variable socio-démographique choisie
        # avec plusieurs parties de texte variables
        # nom de la variable socio-démographique choisie
        dico_nom_var = {
                    "SEXEST": "Genre",
                    "AGERST": "Âge",
                    "REG13ST": "Région",
                    "AGGLO5ST": "Taille d'agglomération",
                    "EMPST": "Type d'emploi occupé",
                    "PCSIST": "Catégorie professionnelle",
                    "EDUR4ST": "Niveau de scolarité atteint",
                    "REL1ST": "Religion",
                    "ECO2ST2": "Revenu mensuel du foyer",
                    "INTPOLST": "Intérêt pour la politique",
                    "Q7ST": "Positionnement idéologique",
                    "PROXST": "Préférence partisane"
        }
        # question de l'enquête associée à la variable socio-démographique choisie
        dico_question_var = {
                    "SEXEST": "Êtes-vous ?",
                    "AGERST": "Quelle est votre date de naissance ?",
                    "REG13ST": "Veuillez indiquer le département et la commune où vous résidez.",
                    "AGGLO5ST": "Veuillez indiquer le département et la commune où vous résidez.",
                    "EMPST": "Quelle est votre situation professionnelle actuelle ?",
                    "PCSIST": "Quelle est votre situation professionnelle actuelle ?",
                    "EDUR4ST": "Choisissez votre niveau de scolarité le plus élevé.",
                    "REL1ST": "Quelle est votre religion, si vous en avez une ?",
                    "ECO2ST2": " Pour finir, nous avons besoin de connaître, à des fins statistiques uniquement, la tranche dans laquelle se situe le revenu MENSUEL NET de votre FOYER après déduction des impôts sur le revenu (veuillez considérer toutes vos sources de revenus: salaires, bourses, prestations retraite et sécurité sociale, dividendes, revenus immobiliers, pensions alimentaires etc.).",
                    "INTPOLST": "De manière générale, diriez-vous que vous vous intéressez à la politique ?",
                    "Q7ST": "Sur une échelle de 0 à 10, où 0 correspond à la gauche et 10 correspond à la droite, où diriez-vous que vous vous situez ?",
                    "PROXST": "De quel parti vous sentez-vous proche ou moins éloigné que les autres ?"
        }
        # modalités de réponse à la question de l'enquête associée à la variable socio-démographique choisie
        dico_modalite_var = {
                    "SEXEST": "1 = 'Homme' ; 2 = 'Femme'",
                    "AGERST": "1 = '18 à 24 ans' ; 2 = '25 à 34 ans' ; 3 = '35 à 49 ans' ; 4 = '50 à 59 ans' ; 5 = '60 ans et plus'",
                    "REG13ST": "1 = 'Ile de France' ; 2 = 'Nord et Est (Hauts de France, Grand Est et Bourgogne Franche Comté)' ; 3 = 'Ouest (Normandie, Bretagne, Pays de la Loire et Centre Val de Loire)' ; 4 = 'Sud ouest (Nouvelle Aquitaine et Occitanie)' ; 5 = 'Sud est (Auvergne Rhône Alpes, Provence Alpes Côte d'Azur et Corse)'",
                    "AGGLO5ST": "1 = 'Zone rurale (moins de 2 000 habitants)' ; 2 = 'Zone urbaine de 2 000 à 9 999 habitants' ; 3 = 'Zone urbaine de 10 000 à 49 999 habitants' ; 4 = 'Zone urbaine de 50 000 à 199 999 habitants' ; 5 = 'Zone urbaine de 200 000 habitants et plus'",
                    "EMPST": "1 = 'Salarié (salarié à plein temps ou à temps partiel)' ; 2 = 'Indépendant (travaille à mon compte)' ; 3 = 'Sans emploi (ne travaille pas actuellement tout recherchant un emploi ou non, personne au foyer, retraité, étudiant ou élève)'",
                    "PCSIST": "1 = 'Agriculteur exploitant, artisan, commerçant, chef d'entreprise' ; 2 = 'Cadre supérieur' ; 3 = 'Profession intermédiaire' ; 4 = 'Employé' ; 5 = 'Ouvrier' ; 6 = 'Retraité, inactif'",
                    "EDUR4ST": "1 = 'Aucun diplôme, CEP' ; 2 = 'BEPC, CAP, BEP' ; 3 = 'Baccalauréat ' ; 4 = 'Diplôme de l'enseignement supérieur'",
                    "REL1ST": "1 = 'Catholique' ; 2 = 'Juive' ; 3 = 'Musulmane' ; 4 = 'Autre religion (protestante, boudhiste ou autre)' ; 5 = 'Sans religion'",
                    "ECO2ST2": "1 = 'Moins de 1 250 euros' ; 2 = 'De 1 250 euros à 1 999 euros' ; 3 = 'De 2 000 à 3 499 euros' ; 4 = 'De 3 500 à 4 999 euros' ; 5 = 'De 3 500 à 4 999 euros'",
                    "INTPOLST": "1 = 'Beaucoup' ; 2 = 'Un peu' ; 3 = 'Pas vraiment' ; 4 = 'Pas du tout'",
                    "Q7ST": "1 = 'Très à gauche' ; 2 = 'Plutôt à gauche' ; 3 = 'Au centre' ; 4 = 'Plutôt à droite' ; 5 = 'Très à droite'",
                    "PROXST": "1 = 'Gauche et écologistes (Lutte Ouvrière, Nouveau Parti Anticapitaliste, Parti Communiste Français, France Insoumise, Parti Socialiste, Europe Ecologie - Les Verts)' ; 2 = 'Centre (La République En Marche !, désormais Renaissance, Le MoDem (Mouvement Démocrate), Horizons, L’UDI (Union des Démocrates et Indépendants))' ; 3 = 'Droite (Les Républicains)' ; 4 = 'Très à droite (Debout la France, Rassemblement national (ex Front National), Reconquête!)' ; 5 = 'Autre parti ou aucun parti'"
        }
        # définir le texte complet à afficher (parties fixes et variables)
        m = ui.modal("La variable '%s' correspond à ou est calculée à partir de la question suivante posée aux répondants : \
                     '%s', \
                     et ses modalités de réponse (inchangées par rapport au questionnaire ou regroupées pour les présents graphiques) sont : \
                     %s." % (dico_nom_var.get("%s" % input.select_VarSD_Abst()),
                             dico_question_var.get("%s" % input.select_VarSD_Abst()),
                             dico_modalite_var.get("%s" % input.select_VarSD_Abst())
                     ),
                     title="Informations complémentaires sur la variable socio-démographique choisie :",
                     easy_close=True
            )
        ui.modal_show(m)

    # graphique onglet 5
    @output
    @render_plotly
    def graph_croise_Abst():

        # importer la base de données au format CSV avec Panda
        csvfile = "data/T_certst1_" + "%s" % input.select_VarSD_Abst().lower() + ".csv"
        data = pd.read_csv(csvfile)
        # supprimer la première colonne (vide) de la base de donnée
        data = data.drop(data.columns[0], axis=1)

        # définir la partie variable du titre
        dico_titre = {
                    "SEXEST": "du genre",
                    "AGERST": "de l'âge",
                    "REG13ST": "de la région de résidence",
                    "AGGLO5ST": "de la taille de l'agglomération de résidence",
                    "EMPST": "du type d'emploi occupé",
                    "PCSIST": "de la catégorie socio-professionnelle",
                    "EDUR4ST": "du niveau de scolarité atteint",
                    "REL1ST": "de la religion",
                    "ECO2ST2": "du revenu mensuel du foyer",
                    "INTPOLST": "de l'intérêt pour la politique",
                    "Q7ST": "du positionnement idéologique",
                    "PROXST": "de la préférence partisane"
        }
        # définir la partie variable de la légende
        dico_legende = {
                    "SEXEST": "Genre",
                    "AGERST": "Âge",
                    "REG13ST": "Région",
                    "AGGLO5ST": "Taille d'agglomération",
                    "EMPST": "Type d'emploi occupé",
                    "PCSIST": "Catégorie professionnelle",
                    "EDUR4ST": "Niveau de scolarité atteint",
                    "REL1ST": "Religion",
                    "ECO2ST2": "Revenu mensuel du foyer",
                    "INTPOLST": "Intérêt pour la politique",
                    "Q7ST": "Positionnement idéologique",
                    "PROXST": "Préférence partisane"
        }
        # définir l'échelle variable de l'axe des ordonnées
        dico_echelleY = {
                    "SEXEST": [10, 40],
                    "AGERST": [5, 45],
                    "REG13ST": [10, 40],
                    "AGGLO5ST": [10, 40],
                    "EMPST": [10, 40],
                    "PCSIST": [10, 50],
                    "EDUR4ST": [10, 40],
                    "REL1ST": [10, 50],
                    "ECO2ST2": [10, 50],
                    "INTPOLST": [0, 70],
                    "Q7ST": [0, 40],
                    "PROXST": [0, 60],
        }

        # arrondir les fréquences croisées pondérées (besoin des étiquettes)
        data["pct"] = round(data["pct"], 2)

        # créer un graphique de courbes
        fig = px.line(data,
                      x="VAGUE",
                      y="pct",
                      # chaque modalité de la variable a une couleur de courbe différente
                      color="%s" % input.select_VarSD_Abst(),
                      # chaque modalité de la variable a un marqueur de valeur différent
                      markers=True,
                      # données à afficher au survol des points
                      hover_data={"%s" % input.select_VarSD_Abst():False,
                                  "CERTST1":False,
                                  "pct":True,
                                  "n":False,
                                  "unweighted_n":False,
                                  "VAGUE":False
                                },
                      # définir les titres des axes et celui de la légende
                      labels={'pct':"Pourcentage de répondants (%)",
                              'CERTST1':"Certitude de s'abstenir",
                              '%s' % input.select_VarSD_Abst(): '%s' % dico_legende.get("%s" % input.select_VarSD_Abst()),
                              'VAGUE': ""},
                      # définir l'apparence du graphique
                      template="plotly_white"
                    )

        # améliorations graphiques variées
        fig.update_traces(hovertemplate=None)
        fig.update_layout(hovermode="x")
        fig.update_layout(yaxis_range=dico_echelleY.get("%s" % input.select_VarSD_Abst())),
        fig.update_traces(textposition="top right", line=dict(width=2), line_shape="spline")
        fig.update_traces(marker=dict(size=8, line=dict(width=2, color='dimgrey')))

        # définir le titre du graphique
        fig.update_layout(
            title="Certitude de s'abstenir en fonction %s" % dico_titre.get("%s" % input.select_VarSD_Abst()),
            xaxis_tickfont_size=12,
            yaxis=dict(
                title='Pourcentage de répondants (%)',
                titlefont_size=12,
                tickfont_size=12,
            )
        )
        # source
        annotations = []
        annotations.append(dict(xref='paper',
                                yref='paper',
                                x=0.925,
                                y=-0.09,
                                text='Enquête électorale française pour les ' +
                                    'élections européennes de juin 2024, ' +
                                    'par Ipsos Sopra Steria, Cevipof, ' +
                                    'Le Monde, Fondation Jean Jaurès et ' +
                                    'Institut Montaigne (2024)',
                                font=dict(family='Arial',
                                        size=12,
                                        color='rgb(153, 122, 144)'),
                                showarrow=False
                                )
        )
        fig.update_layout(annotations=annotations)

        # affiche des lignes verticales grise à chaque vagues avec une annotation de la date
        for date in list(data.VAGUE):
            fig.add_vline(
                x=datetime.datetime.strptime(date, "%Y-%m-%d").timestamp() * 1000,
                line_width=2,
                line_color="grey",
                # annotation_text=datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%B %Y"),
                # annotation_position="top left",
                # annotation_borderpad=10
            )

        return fig

# définir l'app
app = App(app_ui, server)
