from collections import defaultdict
import pydot
import os
import sys
import xml.etree.ElementTree as ET

def maybe_read_node(root, node_name):
    node = root.find(node_name)
    if node is not None:
        return node.text
    return ""

def read_schemes_xml(fg_root):
    schemes_xml_file = os.path.join(fg_root, "Effects/schemes.xml")
    if not os.path.exists(schemes_xml_file):
        print(f"schemes.xml not found. Is \"{fg_root}\" a valid $FG_ROOT?")
        exit(1)

    xmltree = ET.parse(schemes_xml_file)
    xmlroot = xmltree.getroot()

    scheme_list = list()
    # Append the default scheme (empty name)
    scheme_list.append(dict(name = "", description = "Default scheme", fallback = ""))

    for scheme in xmlroot.iter("scheme"):
        scheme_name = maybe_read_node(scheme, "name")
        if scheme_name == "":
            print("Found scheme with no name. Skipping...")
            continue

        scheme_description = maybe_read_node(scheme, "description")
        scheme_fallback = maybe_read_node(scheme, "fallback")
        scheme_list.append(dict(name = scheme_name,
                                description = scheme_description,
                                fallback = scheme_fallback))
    return scheme_list

def is_valid_scheme(scheme_list, name):
    # The default empty scheme is valid
    if name == "":
        return True
    for scheme in scheme_list:
        if scheme["name"] == name:
            return True
    return False

def parse_effect_file(scheme_list, path, graph_node_list):
    xmltree = ET.parse(path)
    xmlroot = xmltree.getroot()

    eff_name = maybe_read_node(xmlroot, "name")
    if eff_name == "":
        print("Found Effect with no name. Skipping...")
        return

    eff_parent = maybe_read_node(xmlroot, "inherits-from")

    for scheme, graph_node in zip(scheme_list, graph_node_list):
        technique_list = list()
        for tniq in xmlroot.iter("technique"):
            tniq_n = int(tniq.attrib.get("n", 0))
            tniq_scheme_name = maybe_read_node(tniq, "scheme")
            # Warn if the scheme is not valid (does not appear in schemes.xml)
            if not is_valid_scheme(scheme_list, tniq_scheme_name):
                print(f"technique n={tniq_n} in Effect \"{eff_name}\" has an invalid scheme \"{tniq_scheme_name}\"")
            if scheme["name"] == tniq_scheme_name:
                tniq_n = int(tniq.attrib.get("n", 0))
                technique_list.append(tniq_n)

        graph_node.append(dict(name = eff_name,
                               parent = eff_parent,
                               techniques = technique_list))

def generate_graph(scheme_list, graph_node_list):
    graph = pydot.Dot("FlightGear Effect Hierarchy", graph_type="digraph", rankdir='RL')

    for scheme, node_list in zip(scheme_list, graph_node_list):
        scheme_label = f"Scheme: {scheme["name"]}\n{scheme["description"]}"
        cluster = pydot.Cluster(scheme["name"], label=scheme_label, fontcolor="red", color="grey")
        graph.add_subgraph(cluster)

        for node in node_list:
            node_unique_name = node["name"] + "/" + scheme["name"]
            shape = ""
            # Add an edge based on whether the node has a parent or not
            if node["parent"]:
                parent_unique_name = node["parent"] + "/" + scheme["name"]
                cluster.add_edge(pydot.Edge(node_unique_name, parent_unique_name))
                shape = "rectangle"
            else:
                shape = "diamond"

            # If a node does not have any techniques for a given scheme, it
            # means it is inactive.
            if node["techniques"]:
                node_label = f"{node["name"]}\n{str(node["techniques"])}"
                cluster.add_node(pydot.Node(node_unique_name,
                                            label=node_label,
                                            shape=shape,
                                            color="blue"))
            else:
                node_label = f"{node["name"]}"
                cluster.add_node(pydot.Node(node_unique_name,
                                            label=node_label,
                                            shape=shape,
                                            color="grey"))
    return graph

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <path to $FG_ROOT>")
        exit(1)

    fg_root = sys.argv[1]
    print(f"Using $FG_ROOT='{fg_root}'")

    print("Reading schemes.xml...")
    scheme_list = read_schemes_xml(fg_root)

    effect_dir = os.path.join(fg_root, "Effects")
    if not os.path.exists(effect_dir):
        print(f"Effects/ directory does not exist. Is \"{fg_root}\" a valid $FG_ROOT?")
        exit(1)

    print("Parsing Effect files...")

    graph_node_list = [[] for _ in range(len(scheme_list))]

    # Exclude the HDR/ and Fallback/ directories from the dir walk
    exclude = set(["HDR", "Fallback"])
    for rootdir, dirs, files in os.walk(effect_dir):
        dirs[:] = [d for d in dirs if d not in exclude]
        for filename in files:
            # Only read Effect files (those with the .eff extension)
            _, ext = os.path.splitext(filename)
            if ext != ".eff":
                continue

            eff_path = os.path.join(rootdir, filename)
            parse_effect_file(scheme_list, eff_path, graph_node_list)

    graph = generate_graph(scheme_list, graph_node_list)

    output_filename = "output.png"
    print(f"Writing to '{output_filename}'...")
    graph.write_png(output_filename)
    print("Done.")

if __name__ == "__main__":
    main()
