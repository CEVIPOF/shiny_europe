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



# connecter le compte sur la plateforme Shiny.io avec le système de programmation local
# rsconnect add --account enquetespolitiques --name enquetespolitiques --token 3BF562671C154D959D98A0C38B28B340 --secret +y8Ze41ys35rl7sESMnhnOgEiudZB96JFfn1fb22
# déployer l'application sur le serveur de Shiny.io via le compte personnel sur la plateforme
# rsconnect deploy shiny C:\Users\53187\Documents\_Elections\2024_Européennes\Appli_Viz --name enquetespolitiques --title appFrUE24



# importer les méthodes utiles
from shiny import App, render, ui, reactive
from shinywidgets import output_widget, render_widget  
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np



#########################################################################################
# Importer les données et faire un modèle de graphique (VERSION TEMPORAIRE)
#########################################################################################


# importer la base de données au format CSV avec Panda
# csvfile = 'C:/Users/53187/Documents/_Elections/2024_Européennes/Resultats_CSV/FR03Final.csv'
# FR03Final = pd.read_csv(csvfile)
# print(FR03Final)
csvfile = 'C:/Users/53187/Documents/_Elections/2024_Européennes/Resultats_CSV/tables_croisees/cas04/CT_w4_cert_red_agerst_red.csv'
CT_w4_cert_red_agerst_red = pd.read_csv(csvfile)
print(CT_w4_cert_red_agerst_red)

# remplacer toutes les valeurs manquantes codées 99 par NA
# CT_w1_cert_org_ager_org = FR03Final.replace(99, np.nan)
# supprimer la première colonne (vide) de la base de donnée
CT_w4_cert_red_agerst_red = CT_w4_cert_red_agerst_red.drop(CT_w4_cert_red_agerst_red.columns[0], axis=1)
print(CT_w4_cert_red_agerst_red)


import plotly.express as px
df = CT_w4_cert_red_agerst_red
nom_var = "de l'âge de l'individu"
vague = "vague 4"

fig = px.bar(df, x="Y4CERTST", y="pct",
             text="pct",
             barmode="group",
             color="Y4AGERST",
             labels={'pct':"Pourcentage de répondants (%)",
                     'Y4CERTST':"Intention d'aller voter : 1 = Certain de ne pas aller voter ; 2 = Ni l'un, ni l'autre ; 3 = Certain d'aller voter",
                     'Y4AGERST': "Âge"},
             text_auto='.1f'
            )
fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
fig.update_xaxes(dtick=1)
fig.update_layout(
    title="Intention d'aller voter en fonction " + nom_var + " à la " + vague,
    xaxis_tickfont_size=12,
    yaxis=dict(
        title='Pourcentage de répondants (%)',
        titlefont_size=12,
        tickfont_size=12,
    ),
    legend=dict(
        orientation="h",
        xanchor="left",
        x=0.01,
        yanchor="top",
        y=-0.20,
        bgcolor='rgba(255, 255, 255, 0)',
        bordercolor='rgba(255, 255, 255, 0)'
    ),
    uniformtext_minsize=12,
    bargap=0.15, # gap between bars of adjacent location coordinates.
    bargroupgap=0.1 # gap between bars of the same location coordinate.
)
# Source
annotations = []
annotations.append(dict(xref='paper',
                        yref='paper',
                        x=0.0,
                        y=1.07,
                        text='Enquête électorale française pour les ' +
                            'élections européennes de juin 2024, ' +
                            'par Ipsos Sopra Steria, Cevipof, ' +
                            'Le Monde, Fondation Jean Jaurès et ' +
                            'Institut Montaigne (2024)',
                        font=dict(family='Arial',
                                  size=12,
                                  color='rgb(105,105,105)'), # 132,132,132
                        showarrow=False
                        )
)
fig.update_layout(annotations=annotations)
fig.show()









#########################################################################################
# Construire l'application
#########################################################################################


# définir une méthode utile pour construire des cadres d'information selon le même format
def ui_card(title, *args):
    return (
        ui.div(
            {"class": "card mb-4"},
            ui.div(title, class_="card-header"),
            ui.div({"class": "card-body"}, *args),
        ),
    )


