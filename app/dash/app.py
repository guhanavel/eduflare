import dash
import dash_bootstrap_components as dbc
from dash import html, Input, Output, State, dcc, ctx
from app.algro import main
import youtube_dl
import os
import whisper
import base64
import gc

def dash_app(server):
    gc.collect()
    app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP],
                    title="Eduflare",
                    meta_tags=[{'name': 'viewport',
                                'content': 'width=device-width, initial-scale=1'}],server=server, url_base_pathname='/')




    items = dbc.Row(
        [
            dbc.Col(
                dbc.NavItem(
                    dbc.NavLink("Home", href="/", style={'color': '#000000', })
                )
            ),
            dbc.Col(
                dbc.NavItem(
                    dbc.NavLink("Team", href="/team", style={'color': '#000000', })
                )
            ),
            dbc.Col(
                dbc.NavItem(
                    dbc.NavLink("Contact", href="/contact", style={'color': '#000000', })
                ),
            ),
            dbc.Col(
                dbc.NavItem(
                    html.Button(
                        dbc.NavLink("Try Out", style={'color': '#000000', }, href='/demo'),
                        style={'border-radius': '30px', 'padding': '0px', 'white-space': 'nowrap',
                               'background-color': '#be282e', 'border': 'none'}
                    )
                )
            )
        ],
        className="g-0 ms-auto flex-nowrap mt-3 mt-md-0",
        align="center",
    )
    navbar = dbc.Navbar(
        dbc.Container(
            [
                html.A(
                    # Use row and col to control vertical alignment of logo / brand
                    dbc.Row(
                        [
                            dbc.Col(html.Img(src="../assets/Eduflare Logo.png", height='50px')),

                        ],
                        align="center",
                        className="g-0",
                    ),
                    href="/",
                    style={"textDecoration": "none"},
                ),

                dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                dbc.Collapse(
                    items,
                    id="navbar-collapse",
                    is_open=False,
                    navbar=True,
                ),

            ]
        ),
        color="#04948C",
        dark=True,

    )

    question_type = dcc.RadioItems(
        id='qns_type_language',
        options=[
            {'label': 'Factual', 'value': 'Factual'},
            {'label': 'Nouns', 'value': 'Nouns'},
            {'label':'Tenses','value':'Tenses'}
        ],
        value='Factual',
        labelStyle={'display': 'block'}
    )


    video_card = dbc.Row(
        [dbc.Input(placeholder="Enter Url here", className='me-1', type="url", id='video_link',
                   style={
                       'width': '100%',
                       'textAlign': 'left',

                   }, ),
         html.H1("Or", style={'text-align': 'center'}),
        dcc.Upload(
                id="upload-video",
                children=html.Div(
                    ["Drag and drop or click to select a file to upload."]
                ),
                style={
                    "width": "100%",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin": "10px",
                },
                multiple=False,
            ),
                    html.H4("Question Context"),
                    question_type,

        dcc.Loading(children=[html.Div(id="display_vid")], type="default"),
        dcc.Loading(html.Div(id="video-text"))
         ],
    )

    text_box = html.Div(
        [
            dbc.Textarea(
                id='textarea-example',
                value='',
                placeholder="Enter your text here",
                className="mb-3",
                style={'width': '100%',
                       'height': '250px',
                       'overflow - y': 'scroll',
                       'scrollbar - color': 'rebeccapurple green',
                       'scrollbar - width': 'thin'
                       },
            ),
                html.H4("Question Context"),
                question_type,
        ], id='text-box'
    )

    type = dcc.RadioItems(
        id='qns_type',
        options=[
            {'label': 'MCQ', 'value': 'MCQ'},
            {'label': 'Short Answer', 'value': 'SAQ'},
        ],
        value='MCQ',
        labelStyle={'display': 'block'}
    )




    cards = dbc.Card(
        [
            dbc.CardBody(
                [

                    dbc.Tabs(
                        [
                            dbc.Tab(video_card, label="Video", tab_id="video_tab"),
                            dbc.Tab(text_box, label="Text", tab_id="text_tab"),

                        ],
                        style={'margin-bottom': '5px'},
                        id="input_tab", active_tab= "text_tab",
                    ),

                ]
            ), dbc.CardFooter([type,
                               dbc.Button("Submit", style={'float': 'right'}, id="submit", n_clicks=0, loading_state={'isloading':True}),
                               dbc.Button("Reset", id="reset", n_clicks=0,)])
        ],
        style={"width": "25rem", 'height': '100%'},

    )

    answer = dbc.Card(
        [
            dbc.CardBody(
                [

                    dcc.Loading(
                    html.Div(id="question_sample")),
                    dcc.Loading(
                    html.Div(id="question_sample_vid")),

                ]
            ), dbc.CardFooter([
            #dbc.Button("Save", style={'align': 'center'}),
            dbc.Button("Export", style={'float': 'right'})

        ])
        ],
        style={"width": "40rem", 'height': '100%'},
    )

    body = html.Div(
        children=[dbc.Row([
            dbc.Col(cards, width=4),
            dbc.Col(answer, width=7),
        ])],
        style={'margin-top': '50px', 'margin-left': '100px', 'margin-right': '0px'}
    )
    app.layout = html.Div(children=[body])

    def predict(name,type):
        if type == "MCQ":
            qe= main.QGen()
            payload = {
                   "input_text": name
               }
            output = qe.predict_mcq(payload)
            gc.collect()
            return output['questions']
        elif type == "SAQ":
            qe = main.QGen()
            payload = {
                "input_text": name
            }
            output = qe.predict_shortq(payload)
            gc.collect()
            return output['questions']


    def save_to_mp3(url):
        """Save a YouTube video URL to mp3.

        Args:
            url (str): A YouTube video URL.

        Returns:
            str: The filename of the mp3 file.
        """
        options = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with youtube_dl.YoutubeDL(options) as downloader:
            downloader.download(["" + url + ""])

        return downloader.prepare_filename(downloader.extract_info(url, download=False)).replace(".m4a", ".mp3")

    def save_file(name, content):
        """Decode and store a file uploaded with Plotly Dash."""
        data = content.encode("utf8").split(b";base64,")[1]
        with open(os.path.join(UPLOAD_DIRECTORY, name), "wb") as fp:
            fp.write(base64.decodebytes(data))


    def uploaded_files(name):
        """List the files in the upload directory."""
        files = []
        for filename in os.listdir(UPLOAD_DIRECTORY):
            path = os.path.join(UPLOAD_DIRECTORY, filename)
            if os.path.isfile(path):
                if filename.contains(name.split(".")[0]):
                    return filename
                else:
                    return None



    @app.callback(
        Output("navbar-collapse", "is_open"),
        [Input("navbar-toggler", "n_clicks"), ],
        [State("navbar-collapse", "is_open")],
    )
    def toggle_navbar_collapse(n, is_open):
        if n:
            return not is_open
        return is_open

    @app.callback(
        Output("question_sample","children"),
        Input("input_tab","active_tab"),
        Input("submit","n_clicks"),
        Input("reset","n_clicks"),
        Input("qns_type","value"),
        Input("textarea-example","value"),
        prevent_inital_call =  True
    )
    def question_gen(tab,n_sumbit,n_clicks,qns,text):
        triggered_id = ctx.triggered_id
        if triggered_id == 'submit':
            if tab == 'text_tab':
                prediction = predict(text, qns)
                output = [html.H1("Questions")]
                if qns == "MCQ":
                    counter = 1
                    for pre in prediction:
                        output.append(dbc.Textarea(value=str(counter) + ") " + pre['question_statement']))
                        counter += 1
                        output.append(html.Br())
                        output.append(dbc.Input(value=pre['answer'], style={'color': 'Green'}))
                        for i in pre['options']:
                            output.append(dbc.Input(value=i))
                        output.append(html.Br())
                elif qns == "SAQ":
                    counter = 1
                    for pre in prediction:
                        output.append(dbc.Textarea(value=str(counter) + ") " + pre['Question']))
                        counter += 1
                        output.append(dbc.Input(value=pre['Answer'], style={'color': 'Green'}))
                        output.append(html.Br())
                gc.collect()
                return output
        elif triggered_id == "reset":
            if tab == 'text_tab':
                gc.collect()
                return []
            elif tab == 'video_tab':
                gc.collect()
                return []
    @app.callback(
        Output("textarea-example","value"),
        Input("reset","n_clicks"),
        prevent_inital_call =  True
    )
    def reset(n):
        triggered_id = ctx.triggered_id
        if triggered_id == 'reset':
            return ""

    @app.callback(
        Output("display_vid","children"),
        Input("video_link","value"),
        Input("upload-video","filename"),
        Input("upload-video","contents"),
        Input("submit", "n_clicks"),
        Input("reset","n_clicks"),
        Input("input_tab","active_tab"),
        prevent_inital_call =  True
    )
    def video_show(link,uploaded_filenames, uploaded_file_contents,n,n_r,tab):
        triggered_id = ctx.triggered_id
        if triggered_id == 'submit':
            if tab == 'video_tab':
                new_link = link.replace("watch?v=","embed/")
                return [ html.Br(),
                    html.Iframe(src=new_link,style={'width':'100%','height':345,'align':'center'})]
        elif triggered_id == "reset":
            if tab == 'video_tab':
                return []
        elif triggered_id == "upload-video":
            if tab == 'video_tab':
                if uploaded_filenames is not None and uploaded_file_contents is not None:
                    for name, data in zip(uploaded_filenames, uploaded_file_contents):
                        save_file(name, data)
                files = uploaded_files(uploaded_filenames)
                if files is not None:
                    return [
                        html.Br(),
                        html.Video(scr=files,style={'width':'100%','height':345,'align':'center'})
                    ]


    @app.callback(
        Output("video-text","children"),
        Input("video_link","value"),
        Input("upload-video","filename"),
        Input("upload-video","contents"),
        Input("submit", "n_clicks"),
        Input("reset","n_clicks"),
        Input("input_tab","active_tab"),
        prevent_inital_call =  True
    )
    def video_trans(link,uploaded_filenames, uploaded_file_contents,n,n_r,tab):
        triggered_id = ctx.triggered_id
        if triggered_id == 'submit':
            if tab == 'video_tab':
                mp3_file = save_to_mp3(link)
                model = whisper.load_model("small")
                result = model.transcribe(mp3_file, fp16=False)
                gc.collect()
                return [
                    html.Br(),
                    dbc.Textarea(value=result['text'],id="trans",style={'width': '100%',
                       'height': '250px',
                       'overflow - y': 'scroll',
                       'scrollbar - color': 'rebeccapurple green',
                       'scrollbar - width': 'thin'
                       },)
                ]
        elif triggered_id == 'reset':
            if tab == 'video_tab':
                return []
        elif triggered_id == "upload-video":
            model = whisper.load_model("base")
            result = model.transcribe(uploaded_files(uploaded_filenames), fp16=False)
            return [
                html.Br(),
                dbc.Textarea(value=result['text'], id="trans")
            ]

    @app.callback(
        Output("question_sample_vid","children"),
        Input("trans","value"),
        Input("qns_type","value"),
    )
    def generate(text,qns):
        prediction = predict(text, qns)
        output = [html.H1("Questions")]
        if qns == "MCQ":
            counter = 1
            for pre in prediction:
                output.append(dbc.Textarea(value=str(counter) + ") " + pre['question_statement']))
                counter += 1
                output.append(html.Br())
                output.append(dbc.Input(value=pre['answer'], style={'color': 'Green'}))
                for i in pre['options']:
                    output.append(dbc.Input(value=i))
                output.append(html.Br())
        elif qns == "SAQ":
            counter = 1
            for pre in prediction:
                output.append(dbc.Textarea(value=str(counter) + ") " + pre['Question']))
                counter += 1
                output.append(dbc.Input(value=pre['Answer'], style={'color': 'Green'}))
                output.append(html.Br())
        gc.collect()
        return output
    return app.server

