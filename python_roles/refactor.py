import glob

file_paths = glob.glob("doc/examples/scripts/**/*.py", recursive=True) + \
             glob.glob("doc/tutorial_src/**/*.py", recursive=True) + \
             glob.glob("src/biotite/**/*.py",  recursive=True) + \
             glob.glob("src/biotite/**/*.pyx", recursive=True)

with open("functions") as f:
    function_names = f.read().split()
with open("classes") as f:
    class_names = f.read().split()
class_names.append("ndarray")

for path in file_paths:
    with open(path) as file:
        content = file.read()
    for function_name in function_names:
        content = content.replace(f" `{function_name}()`", f" :func:`{function_name}()`")
        content = content.replace(f"\n`{function_name}()`", f"\n:func:`{function_name}()`")
    for class_name in class_names:
        content = content.replace(f" `{class_name}`", f" :class:`{class_name}`")
        content = content.replace(f"\n`{class_name}`", f"\n:class:`{class_name}`")
    with open(path, "w") as file:
        file.write(content)