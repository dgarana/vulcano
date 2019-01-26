from vulcano.app.classes import VulcanoApp


app = VulcanoApp()

@app.register("another_command")
def my_command(arg_1, agument_2="Hello"):
    """ This is just The help """
    print(arg_1)
    print(agument_2)


if __name__ == '__main__':
    app.run()