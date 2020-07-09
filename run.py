import json
from collections import ChainMap

from flask import Flask, redirect, render_template, request, flash, url_for
from flask_login import login_user, login_required, logout_user, UserMixin, LoginManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

# Init app
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)


# Models
class ConditionGame:
    """Instance that monitors the game state"""

    _quantity_answers = 2
    _step = 0
    _storyline = 'storyline'

    def get_step(self):
        return self._step

    def get_storyline(self):
        return self._storyline

    def set_step(self, step: int):
        if step >= 0 or step <= 15 and type(step) is int:
            self._step = step

    def set_storyline(self, storyline: str):
        if type(storyline) is str:
            self._storyline = storyline

    def get_quantity_answers(self):
        return self._quantity_answers

    def set_quantity_answers(self, quantity: int):
        if type(quantity) is int:
            self._quantity_answers = quantity


class GameData:
    """Data warehousing questions and answers"""
    DATA = ChainMap(
        {'start_question': ('Вы проснулись в сыром и холодном помещении, чем-то напоминающий подвал, ну или бабушкин '
                            'погреб. Хотя закаток вы тут не обнаружили. И тут сразу же включается экран, в котором вы '
                            'видите какого-то '
                            'психа: - "Привет Билли, я хочу сыграть с тобой в одну игру. Ты ведь любишь играть? Перед '
                            'тобой находится '
                            'будильник. Как только он зазвенит, данное помещение наполнится ядовитым газом. А '
                            'зазвенит он ровно через 2 '
                            'минуты. За эти 2 минуты ты должен найти выход из этого помещения. Аха-ха-ха. ИГРА '
                            'НАЧАЛАСЬ".'),

         'start_answer1': 'Разбить будильник',

         'start_answer2': '5 минут бегать кругами с криками "а-а-а, мы все умрём, а-а-а"',
         },
        {
            'storyline_1_question': ('Вы разбили будильник. Время у вас теперь неограниченно для того чтобы подумать, '
                                     'как выбраться из этого помещения, ну или попытаться всё-таки найти закатки. '
                                     'Вдруг это и правда чей-то '
                                     'погреб. Итак, долго искать вам не пришлось, перед вами 3 двери. <br>На первой '
                                     'двери нарисован лев. <br>На '
                                     'второй двери надпись "зарин" - похоже на чьё-то имя. <br>На третьей двери '
                                     'нарисован мечь.'),

            'storyline_1_answer1': 'Войти в первую дверь',

            'storyline_1_answer2': 'Войти во вторую дверь',

            'storyline_1_answer3': 'Войти в третью дверь'
        },
        {
            'storyline_2_end_message': ('<b>ПОРАЖЕНИЕ!</b> <br><br>Вы бегали кругами издавая крики, покуда не '
                                        'споткнулись об камень и не '
                                        'расшибли себе голову. Умерли вы конечно раньше времени. Ну хоть не от яда, '
                                        'так бы мучались... <br>')
        },
        {
            'storyline_1_1_end_message': ('<b>ПОРАЖЕНИЕ!</b> <br><br>Когда вы вошли в певую дверь, вы обнаружили в '
                                          'ней льва. Всё как и '
                                          'предсказывала сама дверь. Выйти из этой комнаты вы не смогли, так как '
                                          'ручка от двери была только с '
                                          'обратной стороны. Кто кого разтерзал на куски? - спросите вы?.. <br>')
        },
        {
            'storyline_1_2_end_message': ('<b>ПОРАЖЕНИЕ!</b> <br><br>Когда вы открыли дверь и вошли в комнату, '
                                          'вы ничего не обнаружили. Но '
                                          'буквально через несколько секунд вам стало очень плохо, вы стали кашлять и '
                                          'терять сознание. После чего вы '
                                          'наконец-то поняли, что надпись на двери "зарин" - это название ядовитого '
                                          'газа. Сломанный будильник бы '
                                          'никогда не зазвинел, а ядовитого газа вы вдохнули. Молодец, сломали '
                                          'систему... <br>')
        },
        {
            'storyline_1_3_question': ('Когда вы вошли в третью дверь. Вы обнаружили по центру комнаты мечь, немного '
                                       'поразмыслив, вы всё-таки взяли мечь с собой, и тут же вышли из комнаты. В '
                                       'какую дверь дальше?.. '
                                       '<br>В первую дверь с изображением льва '
                                       '<br>Во вторую дверь с надписью "Зарин" '),

            'storyline_1_3_answer1': 'Войти в первую дверь',

            'storyline_1_3_answer2': 'Войти во вторую дверь'
        },
        {
            'storyline_1_3_1_question': ('Когда вы вошли в певую дверь, вы обнаружили в ней льва. Всё как и '
                                         'предсказывала сама дверь. Выйти из этой комнаты вы не смогли, так как ручка '
                                         'от двери была только с '
                                         'обратной стороны, поэтому пришлось сражаться со львом 1 на 1 со своим мечём. '
                                         'Лев напрыгнул на вас, '
                                         'и повалил вас на пол. Вы лежали подо львом 5 минут в шоковом состоянии, '
                                         'не поняв что происходит. '
                                         'Оказывается он напрыгнул прямо на ваш мечь, и сразу же здох. Вы поднялись, '
                                         'и увидели перед собой ещё 2 '
                                         'двери. <br>На первой двери нарисовано лицо(маска) игрока, который всё это '
                                         'затеял. <br>На второй двери написано '
                                         'слово "Не выходить!". <br>Через 5 секунд на экране, который находился в '
                                         'данном помещении, включился таймер '
                                         '"до запуска смертельного газа осталось: 28 секунд". Нужно быстрее что-то '
                                         'предпринять, иначе вам капец. '),

            'storyline_1_3_1_answer1': 'Войти в первую дверь',

            'storyline_1_3_1_answer2': 'Войти во вторую дверь'
        },
        {
            'storyline_1_3_2_end_message': ('<b>ПОРАЖЕНИЕ!</b> <br><br>Когда вы открыли дверь и вошли в комнату, '
                                            'вы ничего не обнаружили. Но '
                                            'буквально через несколько секунд вам стало очень плохо, вы стали кашлять '
                                            'и терять сознание. После чего вы '
                                            'наконец-то поняли, что надпись на двери "зарин" - это название ядовитого '
                                            'газа. Сломанный будильник бы '
                                            'никогда не зазвинел, а ядовитого газа вы вдохнули. Молодец, сломали '
                                            'систему... <br>')
        },
        {
            'storyline_1_3_1_1_question': ('Вы выбили дверь ногой, так как она была закрыта. '
                                           'Перед вами находился создатель этой смертельной игры, и компьютер, '
                                           'на котором он работал, ну или играл…'),

            'storyline_1_3_1_1_answer1': 'Снести ему голову мечём',

            'storyline_1_3_1_1_answer2': ('Договориться с создателем игры, чтобы править его игрой вместе. Игра '
                                          'востребована, и спрос большой, поэтому на ней можно хорошо подняться ')
        },
        {
            'storyline_1_3_1_2_end_message': ('<b>ПОБЕДА!!!</b> <br><br>Вы открыли дверь, и увидели свет яркого '
                                              'солнца, который светил вам в '
                                              'глаза. Молодец, теперь можешь не боятся, что тебя кто-нибудь '
                                              'когда-нибудь похитит, и начнёт с тобой '
                                              'играть в игру, так как ты уже знаешь как нужно побеждать. <br>')
        },
        {
            'storyline_1_3_1_1_1_end_message': ('<b>ПОРАЖЕНИЕ!</b> <br><br>Один взмах, и голова с плеч. '
                                                'Далее вы попытались отключить подачу ядовитого газа, но так и не '
                                                'разобрались в програмном коде. '
                                                'Попытались закрыть дверь, чтобы газ не прошёл, но дверь была выбита '
                                                'с ноги, следовательно она и не закрывалась... '
                                                'Вы постояли, подумали - "лучше б уже с самого начала умер, сразу '
                                                'после прозвона будильника" <br>')
        },
        {
            'storyline_1_3_1_1_2_end_message': ('<b>ПОРАЖЕНИЕ!</b> <br><br>Вы договорились успешно, и начали править '
                                                'этой игрой вместе, '
                                                'но не долго, где-то секунд 10, так как до вас дошёл ядовитый газ, '
                                                'который вы забыли отключить из-за ваших '
                                                'долгих переговоров. <br>')
        }
    )

    def get_start_question(self):
        return self.DATA['start_question']

    def get_start_answer1(self):
        return self.DATA['start_answer1']

    def get_start_answer2(self):
        return self.DATA['start_answer2']

    def get_storyline1_question(self):
        return self.DATA['storyline_1_question']

    def get_storyline1_answer1(self):
        return self.DATA['storyline_1_answer1']

    def get_storyline1_answer2(self):
        return self.DATA['storyline_1_answer2']

    def get_storyline1_answer3(self):
        return self.DATA['storyline_1_answer3']

    def get_storyline2_end_message(self):
        return self.DATA['storyline_2_end_message']

    def get_storyline_1_1_end_message(self):
        return self.DATA['storyline_1_1_end_message']

    def get_storyline_1_2_end_message(self):
        return self.DATA['storyline_1_2_end_message']

    def get_storyline1_3_question(self):
        return self.DATA['storyline_1_3_question']

    def get_storyline1_3_answer1(self):
        return self.DATA['storyline_1_3_answer1']

    def get_storyline1_3_answer2(self):
        return self.DATA['storyline_1_3_answer2']

    def get_storyline1_3_1_question(self):
        return self.DATA['storyline_1_3_1_question']

    def get_storyline1_3_1_answer1(self):
        return self.DATA['storyline_1_3_1_answer1']

    def get_storyline1_3_1_answer2(self):
        return self.DATA['storyline_1_3_1_answer2']

    def get_storyline1_3_2_end_message(self):
        return self.DATA['storyline_1_3_2_end_message']

    def get_storyline1_3_1_1_question(self):
        return self.DATA['storyline_1_3_1_1_question']

    def get_storyline1_3_1_1_answer1(self):
        return self.DATA['storyline_1_3_1_1_answer1']

    def get_storyline1_3_1_1_answer2(self):
        return self.DATA['storyline_1_3_1_1_answer2']

    def get_storyline1_3_1_2_end_message(self):
        return self.DATA['storyline_1_3_1_2_end_message']

    def get_storyline_1_3_1_1_1_end_message(self):
        return self.DATA['storyline_1_3_1_1_1_end_message']

    def get_storyline_1_3_1_1_2_end_message(self):
        return self.DATA['storyline_1_3_1_1_1_end_message']


