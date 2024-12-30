from rdflib import Graph, Dataset, URIRef
from kurrawong.format import format_rdf, format_file, do_format, make_dataset, export_quads
from pathlib import Path
import warnings
import subprocess


def test_format_rdf_one():
    input_file = Path(__file__).parent / "minimal1.ttl"
    output_file = Path(__file__).parent / "minimal1-out.ttl"
    comparison = """PREFIX ex: <http://example.com/>

ex:a
    ex:b ex:c ;
."""

    format_file(input_file, False, output_filename=output_file)
    output_file_text = output_file.read_text().strip()

    assert output_file_text == comparison

    output_file.unlink(missing_ok=True)


def test_format_cli():
    subprocess.check_output(
        ["kurra", "format", "--output-format", "json-ld", "tests/minimal1.ttl"]
    )

    comaprison = """[
  {
    "@id": "http://example.com/a",
    "http://example.com/b": [
      {
        "@id": "http://example.com/c"
      }
    ]
  }
]"""

    output_file = Path(__file__).parent / "minimal1.jsonld"

    assert open(output_file).read() == comaprison

    Path.unlink(output_file)


def test_make_dataset():
    g = Graph()
    g.parse(
        data="""
            PREFIX ex: <http://example.com/>
            
            ex:a ex:b ex:c . 
            """,
        format="turtle",
    )

    d = make_dataset(g, "http://graph.com/a")

    for t in d.quads():
        assert t[0] == URIRef("http://example.com/a")
        assert t[1] == URIRef("http://example.com/b")
        assert t[2] == URIRef("http://example.com/c")
        assert t[3] == URIRef("http://graph.com/a")


def test_export_quads():
    g = Graph()
    g.parse(
        data="""
            PREFIX ex: <http://example.com/>

            ex:a ex:b ex:c . 
            """,
        format="turtle",
    )

    d = make_dataset(g, "http://graph.com/a")

    qds = export_quads(d)

    warnings.filterwarnings("ignore", category=DeprecationWarning)  # ignore RDFLib's ConjunctiveGraph warning
    d2 = Dataset()
    d2.parse(data=qds, format="trig")

    for t in d.quads():
        assert t[0] == URIRef("http://example.com/a")
        assert t[1] == URIRef("http://example.com/b")
        assert t[2] == URIRef("http://example.com/c")
        assert t[3] == URIRef("http://graph.com/a")