from flask import Flask, render_template, request
from xml.etree import ElementTree as ET
from requests import get

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/results", methods=["POST"])
def results():
    url = request.form["url"]
    # reading the file results in -> b'contents_of_file' <- so remove b''
    file = str(request.files["file"].read())[2:-1]

    if url:
        data_type = "url"
        data = url
    elif file:
        data_type = "file"
        data = file
    else:
        data_type = "bad"
        data = ""

    return (
        "<p style='overflow-wrap: break-word;'>"
        + get_x509_cert(data_type, data)
        + "</p>"
    )


def get_x509_cert(data_type, data):
    if data_type == "url":
        r = get(data)
        root = ET.fromstring(r.text)
    elif data_type == "file":
        root = ET.fromstring(data)
    else:
        return "bad form submission"

    return _parse_x509_cert(root)


def _parse_x509_cert(root):
    for child in root.iter():
        if "KeyDescriptor" in child.tag and child.attrib["use"] == "signing":
            for key_child in child.iter():
                if "X509Certificate" in key_child.tag:
                    last_key = key_child.text

    return last_key