# définir la page principale de l'application
app_ui = ui.page_fillable(

    # définir le titre de l'application
    ui.h2("Enquête électorale française sur les élections européennes du 9 juin 2024"
    ),
    
    # définir les onglets contenus dans la page principale de l'application
    ui.navset_card_pill(

        # onglet 01
        ui.nav_panel("Présentation",
                    # texte de présentation du projet et des enquêtes
                    ui.markdown(
                        """
                        Dans la perspective des élections européennes du 9 juin 2024, **Ipsos Sopra Steria**,
                        le **Cevipof** et **Le Monde** ont mis en place en juin 2023 un dispositif d'enquêtes
                        par panel.

                        Composé de plus de 10 000 personnes, ce groupe d'individus est interrogé
                        à 6 reprises de juin 2023 à juin 2024, afin de mieux comprendre les logiques de
                        leurs décisions de vote pour ces élections.
                        
                        Cette application présente brièvement quelques principaux résultats de cette
                        *enquête électorale française pour les élections européennes du 9 juin 2024*,
                        afin de les rendre plus accessibles et de contribuer au débat public.

                        Les résultats détaillés de ce dispositif d'enquêtes, accompagnés de décryptages et
                        d'analyses fouillées, sont disponibles sur la **[page dédiée du Cevipof](https://www.sciencespo.fr/cevipof/fr/content/resultats-et-decrypyages-par-vagues.html)**.

                        Il est rappelé à l'utilisateur que ces résultats graphiques sont **à considérer avec la plus
                        grande prudence d'interprétation** et de jugement, notamment ceux concernant les graphiques
                        de croisement de variables : un lien entre deux variables suggéré graphiquement doit ensuite
                        être complété, validé ou infirmé par des analyses et modélisations statistiques approfondies.
                        Or, la présente application a été pensée uniquement à des fins de vulgarisation scientifique,
                        et non pour permettre une exploration approfondie des données, ni une analyse exhaustive et
                        robuste des potentiels liens structurels entre les variables.

                        Il est par conséquent vivement recommandé à l'utilisateur de **[contacter le Cevipof](https://www.sciencespo.fr/cevipof/fr/liste-de-contacts.html)**
                        et les chercheurs membres du laboratoire en cas de doute, ou pour toute question ou besoin
                        de clarification, de contextualisation ou d'analyse détaillée et commentée de ces
                        principaux résultats graphiques.
                        """
                    )
        ),

        # onglet 02
        ui.nav_panel("Tableau de bord général",
                     "Variables à représenter : INTEURST, CERT et INDPART"
        ),

        # onglet 03
        ui.nav_panel("Intention d'aller voter",
            # définir deux colonnes sur cet onglet (une pour les informations, une pour le graphique)
            ui.layout_columns(
                # colonne 1 de l'onglet : informations et choix de l'utilisateur
                ui.card(
                    # cadre 01 : informations sur la variable de l'intention d'aller voter
                    ui_card("INTENTION D'ALLER VOTER",
                            # bouton 01 avec affichage de texte en bulle
                            ui.tooltip(  
                                ui.input_action_button("Show_CERT_Question", # input ID
                                                       "Question posée dans l'enquête" # texte affiché dans le bouton
                                ),
                                "Les prochaines élections européennes se tiendront le 9 juin 2024 en France. \
                                Pouvez-vous donner une note de 0 à 10 sur votre intention d’aller voter lors de ces élections européennes ? \
                                0 signifiant que vous êtes vraiment tout à fait certain de ne pas aller voter, \
                                et 10 que vous êtes vraiment tout à fait certain d’aller voter.",
                                id="act_but_01",  
                                placement="right" 
                            ),
                            # bouton 02 avec affichage de texte en bulle
                            ui.tooltip(  
                                ui.input_action_button("Show_CERT_Com", # input ID
                                                       "Commentaires sur la variable des graphiques" # texte affiché dans le bouton
                                ),
                                "La variable sur l'intention d'aller voter présentée ici sur les graphiques est une version simplifiée \
                                de la question posée aux répondants de l'enquête. \
                                Ainsi, ses onze modalités de réponse (0 à 10) sont réduites à trois : \
                                1 pour 'Certain de ne pas aller voter' (addition des modalités de réponses 0 à 3 du questionnaire) ; \
                                2 pour 'Ni l'un, ni l'autre' (addition des modalités de réponses 4 à 6 du questionnaire) ; \
                                3 pour 'Certain d'aller voter' (addition des modalités de réponses 7 à 10 du questionnaire).",
                                id="act_but_02",  
                                placement="right" 
                            )
                    ),

                    # cadre 02 : choix de la vague d'enquête
                    ui_card("CHOISIR UNE VAGUE DE l'ENQUÊTE",
                            ui.input_select(
                                id="select_Vague",
                                label="",
                                choices={"w1": "Vague 01",
                                         "w2": "Vague 02",
                                         "w3": "Vague 03",
                                         "w4": "Vague 04",
                                         "w5": "Vague 05",
                                         "w6": "Vague 06"
                                }
                            )
                    ),

                    # cadre 03 : choix de la variable socio-démographique à croiser avec l'intention d'aller voter
                    ui_card("CHOISIR UNE VARIABLE SOCIO- DEMOGRAPHIQUE",
                            # groupe de boutons de sélection
                            ui.input_radio_buttons(
                                id="select_VarSD",
                                label="",
                                choices={"sexest": "Genre",
                                         "agerst": "Âge",
                                         "reg13st": "Région",
                                         "agglo5st": "Taille d'agglomération",
                                         "empst": "Type d'emploi occupé",
                                         "pcsist": "Catégorie professionnelle",
                                         "edur2st": "Niveau de scolarité atteint",
                                         "rel1st": "Religion",
                                         "eco2st2": "Revenu mensuel du foyer",
                                         "intpolst": "Intérêt pour la politique",
                                         "q7st": "Positionnement idéologique",
                                         "proxst": "Préférence partisane"
                                }
                            ),
                            # cadre 04 : informations détaillées sur la variable socio-démographique choisie
                            ui.input_action_button("Show_VarSD_Info", # input ID
                                                   "Afficher sa description" # texte affiché dans le bouton
                            )                            
                    ),

                    ui.output_ui("Vague_value"),
                    ui.output_ui("VarSD_value"),
                    ui.output_ui("Nom_VarSD_Titre"),
                    ui.output_ui("Nom_Vague_Titre"),
                    ui.output_ui("Nom_Cert_Graph"), 
                    ui.output_ui("Nom_VarSD_Graph"),
                    ui.output_ui("Nom_VarSD_Legende"), 
                ),                

                # colonne 2 de l'onglet : graphique des variables
                ui_card("GRAPHIQUE DE L'INTENTION D'ALLER VOTER EN FONCTION D'UNE VARIABLE SOCIO-DEMOGRAPHIQUE",
                        # afficher le graphique ad hoc
                        fig
                        #output_widget(id="graph_croise")
                ),

                # largeurs respectives des deux cadres sur cet onglet 03
                col_widths=(3, 9)
            )
        ),

        # onglet 04
        ui.nav_panel("Exploration thématique",
                    # barre de navigation contenant les sous-onglets thématiques
                    ui.navset_card_pill(
                        # sous-onglet 01
                        ui.nav_panel("Les raisons de l'abstention", # titre du sous-onglet
                                     "Raisons de l'abstention (vague 03)" # contenu du sous-onglet
                        ),
                        # sous-onglet 02
                        ui.nav_panel("Le conflit israelo-palestinien", # titre du sous-onglet
                                     "Conflit israelo-palestinien (vague 02)" # contenu du sous-onglet
                        ),
                        # sous-onglet 03
                        ui.nav_panel("Les enjeux de ces élections", # titre du sous-onglet
                                     "Les enjeux de ces élections (vague XX)" # contenu du sous-onglet
                        ),
                        # sous-onglet 04
                        ui.nav_panel("La perception de l'Union européenne et de ses valeurs", # titre du sous-onglet
                                     "La perception de l'Union européenne et de ses valeurs (vague 04)" # contenu du sous-onglet
                        )
                    )
        ),

        id="tab"
    ) 
)


