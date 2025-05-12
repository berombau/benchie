def create_command(path, testfile, generic=False):
    """Create a command to execute a test file using a given path and interpreter."""
    testcode = testfile.read_text()
    if testfile.name.endswith(".sh"):
        # python3 python_file arg1 arg2 ...
        sh_command = "[" + ", ".join(f'"{item}"' for item in testcode.strip().split(" ")) + "]"
        command = f"""import subprocess; subprocess.run({sh_command})"""
        return command

    if generic:
        return (
            "import {module}; {module}.{"
            + testcode
            + "} \
        "
        )

    if path.is_dir():
        assert (path / "src").exists(), f"Source folder {path / 'src'} does not exist"
        module = list((path / "src").iterdir())[0].name
    else:
        module = path.name.removesuffix(".py")

    command = f"""import {module}; {module}.{testcode}
    """
    return command
