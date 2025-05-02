
def create_command(path, testfile, interpreter="python"):
    """Create a command to execute a test file using a given path and interpreter."""
    testcode = testfile.read_text()
    if testfile.endswith(".sh"):
        # python3 python_file arg1 arg2 ...
        sh_command = testcode.split([" "])
        command = f"""import subprocess; subprocess.run({sh_command})
        """
        return command

    if path.is_dir():
        assert (path / "src").exists(), f"Source folder {path / 'src'} does not exist"
        module = list((path / "src").iterdir())[0].name
    else:
        module = path.name.removesuffix(".py")

    command = f"""import {module}; {module}.{testcode}
    """
    return command