# bloc définissant les méthodes mises en oeuvre pour la réactivité des objets
def server(input, output, session):

    # # définir une valeur de réactivité pour la vague
    # reac_val_vague = reactive.Value("")
    # # définir une valeur de réactivité pour la variable
    # # socio-démographique choisie
    # reac_val_varSD = reactive.Value("")

    # # mettre à jour la valeur de réactivité de la vague
    # # en fonction du choix de l'utilisateur
    # @reactive.effect
    # def reac_eff_vague():
    #     reac_val_vague = input.select_Vague()
    #     return reac_val_vague

    # # mettre à jour la valeur de réactivité de la variable
    # # socio-démographique choisie en fonction du choix de
    # # l'utilisateur
    # @reactive.effect
    # def reac_eff_varsd():
    #     reac_val_varsd = input.select_VarSD()
    #     return reac_val_varsd

    @render.ui
    def Vague_value():
        return input.select_Vague()
    
    @render.ui
    def VarSD_value():
        return input.select_VarSD()

    # définir l'intitulé des variables à mettre à jour
    # dans le titre du graphique
    @render.ui
    #@reactive.effect
    def Nom_VarSD_Titre():
        # définir un dictionnaire de correspondance entre
        # le nom des variables socio-démographiques
        # et l'intitulé correspondant dans le titre du graphique
        dic_noms_varsd_titre = {"sexest": "du genre de l'individu",
                                "agerst": "de l'âge de l'individu",
                                "reg13st": "de la région de résidence",
                                "agglo5st": "de la taille d'agglomération",
                                "empst": "du type d'emploi occupé",
                                "pcsist": "de la catégorie professionnelle",
                                "edur2st": "du niveau de scolarité atteint",
                                "rel1st": "de la religion",
                                "eco2st2": "du revenu mensuel du foyer",
                                "intpolst": "de l'intérêt pour la politique",
                                "q7st": "du positionnement idéologique",
                                "proxst": "de la préférence partisane"
                                }
        noms_varsd_titre = dic_noms_varsd_titre.get(input.select_VarSD())
        #noms_varsd_titre = dic_noms_varsd_titre.get(reac_eff_varsd())
        return noms_varsd_titre
    
    # définir l'intitulé des variables à mettre à jour
    # dans la légende du graphique
    @render.ui
    #@reactive.effect
    def Nom_VarSD_Legende():
        # définir un dictionnaire de correspondance entre
        # le nom de la variable socio-démographique choisie
        # et l'intitulé correspondant dans la légende du graphique
        dic_noms_varsd_legende = {"sexest": "Genre",
                                  "agerst": "Âge",
                                  "reg13st": "Région",
                                  "agglo5st": "Taille d'agglomération",
                                  "empst": "Type d'emploi occupé",
                                  "pcsist": "Catégorie professionnelle",
                                  "edur2st": "Niveau de scolarité atteint",
                                  "rel1st": "Religion",
                                  "eco2st2": "Revenu mensuel du foyer",
                                  "intpolst": "Intérêt pour la politique",
                                  "q7st": "Positionnement idéologique",
                                  "proxst": "Préférence partisane"
                                  }
        noms_varsd_legende = dic_noms_varsd_legende.get(input.select_VarSD())
        #noms_varsd_legende = dic_noms_varsd_legende.get(reac_eff_varsd())      
        return noms_varsd_legende 
    
    # définir l'intitulé de la vague d'enquête à mettre à jour
    # dans le titre du graphique
    @render.ui
    #@reactive.effect
    def Nom_Vague_Titre():
        # définir un dictionnaire de correspondance entre
        # le numéro de la vague de l'enquête choisie
        # et l'intitulé correspondant dans le titre du graphique
        dic_noms_vague_titre = {"w1": "vague 01",
                                "w2": "vague 02",
                                "w3": "vague 03",
                                "w4": "vague 04",
                                "w5": "vague 05",
                                "w6": "vague 06"
                                }
        noms_vague_titre = dic_noms_vague_titre.get(input.select_Vague())
        #noms_vague_titre = dic_noms_vague_titre.get(reac_eff_vague())
        return noms_vague_titre
    
    # définir les noms de la variable d'intention d'aller voter
    # à mettre à jour dans la construction du graphique
    # en fonction de la vague de l'enquête
    @render.ui
    #@reactive.effect
    def Nom_Cert_Graph():
        # définir un dictionnaire de correspondance entre
        # le numéro de la vague de l'enquête choisie
        # et l'intitulé correspondant de la variable
        dic_noms_cert_graph = {"w1": "Y1CERTST",
                               "w2": "Y2CERTST",
                               "w3": "Y3CERTST",
                               "w4": "Y4CERTST",
                               "w5": "Y5CERTST",
                               "w6": "Y6CERTST"
                                }
        noms_cert_graph = dic_noms_cert_graph.get(input.select_Vague())
        #noms_cert_graph = dic_noms_cert_graph.get(reac_eff_vague())
        return noms_cert_graph

    # définir le nom de la variable socio-démographique choisie
    # à mettre à jour dans la construction du graphique
    # en fonction de la vague de l'enquête choisie
    @render.ui
    #@reactive.effect
    def Nom_VarSD_Graph():
        # définir deux dictionnaires imbriqués de correspondance
        # entre le numéro de la vague de l'enquête choisie,
        # la variable socio-démographique choise,
        # et l'intitulé correspondant de la variable à cette vague
        dic_noms_varsd_graph = {"w1": {"sexest": "Y1SEXE",
                                       "agerst": "Y1AGERST",
                                       "reg13st": "Y1REG13",
                                       "agglo5st": "Y1AGGLO5ST",
                                       "empst": "Y1EMPST",
                                       "pcsist": "Y1PCSIST",
                                       "edur2st": "Y1EDUR2",
                                       "rel1st": "Y1REL1",
                                       "eco2st2": "Y1ECO2ST2",
                                       "intpolst": "Y1INTPOLST",
                                       "q7st": "Y1Q7ST",
                                       "proxst": "Y1PROX"
                                      },
                                "w2": {"sexest": "Y2SEXE",
                                       "agerst": "Y2AGERST",
                                       "reg13st": "Y2REG13",
                                       "agglo5st": "Y2AGGLO5ST",
                                       "empst": "Y2EMPST",
                                       "pcsist": "Y2PCSIST",
                                       "edur2st": "Y2EDUR2",
                                       "rel1st": "Y2REL1",
                                       "eco2st2": "Y2ECO2ST2",
                                       "intpolst": "Y2INTPOLST",
                                       "q7st": "Y2Q7ST",
                                       "proxst": "Y2PROX"
                                      },
                                "w3": {"sexest": "Y3SEXE",
                                       "agerst": "Y3AGERST",
                                       "reg13st": "Y3REG13",
                                       "agglo5st": "Y3AGGLO5ST",
                                       "empst": "Y3EMPST",
                                       "pcsist": "Y3PCSIST",
                                       "edur2st": "Y3EDUR2",
                                       "rel1st": "Y3REL1",
                                       "eco2st2": "Y3ECO2ST2",
                                       "intpolst": "Y3INTPOLST",
                                       "q7st": "Y3Q7ST",
                                       "proxst": "Y3PROX"
                                      },
                                "w4": {"sexest": "Y4SEXE",
                                       "agerst": "Y4AGERST",
                                       "reg13st": "Y4REG13",
                                       "agglo5st": "Y4AGGLO5ST",
                                       "empst": "Y4EMPST",
                                       "pcsist": "Y4PCSIST",
                                       "edur2st": "Y4EDUR2",
                                       "rel1st": "Y4REL1",
                                       "eco2st2": "Y4ECO2ST2",
                                       "intpolst": "Y4INTPOLST",
                                       "q7st": "Y4Q7ST",
                                       "proxst": "Y4PROX"
                                      },
                                "w5": {"sexest": "Y5SEXE",
                                       "agerst": "Y5AGERST",
                                       "reg13st": "Y5REG13",
                                       "agglo5st": "Y5AGGLO5ST",
                                       "empst": "Y5EMPST",
                                       "pcsist": "Y5PCSIST",
                                       "edur2st": "Y5EDUR2",
                                       "rel1st": "Y5REL1",
                                       "eco2st2": "Y5ECO2ST2",
                                       "intpolst": "Y5INTPOLST",
                                       "q7st": "Y5Q7ST",
                                       "proxst": "Y5PROX"
                                      },
                                "w6": {"sexest": "Y6SEXE",
                                       "agerst": "Y6AGERST",
                                       "reg13st": "Y6REG13",
                                       "agglo5st": "Y6AGGLO5ST",
                                       "empst": "Y6EMPST",
                                       "pcsist": "Y6PCSIST",
                                       "edur2st": "Y6EDUR2",
                                       "rel1st": "Y6REL1",
                                       "eco2st2": "Y6ECO2ST2",
                                       "intpolst": "Y6INTPOLST",
                                       "q7st": "Y6Q7ST",
                                       "proxst": "Y6PROX"
                                      }
                                }
        noms_varsd_graph = dic_noms_varsd_graph.get(input.select_Vague()).get(input.select_VarSD())
        #noms_varsd_graph = dic_noms_varsd_graph.get(reac_eff_vague()).get(reac_eff_varsd())
        return noms_varsd_graph

    @output
    @render_widget
    def graph_croise():
        # importer la base de données au format CSV avec Panda
        #csvfile = "%s%s%s" % ('C:/Users/53187/Documents/_Elections/2024_Européennes/Appli_Viz/CT_', input.select_Vague(), '_cert_', input.select_VarSD(), '.csv')
        csvfile = "{0}{1}{2}{3}{4}".format('C:/Users/53187/Documents/_Elections/2024_Européennes/Appli_Viz/CT_', input.select_Vague(), '_cert_', input.select_VarSD(), '.csv')
        #csvfile = "{0}{1}{2}{3}{4}".format('C:/Users/53187/Documents/_Elections/2024_Européennes/Appli_Viz/CT_', reac_eff_vague(), '_cert_', reac_eff_varsd(), '.csv')
        # sauvegarder les données dans un Panda dataframe
        CT_wi_cert_VarSD = pd.read_csv(csvfile)
        # supprimer la première colonne (vide) de la base de donnée
        CT_wi_cert_VarSD = CT_wi_cert_VarSD.drop(CT_wi_cert_VarSD.columns[0], axis=1)
        # importer la librairie PlotlyExpress pour construire le graphique
        import plotly.express as px
        # définir la figure contenant le graphique en barres verticales
        fig = px.bar(CT_wi_cert_VarSD,
                    x="Y1CERTST",
                    #x=Nom_Cert_Graph(),
                    y="pct",
                    text="pct",
                    barmode="group",
                    color="Y1SEXEST",
                    #color=Nom_VarSD_Graph(),
                    labels={'pct':"Pourcentage de répondants (%)",
                            'Y1CERTST':"Intention d'aller voter : 1 = Certain de ne pas aller voter ; 2 = Ni l'un, ni l'autre ; 3 = Certain d'aller voter",
                            'Y1SEXEST': "Âge"
                            #Nom_Cert_Graph():"Intention d'aller voter : 1 = Certain de ne pas aller voter ; 2 = Ni l'un, ni l'autre ; 3 = Certain d'aller voter",
                            #Nom_VarSD_Graph(): Nom_VarSD_Legende()
                            },
                            text_auto='.1f'
                    )
        fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
        # fixer le pas numérique sur l'axe des abscisses à 1 (valeurs 1, 2 et 3)
        fig.update_xaxes(dtick=1)
        fig.update_layout(
            #title="Intention d'aller voter en fonction " + nom_var + " à la " + vague,
            title="Intention d'aller voter en fonction " + Nom_VarSD_Titre() + " à la " + Nom_Vague_Titre(),
            xaxis_tickfont_size=12,
            yaxis=dict(
                title='Pourcentage de répondants (%)',
                titlefont_size=12,
                tickfont_size=12,
            ),
            legend=dict(
                orientation="h",
                xanchor="left",
                x=0.01,
                yanchor="top",
                y=-0.20,
                bgcolor='rgba(255, 255, 255, 0)',
                bordercolor='rgba(255, 255, 255, 0)'
            ),
            uniformtext_minsize=12,
            bargap=0.15, # gap between bars of adjacent location coordinates.
            bargroupgap=0.1 # gap between bars of the same location coordinate.
        )
        # Source
        annotations = []
        annotations.append(dict(xref='paper',
                                yref='paper',
                                x=0.0,
                                y=1.07,
                                text='Enquête électorale française pour les ' +
                                    'élections européennes de juin 2024, ' +
                                    'par Ipsos Sopra Steria, Cevipof, ' +
                                    'Le Monde, Fondation Jean Jaurès et ' +
                                    'Institut Montaigne (2024)',
                                font=dict(family='Arial',
                                        size=12,
                                        color='rgb(105,105,105)'), # 132,132,132
                                showarrow=False
                                )
        )
        fig.update_layout(annotations=annotations)
        return fig



    @reactive.effect
    @reactive.event(input.Show_VarSD_Info)
    def _():
        m = ui.modal(# texte à rendre réactif en fonction de la variable SD choisie
                     "La variable 'Genre' correspond à la question suivante posée aux répondants : \
                     'Êtes-vous... ?', \
                     et ses modalités de réponse sont : \
                     1 pour 'Homme' \
                     et 2 pour 'Femme'.",  
                     title="Informations complémentaires sur la variable socio-démographique choisie :",
                     easy_close=True
            )  
        ui.modal_show(m) 



