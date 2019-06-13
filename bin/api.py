from flask import Flask
from flask_restful import Resource, Api, reqparse

from fcm_app.config import config, pg_conn

from efficient_apriori import apriori
import csv
import pandas as pd
import numpy as np
import matplotlib as mp
import matplotlib.pyplot as plt
import networkx as nx

import json

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument('date_from')
parser.add_argument('date_to')
parser.add_argument('max_iters')
parser.add_argument('eps')
parser.add_argument('weights')

# class FCMProcessor(object):
#     def __init__(self, max_iters=100, eps=1e-5, date_from=None, date_to=None):
#         self.max_iters = max_iters
#         self.eps = eps
#         self.date_from = date_from
#         self.date_to = date_to

#     def run(self):

    

#     return ''


class FCMHandler(Resource):
    def get(self):
        args = parser.parse_args()
        print(args)

        # todo remove this "hack"

        concepts = config['concepts']['list']
        target = config['concepts']['target']

        query = """
            copy (select positive, negative, """ + ", ".join(concepts) + """ from stream_events where spam is null)
                to '/tmp/stream_events_classes.csv' with (format csv, header)
        """
        cur = pg_conn.cursor()
        cur.execute(query)
        cur.close()

        df_no_spam = pd.read_csv("/tmp/stream_events_classes.csv")
        for column in df_no_spam:
            df_no_spam[column] = df_no_spam[column].map(lambda x: x if pd.isna(x) else column)

        tuples = []
        for x in df_no_spam.itertuples():
            t = []
            for y in x[1:]:
                if not pd.isna(y):
                    t.append(y)
            if len(t):
                tuples.append(tuple(sorted(t)))

        tuples_len = len(tuples)


        weights = dict()
        weights[target] = 0
        for c in concepts:
            weights[c] = 0

        itemsets, rules = apriori(tuples, min_support=0.0001,  min_confidence=0.001)
        parsed_weights = json.loads(args['weights'])
        for c in weights:
            weights[c] = parsed_weights[c]

        def activation(x, derivative=False):
            return np.tanh(x) # x*(1-x) if derivative else 1/(1+np.exp(-x))

        DG = nx.DiGraph()
        DG.add_node(target)

        print(nx.get_node_attributes(DG, target))

        count_dict = itemsets[2]
        concept_values = dict({target: 0})
        for conc in concepts:
            concept_values[conc] = 0
            tneg = tuple(sorted([conc, 'negative']))
            tpos = tuple(sorted([conc, 'positive']))
            if tpos in count_dict:
                concept_values[conc] += count_dict[tpos] / tuples_len 
            if tneg in count_dict:
                concept_values[conc] -= count_dict[tneg] / tuples_len

            DG.add_node(conc)
            DG.add_weighted_edges_from([(conc, target, weights[conc])])

        print("initial:", concept_values)
        nx.set_node_attributes(DG, concept_values, 'cv')

        EPOCHS = args['max_iters']

        DGtmp = DG.copy()
        DGresult = DG.copy()

        tmp_concepts = concept_values.copy()
        eco_changes = []
        for epoch in range(100):

            old_cv = nx.get_node_attributes(DGresult, 'cv')
            for c, inners in DGresult.pred.items():
                tmp_concepts[c] = activation( old_cv[c] + np.sum([ old_cv[factor_conc] * fc_weight['weight'] for factor_conc, fc_weight in inners.items() ]) )

            nx.set_node_attributes(DGresult, tmp_concepts, 'cv')
            eco_changes.append(tmp_concepts[target])


        labels = nx.get_node_attributes(DGresult, 'cv')
        for l, v in labels.items():
            labels[l] = "{0} {1:.4f}".format(l, v)

        res_cv = nx.get_node_attributes(DGresult, 'cv')
        pos = nx.spring_layout(DGresult)

        cf = plt.gcf()
        cf.set_size_inches(18, 10)

        ax = cf.gca()

        for k in DGresult:
            ncolor = 'b' if res_cv[k] >= 0 else 'red'
            nx.draw_networkx_nodes(DGresult, pos,
                            nodelist=[k],
                            labels=labels,
                            node_color=ncolor,
                            node_size=500,
                            alpha=0.5,
                            ax=ax)

        nx.draw_networkx_edges(DGresult, pos,
                            edgelist=DGresult.edges,
                            width=3, alpha=0.3, edge_color='black', ax=ax)

        nx.draw_networkx_labels(DGresult, pos, labels, font_size=10)
        
        graph_img = '/static/images/plot.png'
        plt.savefig(graph_img, format="PNG", dpi=100)
        # nx.draw(DGresult, with_labels=True, labels=labels, node_color='lightblue', weight=True, font_weight='normal')

        conv_img = '/static/images/conv.png'
        plt.plot(eco_changes)
        plt.savefig(conv_img, format="PNG", dpi=100)

        return {'data': {
            'graph_img': graph_img,
            'conv_img': conv_img,
        }}

api.add_resource(FCMHandler, '/fcm/calculator')

class Concepts(Resource):
    def __init__(self):
        self.supported_concepts = config['concepts']['list']
        self.target = config['concepts']['target']
        self.all_conc = self.supported_concepts.copy()
        self.all_conc.append(self.target)
    def get(self):
        return {
            'data': {
                'list': self.all_conc
            }
        }, 200, {'Access-Control-Allow-Origin': '*'}

api.add_resource(Concepts, '/fcm/concepts')

if __name__ == '__main__':
    app.run(debug=True)