
import os
import re
import subprocess

script_dir = os.path.dirname(__file__)
with open(f'{script_dir}/readme.template.md', "r") as f:
    readme_template = f.read()

def render_insert_point(match):
    insert_point_action = match[1]
    if insert_point_action.startswith('`'):
        insert_point_action = insert_point_action[1:-1]
        insert_point_output = subprocess.check_output(insert_point_action, shell=True).decode('utf-8')
        return insert_point_output
    raise Exception("only support action")

if __name__ == '__main__':
    readme_output = re.sub(r'{{insert_point:(.*)}}', render_insert_point, readme_template)
    with open(f'{script_dir}/../README.md', "w") as f:
        f.write(readme_output)
