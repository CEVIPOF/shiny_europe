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
from shiny import App, reactive, ui
from shinywidgets import output_widget, render_widget 
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np



#########################################################################################
# Importer les données (VERSION TEMPORAIRE)
#########################################################################################


# importer la base de données au format CSV avec Panda
csvfile = 'C:/Users/53187/Documents/_Elections/2024_Européennes/Resultats_CSV/FR03Final.csv'
FR03Final = pd.read_csv(csvfile)
print(FR03Final)

# remplacer toutes les valeurs manquantes codées 99 par NA
FR03Final = FR03Final.replace(99, np.nan)
# supprimer la première colonne (vide) de la base de donnée
FR03Final = FR03Final.drop(FR03Final.columns[0], axis=1)



#########################################################################################
# Sélectionner les données utiles (VERSION TEMPORAIRE)
#########################################################################################


modalites = FR03Final['Y3CERT'].value_counts(sort=False, dropna=True).sort_index(axis=0, ascending=True).index

# sélectionner les variables dépendantes à représenter et les variables à croiser avec elles
FR03 = FR03Final[['IID', 'Y3INTEURST', 'Y3CERT', 'Y3INDPART', # variables dépendantes onglets 01 et 02
                  'Y3IVEUR4', 'Y3IV4DEF', # variables dépendantes onglet 03
                  'Y3RAI_0', 'Y3RAI_1', 'Y3RAI_2', 'Y3RAI_98', # variables dépendantes onglet 04
                  'Y3SEXE', 'Y3AGER', 'Y3REG13', 'Y3AGGLO5',
                  'Y3PCSI', 'Y3EMP', 'Y3EDU', 'Y3ECO2ST', 'Y3Q7'
                  # variables à croiser avec certaines variables dépendantes
                  ]
                ]

# Créer la crosstab de pourcentage
tableau_pourcentage = pd.crosstab(FR03['Y3SEXE'], FR03['Y3CERT'], normalize='index')
tableau_pourcentage = tableau_pourcentage.transpose() 

# définir les variables utiles à l'exemple de graphique
y_var_h = tableau_pourcentage.iloc[:,0]
y_var_f = tableau_pourcentage.iloc[:,1]
x_var = modalites



#########################################################################################
# Définir les fonctions construisant les graphiques (VERSION TEMPORAIRE)
#########################################################################################


#------------------------------------------------------------------------------
# créer une fonction à 2 arguments qui donne l'angle de rotation (en degrés)
# et le type d'alignement (gauche ou droite) de l'étiquette de variables
# sur un axe de graphique
#------------------------------------------------------------------------------
def G_BV_Eff():
    """
    ---------------------------
    Paramètres de la fonction :
    ---------------------------
    +  :
        * type : 
        * description : 
    + ofset :
        * type : 
        * description : 
    """
    fig = make_subplots(rows=1, cols=2, specs=[[{}, {}]], shared_xaxes=True,
                    shared_yaxes=False, vertical_spacing=0.001)

    fig.append_trace(go.Bar(x=y_var_h,
                            y=x_var,
                            name='Homme',
                            orientation='h',
                           ),
                    1, 1
                )

    fig.append_trace(go.Bar(x=y_var_f,
                           y=x_var,
                           name='Femme',
                           orientation='h',
                           ),
                   1, 2
              )

    fig.update_layout(
       title="Intention d'aller voter aux élections européennes du 9 juin 2024",
        yaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=True,
            domain=[0, 0.85],
        ),
        yaxis2=dict(
            showgrid=False,
            showline=False,
            showticklabels=True,
            domain=[0, 0.85],
        ),
        xaxis=dict(
            zeroline=False,
            showline=False,
            showticklabels=True,
            showgrid=True,
            domain=[0, 0.42],
        ),
        xaxis2=dict(
            zeroline=False,
            showline=False,
            showticklabels=True,
            showgrid=True,
            domain=[0.47, 1]
        ),
        legend=dict(x=0, y=1, font_size=12),
        margin=dict(l=100, r=20, t=70, b=70),
        paper_bgcolor='rgb(248, 248, 255)',
        plot_bgcolor='rgb(248, 248, 255)',
    )

    annotations = []

    y_s = np.round(y_var_h, decimals=2)
    y_nw = np.round(y_var_f, decimals=2)

    # Adding labels
    for ydn, yd, xd in zip(y_nw, y_s, x_var):
        annotations.append(dict(xref='x1',
                                yref='y1',
                                y=xd, x=yd + 0.02,
                                text=str(round(yd*100, 2)) + '%',
                                font=dict(family='Arial',
                                        size=14,
                                        color='rgb(50, 171, 96)'),
                                showarrow=False
                                )
                            )
        annotations.append(dict(xref='x2',
                                yref='y2',
                                y=xd, x=ydn + 0.02,
                                text=str(round(ydn*100, 2)) + '%',
                                font=dict(family='Arial',
                                        size=14,
                                        color='rgb(50, 171, 96)'),
                                showarrow=False
                                )
                            )
    # Source
    annotations.append(dict(xref='paper',
                            yref='paper',
                            x=0, y=-0.1,
                            text='Enquête électorale française pour les ' +
                                'élections européennes de juin 2024, ' +
                                'par Ipsos Sopra Steria, Cevipof, ' +
                                'Le Monde, Fondation Jean Jaurès et ' +
                                'Institut Montaigne (2024)',
                            font=dict(family='Arial', size=12, color='rgb(150,150,150)'),
                            showarrow=False
                            )
    )
    fig.update_layout(annotations=annotations)
    #fig.show()
    return fig
