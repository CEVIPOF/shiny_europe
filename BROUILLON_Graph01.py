
# importater des librairies utilisées dans le programme :
import pandas as pd
import numpy as np

# importer la base de données au format CSV avec Panda
csvfile = 'C:/Users/53187/Documents/_Elections/2024_Européennes/Resultats_CSV/FR03Final.csv'
FR03Final = pd.read_csv(csvfile)
print(FR03Final)

# remplacer toutes les valeurs manquantes codées 99 par NA
FR03Final = FR03Final.replace(99, np.nan)
# supprimer la première colonne (vide) de la base de donnée
FR03Final = FR03Final.drop(FR03Final.columns[0], axis=1)

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

# Créer la crosstab de comptage
#tableau_comptage = pd.crosstab(FR03['Y3SEXE'], FR03['Y3CERT'])
#tableau_comptage = tableau_comptage.transpose() 

# Créer la crosstab de pourcentage
tableau_pourcentage = pd.crosstab(FR03['Y3SEXE'], FR03['Y3CERT'], normalize='index')
tableau_pourcentage = tableau_pourcentage.transpose() 

# Concaténer les deux tableaux
#tableau_final = pd.concat([tableau_comptage, tableau_pourcentage], keys=['Comptage', 'Pourcentage'])



import plotly.graph_objects as go
from plotly.subplots import make_subplots

y_var_h = tableau_pourcentage.iloc[:,0]
y_var_f = tableau_pourcentage.iloc[:,1]
x_var = modalites

# Creating two subplots
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
                        showarrow=False))

fig.update_layout(annotations=annotations)

fig.show()


