"""Pytest entry point for RowGraphConverter tests."""

from tabulardf import RowGraphConverter

from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.compare import isomorphic
from rdflib.namespace import RDF

from tests.data import (
    tables,
    targets_graphs_path
)


CRM = Namespace("http://www.cidoc-crm.org/cidoc-crm/")
CRMCLS = Namespace("https://clscor.io/ontologies/CRMcls/")


def row_raph_converter_rule(row_dict: dict) -> Graph():
    """row_rule for building a row graph.

    This callable gets passed the row data as a dictionary
    in the context of a tabulardf.RowGraphConverter.
    """
    corpus_acronym = row_dict["corpusAcronym"]
    corpus_acronym_lower = row_dict["corpusAcronym"].lower()
    corpus_name = row_dict["corpusName"]

    corpus_uri = URIRef(f"https://{corpus_acronym_lower}.clscor.io/entity/corpus")
    appellation_1 = URIRef(f"https://{corpus_acronym_lower}.clscor.io/entity/appellation/1")
    appellation_2 = URIRef(f"https://{corpus_acronym_lower}.clscor.io/entity/appellation/2")

    triples = [
        (
            corpus_uri,
            RDF.type,
            CRMCLS["X1_Corpus"]
        ),
        (
            corpus_uri,
            CRM["P1_is_identified_by"],
            appellation_1
        ),
        (
            corpus_uri,
            CRM["P1_is_identified_by"],
            appellation_2
        ),

        (
            appellation_1,
            RDF.type,
            CRM["E41_Appellation"]
        ),
        (
            appellation_1,
            CRM["P2_has_type"],
            URIRef(
                "https://core.clscor.io/entity/type/appellation_type/full_title"
            )
        ),
        (
            appellation_1,
            RDF.value,
            Literal(corpus_name)
        ),

        (
            appellation_2,
            RDF.type,
            CRM["E41_Appellation"]
        ),
        (
            appellation_2,
            CRM["P2_has_type"],
            URIRef(
                "https://core.clscor.io/entity/type/appellation_type/acronym"
            )
        ),
        (
            appellation_2,
            RDF.value,
            Literal(corpus_acronym)
        ),


    ]

    graph = Graph()

    for triple in triples:
        graph.add(triple)

    return graph


def test_row_graph_converter():
    """Test for the RowGraphConverter class.

    Generate a graph from a row_rule
    and check for graph isomorphism against a target graph.
    """

    # is it possible to define the namespaced graph in the rule?
    graph = Graph()
    graph.bind("crm", CRM)
    graph.bind("crmcls", CRMCLS)

    converter = RowGraphConverter(
        dataframe=tables.cortab_partial_df,
        row_rule=row_raph_converter_rule,
        # graph=graph
    )

    generated_graph = converter.to_graph()
    target_graph = Graph().parse(targets_graphs_path / "cortab_name_acronym.ttl")

    assert isomorphic(generated_graph, target_graph)
