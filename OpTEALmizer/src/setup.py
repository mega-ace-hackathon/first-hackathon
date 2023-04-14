from subprocess import run

def install(*packages):
    return run(["pip", "install", *packages])

def install_requirements():
    return run(["pip", "install", "-r", "requirements.txt"])

install_requirements()

# Tealer is a static analysis tool that includes a TEAL parser that may be
# useful to reuse
install("git+https://github.com/crytic/tealer.git")
