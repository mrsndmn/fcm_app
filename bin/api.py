from flask import Flask
from flask import request, send_from_directory
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

app = Flask(__name__, static_url_path='/static')
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
@app.route('/<path:path>')
def static_file(path):
    print(path)
    return app.send_static_file(path)


class FCMHandler(Resource):
    def get(self):
        args = parser.parse_args()
        print(args)

        # todo remove this "hack"

        concepts = config['concepts']['list']
        target = config['concepts']['target']

        query = """
            copy (select positive, negative, """ + ", ".join(concepts) + """ from stream_events where spam is null and creation_time between to_timestamp(%s) and to_timestamp(%s))
                to '/tmp/stream_events_classes.csv' with (format csv, header)
        """
        cur = pg_conn.cursor()
        # cur.execute(query, args['date_from'], args['date_to'])
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
        if 'weights' not in args or args['weights'] is None:
            args['weights'] = "{}"
        parsed_weights = json.loads(args['weights'])
        for c in weights:
            if c not in parsed_weights:
                continue
            weights[c] = float(parsed_weights[c])

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
        concepts_changes = dict()
        for c in concept_values:
            concepts_changes[c] = []

        effective_iters = 0
        for epoch in range(100):

            old_cv = nx.get_node_attributes(DGresult, 'cv')
            for c, inners in DGresult.pred.items():
                tmp_concepts[c] = activation( old_cv[c] + np.sum([ old_cv[factor_conc] * fc_weight['weight'] for factor_conc, fc_weight in inners.items() ]) )
                concepts_changes[c].append(tmp_concepts[c])

            nx.set_node_attributes(DGresult, tmp_concepts, 'cv')
            effective_iters += 1


        labels = nx.get_node_attributes(DGresult, 'cv')
        for l, v in labels.items():
            labels[l] = "{0} {1:.4f}".format(l, v)

        res_cv = nx.get_node_attributes(DGresult, 'cv')
        pos = nx.spring_layout(DGresult)

        plt.clf()
        cf = plt.gcf()
        cf.set_size_inches(18, 10)

        ax = cf.gca()

        for c, inners in DGresult.pred.items():
            nx.draw_networkx_nodes(DGresult, pos,
                            nodelist=[c],
                            labels=labels,
                            node_color="blue",
                            node_size=500,
                            alpha=0.5,
                            ax=ax)
            for inner in inners:
                edge_color = 'red' if res_cv[inner] < 0 else 'green'
                nx.draw_networkx_edges(DGresult, pos,
                            edgelist=[(inner, c)],
                            width=3, alpha=0.3, edge_color=edge_color, ax=ax)

        nx.draw_networkx_labels(DGresult, pos, labels, font_size=10)

        weight_edge_labels = nx.get_edge_attributes(DGresult,'weight')
        nx.draw_networkx_edge_labels(DGresult, pos,edge_labels=weight_edge_labels)

        graph_img = 'static/images/plot.png'
        # nx.draw(DGresult, with_labels=True, labels=labels, node_color='lightblue', weight=True, font_weight='normal')
        plt.savefig(graph_img, format="PNG", dpi=100)

        plt.clf()
        conv_img = 'static/images/conv.png'

        linspace = [ i for i in range(effective_iters) ]
        for c in concepts_changes:
            plt.plot(linspace, concepts_changes[c], label=c)
        plt.legend()

        plt.savefig(conv_img, format="PNG", dpi=100)
        return {
            'data': [
                'http://116.203.70.12:8000/' + graph_img.split("/")[2],
                'http://116.203.70.12:8000/' + conv_img.split("/")[2]
            ]
        }, 200, {'Access-Control-Allow-Origin': '*'}

        # return {'data': {
        #     'graph_img': graph_img,
        #     'conv_img': conv_img,
        # }}

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