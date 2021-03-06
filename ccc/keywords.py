#! /usr/bin/env python
# -*- coding: utf-8 -*-

# part of module
from .collocates import add_ams
# requirements
from pandas import DataFrame
# logging
import logging
logger = logging.getLogger(__name__)


class Keywords:
    """ keyword analysis """

    def __init__(self, corpus, df_dump, p_query='lemma'):

        self.corpus = corpus

        # activate dump
        self.name = 'tmp_keywords'
        self.size = len(df_dump)

        # consistency check
        if self.size == 0:
            logger.warning('cannot calculate keywords on 0 regions')
            return

        # determine layer to work on
        if p_query not in corpus.attributes_available['name'].values:
            logger.warning(
                'p_att "%s" not available, falling back to primary layer' % p_query
            )
            p_query = 'word'
        self.p_query = p_query

        # collect context and save result
        logger.info('collecting token counts of subcorpus')
        counts = corpus.counts.dump(
            df_dump, start='match', end='matchend', p_atts=[p_query], split=True
        )
        counts.columns = ['f']

        self.counts = counts

    def show(self, order='f', cut_off=100, ams=None,
             min_freq=2, frequencies=True, flags=None):

        # consistency check
        if self.counts.empty:
            logger.warning("nothing to show")
            return DataFrame()

        # get frequencies
        f = self.counts.loc[~(self.counts['f'] < min_freq)]
        f.index = f.index.get_level_values(self.p_query)

        # get marginals
        f2 = self.corpus.marginals(
            f.index, self.p_query
        )
        f2.columns = ['f2']

        # get sub-corpus size
        f1 = self.counts['f'].sum()

        # get corpus size
        N = self.corpus.corpus_size

        keywords = add_ams(
            f, f1, f2, N,
            min_freq, order, cut_off, flags, ams, frequencies
        )

        return keywords
