import markdownify 
import os
import re

PAT1 = re.compile(r"\n +\|")
PAT2 = re.compile(r"\| \n")
PAT3 = re.compile(r"`\n ")
PAT10 = re.compile(r"(\n ){2,}")
PAT20 = re.compile(r"\n (?! )")
PAT30 = re.compile(r"(\n\t+)+ ")


def refine_md(md_file_name):
    print(f"# post {md_file_name}")
    with open(f"../data/md1/{md_file_name}") as f:
        html_content = f.read()

    md_content = markdownify.markdownify(html_content, heading_style="ATX").replace("\n\n", "\n")
    md_content = re.sub(PAT1, " |", md_content)
    md_content = re.sub(PAT2, "| ", md_content)
    md_content = re.sub(PAT3, "`\n", md_content)
    md_content = re.sub(PAT10, "\n", md_content)
    md_content = re.sub(PAT20, "", md_content)
    md_content = re.sub(PAT30, "", md_content)
    with open(f"../data/md2/{md_file_name}", "w") as f:
        f.write(md_content)

if __name__ == '__main__':
    md_list = os.listdir("../data/md1")
    for md_file_name in md_list:
        refine_md(md_file_name)
    # refine_md("2019-10-20-1006.md")
    # refine_md("2022-03-14-1206.md")
    # refine_md("2021-09-11-1144.md")
    # refine_md("2016-08-08-3.md")
    # refine_md("2016-08-09-4.md")
    # refine_md("2018-08-21-746.md")
    # refine_md("2017-05-01-135.md")
    # refine_md("2023-08-12-1344.md")