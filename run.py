from app import init_app


app = init_app()


if __name__ == "__main__":
    #serve(app, host='0.0.0.0', port=22)
    app.run(host='0.0.0.0',port=80)