#------------------------------------------------------------------------------
# FIN de la fonction
#------------------------------------------------------------------------------



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
                    ui_card(
                            "INTENTION D'ALLER VOTER",
                            ui.tooltip(  
                                ui.input_action_button("Select_EDUR4", # input ID
                                                       "Question posée dans l'enquête"
                                ),
                                "Les prochaines élections européennes se tiendront le 9 juin 2024 en France. Pouvez-vous donner une note de 0 à 10 sur votre intention d’aller voter lors de ces élections européennes ? \n" + "0 signifiant que vous êtes vraiment tout à fait certain de ne pas aller voter et 10 que vous êtes vraiment tout à fait certain d’aller voter.",  
                                id="act_but_01",  
                                placement="right" 
                            )
                    ),

                    # cadre 02 : choix de la variable socio-démographique à croiser avec l'intention d'aller voter
                    ui_card("VARIABLES SOCIO-DEMOGRAPHIQUES",
                            # variable SD 01 : genre
                            ui.tooltip(  
                                ui.input_checkbox("Select_SEXE", # input ID
                                                  "Genre"
                                ),
                                "GENRE. Êtes-vous... ?",  
                                id="box_ttip_01",  
                                placement="right" 
                            ),
                            # variable SD 02 : âge
                            ui.tooltip(  
                                ui.input_checkbox("Select_AGER", # input ID
                                                  "Âge"
                                ),
                                "Âge du répondant (6 classes)",  
                                id="box_ttip_02",  
                                placement="right" 
                            ),
                            # variable SD 03 : région
                            ui.tooltip(  
                                ui.input_checkbox("Select_REG13", # input ID
                                                  "Région de résidence"
                                ),
                                "Région de résidence (13 classes)",  
                                id="box_ttip_03",  
                                placement="right" 
                            ),
                            # variable SD 04 : taille d'agglomération
                            ui.tooltip(  
                                ui.input_checkbox("Select_AGGLO5", # input ID
                                                  "Taille de l'agglomération"
                                ),
                                "Catégorie d'agglomération (5 classes)",  
                                id="box_ttip_04",  
                                placement="right" 
                            ),
                            # variable SD 05 : type d'emploi occupé
                            ui.tooltip(  
                                ui.input_checkbox("Select_EMP", # input ID
                                                  "Type d'emploi occupé"
                                ),
                                "Quelle est votre situation professionnelle actuelle ?",  
                                id="box_ttip_05",  
                                placement="right" 
                            ),
                            # variable SD 06 : catégorie socio-professionnelle
                            ui.tooltip(  
                                ui.input_checkbox("Select_PCSI", # input ID
                                                  "Catégorie socio-professionnelle"
                                ),
                                "Catégorie socio-professionnelle (8 classes)",  
                                id="box_ttip_06",  
                                placement="right" 
                            ),
                            # variable SD 07 : niveau de scolarité
                            ui.tooltip(  
                                ui.input_checkbox("Select_EDUR4", # input ID
                                                  "Niveau de scolarité atteint"
                                ),
                                "Choisissez votre niveau de scolarité le plus élevé (4 classes)",  
                                id="box_ttip_07",  
                                placement="right" 
                            ),
                            # variable SD 08 : religion
                            ui.tooltip(  
                                ui.input_checkbox("Select_REL1", # input ID
                                                  "Religion"
                                ),
                                "Quelle est votre religion, si vous en avez une ?",  
                                id="box_ttip_08",  
                                placement="right" 
                            ),
                            # variable SD 09 : revenu mensuel du foyer
                            ui.tooltip(  
                                ui.input_checkbox("Select_ECO2ST", # input ID
                                                  "Revenu mensuel du foyer"
                                ),
                                "Pour finir, nous avons besoin de connaître, à des fins statistiques uniquement, la tranche dans laquelle se situe le revenu MENSUEL NET de votre FOYER après déduction des impôts sur le revenu (veuillez considérer toutes vos sources de revenus: salaires, bourses, prestations retraite et sécurité sociale, dividendes, revenus immobiliers, pensions alimentaires etc.).",  
                                id="box_ttip_09",  
                                placement="right" 
                            ),
                            # variable SD 10 : intérêt pour la politique
                            ui.tooltip(  
                                ui.input_checkbox("Select_INTPOL", # input ID
                                                  "Intérêt pour la politique"
                                ),
                                "De manière générale, diriez-vous que vous vous intéressez à la politique ?",  
                                id="box_ttip_10",  
                                placement="right" 
                            ),
                            # variable SD 11 : préférence partisane
                            ui.tooltip(  
                                ui.input_checkbox("Select_Q7", # input ID
                                                  "Préférence partisane"
                                ),
                                "Sur une échelle de 0 à 10, où 0 correspond à la gauche et 10 correspond à la droite, où diriez-vous que vous vous situez ?",  
                                id="box_ttip_11",  
                                placement="right" 
                            ),
                            # bouton pour afficher le graphique croisée
                            ui.input_action_button("View_Graph", # input ID
                                                   "Afficher le graphique croisé"
                            )     
                    )
                ),                

                # colonne 2 de l'onglet : graphique des variables
                ui_card("GRAPHIQUE CROISE ENTRE L'INTENTION D'ALLER VOTER ET LA VARIABLE SOCIO-DEMOGRAPHIQUE CHOISIE"
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
                        ui.nav_panel("La France et l'Europe", # titre du sous-onglet
                                      "Tableau de bord sur le thème 01 (vague 01)" # contenu du sous-onglet
                        ),
                        # sous-onglet 02
                        ui.nav_panel("La guerre en Ukraine", # titre du sous-onglet
                                      "Tableau de bord sur le thème 02 (vague 01)" # contenu du sous-onglet
                        ),
                        # sous-onglet 03
                        ui.nav_panel("Le conflit israelo-palestinien", # titre du sous-onglet
                                      "Conflit israelo-palestinien (vague 02)" # contenu du sous-onglet
                        ),
                        # sous-onglet 04
                        ui.nav_panel("Les raisons de l'abstention", # titre du sous-onglet
                                      "Raisons de l'abstention (vague 03)" # contenu du sous-onglet
                        ),
                        # sous-onglet 05
                        ui.nav_panel("La perception de l'Union européenne et de ses valeurs", # titre du sous-onglet
                                      "La perception de l'Union européenne et de ses valeurs (vague 04)" # contenu du sous-onglet
                        ),
                                      
                        # sous-onglet 06
                        ui.nav_panel("Thème 06", # titre du sous-onglet
                                      "Tableau de bord sur le thème 05 (vague 05)" # contenu du sous-onglet
                        ),    
                        # sous-onglet 07
                        ui.nav_panel("Thème 07", # titre du sous-onglet
                                      "Tableau de bord sur le thème 06 (vague 06)" # contenu du sous-onglet
                        )
                    )
            ),

        # onglet 05
        ui.nav_panel("Etude des échantillons de répondants",
                     "Tableau de bord méthodologique sur les échantillons de répondants à chaque vague avec les problématiques soulevées"
        ),
                    
        id="tab"
    ) 
)


# bloc définissant les méthodes mises en oeuvre pour la réactiivté des objets
def server(input, output, session):

    # graphique interactif sur l'onglet 03
    # @render_widget  
    # def plot():  
    #     scatterplot = px.histogram(
    #         data_frame=penguins,
    #         x="body_mass_g",
    #         nbins=input.n(),
    #     ).update_layout(
    #         title={"text": "Penguin Mass", "x": 0.5},
    #         yaxis_title="Count",
    #         xaxis_title="Body Mass (g)",
    #     )
    #     return scatterplot

    # réactivité du bouton des étiquettes de l'intention d'aller voter
    @reactive.effect
    @reactive.event(input.Etiq_IAV)
    def _():
        type_txt = "Les prochaines élections européennes se tiendront le 9 juin 2024 en France. Pouvez-vous donner une note de 0 à 10 sur votre intention d’aller voter lors de ces élections européennes ? \n" + "0 signifiant que vous êtes vraiment tout à fait certain de ne pas aller voter et 10 que vous êtes vraiment tout à fait certain d’aller voter."
        ui.notification_show(
            type_txt,
            duration=10,
            close_button=True
        )



# définir l'application comme fonction des deux modules définis ci-dessus
app = App(app_ui, server)


