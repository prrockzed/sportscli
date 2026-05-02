import typer

app = typer.Typer()

@app.command()
def cricket():
    print("Fetching cricket scores...")

@app.command()
def chess():
    print("Fetching chess tournaments...")

if __name__ == "__main__":
    app()
