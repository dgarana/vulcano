from vulcano.app.classes import VulcanoApp


app = VulcanoApp()

@app.register("another_command")
def my_command():
    """ This is just The help """
    print("This is my command")


if __name__ == '__main__':
    app.run()