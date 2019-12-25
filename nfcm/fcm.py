import matplotlib.pyplot as plt
import networkx as nx

import numpy as np
import random

import torch
import torch.nn as nn


class FCM:
    class FCMModelFC(nn.Module):
        def __init__(self, len_precending, hidden_size):
            super().__init__()
            self.seq = torch.nn.Sequential(
                torch.nn.Linear(len_precending, hidden_size),
                torch.nn.Sigmoid(),
                torch.nn.Linear(hidden_size, hidden_size//2),
                torch.nn.Sigmoid(),
                torch.nn.Linear(hidden_size//2, 1),
                torch.nn.Sigmoid(),
            )

        def forward(self, x):
            return self.seq(x)

    def __init__(self, name="Fuzzy Cognitive Map", activation=None, neural=True,
                 learning_rate=1e-3, hidden_size=40):
        self.name = name

        def sigmoid(x):
            """Сигмоидальная функция"""
            return 1 / (1 + np.exp(-x))

        self.activation = activation if activation is not None else sigmoid
        self.graph = nx.DiGraph()
        self.hidden_size = hidden_size
        self.learning_rate = learning_rate
        self.loss_function = torch.nn.L1Loss()
        self.neural = neural

        self.current_epoch = 0
        self.max_epoch = 0

    @classmethod
    def init_from_concept_list(self, concepts):
        """
        Инициализирует полносвязную карту с рандомными весами
        из списка концептов concepts
        :param concepts -- список концептов
        """
        fcm = self()
        for c in concepts:
            fcm.add_new_concept(c, value=None)
        for c1 in concepts:
            for c2 in concepts:
                fcm.connect_concepts(c_from=c1, c_to=c2,
                                     weight=random.random())
                fcm.connect_concepts(c_from=c2, c_to=c1,
                                     weight=random.random())

        return fcm

    def freeze(self):
        '''
        Этот метод должен вызываться, если
        топология карты меняться не будет.
        Строим модельки для каждого концепта.
        '''
        for c in self.graph:
            len_precending = self.get_pred_concepts_tensor(c).shape[0]
            if len_precending <= 0:
                continue
            self.graph.nodes[c]['model'] = self.FCMModelFC(
                len_precending, self.hidden_size)
            self.graph.nodes[c]['model'].train()

    def new_epoch(self):
        '''
        Добивает значение концептов, которые еще не обновлялись на новый
        '''

        if self.current_epoch != self.max_epoch:
            raise Exception(f'Can create new epoch only on the last epoch')

        max_len = 0
        for c in self.graph:
            h = self.graph.nodes[c]['history']
            max_len = max(max_len, len(h))

        for c in self.graph:
            h = self.graph.nodes[c]['history']
            for i in range(len(h), max_len):
                h.append(0)

        self.current_epoch = max_len - 1
        self.max_epoch = max_len - 1
        return

    def to_epoch(self, epoch):
        """
        Переключает значения концептов карты на заданную эпоху
        :param epoch -- номер эпохи, значения концептов которой нужно применить
        """
        if epoch > self.max_epoch:
            raise Exception(
                f'epoch num too big: {epoch} (max {self.max_epoch})')

        self.current_epoch = epoch

        for c in self.graph:
            h = self.graph.nodes[c]['history']
            self.set_current_concept_value(c, h[epoch])
        return

    def set_concept_value(self, concept, value, promise_use_new_epoch=False):
        """
        Устанавливает значение переданного концепта в соответствующее значение.
        Предыдущее значение сохраняется в истории
        """
        if self.current_epoch != self.max_epoch:
            raise Exception(
                f"To set value for concept you must be on the last epoch current_epoch={self.current_epoch} max_epoch={self.max_epoch}")
        h = self.graph.nodes[concept]['history']
        if not promise_use_new_epoch and len(h) != self.current_epoch + 1:
            raise Exception(
                f"concept {concept} You must use fcm.new_epoch to update concepts: len(hist)={len(h)} current_epoch={self.current_epoch}, hist={h}")

        h.append(value)

        print(f'new conc {concept} {value} hid:{id(h)} hlen{len(h)}')
        return self.set_current_concept_value(concept, value)

    def set_current_concept_value(self, concept, value):
        """
        Устанавливает значение концепта. Но не меняет историю концепта.
        """
        self.graph.nodes[concept]['concept_value'] = value
        return

    def add_new_concept(self, cname, value=None):
        """
        Добавить новый концепт в карту.
        """
        h = []
        if value is not None:
            h.append(value)
        self.graph.add_node(cname, concept_value=value, history=h)
        return

    def connect_concepts(self, c_from=None, c_to=None, weight=0):
        """
        Метод позволяет связать концепты между собой и указать вес связи.
        """
        if c_from is None or c_to is None:
            raise Exception("c_from and c_to is required for link_concepts")
        self.graph.add_weighted_edges_from([(c_from, c_to, weight)])
        return

    def get_pred_concepts(self, concept_name):
        """
        Получить предшествующие концепты
        """
        pred_concepts = []
        for pred in self.graph.predecessors(concept_name):
            #             if pred == concept_name:
            #                 continue
            cv = self.get_concept_value(pred)
            pred_concepts.append(cv)
        return pred_concepts

    def get_pred_concepts_tensor(self, concept_name):
        """
        То же, что и get_pred_concepts, но результатом будет
        тензор pytorch
        """
        pred_concepts = self.get_pred_concepts(concept_name)
        return torch.autograd.Variable(torch.FloatTensor(pred_concepts))

    # берем из графа -- значения концептов других вершин
    def fit_concept(self, concept_name, future_concept_value, epochs=100, plot=False):
        """
        Обучаем определенный концепт предсказывать текущее значение
        концепта по состоянию предшествующих концептов.
        """

        if concept_name not in self.graph:
            raise KeyError()

        pc = self.get_pred_concepts(concept_name)
        pc = np.array(pc)
        pred_concepts = self.get_pred_concepts_tensor(concept_name)
        loss_history = []

        loss_fn = self.loss_function
        model = self.graph.nodes[concept_name]['model']
        model.train()

        optimizer = torch.optim.SGD(model.parameters(), lr=self.learning_rate)

        future_concept_value = torch.FloatTensor([future_concept_value])

        for t in range(epochs):
            optimizer.zero_grad()

            predict = model(pred_concepts)
            loss = loss_fn(predict, future_concept_value)
            loss_history.append(loss.data)
            print('predict {0:.2f}'.format(predict.item()),
                  'nv {0:.2f}'.format(future_concept_value.item()),
                  'loss {0:2f}'.format(loss.data))

            loss.backward()
            optimizer.step()

        if plot:
            plt.plot(loss_history, label=f'{self.current_epoch}')

        print('mean loss hist:', np.mean(loss_history), future_concept_value)
        return loss_history

    def fit_on_history(self, epochs=10):
        """
        Обучает веса концептов или модели, связанные с концептами на основе созраненной истории
        о том, как менялось состояние карты.
        """

        if self.max_epoch < 1:
            raise Exception('Need history fot fitting on history')

        for epoch in range(self.max_epoch):
            self.to_epoch(epoch)
            for c in self.graph:
                self.fit_concept(c, self.get_concept_value(
                    c, epoch=epoch+1), epochs=epochs)
        self.to_epoch(self.max_epoch)
        return

    def _get_labels(self):
        labels = nx.get_node_attributes(self.graph, 'concept_value')
        for l, v in labels.items():
            labels[l] = "{0}\n{1:.2f}".format(l, v)
        return labels

    def evalute(self, epochs=10, eps=1e-5, once=False, oblivion=False):
        """
        Вычисляет значение карты на следующей итерации.
        """
        DGresult = self.graph
        if once:
            epochs = 1

        if oblivion:
            for c in self.graph:
                self.graph.nodes[c]['history'] = []

        new_concept_values = dict()

        for _ in range(epochs):
            old_cv = nx.get_node_attributes(DGresult, 'concept_value')
            for c, inners in DGresult.pred.items():
                if not self.neural:
                    # todo move to separate function
                    weighted_concepts_sum = [
                        old_cv[factor_conc] * fc_weight['weight'] for factor_conc, fc_weight in inners.items()]
                    new_concept_value = self.activation(
                        old_cv[c] + np.sum(weighted_concepts_sum))
                    self.set_concept_value(c, new_concept_value)
                else:
                    pred_concepts = self.get_pred_concepts_tensor(c)
                    if len(pred_concepts) == 0:
                        continue
                    with torch.no_grad():
                        self.graph.nodes[c]['model'].eval()

                        new_concept_value = self.graph.nodes[c]['model'](
                            pred_concepts).item()
                        print("eval", c, "new_concept_value:",
                              new_concept_value, 'pred:', pred_concepts)
                        new_concept_values[c] = new_concept_value
                        if not once:
                            self.set_concept_value(c, new_concept_value)
            if not once:
                self.new_epoch()

        if once:
            return new_concept_values

        return

    def concepts(self):
        """
        Получить список концептов карты
        """
        return self.graph.nodes

    def get_concept_value(self, concept, epoch=None):
        """
        Получить значение определенного концептв
        """
        if epoch is None:
            epoch = self.current_epoch
        return self.graph.nodes[concept]['history'][epoch]

    def get_concept_values(self):
        """
        Получить значения всех концептов
        """
        return nx.get_node_attributes(self.graph, 'concept_value')

    def plot_map(self, plotsize=(15, 15), draw_edges=True):
        """
        Строит граф карты.
        """
        pos = nx.circular_layout(self.graph)

        plt.clf()
        cf = plt.gcf()
        cf.set_size_inches(*plotsize)
        ax = cf.gca()

        DGresult = self.graph

        labels = self._get_labels()
        nx.draw_networkx_nodes(self.graph, pos,
                               labels=labels,
                               node_color="blue",
                               node_size=1000,
                               alpha=0.3,
                               ax=ax)
        nx.draw_networkx_labels(DGresult, pos, labels, font_size=10)

        if draw_edges:
            for c, inners in DGresult.pred.items():
                for inner in inners:
                    edge_color = 'green'
                    nx.draw_networkx_edges(DGresult, pos,
                                           edgelist=[(inner, c)],
                                           width=3, alpha=0.3, edge_color=edge_color, ax=ax, arrowsize=30)

            weight_edge_labels = nx.get_edge_attributes(DGresult, 'weight')
            for k, v in weight_edge_labels.items():
                weight_edge_labels[k] = "{:.2}".format(v)
            nx.draw_networkx_edge_labels(
                DGresult, pos, edge_labels=weight_edge_labels, label_pos=0.25)

    def plot_concept_history(self, hstart=0, hend=None):
        """
        Строит график изменения значений концептов карты
        """
        cf = plt.gcf()
        cf.set_size_inches(18, 10)

        history = nx.get_node_attributes(self.graph, 'history')
        for c in history:
            h = history[c]
            if hend is not None:
                h = h[hstart:hend]
            plt.plot(range(len(history[c])), h, label=c)
            plt.xlabel('iteration')
            plt.ylabel('concept value')
            plt.grid()
            plt.legend()