# définir l'application comme fonction des deux modules définis ci-dessus
app = App(app_ui, server)






















# # importer la base de données au format CSV avec Panda
# csvfile = 'C:/Users/53187/Documents/_Elections/2024_Européennes/Appli_Viz/CT_w4_cert_agerst.csv'
# CT_w4_cert_agerst = pd.read_csv(csvfile)
# # supprimer la première colonne (vide) de la base de donnée
# CT_w4_cert_agerst = CT_w4_cert_agerst.drop(CT_w4_cert_agerst.columns[0], axis=1)

# df = CT_w4_cert_agerst
# nom_var = "de l'âge de l'individu"
# vague = "vague 4"

# import plotly.express as px
# fig = px.bar(df,
#              x="Y4CERTST",
#              y="pct",
#              text="pct",
#              barmode="group",
#              color="Y4AGERST",
#              labels={'pct':"Pourcentage de répondants (%)",
#                      'Y4CERTST':"Intention d'aller voter : 1 = Certain de ne pas aller voter ; 2 = Ni l'un, ni l'autre ; 3 = Certain d'aller voter",
#                      'Y4AGERST': "Âge"},
#                      text_auto='.1f'
#             )
# fig.update_traces(textfont_size=12, textangle=0, textposition="outside", cliponaxis=False)
# fig.update_layout(
#     title="Intention d'aller voter en fonction " + nom_var + " à la " + vague,
#     xaxis_tickfont_size=12,
#     yaxis=dict(
#         title='Pourcentage de répondants (%)',
#         titlefont_size=12,
#         tickfont_size=12,
#     ),
#     legend=dict(
#         orientation="h",
#         yanchor="top",
#         y=-0.20,
#         xanchor="left",
#         x=0.01,
#         bgcolor='rgba(255, 255, 255, 0)',
#         bordercolor='rgba(255, 255, 255, 0)'
#     ),
#     uniformtext_minsize=12,
#     bargap=0.15, # gap between bars of adjacent location coordinates.
#     bargroupgap=0.1 # gap between bars of the same location coordinate.
# )
# # Source
# annotations = []
# annotations.append(dict(xref='paper',
#                         yref='paper',
#                         x=0.0,
#                         y=0.99,
#                         text='Enquête électorale française pour les ' +
#                              'élections européennes de 2024, ' +
#                              'par Ipsos Sopra Steria, Cevipof, ' +
#                              'Le Monde, Fondation J. Jaurès et ' +
#                              'Institut Montaigne (2024)',
#                         font=dict(family='Arial',
#                                   size=12,
#                                   color='rgb(132,132,132)' # gris (du fond du graphique plotly): rgb(150,150,150)
#                         ),
#                         showarrow=False
#                     )
# )
# fig.update_layout(annotations=annotations)
# fig.show()


