from qs.database import IndexItem


def show_index(db_index: IndexItem, indent=0):
    """
    + Root
      |
      + Node1
    """

    pad = "".join(" " for i in range(indent))

    if indent == 0:
        print("*" * 80)
    else:
        print(f"{pad}|")
    print(f"{pad}+ {db_index.node}")
    if db_index.children:
        for child in db_index.children.values():
            show_index(child, indent=indent + 2)
