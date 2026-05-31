def run():
    import sys
    from client.app import GameSaveApplication
    app = GameSaveApplication(sys.argv)
    sys.exit(app.run())


if __name__ == "__main__":
    run()
