#!/usr/bin/env python3
__author__ = "tomarovsky"
from ete3 import TextFace, Tree, faces, AttrFace, TreeStyle, NodeStyle
from argparse import ArgumentParser
from matplotlib.patches import Patch
import matplotlib.pyplot as plt


def newick_to_nhx(newick_file) -> str:
    with open(newick_file, "r") as file:
        tree_string = ""
        newick = file.readline().replace("_", " ").strip().split("'")
        tree_string += newick[0]
        for i in range(1, len(newick), 2):
            line = ""
            flag = True
            for s in newick[i + 1]:
                if s == ")" or s == ",":
                    if flag is True:
                        nhx = newick[i].replace(",", ".").replace(";", ":")[1:]
                        line += f"[&&NHX:{nhx}{s}"
                        flag = False
                    else:
                        line += s
                else:
                    line += s
            tree_string += line
        # print(tree_string)
        return tree_string


def mylayout(node):
    if node.is_leaf():
        N = AttrFace("name", fgcolor="black", text_prefix="  ", fstyle="italic", fsize=12)
        faces.add_face_to_node(N, node, 0)
        node.img_style["size"] = 1
        node.img_style["shape"] = "circle"
        node.img_style["fgcolor"] = "Black"
        # node.dist = 0 # ASTRAL does not generate terminal branch lengths


def export_legend(palette, filename, dpi=400):
    # Create empty figure with the legend
    handles = [Patch(label=f">= {label}", color=color) for label, color in palette.items()]
    fig = plt.figure()
    legend = fig.gca().legend(handles=handles, framealpha=1, frameon=True, title="       Colors of \nnormalized values")  # spaces to center title
    # Render the legend
    fig.canvas.draw()
    # Export the figure, limiting the bounding box to the legend area,
    # slighly extended to ensure the surrounding rounded corner box of
    # is not cropped. Transparency is enabled, so it is not an issue.
    bbox = legend.get_window_extent().padded(2)
    bbox = bbox.transformed(fig.dpi_scale_trans.inverted())
    fig.savefig(filename, dpi=dpi, transparent=True, bbox_inches=bbox)
    # Delete the legend along with its temporary figure
    plt.close(fig)


def main():
    t = Tree(newick_to_nhx(args.input))
    if args.outgroup:
        outgroup = args.outgroup.replace("_", " ")
        if "," in outgroup:
            try:
                nodes_to_root = outgroup.split(",")
                common_ancestor = t.get_common_ancestor(*nodes_to_root)
                t.set_outgroup(common_ancestor)
            except:
                R = t.get_midpoint_outgroup()
                t.set_outgroup(R)
                nodes_to_root = outgroup.split(",")
                common_ancestor = t.get_common_ancestor(*nodes_to_root)
                t.set_outgroup(common_ancestor)
        else:
            t.set_outgroup(outgroup)
    else:
        t.unroot()
    ts = TreeStyle()
    ts.mode = "r"
    ts.layout_fn = mylayout
    ts.show_leaf_name = False
    for n in t.traverse():
        nstyle = NodeStyle()
        nstyle["fgcolor"] = "Blue"
        nstyle["size"] = 0
        n.set_style(nstyle)
        if hasattr(n, "q1"):
            value = float(getattr(n, "EN"))
            normalized_value = value / args.number_of_genes * 100
            for threshold in sorted(args.thresholds_and_colors.keys()):
                if normalized_value >= threshold:
                    color = args.thresholds_and_colors[threshold]
            n.add_face(TextFace(f"  {value:.0f} ", fgcolor=color), column=2, position="branch-bottom")
            n.add_face(TextFace(f" {normalized_value:.2f}% ", fgcolor=color), column=2, position="branch-top")

    ts.show_branch_length = False
    ts.show_branch_support = False
    ts.branch_vertical_margin = -4
    if args.show:
        t.show(tree_style=ts)
    else:
        for f in args.output_formats:
            t.render(f"{args.output}.{f}", w=args.width, units="px", tree_style=ts)
        export_legend(args.thresholds_and_colors, f"{args.output}.legend.png")


if __name__ == "__main__":
    parser = ArgumentParser(description="script to visualize ASTRAL lll phylogenetic trees using ete3 (required python3 < 3.10)")
    group_required = parser.add_argument_group("Required options")
    group_required.add_argument("-i", "--input", type=str, help="NEWICK treefile from Astral lll with full annotation option (-t 2)")
    group_required.add_argument("-o", "--output", type=str, help="outfile prefix")
    group_additional = parser.add_argument_group("Additional options")
    group_additional.add_argument("-g", "--outgroup", type=str, default=False, help="outgroup species name (default = unrooted)")

    # colorification:
    group_additional.add_argument(
        "--thresholds_and_colors",
        type=lambda s: dict(zip([int(s) for i in s[::2]], s[1::2])),
        default={90: "#00b050", 70: "#008cf0", 50: "#883ac2", 0: "#ff0000"},
        help="colors per metrics."
        "Example input: '90,Green,70,Gold,50,OrangeRed,0,Red'. "
        "This means that normalized values above 90 will be colored Green, values above 70 will be colored Gold, etc.",
    )
    group_additional.add_argument(
        "-n", "--number_of_genes", type=int, help="total number of gene trees in ASTRAL input treefle (necessary to normalize 'EN' option value)"
    )

    # figure options:
    group_additional.add_argument("--width", type=int, default=1500, help="width for result rendering")
    group_additional.add_argument("--show", action="store_true", help="option to show tree using GUI")
    group_additional.add_argument(
        "-e",
        "--output_formats",
        dest="output_formats",
        type=lambda s: s.split(","),
        default=("png"),
        help="Comma-separated list of formats (supported by ete3) of output figure. Default: svg,png",
    )
    args = parser.parse_args()
    main()