class Users(db.Model, UserMixin):
    """The model corresponding to the users table in the database"""
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)


class Game:
    """Game process management, data exchange between the user and GameData"""

    def __init__(self, storyline):
        self.storyline = storyline
        self._processed_data()
        self._check_data()

    def _processed_data(self):
        """Comparing data from the current stage of the game and the previous one"""
        try:
            self.current_question = GameData.DATA[self.storyline + '_question']
        except KeyError:
            self.current_question = None
        try:
            self.current_answer1 = GameData.DATA[self.storyline + '_answer1']
        except KeyError:
            self.current_answer1 = None
        try:
            self.current_answer2 = GameData.DATA[self.storyline + '_answer2']
        except KeyError:
            self.current_answer2 = None
        try:
            self.current_answer3 = GameData.DATA[self.storyline + '_answer3']
        except KeyError:
            self.current_answer3 = None

    def _check_data(self):
        """Determining the number of responses, determining the end message, determining the status"""
        counter = -1
        self._data = {}
        if self.current_question is not None:
            counter = 1
            self._data['question'] = self.current_question
            if self.current_answer1 is not None:
                self._data['answer1'] = self.current_answer1
                if self.current_answer2 is not None:
                    counter = 2
                    self._data['answer2'] = self.current_answer2
                    if self.current_answer3 is not None:
                        counter = 3
                        self._data['answer3'] = self.current_answer3
        else:
            self._data['end_message'] = GameData.DATA[self.storyline + '_end_message']

        self._status = counter

    def get_data(self):
        return self._data

    def get_status(self):
        return self._status


