from vulcano.app.classes import VulcanoApp


app = VulcanoApp()

@app.command("hi", "Salute people given form parameter")
def salute_method_here(name, title="Mr."):
    print("Hi! {} {} :) Glad to see you.".format(title, name))


@app.command()
def bye(name="User"):
    """ Say goodbye to someone """
    print("Bye {}!".format(name))


if __name__ == '__main__':
    app.run()