def check_answer(selection, quantity_answers):
    """Checking whether the user's selection is correct"""
    if quantity_answers == 2:
        if selection in ('1', '2'):
            return True
        else:
            return False
    elif quantity_answers == 3:
        if selection in ('1', '2', '3'):
            return True
        else:
            return False
    else:
        return False


# Routes
@app.route('/')
def index():
    return render_template('index.html')


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(user_id)


@app.route('/login', methods=['GET', 'POST'])
def login_page():
    login = request.form.get('login')
    password = request.form.get('password')

    if login and password:
        user = Users.query.filter_by(login=login).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            next_page = request.args.get('next')
            if next_page is None:
                return redirect('/')

            return redirect(next_page)

        else:
            flash('Поле логин или пароль заполнено некорректно!')
    else:
        if request.method == 'POST':
            flash('Ошибка авторизации!')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    login = request.form.get('login')
    password = request.form.get('password')
    password2 = request.form.get('password2')

    if request.method == 'POST':
        if not (login or password or password2):
            flash('Пожалуйста заполните все поля')
        elif password != password2:
            flash('Пароль и повтор пароля не совпадают!')
        else:
            hash_pwd = generate_password_hash(password)
            new_user = Users(login=login, password=hash_pwd)
            db.session.add(new_user)
            db.session.commit()

            return redirect(url_for('login_page'))

    return render_template('register.html')


@app.route('/game', methods=['POST', 'GET'])
@login_required
def start_game():
    condition_game.set_step(0)
    condition_game.set_storyline('storyline')
    condition_game.set_quantity_answers(2)

    return render_template('game.html')


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()

    return redirect('/')


@app.route('/start', methods=['GET', 'POST'])
@login_required
def processed_data():
    if condition_game.get_step() == 0:
        selection = request.form['selection']
        if selection == 'Старт':
            condition_game.set_step(1)
            condition_game.set_storyline(condition_game.get_storyline())

            return json.dumps({'question': GameData().get_start_question(), 'answer1': GameData().get_start_answer1(),
                               'answer2': GameData().get_start_answer2()})

    if condition_game.get_step() == 1:
        selection = request.form['selection']
        quantity_answers = condition_game.get_quantity_answers()
        result = check_answer(selection, quantity_answers)
        if result:
            condition_game.set_storyline(condition_game.get_storyline() + '_{}'.format(selection))
            game = Game(condition_game.get_storyline())
            status = game.get_status()
            condition_game.set_quantity_answers(status)
            data = game.get_data()

            if status != -1:
                if status == 2:
                    return json.dumps(
                        {'question': data['question'], 'answer1': data['answer1'], 'answer2': data['answer2']})
                elif status == 3:
                    return json.dumps(
                        {'question': data['question'], 'answer1': data['answer1'], 'answer2': data['answer2'],
                         'answer3': data['answer3']})
            else:
                return json.dumps({'end_message': data['end_message']})


@app.after_request
def redirect_to_signin(response):
    if response.status_code == 401:
        return redirect(url_for('login_page') + '?next=' + request.url)

    return response


# Start app
if __name__ == '__main__':
    condition_game = ConditionGame()
    app.secret_key = 'some secret key'
    app.run(debug=True)
